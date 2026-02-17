"""Mutation testing tool for documents based on Assumption Mutation pattern and MutaDoc.

Applies 5 mutation strategies (contradiction, ambiguity, deletion, inversion, boundary)
to detect hidden vulnerabilities in documents. Supports preset configurations for
different document types (contract, API spec, academic paper, policy).

Zero-infrastructure: standard library only, no LLM API calls.
"""
import json
import re
import time
from pathlib import Path
from typing import Any

CQ_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent

# ============================================================
# Vague modifier catalog (Ambiguity strategy)
# ============================================================
VAGUE_MODIFIERS: list[str] = [
    "appropriate", "reasonable", "sufficient", "timely", "adequate",
    "significant", "substantial", "promptly", "approximately", "generally",
    "normally", "typically", "usually", "fairly", "properly", "suitably",
    "as needed", "as appropriate", "where applicable", "to the extent possible",
    "best efforts", "commercially reasonable", "good faith", "material",
    "immaterial", "de minimis", "nominal", "undue", "excessive", "unreasonable",
    "satisfactory", "acceptable", "moderate", "suitable", "proper",
]

# ============================================================
# Claim/assumption indicators (Inversion strategy)
# ============================================================
CLAIM_INDICATORS: list[str] = [
    "we assume", "it is expected", "based on", "given that",
    "assuming", "in our view", "we believe", "it appears",
    "this suggests", "evidence indicates", "the data shows",
    "we hypothesize", "it is likely", "presumably",
]

# ============================================================
# Obligation keywords for severity escalation
# ============================================================
OBLIGATION_KEYWORDS = re.compile(
    r"\b(shall|must|obligat|required|entitled|rights?|deadline|within\s+\d+\s*days?)\b",
    re.IGNORECASE,
)
SCOPE_KEYWORDS = re.compile(
    r"\b(scope|defin|means|includ|condition|criteria)\b",
    re.IGNORECASE,
)
STRONG_OBLIGATION_KEYWORDS = re.compile(
    r"\b(shall|must|certif|warrant|guarant)\b",
    re.IGNORECASE,
)
EVIDENCE_KEYWORDS = re.compile(
    r"\b(because|therefore|evidence|data shows|according to|based on|proven|"
    r"demonstrated|research|study|analysis|since|due to)\b",
    re.IGNORECASE,
)
CRITICAL_BOUNDARY_KEYWORDS = re.compile(
    r"\b(shall|must|obligat|required|SLA|uptime|deadline|penalty|liability|"
    r"cap|limit|maximum|minimum)\b",
    re.IGNORECASE,
)
MAJOR_BOUNDARY_KEYWORDS = re.compile(
    r"\b(should|recommend|target|goal|expect|estimate)\b",
    re.IGNORECASE,
)

# Numeric parameter pattern
NUMERIC_PARAM_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*"
    r"(days?|hours?|minutes?|seconds?|percent|%|USD|\$|EUR|€|months?|years?|"
    r"weeks?|business\s*days?|times?|attempts?|retries?)",
    re.IGNORECASE,
)

# Range pattern
RANGE_RE = re.compile(
    r"(?:between|from)\s+(\d+(?:\.\d+)?)\s*(?:and|to)\s+(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# Section heading pattern
SECTION_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)

# Severity ordering
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3}


def _parse_sections(content: str) -> list[dict[str, Any]]:
    """Parse markdown into sections with line numbers."""
    lines = content.split("\n")
    sections: list[dict[str, Any]] = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            sections.append({
                "level": len(m.group(1)),
                "name": m.group(2).strip(),
                "start_line": i + 1,
                "end_line": 0,
            })
    # Set end lines
    for i, sec in enumerate(sections):
        if i + 1 < len(sections):
            sec["end_line"] = sections[i + 1]["start_line"] - 1
        else:
            sec["end_line"] = len(lines)
    return sections


def _get_section_text(lines: list[str], start: int, end: int) -> str:
    """Get text between line numbers (1-indexed)."""
    return "\n".join(lines[start - 1:end])


def _get_context(lines: list[str], line_num: int, window: int = 5) -> str:
    """Get context lines around a line number (1-indexed)."""
    start = max(0, line_num - 1 - window)
    end = min(len(lines), line_num + window)
    return "\n".join(lines[start:end])


def _find_section_for_line(sections: list[dict[str, Any]], line_num: int) -> str:
    """Find which section a line belongs to."""
    for sec in reversed(sections):
        if line_num >= sec["start_line"]:
            return sec["name"]
    return "Document"


