# CQE Patterns v0.1

> Cognitive Quality Engineering — A pattern catalog for LLM agent systems.
>
> Just as GoF gave Object-Oriented Programming its Design Patterns,
> CQE gives LLM agent design its vocabulary, tools, and measurement framework.

**Version**: 0.1.0
**Status**: Phase 1 — Foundation Complete
**License**: MIT

---

## Pattern Catalog

| # | Pattern | Weight | Evidence | Category | Problem |
|---|---------|--------|----------|----------|---------|
| 01 | [Attention Budget](01_attention_budget.md) | Foundational | B | knowledge | Uncontrolled token consumption degrades output quality silently |
| 02 | [Context Gate](02_context_gate.md) | Foundational | B | knowledge | Irrelevant context contaminates agent reasoning and wastes budget |
| 03 | [Cognitive Profile](03_cognitive_profile.md) | Foundational | B | knowledge | Generic personas produce shallow, undifferentiated analysis |
| 04 | [Wave Scheduler](04_wave_scheduler.md) | Situational | B | application | All-at-once execution degrades quality through resource contention |
| 05 | [Assumption Mutation](05_assumption_mutation.md) | Situational | B | verification | Untested assumptions hide vulnerabilities that surface in production |
| 06 | [Experience Distillation](06_experience_distillation.md) | Advanced | B | knowledge | Valuable operational knowledge is lost between sessions |
| 07 | [File-Based I/O](07_file_based_io.md) | Foundational | B | knowledge | In-memory agent communication lacks reliability and auditability |
| 08 | [Template-Driven Role](08_template_driven_role.md) | Situational | B | knowledge | Ad-hoc role definitions lead to inconsistent agent behavior |

### Weight Classification

| Weight | Meaning | Patterns |
|--------|---------|----------|
| **Foundational** | Every LLM agent system should implement these | 01, 02, 03, 07 |
| **Situational** | Apply under specific conditions (multi-agent, adversarial, etc.) | 04, 05, 08 |
| **Advanced** | Effective only in mature, long-running systems | 06 |

### Evidence Levels

| Level | Definition |
|-------|-----------|
| **A** | Quantitatively verified (A/B test results available) |
| **B** | Confirmed across multiple projects (inductively derived) |
| **C** | Theoretical reasoning (design principle) |
| **D** | Hypothesis stage (verification needed) |

All 8 patterns are currently at Evidence Level B. Upgrade paths to Level A are documented in each pattern's Evidence section.

### Categories

| Category | Description | Patterns |
|----------|-------------|----------|
| **knowledge** | Concepts and vocabulary for agent design | 01, 02, 03, 06, 07, 08 |
| **application** | Operational strategies for execution | 04 |
| **verification** | Quality assurance and adversarial testing | 05 |

---

## Dependency Graph

Patterns are interconnected. The dependency graph shows which patterns must be understood before others:

```
                    ┌──────────────────┐
                    │ 01 Attention     │   Foundational layer:
                    │    Budget        │   Start here.
                    └────────┬─────────┘   Defines the core resource model.
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ 02 Context     │  │ 07 File-Based  │  │ 03 Cognitive   │
│    Gate        │  │    I/O         │  │    Profile     │
└────────┬───────┘  └────────┬───────┘  └────────┬───────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
              ┌──────────────┼──────────────────┐
              ▼              ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │ 04 Wave        │ │ 08 Template-   │ │ 06 Experience  │
    │    Scheduler   │ │    Driven Role │ │    Distillation│
    └────────────────┘ └────────────────┘ └────────────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ 05 Assumption      │   Richest interactions.
                  │    Mutation        │   Bridges to Phase 2
                  └────────────────────┘   (MutaDoc).
```

**Key relationships**:
- Attention Budget → Context Gate: Budget is meaningless without filtering
- Attention Budget → Wave Scheduler: Budget determines wave capacity
- File-Based I/O → Context Gate: Files are natural gate boundaries
- Cognitive Profile → Template-Driven Role: Profile is content, template is structure
- All patterns → Assumption Mutation: Mutation tests the assumptions of every other pattern

---

## Recommended Reading Order

