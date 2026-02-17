# Phase 1: Foundation — Detailed Implementation Plan

> **date**: 2026-02-17
> **scope**: CQE Patterns v0.1 + cqlint v0.1 + CQ Benchmark v0.1 specification
> **principle**: Zero Infrastructure (Bash + Markdown + Claude Code)

---

## 1. CQE Patterns v0.1 — 8 Core Patterns

### 1.1 Pattern Summary Table

| # | Pattern | 1-Line Summary | Weight | Evidence | Effort |
|---|---------|---------------|--------|----------|--------|
| 01 | **Attention Budget** | LLM attention is finite — allocate explicit token budgets per task to prevent silent overflow | Foundational | B | M |
| 02 | **Context Gate** | Filter information between agent stages to prevent attention contamination | Foundational | B | M |
| 03 | **Cognitive Profile** | Define specialized cognitive personas rather than using generic agents | Foundational | B | M |
| 04 | **Wave Scheduler** | Execute tasks in sequenced waves rather than all-at-once to preserve quality | Situational | B | S |
| 05 | **Assumption Mutation** | Intentionally challenge premises to discover hidden vulnerabilities | Situational | B | L |
| 06 | **Experience Distillation** | Extract and accumulate learning from execution to prevent repeated failures | Advanced | B | M |
| 07 | **File-Based I/O** | Use file-system communication for reliability, transparency, and environment independence | Foundational | B | S |
| 08 | **Template-Driven Role** | Define roles through explicit templates to ensure consistent quality | Situational | B | S |

**Effort legend**: S = 1 pattern file (~200 lines), M = 1 pattern file (~300-400 lines, richer examples), L = 1 pattern file (~400-500 lines, complex interactions)

### 1.2 Pattern Document Structure (GoF-Inspired)

Each pattern file (`patterns/NN_snake_case.md`) must contain the following sections:

```markdown
# Pattern: [Name]

## Classification
- **Weight**: Foundational / Situational / Advanced
- **Evidence Level**: A / B / C / D
- **Category**: [knowledge | verification | application | measurement]

## Problem
What goes wrong without this pattern? Concrete failure scenario.

## Context
When does this problem arise? What system characteristics trigger it?

## Solution
The pattern's prescription. Concrete, implementable guidance.

## Anti-Pattern
What happens when this pattern is misapplied? (GoF weakness addressed from v0.1)
- **[F001]** Named failure mode 1 — description
- **[F002]** Named failure mode 2 — description
- **[F003]** Named failure mode 3 — description

## Failure Catalog
Real examples of this pattern's absence or misuse, drawn from crew's execution history.

| ID | Failure | Root Cause | Detection Point |
|----|---------|-----------|-----------------|
| FC-01 | ... | ... | ... |

## Interaction Catalog
How this pattern combines with or conflicts with other patterns.

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| ... | complements / conflicts / enables / requires | ... |

## Known Uses
Where this pattern has been applied (crew, other frameworks).

## Implementation Guidance
Concrete steps to apply this pattern. Configuration examples.

## Evidence
What data supports this pattern? How was it validated?
- **Level B**: Confirmed across [N] projects. Details: ...
- **Upgrade path to A**: [what quantitative validation would be needed]
```

### 1.3 Per-Pattern Task Definitions

#### Pattern 01: Attention Budget

| Attribute | Detail |
|-----------|--------|
| **Problem** | LLM attention is finite but developers don't manage it, leading to silent quality degradation when context grows |
| **Key Anti-Patterns** | Budget Illusion (set budget but ignore quality), Uniform Budget (same budget regardless of complexity), Budget-Only Monitoring (track tokens but not output quality) |
| **Key Interactions** | Requires Context Gate (budget is useless if context is contaminated), Enables Wave Scheduler (budget informs wave sizing) |
| **Evidence Source** | crew's execution history — tasks exceeding implicit budget showed measurable quality drops |
| **Effort** | M |

#### Pattern 02: Context Gate

