"""MCP wrapper for cqlint — Cognitive Quality Linter.

Runs cqlint.sh as a subprocess and returns structured results.
Maps to CQE Patterns CQ001-CQ005.
"""

import asyncio
import json
from pathlib import Path

CQ_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent
CQLINT_PATH = CQ_ENGINE_ROOT / "cqlint" / "cqlint.sh"


async def cqlint(
    target_path: str,
    rules: str = "all",
    output_format: str = "text",
) -> str:
    """Run cognitive quality linter on a file or directory.

    Args:
        target_path: Path to the file or directory to lint.
        rules: Comma-separated rule IDs (e.g., "CQ001,CQ003") or "all".
        output_format: Output format — "text", "json", or "markdown".
    """
    # Validate cqlint.sh exists
    if not CQLINT_PATH.is_file():
        return json.dumps(
            {
                "violations": [],
                "summary": {"errors": 0, "warnings": 0, "info": 0},
                "passed": True,
                "note": f"cqlint.sh not found at {CQLINT_PATH}",
            },
            indent=2,
        )

    # Validate target path exists
    target = Path(target_path)
    if not target.exists():
        return json.dumps(
            {
                "error": f"Target path does not exist: {target_path}",
                "violations": [],
                "summary": {"errors": 0, "warnings": 0, "info": 0},
                "passed": True,
            },
            indent=2,
        )

    # Build command arguments
    cmd = ["bash", str(CQLINT_PATH), "check", str(target), "--format", "json"]

    if rules != "all":
        # cqlint.sh accepts --rule CQ001 for single rule
        # For multiple rules, call once per rule and merge results
        rule_list = [r.strip() for r in rules.split(",") if r.strip()]
        if len(rule_list) == 1:
            cmd.extend(["--rule", rule_list[0]])

    # Execute cqlint.sh
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=30
        )
    except asyncio.TimeoutError:
        return json.dumps(
            {
                "error": "cqlint.sh timed out after 30 seconds",
                "violations": [],
                "summary": {"errors": 0, "warnings": 0, "info": 0},
                "passed": True,
            },
            indent=2,
        )
    except OSError as exc:
        return json.dumps(
            {
                "error": f"Failed to execute cqlint.sh: {exc}",
                "violations": [],
                "summary": {"errors": 0, "warnings": 0, "info": 0},
                "passed": True,
            },
            indent=2,
        )

    raw_output = stdout.decode("utf-8", errors="replace").strip()

    # Parse JSON output from cqlint.sh
    violations = []
    if raw_output:
        try:
            parsed = json.loads(raw_output)
            # cqlint.sh JSON output may be the full result or just an array
            if isinstance(parsed, list):
                violations = parsed
            elif isinstance(parsed, dict):
                violations = parsed.get("violations", parsed.get("results", []))
        except json.JSONDecodeError:
            # Fallback: parse text output line by line
            violations = _parse_text_output(raw_output)

    # Filter by rules if multiple were specified
    if rules != "all":
        rule_set = {r.strip().upper() for r in rules.split(",") if r.strip()}
        violations = [
            v for v in violations
            if v.get("rule", "").upper() in rule_set
        ]

    # Build summary
    errors = sum(1 for v in violations if v.get("severity") == "error")
    warnings = sum(1 for v in violations if v.get("severity") == "warning")
    info = sum(1 for v in violations if v.get("severity") == "info")

    result = {
        "violations": violations,
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "info": info,
        },
        "passed": errors == 0,
    }

    # Format output
    if output_format == "markdown":
        result["formatted"] = _format_markdown(violations, result["passed"])
    elif output_format == "text":
        result["formatted"] = _format_text(violations, result["passed"])

    return json.dumps(result, indent=2)


def _parse_text_output(text: str) -> list[dict]:
    """Parse cqlint.sh text output into structured violations."""
    violations = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Attempt to parse lines like: [ERROR] CQ002 file.yaml:10 message
        parts = line.split(None, 3)
        if len(parts) >= 3:
            severity_raw = parts[0].strip("[]").lower()
            if severity_raw in ("error", "warning", "info"):
                rule = parts[1] if len(parts) > 1 else ""
                location = parts[2] if len(parts) > 2 else ""
                message = parts[3] if len(parts) > 3 else ""
                file_name = ""
                line_num = 0
                if ":" in location:
                    file_name, _, line_str = location.partition(":")
                    try:
                        line_num = int(line_str)
                    except ValueError:
                        file_name = location
                else:
                    file_name = location
                violations.append({
                    "rule": rule,
                    "severity": severity_raw,
                    "file": file_name,
                    "line": line_num,
                    "message": message,
                })
    return violations


def _format_markdown(violations: list[dict], passed: bool) -> str:
    """Format violations as Markdown."""
    lines = ["# cqlint Results\n"]
    if passed:
        lines.append("**Status**: PASSED\n")
    else:
        lines.append("**Status**: FAILED\n")
    if not violations:
        lines.append("No violations found.\n")
        return "\n".join(lines)
    lines.append("| Rule | Severity | File | Line | Message |")
    lines.append("|------|----------|------|------|---------|")
    for v in violations:
        lines.append(
            f"| {v.get('rule', '')} | {v.get('severity', '')} "
            f"| {v.get('file', '')} | {v.get('line', '')} "
            f"| {v.get('message', '')} |"
        )
    return "\n".join(lines)


def _format_text(violations: list[dict], passed: bool) -> str:
    """Format violations as plain text."""
    lines = []
    for v in violations:
        severity = v.get("severity", "").upper()
        rule = v.get("rule", "")
        file_name = v.get("file", "")
        line_num = v.get("line", "")
        message = v.get("message", "")
        loc = f"{file_name}:{line_num}" if line_num else file_name
        lines.append(f"[{severity}] {rule} {loc} {message}")
    if not lines:
        lines.append("No violations found.")
    status = "PASSED" if passed else "FAILED"
    lines.append(f"\nStatus: {status}")
    return "\n".join(lines)
