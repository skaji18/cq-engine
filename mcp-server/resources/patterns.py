"""CQE Pattern catalog resource.

Provides the cq_engine://patterns resource — a structured index of all
CQE patterns with names, summaries, and file locations.
"""

import json
import re
from pathlib import Path

CQ_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent
PATTERNS_DIR = CQ_ENGINE_ROOT / "patterns"


def _extract_summary(content: str) -> str:
    """Extract the first meaningful paragraph after the H1 heading."""
    lines = content.split("\n")
    in_header = True
    paragraph_lines: list[str] = []
    for line in lines:
        # Skip the H1 line itself
        if in_header and line.startswith("# "):
            in_header = False
            continue
        if in_header:
            continue
        # Skip classification block, blank lines, and front matter
        stripped = line.strip()
        if not stripped:
            if paragraph_lines:
                break  # End of first paragraph
            continue
        if stripped.startswith("##"):
            if paragraph_lines:
                break
            continue
        if stripped.startswith("- **") or stripped.startswith(">"):
            continue
        if stripped.startswith("---"):
            continue
        paragraph_lines.append(stripped)

    summary = " ".join(paragraph_lines)
    # Truncate to a reasonable length
    if len(summary) > 300:
        summary = summary[:297] + "..."
    return summary


def _extract_title(content: str) -> str:
    """Extract the pattern name from the H1 heading."""
    match = re.search(r"^#\s+Pattern:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback: any H1
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def _extract_classification(content: str) -> dict:
    """Extract weight and evidence level from Classification section."""
    result: dict[str, str] = {}
    weight_match = re.search(
        r"\*\*Weight\*\*:\s*(\w+)", content
    )
    if weight_match:
        result["weight"] = weight_match.group(1)
    evidence_match = re.search(
        r"\*\*Evidence Level\*\*:\s*(\w)", content
    )
    if evidence_match:
        result["evidence_level"] = evidence_match.group(1)
    category_match = re.search(
        r"\*\*Category\*\*:\s*(\w+)", content
    )
    if category_match:
        result["category"] = category_match.group(1)
    return result


async def patterns_catalog() -> str:
    """Provide the CQE Pattern catalog.

    Returns a JSON object listing all patterns with their names,
    file locations, summaries, and classification metadata.
    """
    if not PATTERNS_DIR.is_dir():
        return json.dumps(
            {
                "patterns": [],
                "total": 0,
                "version": "v0.1",
                "error": f"Patterns directory not found: {PATTERNS_DIR}",
            },
            indent=2,
        )

    pattern_files = sorted(PATTERNS_DIR.glob("[0-9][0-9]_*.md"))
    patterns = []

    for pf in pattern_files:
        content = pf.read_text(encoding="utf-8")
        pattern_id = pf.stem.split("_")[0]  # "01", "02", etc.
        name = _extract_title(content)
        summary = _extract_summary(content)
        classification = _extract_classification(content)

        patterns.append({
            "id": pattern_id,
            "name": name,
            "file": pf.name,
            "summary": summary,
            **classification,
        })

    # Include README if it exists
    readme_path = PATTERNS_DIR / "README.md"
    readme_summary = ""
    if readme_path.is_file():
        readme_content = readme_path.read_text(encoding="utf-8")
        readme_summary = _extract_summary(readme_content)

    result = {
        "patterns": patterns,
        "total": len(patterns),
        "version": "v0.1",
    }
    if readme_summary:
        result["catalog_description"] = readme_summary

    return json.dumps(result, indent=2)