| Attribute | Detail |
|-----------|--------|
| **Problem** | Passing all information from one agent to the next contaminates attention and wastes budget on irrelevant data |
| **Key Anti-Patterns** | Gate Bypass (routing around the gate for "efficiency"), Over-Filtering (removing too much context, causing incomplete work), Stale Gate (filter rules not updated as tasks evolve) |
| **Key Interactions** | Requires Attention Budget (gate filtering criteria depend on budget), Complements File-Based I/O (files are natural gate boundaries) |
| **Evidence Source** | crew's YAML-based inter-agent communication as a natural Context Gate implementation |
| **Effort** | M |

#### Pattern 03: Cognitive Profile

| Attribute | Detail |
|-----------|--------|
| **Problem** | Generic agents ("you are a helpful assistant") underperform specialized ones because LLMs respond to persona framing |
| **Key Anti-Patterns** | Profile Bloat (overloading a persona with contradictory traits), Profile Drift (persona not maintained as tasks change), Shallow Profile (name-only persona with no behavioral specification) |
| **Key Interactions** | Enables Template-Driven Role (profile is the content, template is the structure), Used by Assumption Mutation (adversarial personas are specialized profiles) |
| **Evidence Source** | crew's persona system — specialized agents consistently outperformed generic ones |
| **Effort** | M |

#### Pattern 04: Wave Scheduler

| Attribute | Detail |
|-----------|--------|
| **Problem** | Launching all tasks simultaneously degrades quality because of resource contention and dependency violations |
| **Key Anti-Patterns** | Wave Overload (too many tasks per wave), Sequential Fallback (giving up on parallelism entirely), Dependency Blindness (ignoring task dependencies in wave assignment) |
| **Key Interactions** | Requires Attention Budget (budget determines wave capacity), Requires File-Based I/O (wave boundaries need reliable state transfer) |
| **Evidence Source** | crew's wave-based execution showed quality improvement over all-at-once deployment |
| **Effort** | S |

#### Pattern 05: Assumption Mutation

| Attribute | Detail |
|-----------|--------|
| **Problem** | Unverified assumptions hide vulnerabilities that only surface in production or adversarial conditions |
| **Key Anti-Patterns** | Mutation Theater (running mutations but ignoring results), Weak Mutation (only testing trivial assumptions), Mutation Fatigue (generating so many mutations that critical ones are buried) |
| **Key Interactions** | Foundation for MutaDoc (document mutation = Assumption Mutation applied to text), Foundation for ThinkTank (cross-critique = social Assumption Mutation), Complements Cognitive Profile (adversarial personas are mutation agents) |
| **Evidence Source** | Prior adversarial analysis experiments — both demonstrated assumption mutation value |
| **Effort** | L (richest interaction catalog — bridges to MutaDoc and ThinkTank) |

#### Pattern 06: Experience Distillation

| Attribute | Detail |
|-----------|--------|
| **Problem** | Without learning from execution, systems repeat the same failures across projects and sessions |
| **Key Anti-Patterns** | Unfiltered Memory (accumulating everything without distillation), Stale Learning (never updating or pruning learned knowledge), Context Leak (learning data contaminating unrelated tasks) |
| **Key Interactions** | Requires File-Based I/O (learning must be persisted), Feeds back to all patterns (learned experiences improve pattern application) |
| **Evidence Source** | crew's LP (Learned Preferences) system — projects with accumulated learning showed fewer repeated failures |
| **Effort** | M |

#### Pattern 07: File-Based I/O

| Attribute | Detail |
|-----------|--------|
| **Problem** | In-memory agent communication lacks reliability, transparency, and auditability |
| **Key Anti-Patterns** | File Sprawl (too many unstructured files), Schema Drift (file formats changing without coordination), Lock Contention (multiple agents writing to the same file) |
| **Key Interactions** | Enables Context Gate (files are natural filter boundaries), Enables Experience Distillation (files provide persistent storage), Enables Wave Scheduler (files carry state between waves) |
| **Evidence Source** | crew's YAML-based communication — compared to in-memory approaches, file-based showed better debugging and recovery |
| **Effort** | S |

#### Pattern 08: Template-Driven Role

