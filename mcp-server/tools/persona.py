"""Cognitive Profile persona selection tool.

Selects the best-fit persona for a given task based on CQE Pattern 03
(Cognitive Profile). Supports built-in personas and custom persona
directories (e.g., mutadoc/personas/).
"""

import json
import re
from pathlib import Path
from typing import Optional

CQ_ENGINE_ROOT = Path(__file__).resolve().parent.parent.parent

# --- Built-in Persona Registry ---

PERSONAS = {
    "senior_engineer": {
        "expertise": "Code architecture, performance optimization, testing",
        "cognitive_style": "systematic, detail-oriented, risk-aware",
        "keywords": [
            "code", "implement", "refactor", "optimize", "debug", "build",
            "function", "class", "module", "test", "bug", "performance",
            "architecture", "deploy", "compile", "lint",
        ],
        "prompt": (
            "You are a Senior Software Engineer with 15+ years of experience "
            "in production systems. You prioritize correctness, maintainability, "
            "and performance. You review code with a skeptical eye for edge cases, "
            "error handling gaps, and architectural anti-patterns. When you find an "
            "issue, you explain both the problem and the fix concretely."
        ),
    },
    "legal_analyst": {
        "expertise": "Contract review, compliance, regulation analysis",
        "cognitive_style": "precise, adversarial, obligation-focused",
        "keywords": [
            "contract", "legal", "compliance", "regulation", "terms",
            "clause", "obligation", "liability", "indemnify", "warranty",
            "agreement", "policy", "law", "rights", "enforce",
        ],
        "prompt": (
            "You are a Legal Analyst specializing in contract review and "
            "regulatory compliance. You read every clause with an eye for "
            "ambiguity, contradictions, and unintended obligations. You identify "
            "vague language that could be exploited and missing protections that "
            "expose risk. Your analysis is precise, citing specific sections."
        ),
    },
    "security_auditor": {
        "expertise": "Vulnerability analysis, threat modeling, attack surface assessment",
        "cognitive_style": "adversarial, paranoid, thorough",
        "keywords": [
            "security", "vulnerability", "threat", "attack", "auth",
            "authentication", "authorization", "encryption", "injection",
            "exploit", "penetration", "firewall", "access", "permission",
            "token", "credential",
        ],
        "prompt": (
            "You are a Security Auditor with deep expertise in application "
            "security. You assume all external input is malicious. You trace "
            "data flows from entry points to storage, looking for injection "
            "vectors, authentication bypasses, privilege escalation paths, and "
            "information leaks. You rate findings by exploitability and impact."
        ),
    },
    "technical_writer": {
        "expertise": "Documentation, API specifications, developer guides",
        "cognitive_style": "audience-aware, clarity-focused, structured",
        "keywords": [
            "document", "readme", "spec", "api", "guide", "documentation",
            "tutorial", "reference", "write", "explain", "describe",
            "manual", "specification", "overview",
        ],
        "prompt": (
            "You are a Technical Writer who creates clear, accurate documentation "
            "for developer audiences. You focus on structure, completeness, and "
            "audience awareness. You ensure every term is defined, every example "
            "is runnable, and every section answers a specific reader question. "
            "You flag gaps where readers would be confused or blocked."
        ),
    },
    "data_scientist": {
        "expertise": "Data analysis, statistical methods, ML evaluation",
        "cognitive_style": "empirical, hypothesis-driven, skeptical of claims",
        "keywords": [
            "data", "analysis", "model", "statistics", "metric",
            "dataset", "training", "evaluation", "accuracy", "benchmark",
            "hypothesis", "experiment", "correlation", "regression", "ml",
            "machine learning",
        ],
        "prompt": (
            "You are a Data Scientist with expertise in statistical analysis and "
            "machine learning. You evaluate claims with empirical rigor, demanding "
            "evidence for every assertion. You check for confounding variables, "
            "selection bias, and statistical significance. You distinguish "
            "correlation from causation and flag unvalidated assumptions."
        ),
    },
    "project_manager": {
        "expertise": "Planning, coordination, risk management, stakeholder alignment",
        "cognitive_style": "strategic, pragmatic, risk-aware",
        "keywords": [
            "plan", "schedule", "risk", "coordinate", "milestone",
            "project", "deadline", "resource", "scope", "budget",
            "stakeholder", "timeline", "priority", "dependency", "blocker",
        ],
        "prompt": (
            "You are a Project Manager experienced in complex multi-team "
            "delivery. You think in terms of dependencies, critical paths, and "
            "risk mitigation. You identify scope creep, resource bottlenecks, "
            "and missing contingencies. You communicate clearly with both "
            "technical and non-technical stakeholders."
        ),
    },
}

