"""Experience Distillation learning tool for CQ Engine MCP Server.

Records observations from agent execution, detects duplicates via Jaccard
similarity, and maps learnings to CQE Patterns.
"""

import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

CQ_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent

VALID_CATEGORIES = ("pattern_usage", "failure", "preference", "optimization")

PATTERN_KEYWORD_MAP: dict[str, str] = {
    "attention": "Pattern 01: Attention Budget",
    "budget": "Pattern 01: Attention Budget",
    "token": "Pattern 01: Attention Budget",
    "context": "Pattern 02: Context Gate",
    "filter": "Pattern 02: Context Gate",
    "gate": "Pattern 02: Context Gate",
    "persona": "Pattern 03: Cognitive Profile",
    "role": "Pattern 03: Cognitive Profile",
    "profile": "Pattern 03: Cognitive Profile",
    "mutation": "Pattern 05: Assumption Mutation",
    "test": "Pattern 05: Assumption Mutation",
    "assumption": "Pattern 05: Assumption Mutation",
    "learn": "Pattern 06: Experience Distillation",
    "experience": "Pattern 06: Experience Distillation",
    "distill": "Pattern 06: Experience Distillation",
    "file": "Pattern 07: File-Based I/O",
    "io": "Pattern 07: File-Based I/O",
    "output": "Pattern 07: File-Based I/O",
    "template": "Pattern 08: Template-Driven Role",
    "driven": "Pattern 08: Template-Driven Role",
}

LEARNED_BASE = Path("~/.cq-engine/learned").expanduser()


def _generate_id() -> str:
    """Generate learning ID: L + YYYYMMDD + _ + HHMM + _ + 4-digit hex."""
    now = datetime.now(timezone.utc)
    hex_part = format(random.randint(0, 0xFFFF), "04x")
    return f"L{now.strftime('%Y%m%d')}_{now.strftime('%H%M')}_{hex_part}"


def _tokenize(text: str) -> set[str]:
    """Tokenize text to lowercase word set for similarity comparison."""
    return set(text.lower().split())


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union > 0 else 0.0


def _get_storage_path(project: str) -> Path:
    """Return JSONL storage path based on project scope."""
    if project:
        return LEARNED_BASE / "projects" / f"{project}.jsonl"
    return LEARNED_BASE / "global.jsonl"


def _load_existing(path: Path) -> list[dict]:
    """Load existing learning entries from a JSONL file."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _find_pattern_suggestion(tokens: set[str]) -> str:
    """Map observation tokens to a CQE Pattern suggestion."""
    pattern_scores: dict[str, int] = {}
    for token in tokens:
        pattern = PATTERN_KEYWORD_MAP.get(token)
        if pattern:
            pattern_scores[pattern] = pattern_scores.get(pattern, 0) + 1
    if not pattern_scores:
        return ""
    best = max(pattern_scores, key=lambda k: pattern_scores[k])
    return f"Related to {best}"


async def learn(
    observation: str,
    category: str,
    confidence: float = 0.5,
    project: str = "",
) -> str:
    """Record a learning observation from agent execution.

    Args:
        observation: Learning content in natural language.
        category: One of "pattern_usage", "failure", "preference", "optimization".
        confidence: Confidence level 0.0-1.0.
        project: Project scope (empty string for global).
    """
    # Validate category
    if category not in VALID_CATEGORIES:
        return json.dumps(
            {
                "error": f"Invalid category '{category}'. Must be one of: {', '.join(VALID_CATEGORIES)}",
                "stored": False,
            },
            indent=2,
        )

    # Clamp confidence
    confidence = max(0.0, min(1.0, confidence))

    # Generate ID and timestamp
    learning_id = _generate_id()
    timestamp = datetime.now(timezone.utc).isoformat()

    # Tokenize observation
    obs_tokens = _tokenize(observation)

    # Load existing entries for duplicate/similarity check
    storage_path = _get_storage_path(project)
    existing = _load_existing(storage_path)

    # Compute similarities
    related_learnings = []
    duplicate_warning = False

    for entry in existing:
        entry_tokens = _tokenize(entry.get("observation", ""))
        sim = _jaccard_similarity(obs_tokens, entry_tokens)
        if sim > 0.6:
            duplicate_warning = True
            related_learnings.append(
                {
                    "id": entry.get("id", ""),
                    "observation": entry.get("observation", ""),
                    "similarity": round(sim, 2),
                }
            )
        elif sim > 0.3:
            related_learnings.append(
                {
                    "id": entry.get("id", ""),
                    "observation": entry.get("observation", ""),
                    "similarity": round(sim, 2),
                }
            )

    # Sort related by similarity descending, limit to top 5
    related_learnings.sort(key=lambda x: x["similarity"], reverse=True)
    related_learnings = related_learnings[:5]

    # Pattern suggestion
    pattern_suggestion = _find_pattern_suggestion(obs_tokens)

    # Extract keyword tags
    tags = sorted(obs_tokens & set(PATTERN_KEYWORD_MAP.keys()))
    if not tags:
        # Use top frequency words (3+ chars) as tags, up to 5
        tags = sorted([t for t in obs_tokens if len(t) >= 4])[:5]

    # Build JSONL entry
    entry = {
        "id": learning_id,
        "observation": observation,
        "category": category,
        "confidence": confidence,
        "project": project,
        "timestamp": timestamp,
        "tags": tags,
    }

    # Ensure storage directory exists and append
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    with open(storage_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Build response
    result = {
        "learning_id": learning_id,
        "stored": True,
        "related_learnings": related_learnings,
        "pattern_suggestion": pattern_suggestion,
        "duplicate_warning": duplicate_warning,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)