| Attribute | Detail |
|-----------|--------|
| **Problem** | Implicit or ad-hoc role definitions cause inconsistent quality across agents performing similar functions |
| **Key Anti-Patterns** | Template Rigidity (templates too strict to adapt to novel tasks), Template Sprawl (too many overlapping templates), Undocumented Deviation (agents silently deviating from templates) |
| **Key Interactions** | Requires Cognitive Profile (template structures the profile), Complements File-Based I/O (templates are files), Used by Wave Scheduler (templates define what each wave member does) |
| **Evidence Source** | crew's instructions/*.md system — templated roles outperformed free-form instructions |
| **Effort** | S |

### 1.4 Pattern Dependencies (Writing Order)

```
                    ┌──────────────────┐
                    │ 01 Attention     │   Foundational layer:
                    │    Budget        │   Write these 4 first.
                    └────────┬─────────┘   They define core vocabulary.
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
                  │ 05 Assumption      │   Write last:
                  │    Mutation        │   Richest interactions,
                  └────────────────────┘   bridges to Phase 2.
```

**Recommended writing order**:

| Order | Pattern | Rationale |
|-------|---------|-----------|
| 1st | 01 Attention Budget | Defines the core resource model. All other patterns reference "budget" |
| 2nd | 07 File-Based I/O | Infrastructure pattern. Many patterns depend on file-based state |
| 3rd | 02 Context Gate | Directly depends on Attention Budget. Critical for agent communication |
| 4th | 03 Cognitive Profile | Complements Context Gate (what goes through the gate depends on the profile) |
| 5th | 08 Template-Driven Role | Structures Cognitive Profile. Short pattern, quick to write |
| 6th | 04 Wave Scheduler | Depends on Budget + File I/O. Operational pattern |
| 7th | 06 Experience Distillation | Depends on File I/O. Advanced pattern, fewer references from others |
| 8th | 05 Assumption Mutation | Richest interaction catalog. Must reference all prior patterns. Bridges to Phase 2 (MutaDoc) |

### 1.5 Pattern Completion Criteria

A pattern is **complete** when it has:

| # | Criterion | Verification |
|---|-----------|-------------|
| PC-1 | All sections from §1.2 template filled | Manual review — no placeholder text |
| PC-2 | At least 3 Anti-Patterns with [F0xx] IDs | Count ≥ 3 |
| PC-3 | At least 2 Failure Catalog entries from crew history | Count ≥ 2 |
| PC-4 | Interaction Catalog covers all related patterns | Cross-reference check against dependency graph |
| PC-5 | Evidence section cites specific data source | Non-empty, references actual execution data |
| PC-6 | Implementation Guidance includes config example | Runnable YAML or Markdown example present |
| PC-7 | Weight classification justified | Foundational/Situational/Advanced with rationale |
| PC-8 | Written in arXiv-compatible format | Publishable as academic paper section |

---

## 2. cqlint v0.1 — 5 Initial Rules

### 2.1 Rule Summary Table

| Rule | Name | Detects | Pattern | Severity | Effort |
|------|------|---------|---------|----------|--------|
| CQ001 | `attention-budget-missing` | Task definition lacks token budget specification | #01 Attention Budget | WARNING | S |
| CQ002 | `context-contamination-risk` | No filtering between agent stages | #02 Context Gate | ERROR | M |
| CQ003 | `generic-persona` | Persona undefined or too generic | #03 Cognitive Profile | WARNING | S |
| CQ004 | `no-mutation-critical` | High-risk task without mutation/review step | #05 Assumption Mutation | ERROR | M |
| CQ005 | `learning-disabled` | No learning/experience accumulation mechanism | #06 Experience Distillation | WARNING | S |

### 2.2 Per-Rule Task Definitions

#### CQ001: attention-budget-missing

