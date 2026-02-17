"""CQE Context Gate tool based on the Context Gate pattern.

Filters and ranks files by relevance to a given task, selecting the
most useful context within a token budget. Follows CQE Pattern #02
(Context Gate) principles:
- Receiver-Defined Filtering
- Structured Handoff
- Audit Trail Preservation
"""
import json
import math
import os
import time
from pathlib import Path

# cq-engine repository root
CQ_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent

# --- File extension relevance weights ---
# Higher weight = more likely to be substantive code/content
EXTENSION_WEIGHTS = {
    # Source code (high relevance)
    ".py": 0.9, ".js": 0.9, ".ts": 0.9, ".rs": 0.9, ".go": 0.9,
    ".java": 0.9, ".rb": 0.9, ".c": 0.9, ".cpp": 0.9, ".h": 0.9,
    ".sh": 0.8, ".bash": 0.8,
    # Configuration (medium-high relevance)
    ".yaml": 0.75, ".yml": 0.75, ".json": 0.7, ".toml": 0.7,
    ".ini": 0.6, ".cfg": 0.6, ".conf": 0.6, ".env": 0.5,
    # Documentation (medium relevance)
    ".md": 0.6, ".rst": 0.6, ".txt": 0.5, ".adoc": 0.6,
    # Build/package (lower relevance)
    ".lock": 0.2, ".sum": 0.2,
    # Data (variable relevance)
    ".csv": 0.4, ".xml": 0.5, ".html": 0.5, ".sql": 0.7,
    # Binary/generated (low relevance)
    ".png": 0.1, ".jpg": 0.1, ".gif": 0.1, ".svg": 0.3,
    ".woff": 0.05, ".woff2": 0.05, ".ttf": 0.05, ".eot": 0.05,
    ".min.js": 0.1, ".min.css": 0.1, ".map": 0.1,
}

# Common low-relevance path segments
LOW_RELEVANCE_PATHS = {
    "node_modules", ".git", "__pycache__", ".tox", ".pytest_cache",
    "dist", "build", ".eggs", "vendor", "venv", ".venv",
    "coverage", ".coverage", ".nyc_output",
}

# Keywords extracted from common task descriptions for relevance scoring
TASK_DOMAIN_KEYWORDS = {
    "auth": ["auth", "login", "session", "token", "jwt", "oauth", "credential", "password"],
    "api": ["api", "endpoint", "route", "handler", "request", "response", "rest", "graphql"],
    "database": ["database", "db", "model", "schema", "migration", "query", "sql", "orm"],
    "test": ["test", "spec", "fixture", "mock", "assert", "expect", "coverage"],
    "ui": ["component", "view", "template", "style", "css", "layout", "render", "ui", "frontend"],
    "config": ["config", "setting", "env", "environment", "deploy", "ci", "docker"],
    "docs": ["doc", "readme", "guide", "tutorial", "changelog", "license"],
}


def _extract_task_keywords(task_description: str) -> set[str]:
    """Extract meaningful keywords from a task description."""
    # Normalize and split
    words = set(task_description.lower().split())
    # Remove very short words and common stop words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                  "to", "of", "in", "for", "on", "with", "at", "by", "from",
                  "it", "its", "this", "that", "and", "or", "but", "not",
                  "all", "any", "do", "does", "did", "has", "have", "had",
                  "will", "would", "should", "could", "can", "may", "might"}
    keywords = {w for w in words if len(w) > 2 and w not in stop_words}
    return keywords


