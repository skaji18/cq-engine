"""CQE Task Decomposition tool based on the Attention Budget pattern.

Decomposes a task description into budget-aware subtasks with dependency
analysis, following CQE Pattern #01 (Attention Budget) principles:
- Budget Before Execution
- Complexity-Proportional Allocation
- Overflow Prevention via decomposition
"""
import json
import math
import os
import re
import time
from pathlib import Path

# cq-engine repository root
CQ_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent

# --- Complexity keywords and weights ---
# Keywords that indicate task complexity, grouped by impact level
COMPLEXITY_KEYWORDS = {
    # High complexity indicators (weight: 3)
    "refactor": 3, "redesign": 3, "migrate": 3, "rewrite": 3,
    "architect": 3, "integrate": 3, "across": 3, "end-to-end": 3,
    "cross-cutting": 3, "system-wide": 3, "comprehensive": 3,
    # Medium complexity indicators (weight: 2)
    "and": 2, "then": 2, "also": 2, "additionally": 2,
    "implement": 2, "analyze": 2, "compare": 2, "evaluate": 2,
    "multiple": 2, "several": 2, "various": 2, "each": 2,
    "both": 2, "transform": 2, "optimize": 2, "debug": 2,
    # Low complexity indicators (weight: 1)
    "update": 1, "fix": 1, "add": 1, "remove": 1,
    "check": 1, "verify": 1, "test": 1, "review": 1,
    "rename": 1, "move": 1, "copy": 1, "format": 1,
}

# Dependency signal keywords
DEPENDENCY_SIGNALS = {
    "after": "sequential",
    "based on": "data_dependency",
    "using output of": "data_dependency",
    "depends on": "data_dependency",
    "requires": "prerequisite",
    "before": "sequential",
    "once": "sequential",
    "following": "sequential",
    "then": "sequential",
}

# Budget sizing from Attention Budget pattern (Section: Budget Sizing Heuristic)
BUDGET_TIERS = [
    (10, "low", 5000, 15000),      # score <= 10: Low complexity
    (25, "medium", 15000, 50000),   # score <= 25: Medium complexity
    (50, "high", 50000, 120000),    # score <= 50: High complexity
    (999, "critical", 120000, 200000),  # score > 50: Critical complexity
]


def _estimate_complexity(description: str) -> dict:
    """Estimate task complexity using keyword heuristics.

    Returns a dict with score, level, keyword_hits, and word_count.
    """
    words = description.lower().split()
    word_count = len(words)
    description_lower = description.lower()

    keyword_hits = {}
    score = 0

    for keyword, weight in COMPLEXITY_KEYWORDS.items():
        count = description_lower.count(keyword)
        if count > 0:
            keyword_hits[keyword] = {"count": count, "weight": weight}
            score += count * weight

    # Base complexity from word count (longer descriptions = more complex)
    score += word_count // 20

    # Determine complexity level
    level = "low"
    for threshold, tier_level, _, _ in BUDGET_TIERS:
        if score <= threshold:
            level = tier_level
            break

    return {
        "score": score,
        "level": level,
        "keyword_hits": keyword_hits,
        "word_count": word_count,
    }


def _estimate_tokens(text: str) -> int:
    """Estimate token count from text (words * 1.3 approximation)."""
    word_count = len(text.split())
    return int(math.ceil(word_count * 1.3))