| Attribute | Detail |
|-----------|--------|
| **Detection target** | YAML/Markdown task definitions that lack explicit token budget, context size limit, or attention allocation |
| **Pattern mapping** | #01 Attention Budget |
| **Implementation approach** | Bash + grep/awk — scan YAML files for `budget`, `token_limit`, `max_tokens`, `attention_budget` fields. If absent in a task definition block, emit WARNING |
| **Parser requirement** | YAML key-value scanner (lightweight, no full YAML parser needed) |
| **Output format** | `WARNING CQ001: File "path":line — Task "name" has no attention budget defined.` |
| **Test cases** | |
| — Pass | Task YAML with `attention_budget: 4000` field present |
| — Pass | Task YAML with `max_tokens: 8000` field present |
| — Fail | Task YAML with no budget-related field |
| — Fail | Task YAML with `attention_budget: null` |
| **Completion criteria** | Correctly identifies budget presence/absence in crew YAML format and generic YAML format |

#### CQ002: context-contamination-risk

| Attribute | Detail |
|-----------|--------|
| **Detection target** | Multi-stage agent configurations where output from stage N flows to stage N+1 without explicit filtering |
| **Pattern mapping** | #02 Context Gate |
| **Implementation approach** | Bash + pattern matching — analyze agent pipeline definitions for `input`/`output`/`context` fields. Flag when stage N+1's input references stage N's full output without a `filter`, `gate`, or `select` directive |
| **Parser requirement** | Multi-file YAML scanner with stage-linking detection |
| **Output format** | `ERROR CQ002: File "path":line — Agent "name" receives unfiltered output from "source" (Context Gate missing).` |
| **Test cases** | |
| — Pass | Pipeline with explicit `context_filter: [summary, key_findings]` between stages |
| — Pass | Pipeline with `gate: true` directive on input |
| — Fail | Pipeline where agent B's input is `source: agent_A.output` with no filter |
| — Fail | Pipeline with `gate: false` or `gate: disabled` |
| **Completion criteria** | Correctly detects unfiltered context flow in both crew YAML and generic multi-agent YAML |

#### CQ003: generic-persona

| Attribute | Detail |
|-----------|--------|
| **Detection target** | Agent definitions with no persona, a default persona ("assistant", "helper"), or a persona shorter than a meaningful threshold |
| **Pattern mapping** | #03 Cognitive Profile |
| **Implementation approach** | Bash + string matching — scan agent definitions for `persona`, `role`, `profile`, `system_prompt` fields. Flag if absent, if value matches a generic keyword list, or if value is under 20 characters |
| **Parser requirement** | YAML field scanner with string-length check |
| **Output format** | `WARNING CQ003: File "path":line — Agent "name" has generic or undefined persona.` |
| **Test cases** | |
| — Pass | Agent with `persona: "Senior security auditor specializing in contract review"` |
| — Pass | Agent with `cognitive_profile: path/to/profile.md` |
| — Fail | Agent with no persona field |
| — Fail | Agent with `persona: "assistant"` |
| — Fail | Agent with `persona: "helper"` |
| **Completion criteria** | Correctly flags generic/missing personas while allowing file-reference personas |

#### CQ004: no-mutation-critical

| Attribute | Detail |
|-----------|--------|
| **Detection target** | Tasks marked as high-risk or critical that have no mutation, review, or verification step |
| **Pattern mapping** | #05 Assumption Mutation |
| **Implementation approach** | Bash + grep — scan task definitions for `danger_level: high` or `danger_level: critical`. If found, check for presence of `mutation`, `review`, `verify`, `test`, `adversarial` in the same task block or as a dependent task |
| **Parser requirement** | YAML block scanner with cross-reference to dependent tasks |
| **Output format** | `ERROR CQ004: File "path":line — High-risk task "name" has no mutation or verification step.` |
| **Test cases** | |
| — Pass | Task with `danger_level: critical` and `mutation: true` |
| — Pass | Task with `danger_level: high` and a `depends_on` task containing "review" |
| — Pass | Task with `danger_level: low` and no mutation (low-risk, not required) |
| — Fail | Task with `danger_level: critical` and no mutation/review/verify field |
| — Fail | Task with `danger_level: high` and no verification step |
| **Completion criteria** | Correctly enforces mutation/review on high/critical tasks while ignoring low-risk tasks |

#### CQ005: learning-disabled