def _path_segments(filepath: str) -> set[str]:
    """Extract meaningful path segments from a file path."""
    parts = Path(filepath).parts
    segments = set()
    for part in parts:
        # Split on common separators
        for sub in part.replace("-", "_").replace(".", "_").split("_"):
            if len(sub) > 2:
                segments.add(sub.lower())
    # Add the stem (filename without extension)
    stem = Path(filepath).stem.lower()
    for sub in stem.replace("-", "_").split("_"):
        if len(sub) > 2:
            segments.add(sub)
    return segments


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _estimate_file_tokens(filepath: str) -> int:
    """Estimate token count from file size (bytes / 4 approximation)."""
    try:
        size_bytes = os.path.getsize(filepath)
        return max(1, size_bytes // 4)
    except OSError:
        return 1000  # Default estimate if file is inaccessible


def _file_modified_days_ago(filepath: str) -> float:
    """Return the number of days since the file was last modified."""
    try:
        mtime = os.path.getmtime(filepath)
        return (time.time() - mtime) / 86400.0
    except OSError:
        return 365.0  # Default to 1 year if inaccessible


def _score_file(filepath: str, task_keywords: set[str]) -> dict:
    """Score a file's relevance to the task.

    Returns a dict with relevance_score (0.0–1.0) and component scores.
    """
    path_obj = Path(filepath)
    extension = path_obj.suffix.lower()

    # Check for low-relevance path segments
    for segment in LOW_RELEVANCE_PATHS:
        if segment in filepath:
            return {
                "relevance_score": 0.01,
                "extension_score": 0.0,
                "keyword_score": 0.0,
                "reason": f"Low-relevance path segment: {segment}",
            }

    # Component 1: Extension weight (0.0–0.9)
    extension_score = EXTENSION_WEIGHTS.get(extension, 0.3)

    # Component 2: Path-keyword overlap (Jaccard similarity)
    path_segs = _path_segments(filepath)
    keyword_score = _jaccard_similarity(path_segs, task_keywords)

    # Component 3: Domain keyword boost
    domain_boost = 0.0
    for domain, domain_keywords in TASK_DOMAIN_KEYWORDS.items():
        task_domain_overlap = task_keywords & set(domain_keywords)
        path_domain_overlap = path_segs & set(domain_keywords)
        if task_domain_overlap and path_domain_overlap:
            domain_boost = max(domain_boost, 0.2)

    # Combined relevance score (weighted average)
    relevance = (
        extension_score * 0.3
        + keyword_score * 0.5
        + domain_boost * 0.2
    )

    return {
        "relevance_score": round(min(1.0, relevance), 3),
        "extension_score": round(extension_score, 3),
        "keyword_score": round(keyword_score, 3),
        "domain_boost": round(domain_boost, 3),
    }


async def gate(
    task_description: str,
    available_files: list[str],
    max_files: int = 5,
    max_tokens: int = 30000,
) -> str:
    """Filter and rank files by relevance to a task using the Context Gate pattern.

    Selects the most relevant files within a token budget, providing
    context health metrics and exclusion reasons.

    Args:
        task_description: Description of the task that needs context.
        available_files: List of file paths available for context.
        max_files: Maximum number of files to include (default: 5).
        max_tokens: Maximum total tokens for selected context (default: 30000).
    """
    start = time.time()

    if not task_description or not task_description.strip():
        return json.dumps({
            "error": "task_description is required and must be non-empty",
        }, indent=2)

    if not available_files:
        return json.dumps({
            "error": "available_files is required and must be non-empty",
        }, indent=2)

    # Step 1: Extract task keywords
    task_keywords = _extract_task_keywords(task_description)

    # Step 2: Score all files
    scored_files = []
    for filepath in available_files:
        score_info = _score_file(filepath, task_keywords)
        estimated_tokens = _estimate_file_tokens(filepath)
        days_ago = _file_modified_days_ago(filepath)

        scored_files.append({
            "path": filepath,
            "relevance_score": score_info["relevance_score"],
            "estimated_tokens": estimated_tokens,
            "days_since_modified": round(days_ago, 1),
            "score_details": score_info,
        })

    # Step 3: Rank by efficiency (relevance / tokens) — quality-weighted ranking
    for sf in scored_files:
        token_cost = max(1, sf["estimated_tokens"])
        sf["efficiency"] = sf["relevance_score"] / (token_cost / 10000)

    scored_files.sort(key=lambda x: x["efficiency"], reverse=True)

    # Step 4: Select files within budget and count constraints
    selected = []
    excluded = []
    running_tokens = 0
    unrelated_count = 0

    for sf in scored_files:
        # Skip very low relevance files
        if sf["relevance_score"] < 0.05:
            excluded.append({
                "path": sf["path"],
                "reason": f"Low relevance ({sf['relevance_score']:.2f})",
            })
            unrelated_count += 1
            continue

        # Check constraints
        if len(selected) >= max_files:
            excluded.append({
                "path": sf["path"],
                "reason": f"Max files reached ({max_files})",
            })
            continue

        if running_tokens + sf["estimated_tokens"] > max_tokens:
            excluded.append({
                "path": sf["path"],
                "reason": f"Token budget exceeded ({running_tokens + sf['estimated_tokens']} > {max_tokens})",
            })
            continue

        selected.append({
            "path": sf["path"],
            "relevance_score": sf["relevance_score"],
            "estimated_tokens": sf["estimated_tokens"],
        })
        running_tokens += sf["estimated_tokens"]

    # Step 5: Calculate Context Health Score
    total_files = len(available_files)
    density = round(running_tokens / max_tokens, 3) if max_tokens > 0 else 0.0
    contamination_risk = round(unrelated_count / total_files, 3) if total_files > 0 else 0.0

    # Freshness: based on most recently modified selected file
    if selected:
        newest_days = min(
            (sf["days_since_modified"] for sf in scored_files
             if sf["path"] in {s["path"] for s in selected}),
            default=365.0,
        )
        freshness = round(min(1.0, 7.0 / max(1.0, newest_days)), 3)
    else:
        freshness = 0.0

    context_health = {
        "density": density,
        "contamination_risk": contamination_risk,
        "freshness": freshness,
    }

    elapsed = time.time() - start

    result = {
        "selected_files": selected,
        "excluded_files": excluded,
        "context_health": context_health,
        "summary": {
            "selected_count": len(selected),
            "excluded_count": len(excluded),
            "total_tokens": running_tokens,
            "max_tokens": max_tokens,
        },
        "elapsed_ms": round(elapsed * 1000, 1),
    }

    return json.dumps(result, indent=2)