def _split_into_chunks(description: str, num_chunks: int) -> list[str]:
    """Split task description into semantic chunks at sentence boundaries."""
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', description.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= 1:
        # Single sentence — split on conjunctions and semicolons
        parts = re.split(r'\s*(?:;\s*|,?\s+and\s+|,?\s+then\s+|,?\s+also\s+)', description)
        parts = [p.strip() for p in parts if p.strip()]
        sentences = parts if len(parts) > 1 else [description]

    if len(sentences) <= num_chunks:
        return sentences

    # Distribute sentences across chunks
    chunks = []
    chunk_size = max(1, len(sentences) // num_chunks)
    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
        if len(chunks) >= num_chunks:
            # Append remaining sentences to the last chunk
            remaining = " ".join(sentences[i + chunk_size:])
            if remaining:
                chunks[-1] += " " + remaining
            break

    return chunks


def _detect_dependencies(chunks: list[str]) -> list[list[str]]:
    """Detect dependencies between subtask chunks.

    Returns a list of dependency lists, one per chunk.
    Each dependency list contains the IDs of chunks this chunk depends on.
    """
    dependencies = [[] for _ in chunks]

    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        for signal in DEPENDENCY_SIGNALS:
            if signal in chunk_lower and i > 0:
                # Dependency on the previous chunk
                prev_id = f"ST-{i}"
                if prev_id not in dependencies[i]:
                    dependencies[i].append(prev_id)
                break

    return dependencies


def _generate_dependency_graph(subtasks: list[dict]) -> str:
    """Generate an ASCII dependency graph from subtasks."""
    if len(subtasks) <= 1:
        return subtasks[0]["id"] if subtasks else ""

    lines = []
    # Find independent tasks (no dependencies) and dependent chains
    independent = [st for st in subtasks if not st["dependencies"]]
    dependent = [st for st in subtasks if st["dependencies"]]

    if not dependent:
        # All independent — parallel execution
        ids = [st["id"] for st in subtasks]
        return " | ".join(ids) + "  (all parallel)"

    # Build simple chain representation
    placed = set()
    for st in subtasks:
        if st["id"] in placed:
            continue
        if not st["dependencies"]:
            # Start of a chain or standalone
            chain = [st["id"]]
            placed.add(st["id"])
            # Follow the chain forward
            current_id = st["id"]
            for other in subtasks:
                if current_id in other["dependencies"] and other["id"] not in placed:
                    chain.append(other["id"])
                    placed.add(other["id"])
                    current_id = other["id"]
            lines.append(" ──▶ ".join(chain))

    # Add any remaining unplaced tasks
    for st in subtasks:
        if st["id"] not in placed:
            lines.append(st["id"])

    return "\n".join(lines)


async def decompose(
    task_description: str,
    budget: int = 50000,
    max_subtasks: int = 8,
) -> str:
    """Decompose a task into budget-aware subtasks using the Attention Budget pattern.

    Analyzes task complexity and splits it into subtasks, each with an
    estimated token budget and dependency information.

    Args:
        task_description: Natural language description of the task to decompose.
        budget: Maximum token budget per subtask (default: 50000).
        max_subtasks: Maximum number of subtasks to generate (default: 8).
    """
    start = time.time()

    if not task_description or not task_description.strip():
        return json.dumps({
            "error": "task_description is required and must be non-empty",
        }, indent=2)

    # Step 1: Estimate complexity
    complexity = _estimate_complexity(task_description)

    # Step 2: Determine number of subtasks based on complexity
    if complexity["level"] == "low":
        num_subtasks = 1
    elif complexity["level"] == "medium":
        num_subtasks = min(max_subtasks, max(2, complexity["score"] // 10))
    elif complexity["level"] == "high":
        num_subtasks = min(max_subtasks, max(3, complexity["score"] // 8))
    else:  # critical
        num_subtasks = min(max_subtasks, max(4, complexity["score"] // 6))

    # Step 3: Split into semantic chunks
    chunks = _split_into_chunks(task_description, num_subtasks)
    num_subtasks = len(chunks)  # Actual number may differ from planned

    # Step 4: Detect dependencies
    dep_lists = _detect_dependencies(chunks)

    # Step 5: Build subtask list with budget estimation
    subtasks = []
    total_budget = 0

    for i, chunk in enumerate(chunks):
        subtask_id = f"ST-{i + 1}"
        estimated_tokens = _estimate_tokens(chunk)

        # Apply budget per-subtask cap
        if estimated_tokens > budget:
            # Mark as needs further decomposition
            estimated_tokens = budget
            chunk += " [NOTE: May need further decomposition — exceeds per-subtask budget]"

        # Scale estimation based on complexity level
        if complexity["level"] in ("high", "critical"):
            # Complex tasks need more tokens than word count suggests
            estimated_tokens = int(estimated_tokens * 1.5)

        # Ensure minimum budget
        estimated_tokens = max(estimated_tokens, 2000)

        subtask = {
            "id": subtask_id,
            "description": chunk,
            "estimated_tokens": min(estimated_tokens, budget),
            "dependencies": dep_lists[i],
        }
        subtasks.append(subtask)
        total_budget += subtask["estimated_tokens"]

    # Step 6: Generate dependency graph
    dep_graph = _generate_dependency_graph(subtasks)

    # Step 7: Determine overflow strategy
    overflow_strategy = "none"
    if total_budget > budget * max_subtasks:
        overflow_strategy = "checkpoint_and_spawn"
    elif any(st["estimated_tokens"] >= budget * 0.9 for st in subtasks):
        overflow_strategy = "summarize_and_continue"

    elapsed = time.time() - start

    result = {
        "subtasks": subtasks,
        "total_budget": total_budget,
        "dependency_graph": dep_graph,
        "complexity": {
            "score": complexity["score"],
            "level": complexity["level"],
            "word_count": complexity["word_count"],
        },
        "overflow_strategy": overflow_strategy,
        "budget_per_subtask": budget,
        "elapsed_ms": round(elapsed * 1000, 1),
    }

    return json.dumps(result, indent=2)