# Task type keyword mappings for auto-detection
TASK_TYPE_KEYWORDS = {
    "code": [
        "code", "implement", "refactor", "debug", "build", "compile",
        "function", "class", "test", "fix", "bug", "deploy",
    ],
    "document": [
        "document", "write", "readme", "spec", "guide", "manual",
        "tutorial", "describe", "explain",
    ],
    "analysis": [
        "analyze", "data", "model", "statistics", "evaluate", "benchmark",
        "metric", "experiment", "hypothesis",
    ],
    "review": [
        "review", "audit", "check", "inspect", "assess", "validate",
        "security", "compliance", "contract", "legal",
    ],
}


def _detect_task_type(task_description: str) -> str:
    """Detect task type from description using keyword frequency."""
    desc_lower = task_description.lower()
    scores: dict[str, int] = {}
    for task_type, keywords in TASK_TYPE_KEYWORDS.items():
        scores[task_type] = sum(1 for kw in keywords if kw in desc_lower)
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return "code"  # default
    return best


def _compute_fit_score(persona: dict, task_description: str) -> float:
    """Compute fit score (0.0-1.0) based on keyword overlap."""
    desc_lower = task_description.lower()
    keywords = persona["keywords"]
    if not keywords:
        return 0.0
    matches = sum(1 for kw in keywords if kw in desc_lower)
    # Normalize: cap at 1.0, weight toward partial matches
    raw = matches / max(len(keywords) * 0.3, 1)
    return round(min(raw, 1.0), 2)


def _check_cq003(task_description: str) -> Optional[str]:
    """Check for CQ003 violation: generic or too-brief task description."""
    words = task_description.strip().split()
    if len(words) < 3:
        return (
            "CQ003 warning: Task description is too brief "
            f"({len(words)} words). Provide more context for accurate "
            "persona selection."
        )
    generic_only = {"do", "task", "work", "thing", "stuff", "help", "make", "run"}
    meaningful = [w for w in words if w.lower() not in generic_only]
    if len(meaningful) < 2:
        return (
            "CQ003 warning: Task description uses only generic terms. "
            "Add specific domain or action words for better persona matching."
        )
    return None


async def _load_custom_personas(custom_dir: str) -> dict:
    """Load custom personas from .md files in the given directory."""
    custom = {}
    dir_path = Path(custom_dir)
    if not dir_path.is_dir():
        return custom
    for md_file in sorted(dir_path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        # Extract persona name from H1
        name_match = re.search(r"^#\s+Persona:\s*(.+)$", content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else md_file.stem
        # Extract role description from first paragraph after ## Role Description
        role_match = re.search(
            r"##\s+Role Description\s*\n+(.+?)(?:\n\n|\n##)",
            content,
            re.DOTALL,
        )
        role = role_match.group(1).strip() if role_match else ""
        # Extract keywords from cognitive traits or role text
        keywords = re.findall(r"\b\w{4,}\b", role.lower())[:20]
        custom[md_file.stem] = {
            "expertise": role[:120] if role else f"Custom persona: {name}",
            "cognitive_style": "custom",
            "keywords": keywords,
            "prompt": f"You are {name}. {role[:500]}",
            "source": str(md_file),
        }
    return custom


async def persona(
    task_description: str,
    task_type: str = "auto",
    custom_persona_dir: str = "",
) -> str:
    """Select the best-fit cognitive persona for a task.

    Args:
        task_description: Description of the task to be performed.
        task_type: Task category — "code", "document", "analysis",
            "review", or "auto" for automatic detection.
        custom_persona_dir: Optional path to a directory containing
            custom persona .md files (e.g., mutadoc/personas/).
    """
    # CQ003 check
    cq003_warning = _check_cq003(task_description)

    # Auto-detect task type if needed
    detected_type = task_type
    if task_type == "auto":
        detected_type = _detect_task_type(task_description)

    # Build combined persona registry
    all_personas = dict(PERSONAS)
    if custom_persona_dir:
        custom = await _load_custom_personas(custom_persona_dir)
        all_personas.update(custom)

    # Score all personas
    scored = []
    for name, p in all_personas.items():
        fit = _compute_fit_score(p, task_description)
        scored.append((name, fit, p))

    scored.sort(key=lambda x: x[1], reverse=True)

    # Best match
    best_name, best_score, best_persona = scored[0]

    # Alternatives (next 2, with score > 0)
    alternatives = [
        {"name": name, "fit_score": score}
        for name, score, _ in scored[1:3]
        if score > 0
    ]

    result: dict = {
        "selected_persona": {
            "name": best_name,
            "expertise": best_persona["expertise"],
            "cognitive_style": best_persona["cognitive_style"],
            "fit_score": best_score,
        },
        "alternatives": alternatives,
        "persona_prompt": best_persona["prompt"],
        "detected_task_type": detected_type,
    }

    if cq003_warning:
        result["warning"] = cq003_warning

    if custom_persona_dir and "source" in best_persona:
        result["selected_persona"]["source"] = best_persona["source"]

    return json.dumps(result, indent=2)