def _load_preset(preset_name: str) -> dict[str, Any]:
    """Load a preset configuration from mutadoc/presets/."""
    preset_path = CQ_ENGINE_ROOT / "mutadoc" / "presets" / f"{preset_name}.md"
    if not preset_path.exists():
        return {}
    text = preset_path.read_text(encoding="utf-8")
    # Extract YAML front matter between --- lines
    parts = text.split("---")
    if len(parts) < 3:
        return {}
    front_matter = parts[1].strip()
    # Simple YAML parsing (no PyYAML dependency)
    config: dict[str, Any] = {}
    config["strategies"] = {}
    config["severity_overrides"] = {}
    current_block = ""
    for line in front_matter.split("\n"):
        stripped = line.strip()
        if stripped.startswith("name:"):
            config["name"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("default_persona:"):
            config["default_persona"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped == "strategies:":
            current_block = "strategies"
        elif stripped == "severity_overrides:":
            current_block = "severity_overrides"
        elif stripped == "domain_terminology:":
            current_block = "domain_terminology"
        elif stripped == "output_format:":
            current_block = ""
        elif current_block == "strategies" and ":" in stripped:
            strat_name = stripped.split(":")[0].strip()
            if strat_name in ("contradiction", "ambiguity", "deletion", "inversion", "boundary"):
                weight_m = re.search(r"weight:\s*([\d.]+)", stripped)
                enabled_m = re.search(r"enabled:\s*(true|false)", stripped)
                config["strategies"][strat_name] = {
                    "weight": float(weight_m.group(1)) if weight_m else 1.0,
                    "enabled": enabled_m.group(1) == "true" if enabled_m else True,
                }
        elif current_block == "severity_overrides" and ":" in stripped:
            key, val = stripped.split(":", 1)
            config["severity_overrides"][key.strip().strip("- ")] = val.strip().strip('"')
    return config


def _severity_meets_threshold(severity: str, threshold: str) -> bool:
    """Check if a severity level meets or exceeds the threshold."""
    return SEVERITY_ORDER.get(severity.lower(), 3) <= SEVERITY_ORDER.get(threshold.lower(), 3)


# ============================================================
# Strategy: Contradiction
# ============================================================
def _run_contradiction(lines: list[str], sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect cross-section contradictions via numeric and modal verb analysis."""
    mutations: list[dict[str, Any]] = []
    content = "\n".join(lines)

    # 1. Numeric contradiction: same unit, different values across sections
    seen_values: dict[str, list[tuple[str, int, str]]] = {}
    for i, line in enumerate(lines):
        for m in NUMERIC_PARAM_RE.finditer(line):
            val = m.group(1)
            unit = m.group(2).lower().rstrip("s")
            # Normalize units
            if unit in ("%", "percent"):
                unit = "percent"
            key = unit
            section_name = _find_section_for_line(sections, i + 1)
            seen_values.setdefault(key, []).append((val, i + 1, section_name))

    reported_pairs: set[tuple[str, str]] = set()
    for unit, occurrences in seen_values.items():
        if len(occurrences) < 2:
            continue
        for a_idx in range(len(occurrences)):
            for b_idx in range(a_idx + 1, len(occurrences)):
                val_a, line_a, sec_a = occurrences[a_idx]
                val_b, line_b, sec_b = occurrences[b_idx]
                if val_a == val_b:
                    continue
                if sec_a == sec_b:
                    continue
                pair_key = (min(val_a, val_b), max(val_a, val_b))
                if pair_key in reported_pairs:
                    continue
                reported_pairs.add(pair_key)
                mutations.append({
                    "id": "",
                    "strategy": "contradiction",
                    "location": {"line": line_a, "section": sec_a},
                    "original": f"{val_a} {unit} (line {line_a}) vs {val_b} {unit} (line {line_b})",
                    "mutated": f"Conflicting values for '{unit}': {val_a} vs {val_b}",
                    "severity": "major",
                    "detected": False,
                    "_desc": f"Potentially conflicting values: '{val_a} {unit}' in {sec_a} vs '{val_b} {unit}' in {sec_b}",
                })

    # 2. Modal verb contradiction: "shall" vs "shall not" for same subject
    shall_lines: list[tuple[int, str, str]] = []
    shall_not_lines: list[tuple[int, str, str]] = []
    shall_re = re.compile(r"(\w+)\s+shall\b(?!\s+not\b)", re.IGNORECASE)
    shall_not_re = re.compile(r"(\w+)\s+(?:shall\s+not|shall\s+never|must\s+not)\b", re.IGNORECASE)

    for i, line in enumerate(lines):
        for m in shall_re.finditer(line):
            shall_lines.append((i + 1, m.group(1).lower(), line.strip()))
        for m in shall_not_re.finditer(line):
            shall_not_lines.append((i + 1, m.group(1).lower(), line.strip()))

    for pos_line, pos_subj, pos_text in shall_lines:
        for neg_line, neg_subj, neg_text in shall_not_lines:
            if pos_subj == neg_subj and pos_line != neg_line:
                mutations.append({
                    "id": "",
                    "strategy": "contradiction",
                    "location": {"line": pos_line, "section": _find_section_for_line(sections, pos_line)},
                    "original": pos_text,
                    "mutated": f"'{pos_subj}' has both affirmative (line {pos_line}) and negative (line {neg_line}) obligations",
                    "severity": "critical",
                    "detected": False,
                    "_desc": f"Same subject '{pos_subj}' with contradictory modal verbs",
                })

    return mutations


# ============================================================
# Strategy: Ambiguity
# ============================================================
def _run_ambiguity(lines: list[str], sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect vague modifiers and assess severity based on context."""
    mutations: list[dict[str, Any]] = []

    for modifier in VAGUE_MODIFIERS:
        pattern = re.compile(r"\b" + re.escape(modifier) + r"\b", re.IGNORECASE)
        for i, line in enumerate(lines):
            if pattern.search(line):
                line_num = i + 1
                severity = "minor"
                if OBLIGATION_KEYWORDS.search(line):
                    severity = "critical"
                elif SCOPE_KEYWORDS.search(line):
                    severity = "major"

                section_name = _find_section_for_line(sections, line_num)
                context = _get_context(lines, line_num, window=5)

                mutations.append({
                    "id": "",
                    "strategy": "ambiguity",
                    "location": {"line": line_num, "section": section_name},
                    "original": line.strip(),
                    "mutated": f"'{modifier}' → extreme test: replace with 'zero' or 'unlimited'",
                    "severity": severity,
                    "detected": False,
                    "_desc": f"Vague modifier '{modifier}' — meaning is undefined and open to interpretation",
                })

    return mutations


# ============================================================
# Strategy: Deletion
# ============================================================
def _run_deletion(lines: list[str], sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find dead clauses via cross-reference counting."""
    mutations: list[dict[str, Any]] = []
    full_text = "\n".join(lines)

    for i, sec in enumerate(sections):
        name = sec["name"]
        start = sec["start_line"]
        end = sec["end_line"]

        # Count references to this section name from outside the section
        name_escaped = re.escape(name)
        ref_count = 0

        # Text before section
        if start > 1:
            before_text = "\n".join(lines[:start - 1])
            ref_count += len(re.findall(name_escaped, before_text, re.IGNORECASE))

        # Text after section
        if end < len(lines):
            after_text = "\n".join(lines[end:])
            ref_count += len(re.findall(name_escaped, after_text, re.IGNORECASE))

        if ref_count == 0:
            mutations.append({
                "id": "",
                "strategy": "deletion",
                "location": {"line": start, "section": name},
                "original": f"Section '{name}' ({end - start + 1} lines)",
                "mutated": f"Remove section '{name}' and observe: zero structural impact",
                "severity": "minor",
                "detected": True,
                "_desc": f"Dead clause — no other section references '{name}' (impact score: 0)",
            })
        elif ref_count >= 3:
            mutations.append({
                "id": "",
                "strategy": "deletion",
                "location": {"line": start, "section": name},
                "original": f"Section '{name}' ({end - start + 1} lines)",
                "mutated": f"Remove section '{name}': {ref_count} sections would lose a dependency",
                "severity": "major",
                "detected": True,
                "_desc": f"Critical dependency — {ref_count} other sections reference '{name}'",
            })

    return mutations


# ============================================================
# Strategy: Inversion
# ============================================================
def _run_inversion(lines: list[str], sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect unsupported claims vulnerable to inversion."""
    mutations: list[dict[str, Any]] = []

    for indicator in CLAIM_INDICATORS:
        pattern = re.compile(r"\b" + re.escape(indicator) + r"\b", re.IGNORECASE)
        for i, line in enumerate(lines):
            if pattern.search(line):
                line_num = i + 1
                context = _get_context(lines, line_num, window=3)
                has_evidence = bool(EVIDENCE_KEYWORDS.search(context))

                if not has_evidence:
                    severity = "major"
                    if STRONG_OBLIGATION_KEYWORDS.search(line):
                        severity = "critical"

                    section_name = _find_section_for_line(sections, line_num)
                    mutations.append({
                        "id": "",
                        "strategy": "inversion",
                        "location": {"line": line_num, "section": section_name},
                        "original": line.strip(),
                        "mutated": f"Invert: if the opposite of '{indicator}...' were true, does the document hold?",
                        "severity": severity,
                        "detected": False,
                        "_desc": f"Claim '{indicator}...' has no supporting evidence — vulnerable to inversion",
                    })

    return mutations


# ============================================================
# Strategy: Boundary
# ============================================================
def _run_boundary(lines: list[str], sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze numeric parameter sensitivity at boundaries."""
    mutations: list[dict[str, Any]] = []

    for i, line in enumerate(lines):
        for m in NUMERIC_PARAM_RE.finditer(line):
            val_str = m.group(1)
            unit = m.group(2)
            line_num = i + 1

            try:
                val = float(val_str)
            except ValueError:
                continue

            val_10x = val * 10
            val_01x = val / 10 if val != 0 else 0

            # Format values
            fmt_10x = f"{val_10x:g}"
            fmt_01x = f"{val_01x:g}"

            severity = "minor"
            if CRITICAL_BOUNDARY_KEYWORDS.search(line):
                severity = "critical"
            elif MAJOR_BOUNDARY_KEYWORDS.search(line):
                severity = "major"

            section_name = _find_section_for_line(sections, line_num)
            mutations.append({
                "id": "",
                "strategy": "boundary",
                "location": {"line": line_num, "section": section_name},
                "original": f"{val_str} {unit}",
                "mutated": f"Boundary test: 10x={fmt_10x} {unit}, 0.1x={fmt_01x} {unit}",
                "severity": severity,
                "detected": False,
                "_desc": f"Numeric parameter '{val_str} {unit}' — boundary sensitivity test",
            })

        # Also check for range expressions
        for m in RANGE_RE.finditer(line):
            low_str = m.group(1)
            high_str = m.group(2)
            line_num = i + 1
            section_name = _find_section_for_line(sections, line_num)
            mutations.append({
                "id": "",
                "strategy": "boundary",
                "location": {"line": line_num, "section": section_name},
                "original": f"Range {low_str} to {high_str}",
                "mutated": f"Boundary: what if below {low_str} or above {high_str}?",
                "severity": "major",
                "detected": False,
                "_desc": f"Range boundary — behavior undefined outside [{low_str}, {high_str}]",
            })

    return mutations


# ============================================================
# Kill score calculation
# ============================================================
def _check_cqlint_detection(target_path: str) -> bool:
    """Check if cqlint.sh exists and can detect mutations. Returns False if unavailable."""
    cqlint_path = CQ_ENGINE_ROOT / "cqlint" / "cqlint.sh"
    return cqlint_path.exists()


def _calculate_kill_score(mutations: list[dict[str, Any]]) -> float:
    """Calculate mutation kill score as percentage of detected mutations."""
    if not mutations:
        return 100.0
    detected = sum(1 for m in mutations if m.get("detected", False))
    return round(detected / len(mutations) * 100, 1)


# ============================================================
# Main tool function
# ============================================================
async def mutate(
    target_path: str,
    strategies: str = "all",
    severity_threshold: str = "minor",
    preset: str = "",
) -> str:
    """Run mutation testing on a document to detect hidden vulnerabilities.

    Applies 5 mutation strategies (contradiction, ambiguity, deletion, inversion,
    boundary) to identify unverified assumptions, vague language, contradictions,
    dead clauses, and fragile numeric parameters.

    Args:
        target_path: Path to the document file to test (Markdown or plain text).
        strategies: Comma-separated strategy names or "all". Options:
            contradiction, ambiguity, deletion, inversion, boundary.
        severity_threshold: Minimum severity to include in results.
            Options: info, minor, major, critical.
        preset: Optional document type preset. Options:
            contract, api_spec, academic_paper, policy.

    Returns:
        JSON string with mutation results including findings, kill score, and summary.
    """
    start_time = time.time()

    # Validate target file
    target = Path(target_path)
    if not target.exists():
        return json.dumps({"error": f"File not found: {target_path}"}, indent=2)
    if not target.is_file():
        return json.dumps({"error": f"Not a file: {target_path}"}, indent=2)

    content = target.read_text(encoding="utf-8")
    lines = content.split("\n")
    sections = _parse_sections(content)

    # Load preset if specified
    preset_config: dict[str, Any] = {}
    if preset:
        preset_config = _load_preset(preset)
        if not preset_config:
            return json.dumps({"error": f"Preset not found: {preset}"}, indent=2)

    # Determine active strategies
    all_strategies = ["contradiction", "ambiguity", "deletion", "inversion", "boundary"]
    if strategies == "all":
        active_strategies = all_strategies[:]
    else:
        active_strategies = [s.strip().lower() for s in strategies.split(",")]
        invalid = [s for s in active_strategies if s not in all_strategies]
        if invalid:
            return json.dumps(
                {"error": f"Unknown strategies: {', '.join(invalid)}. Valid: {', '.join(all_strategies)}"},
                indent=2,
            )

    # Filter by preset-enabled strategies
    if preset_config.get("strategies"):
        active_strategies = [
            s for s in active_strategies
            if preset_config["strategies"].get(s, {}).get("enabled", True)
        ]

    # Run strategies
    all_mutations: list[dict[str, Any]] = []

    strategy_runners = {
        "contradiction": _run_contradiction,
        "ambiguity": _run_ambiguity,
        "deletion": _run_deletion,
        "inversion": _run_inversion,
        "boundary": _run_boundary,
    }

    for strat_name in active_strategies:
        runner = strategy_runners.get(strat_name)
        if runner:
            strat_mutations = runner(lines, sections)
            all_mutations.extend(strat_mutations)

    # Apply severity overrides from preset
    if preset_config.get("severity_overrides"):
        overrides = preset_config["severity_overrides"]
        for mut in all_mutations:
            if mut["strategy"] == "ambiguity" and OBLIGATION_KEYWORDS.search(mut.get("original", "")):
                if "ambiguity_in_obligation" in overrides:
                    mut["severity"] = overrides["ambiguity_in_obligation"].lower()
            if mut["strategy"] == "contradiction":
                if "contradictory_clauses" in overrides:
                    mut["severity"] = overrides["contradictory_clauses"].lower()

    # Filter by severity threshold
    all_mutations = [
        m for m in all_mutations
        if _severity_meets_threshold(m["severity"], severity_threshold)
    ]

    # Assign IDs
    for idx, mut in enumerate(all_mutations):
        mut["id"] = f"M{idx + 1:03d}"

    # Separate surviving vs killed
    surviving = [m for m in all_mutations if not m.get("detected", False)]
    killed = [m for m in all_mutations if m.get("detected", False)]

    # Calculate kill score
    kill_score = _calculate_kill_score(all_mutations)

    # Build summary by strategy
    by_strategy: dict[str, int] = {}
    for m in all_mutations:
        strat = m["strategy"]
        by_strategy[strat] = by_strategy.get(strat, 0) + 1

    # Build summary by severity
    by_severity: dict[str, int] = {}
    for m in all_mutations:
        sev = m["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1

    elapsed = round(time.time() - start_time, 3)

    # Clean internal fields from output
    output_mutations = []
    for m in all_mutations:
        out = {
            "id": m["id"],
            "strategy": m["strategy"],
            "location": m["location"],
            "original": m["original"],
            "mutated": m["mutated"],
            "severity": m["severity"],
            "detected": m["detected"],
        }
        output_mutations.append(out)

    surviving_output = [
        {
            "id": m["id"],
            "strategy": m["strategy"],
            "location": m["location"],
            "original": m["original"],
            "mutated": m["mutated"],
            "severity": m["severity"],
        }
        for m in surviving
    ]

    result = {
        "mutations": output_mutations,
        "kill_score": kill_score,
        "surviving_mutations": surviving_output,
        "summary": {
            "total": len(all_mutations),
            "killed": len(killed),
            "survived": len(surviving),
            "by_strategy": by_strategy,
            "by_severity": by_severity,
        },
        "metadata": {
            "target": str(target_path),
            "strategies_applied": active_strategies,
            "severity_threshold": severity_threshold,
            "preset": preset if preset else None,
            "sections_analyzed": len(sections),
            "lines_analyzed": len(lines),
            "elapsed_seconds": elapsed,
        },
    }

    return json.dumps(result, indent=2)