| Attribute | Detail |
|-----------|--------|
| **Detection target** | Project configurations that have no learning/experience accumulation mechanism |
| **Pattern mapping** | #06 Experience Distillation |
| **Implementation approach** | Bash + grep — scan project root for learning-related configuration: `memory/`, `learned/`, `experience/` directories, or `learning: true`/`experience_distillation: enabled` in config files |
| **Parser requirement** | Directory structure scanner + YAML config scanner |
| **Output format** | `WARNING CQ005: Project has no learning mechanism. Experience Distillation pattern not implemented.` |
| **Test cases** | |
| — Pass | Project with `memory/` directory containing `.md` files |
| — Pass | Project config with `learning: enabled` |
| — Fail | Project with no learning-related directory or config |
| — Fail | Project with `learning: disabled` |
| **Completion criteria** | Correctly detects presence/absence of learning mechanism at project level |

### 2.3 cqlint Architecture

```
cqlint/
├── cqlint.sh              # Entry point — orchestrates rule execution
├── lib/
│   ├── parser_yaml.sh     # YAML key-value scanner (lightweight)
│   ├── parser_dir.sh      # Directory structure scanner
│   ├── output.sh          # Formatting: terminal colors, Markdown report
│   └── utils.sh           # Shared utilities (file discovery, path handling)
├── rules/
│   ├── CQ001_budget_missing.sh       # Rule implementation
│   ├── CQ002_context_contamination.sh
│   ├── CQ003_generic_persona.sh
│   ├── CQ004_no_mutation_critical.sh
│   └── CQ005_learning_disabled.sh
├── adapters/
│   ├── crew_yaml.sh       # crew-specific YAML field mappings
│   └── generic_yaml.sh    # Generic agent YAML field mappings
├── rules/
│   ├── CQ001_budget_missing.md       # Rule documentation
│   ├── CQ002_context_contamination.md
│   ├── CQ003_generic_persona.md
│   ├── CQ004_no_mutation_critical.md
│   └── CQ005_learning_disabled.md
└── tests/
    ├── fixtures/
    │   ├── pass/           # Configurations that should pass all rules
    │   └── fail/           # Configurations that should trigger specific rules
    └── run_tests.sh        # Test runner
```

**Usage**:
```bash
# Scan a directory
cqlint check path/to/agent-config/

# Scan specific files
cqlint check my-agent.yaml --rules CQ001,CQ002

# Use specific adapter
cqlint check . --adapter crew

# Output as Markdown report
cqlint check . --format markdown > cqlint-report.md
```

### 2.4 cqlint Completion Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| CL-1 | `cqlint check .` runs without error on any directory | Manual test on 3+ different project types |
| CL-2 | All 5 rules implemented and documented | Rule file + doc file for each CQ001-CQ005 |
| CL-3 | Test fixtures for each rule (pass + fail) | `tests/fixtures/pass/` and `tests/fixtures/fail/` populated |
| CL-4 | `run_tests.sh` passes all test cases | Zero test failures |
| CL-5 | 30-second experience works | New user can run `cqlint check .` and see actionable output in < 30s |
| CL-6 | crew adapter functional | `cqlint check . --adapter crew` works on multi-agent system YAML files |
| CL-7 | Generic adapter functional | `cqlint check . --adapter generic` works on non-crew YAML |
| CL-8 | Output includes rule ID, severity, file, line, and message | All fields present in output |

---

## 3. CQ Benchmark v0.1 — 4-Axis Specification

### 3.1 Axis Summary Table

| Axis | Purpose | Sub-Metrics | Effort |
|------|---------|-------------|--------|
| **Context Health** | Measure quality of information flowing through agents | 3 sub-metrics | M |
| **Decision Quality** | Measure quality of agent decision-making | 3 sub-metrics | M |
| **Document Integrity** | Measure quality of produced documents | 3 sub-metrics | S |
| **Evolution** | Measure system's ability to learn and improve | 3 sub-metrics | S |

### 3.2 Per-Axis Specification Tasks

#### Axis 1: Context Health Score

