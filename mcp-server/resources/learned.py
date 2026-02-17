"""Accumulated learning resource.

Provides the cq_engine://learned resource — a structured view of
distilled operational knowledge accumulated through CQE Pattern 06
(Experience Distillation).
"""

import json
from pathlib import Path
from typing import Any

LEARNED_DIR = Path.home() / ".cq-engine" / "learned"
MAX_ENTRIES = 50


async def learned_entries() -> str:
    """Provide accumulated learning entries.

    Reads JSONL files from ~/.cq-engine/learned/ and returns the most
    recent entries with category-level aggregation. Returns an empty
    list if the directory does not exist.
    """
    if not LEARNED_DIR.is_dir():
        return json.dumps(
            {
                "entries": [],
                "total": 0,
                "categories": {},
                "source": str(LEARNED_DIR),
                "note": "No learned entries found. Directory does not exist.",
            },
            indent=2,
        )

    # Collect all entries from JSONL files
    all_entries: list[dict[str, Any]] = []

    for jsonl_file in sorted(LEARNED_DIR.glob("*.jsonl")):
        try:
            content = jsonl_file.read_text(encoding="utf-8")
            for line_num, line in enumerate(content.splitlines(), 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry.setdefault("source_file", jsonl_file.name)
                    entry.setdefault("source_line", line_num)
                    all_entries.append(entry)
                except json.JSONDecodeError:
                    continue
        except OSError:
            continue

    # Also check for .json files (single-entry format)
    for json_file in sorted(LEARNED_DIR.glob("*.json")):
        try:
            content = json_file.read_text(encoding="utf-8")
            entry = json.loads(content)
            if isinstance(entry, list):
                for item in entry:
                    item.setdefault("source_file", json_file.name)
                    all_entries.append(item)
            elif isinstance(entry, dict):
                entry.setdefault("source_file", json_file.name)
                all_entries.append(entry)
        except (json.JSONDecodeError, OSError):
            continue

    # Sort by timestamp (newest first) if available
    all_entries.sort(
        key=lambda e: e.get("timestamp", e.get("date", "")),
        reverse=True,
    )

    # Take most recent entries
    recent = all_entries[:MAX_ENTRIES]

    # Category aggregation
    categories: dict[str, int] = {}
    for entry in all_entries:
        category = entry.get(
            "category",
            entry.get("signal_type", entry.get("type", "uncategorized")),
        )
        categories[category] = categories.get(category, 0) + 1

    result = {
        "entries": recent,
        "total": len(all_entries),
        "returned": len(recent),
        "categories": categories,
        "source": str(LEARNED_DIR),
    }

    return json.dumps(result, indent=2)