| Order | Pattern | Rationale |
|-------|---------|-----------|
| 1st | [01 Attention Budget](01_attention_budget.md) | Defines the core resource model. All other patterns reference "budget" |
| 2nd | [07 File-Based I/O](07_file_based_io.md) | Infrastructure pattern. Many patterns depend on file-based state |
| 3rd | [02 Context Gate](02_context_gate.md) | Directly depends on Attention Budget. Critical for agent communication |
| 4th | [03 Cognitive Profile](03_cognitive_profile.md) | Complements Context Gate (what passes through the gate depends on the profile) |
| 5th | [08 Template-Driven Role](08_template_driven_role.md) | Structures Cognitive Profile. Provides the format for role definitions |
| 6th | [04 Wave Scheduler](04_wave_scheduler.md) | Depends on Budget + File I/O. Operational scheduling pattern |
| 7th | [06 Experience Distillation](06_experience_distillation.md) | Depends on File I/O. Advanced pattern for long-running systems |
| 8th | [05 Assumption Mutation](05_assumption_mutation.md) | Richest interaction catalog. References all prior patterns. Bridges to Phase 2 |

---

## Quick Start

### If you are new to CQE

Start with the **4 Foundational patterns** — these apply to every LLM agent system:

1. **[Attention Budget](01_attention_budget.md)** — Set explicit token budgets for every task
2. **[File-Based I/O](07_file_based_io.md)** — Use files (not memory) for inter-agent communication
3. **[Context Gate](02_context_gate.md)** — Filter information between agent stages
4. **[Cognitive Profile](03_cognitive_profile.md)** — Define specialized personas, not generic agents

These 4 patterns address the most common quality failures in multi-agent systems.

### If you already have a working multi-agent system

Add **Situational patterns** where they apply:

- **[Wave Scheduler](04_wave_scheduler.md)** — If you run parallel tasks, schedule them in dependency-aware waves
- **[Template-Driven Role](08_template_driven_role.md)** — If your agents need consistent behavior, define roles via templates
- **[Assumption Mutation](05_assumption_mutation.md)** — If you produce high-stakes outputs, test your assumptions adversarially

### If you have a mature, long-running system

Add the **Advanced pattern**:

- **[Experience Distillation](06_experience_distillation.md)** — Extract and accumulate learning from execution to prevent repeated failures

### Common anti-patterns to avoid

See the [Anti-Pattern Index](anti-patterns/README.md) for a cross-pattern catalog of failure modes — 34 named anti-patterns with reverse links to their parent patterns.

---

## Pattern Format

Each pattern follows a structured GoF-inspired format with 10 required sections:

```
# Pattern: [Name]

## Classification
  Weight (Foundational / Situational / Advanced)
  Evidence Level (A / B / C / D)
  Category (knowledge / verification / application / measurement)

## Problem           — What goes wrong without this pattern
## Context           — When does this problem arise
## Solution          — The pattern's prescription
## Anti-Pattern      — Named failure modes ([F001], [F002], ...)
## Failure Catalog   — Real examples from production systems
## Interaction Catalog — How this pattern combines with others
## Known Uses        — Where this pattern has been applied
## Implementation Guidance — Concrete steps and config examples
## Evidence          — Data supporting the pattern
```

### What makes CQE Patterns different from other pattern catalogs

1. **Anti-Patterns from day one** — GoF's biggest weakness was not telling you when NOT to use a pattern. CQE includes anti-patterns and failure catalogs as first-class sections, not afterthoughts.
2. **Interaction Catalog** — GoF had "Related Patterns" but no detailed interaction analysis. CQE explicitly documents how patterns combine, conflict, and depend on each other.
3. **Evidence Levels** — Every pattern declares how strongly it is supported by data. No pretending that hypotheses are proven truths.
4. **Weight Classification** — Patterns are tiered by applicability so teams can adopt incrementally, not all-or-nothing.

---

## Directory Structure

```
patterns/
├── README.md                        # This file — catalog overview
├── 01_attention_budget.md           # Foundational: Token budget management
├── 02_context_gate.md               # Foundational: Information filtering
├── 03_cognitive_profile.md          # Foundational: Specialized personas
├── 04_wave_scheduler.md             # Situational: Dependency-aware scheduling
├── 05_assumption_mutation.md        # Situational: Adversarial testing
├── 06_experience_distillation.md    # Advanced: Operational learning
├── 07_file_based_io.md              # Foundational: File-based communication
├── 08_template_driven_role.md       # Situational: Role templates
└── anti-patterns/
    └── README.md                    # Cross-pattern anti-pattern index
```