| Sub-Metric | Definition | Measurement Method | Baseline |
|-----------|-----------|-------------------|----------|
| **Information Density** | Ratio of task-relevant tokens to total tokens in agent context | `relevant_tokens / total_tokens`. Relevance determined by task keyword overlap | Baseline TBD — measure on 10 crew execution samples |
| **Contamination Level** | Proportion of context that originated from unrelated prior tasks | Track context provenance. `unrelated_tokens / total_tokens` | Baseline TBD — measure on 10 crew executions with/without Context Gate |
| **Freshness** | Age of information in context relative to current task requirements | `(current_time - info_timestamp) / task_lifetime` weighted by importance | Baseline TBD — measure staleness across 10 multi-step tasks |

**Specification task**: Define exact formulas, edge cases, and aggregation method (weighted average vs. worst-of-3).

**Completion criteria**: Specification document with formulas, worked examples for each sub-metric, and identified baseline measurement plan.

#### Axis 2: Decision Quality Score

| Sub-Metric | Definition | Measurement Method | Baseline |
|-----------|-----------|-------------------|----------|
| **Perspective Diversity** | Number of genuinely independent viewpoints considered before a decision | Count distinct perspectives using semantic similarity (cosine distance > threshold = independent) | Baseline TBD — measure on 10 sequential vs. parallel analysis samples |
| **Anchoring Elimination** | Degree to which later analyses are independent of earlier ones | Correlation between generation order and perspective similarity. Zero = no anchoring | Baseline: sequential generation (ChatGPT-style) — measure anchoring effect |
| **Blind-Spot Coverage** | Proportion of stakeholder concerns addressed in the final analysis | `addressed_concerns / total_stakeholder_concerns` (stakeholder list predefined per domain) | Baseline TBD — measure coverage on 5 decision cases |

**Specification task**: Define similarity thresholds, stakeholder concern taxonomies, and aggregation method.

**Completion criteria**: Specification document with measurement protocols, threshold definitions, and pilot measurement plan.

#### Axis 3: Document Integrity Score

| Sub-Metric | Definition | Measurement Method | Baseline |
|-----------|-----------|-------------------|----------|
| **Mutation Kill Rate** | Proportion of applied mutations that were detected as problems | `detected_mutations / total_mutations * 100%` | No baseline needed — this is the absolute measure |
| **Contradiction Count** | Number of internal contradictions in the document | Count instances where two clauses/statements make incompatible claims | Baseline TBD — measure on 5 sample documents |
| **Ambiguity Score** | Density of ambiguous terms that could be interpreted multiple ways | `ambiguous_terms / total_terms * 100%`. Ambiguity defined by mutation sensitivity | Baseline TBD — measure on 5 sample documents |

**Specification task**: Define mutation strategy set for each document type, contradiction detection criteria, and ambiguity classification.

**Completion criteria**: Specification document with formulas, document-type-specific measurement guides, and connection to MutaDoc (Phase 2).

#### Axis 4: Evolution Score

| Sub-Metric | Definition | Measurement Method | Baseline |
|-----------|-----------|-------------------|----------|
| **Pattern Conformance** | Proportion of agent configurations that comply with CQE Patterns | `passing_rules / total_rules` as measured by cqlint | Baseline: cqlint scan of crew before CQE adoption |
| **Learning Accumulation Rate** | Rate at which actionable learning is extracted from execution | `new_learnings_per_task` over rolling window | Baseline TBD — measure on 20 crew task executions |
| **Recurrence Rate** | Proportion of failures that repeat a previously-encountered failure mode | `recurring_failures / total_failures` | Baseline TBD — analyze 50 crew execution logs |

**Specification task**: Define cqlint integration for Pattern Conformance, learning taxonomy for accumulation tracking, and failure fingerprinting for recurrence detection.

**Completion criteria**: Specification document with formulas, cqlint data flow, and integration points for Phase 2+ measurement scripts.

### 3.3 CQ Benchmark Specification Structure

```
benchmark/
├── README.md                      # Overview and quick reference
├── spec.md                        # Full specification (all 4 axes)
└── measures/
    ├── context_health.md          # Axis 1 detailed spec
    ├── decision_quality.md        # Axis 2 detailed spec
    ├── document_integrity.md      # Axis 3 detailed spec
    └── evolution.md               # Axis 4 detailed spec
```

### 3.4 CQ Benchmark Completion Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| BM-1 | All 4 axes specified with formulas | Each axis has 3 sub-metrics with mathematical definitions |
| BM-2 | Worked example for each sub-metric | At least 1 calculation walkthrough per sub-metric |
| BM-3 | Baseline measurement plan defined | Each axis specifies what to measure, sample size, and data source |
| BM-4 | Aggregation method documented | How sub-metrics combine into axis score, and how axes combine into overall CQ score |
| BM-5 | Phase 2+ integration points identified | Document how MutaDoc, ThinkTank, and cqlint feed data into Benchmark |
| BM-6 | Hypothesis validation mapping | Each Phase 1-4 hypothesis mapped to specific Benchmark metric(s) |

---

## 4. Phase 1 Overall

### 4.1 Milestone Definitions

| # | Milestone | Description | Deliverables | Depends On |
|---|-----------|-------------|-------------|------------|
| **M1.1** | Pattern catalog core | 4 Foundational patterns written and reviewed | `01_attention_budget.md`, `02_context_gate.md`, `03_cognitive_profile.md`, `07_file_based_io.md` | None |
| **M1.2** | Pattern catalog complete | All 8 patterns written and reviewed | Remaining 4 pattern files + `patterns/README.md` (index + relationship diagram) | M1.1 |
| **M1.3** | cqlint scaffold | Entry point, parser, and output modules working | `cqlint.sh`, `lib/`, `adapters/`, basic `--help` and file discovery | None |
| **M1.4** | cqlint rules implemented | All 5 rules detecting violations | `rules/CQ001-CQ005*.sh`, test fixtures | M1.1 (rules reference patterns), M1.3 |
| **M1.5** | cqlint 30-second experience | End-to-end: `cqlint check .` produces useful output | Test runner passes, crew adapter works | M1.4 |
| **M1.6** | CQ Benchmark spec | 4-axis specification complete | `spec.md` + 4 axis detail files | M1.1 (patterns inform metrics) |
| **M1.7** | Phase 1 integration test | All components work together, README updated | Integration test passing, `patterns/README.md` references cqlint and benchmark | M1.2, M1.5, M1.6 |

### 4.2 Dependency Diagram

```
                            PHASE 1 DEPENDENCY GRAPH
                            ========================

   ┌──────────────┐                                ┌──────────────┐
   │   M1.1       │                                │   M1.3       │
   │  4 Foundation │                                │  cqlint      │
   │  Patterns     │                                │  scaffold    │
   └──────┬───────┘                                └──────┬───────┘
          │                                               │
          ├─────────────────────┐                          │
          │                     │                          │
          ▼                     ▼                          ▼
   ┌──────────────┐     ┌──────────────┐          ┌──────────────┐
   │   M1.2       │     │   M1.6       │          │   M1.4       │
   │  All 8       │     │  CQ Benchmark│          │  5 cqlint    │
   │  Patterns     │     │  spec        │◀─────────│  rules       │
   └──────┬───────┘     └──────┬───────┘          └──────┬───────┘
          │                     │                          │
          │                     │                          ▼
          │                     │                  ┌──────────────┐
          │                     │                  │   M1.5       │
          │                     │                  │  30-second   │
          │                     │                  │  experience  │
          │                     │                  └──────┬───────┘
          │                     │                          │
          └─────────────────────┼──────────────────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │   M1.7       │
                        │  Integration │
                        │  test        │
                        └──────────────┘

   Legend:
   ─────▶  "depends on" (arrow points from dependent to dependency)
   M1.1 and M1.3 can start in parallel (no dependencies)
   M1.4 depends on BOTH M1.1 (patterns define rules) AND M1.3 (scaffold)
```

### 4.3 Parallel Execution Opportunities

| Parallel Track A | Parallel Track B | Notes |
|-----------------|-----------------|-------|
| M1.1 (4 Foundational Patterns) | M1.3 (cqlint scaffold) | Independent — can start simultaneously |
| M1.2 (remaining 4 patterns) | M1.4 (5 rules) after M1.1+M1.3 | M1.2 and M1.4 can overlap if Foundational patterns (M1.1) are done |
| M1.6 (Benchmark spec) | M1.5 (30-second experience) | Independent after M1.1 |

### 4.4 Phase 1 Completion Criteria (Definition of Done)

Phase 1 is **complete** when ALL of the following are satisfied:

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| P1-1 | 8 pattern files pass all PC-1 through PC-8 criteria | Checklist review per pattern |
| P1-2 | `patterns/README.md` contains index table and relationship diagram | File exists and is non-trivial |
| P1-3 | `cqlint check .` runs on any directory and produces output | Manual test on 3 project types |
| P1-4 | All 5 cqlint rules pass their test fixtures | `run_tests.sh` exits 0 |
| P1-5 | 30-second experience validated | Timed test: clone repo → run `cqlint check examples/` → useful output in < 30s |
| P1-6 | CQ Benchmark spec passes all BM-1 through BM-6 criteria | Checklist review |
| P1-7 | All documentation written in English, arXiv-compatible format | Review for publishability |
| P1-8 | No placeholder text remaining in any deliverable | `grep -r "TODO\|TBD\|PLACEHOLDER"` returns zero results (in delivered files) |

### 4.5 Risks and Mitigations

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|-----------|------------|
| R1 | Pattern misuse epidemic (Strategy Hell) | Undermines CQE credibility | Medium | Anti-Patterns + Failure Catalog + Weight classification included from v0.1. Users can start with 3 Foundational patterns only |
| R2 | "8 patterns = too many to adopt" | Slows adoption | Medium | Weight classification (Foundational / Situational / Advanced). Marketing: "Start with 3, grow to 8" |
| R3 | Evidence Level B for all patterns (no quantitative validation) | Academic skepticism | High | Explicitly disclose Evidence Levels. Define upgrade path to Level A. Write in arXiv-compatible format for future publication |
| R4 | cqlint false positives annoy users | Tool rejection | Medium | Conservative defaults (WARNING not ERROR for uncertain detections). `--strict` flag for those who want ERROR |
| R5 | cqlint Bash approach doesn't scale to complex YAML | Technical limitation | Low | Bash handles 90% of cases. For complex cases, fall back to Claude Code as parser (via Task tool) |
| R6 | CQ Benchmark metrics unmeasurable in practice | Spec becomes shelfware | Medium | Each metric must have a "minimal viable measurement" that can be computed from existing data (crew logs) |
| R7 | Scope creep — Phase 1 expands into implementation | Delays Phase 2 (MutaDoc) | Medium | Strict Phase 1 = specification + tooling scaffold. No application-layer code. CQ Benchmark is spec-only |

### 4.6 Phase 1 → Phase 2 Transition Criteria

Phase 2 (MutaDoc) may begin when:

| # | Criterion | Rationale |
|---|-----------|-----------|
| T1 | M1.1 complete (4 Foundational patterns) | MutaDoc needs at minimum Assumption Mutation pattern |
| T2 | M1.3 complete (cqlint scaffold) | MutaDoc will be validated using cqlint |
| T3 | M1.6 started (Benchmark spec) | MutaDoc hypothesis validation needs Benchmark metrics defined |

**Note**: Full Phase 1 completion (M1.7) is NOT required before Phase 2 can start. The remaining 4 Situational/Advanced patterns (M1.2) and 30-second experience polish (M1.5) can proceed in parallel with early Phase 2 work.

---

## Appendix: Task Effort Summary

| Component | Task Count | Total Effort |
|-----------|-----------|-------------|
| CQE Patterns | 8 pattern files + 1 index | 3S + 3M + 1L = ~2,800 lines of Markdown |
| cqlint | 5 rules + scaffold + 2 adapters + tests | 3S + 2M = ~1,500 lines of Bash + Markdown |
| CQ Benchmark | 4 axis specs + 1 overview | 2S + 2M = ~1,200 lines of Markdown |
| Integration | README, cross-references, integration test | S = ~200 lines |
| **Total** | | **~5,700 lines estimated** |
