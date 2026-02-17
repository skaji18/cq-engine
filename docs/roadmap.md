# Cognitive Quality Engineering — Implementation Roadmap

> **Version**: 2.0.0
> **Repository**: `cq-engine`
> **License**: MIT
> **Origin**: Initial exploration (5 Directions + DSL/CTL analysis)
> **Purpose**: Public GitHub repository roadmap for the CQE ecosystem
> **Detail files**: Each phase has a dedicated detail document in `docs/phases/`

---

## 1. Vision & Goals

### The Vision

Establish **Cognitive Quality Engineering (CQE)** as a new engineering discipline — not just a product, but a field with named concepts, verification tools, killer applications, and a distribution platform that reaches every Claude Code user.

Just as GoF gave Object-Oriented Programming its "Design Patterns," CQE gives LLM agent design its vocabulary, tools, and measurement framework.

### The Goal

Build and ship the CQE ecosystem in four sequential phases:

1. **Name the concepts** — Create the pattern catalog and linter that define the discipline
2. **Prove the value** — Build MutaDoc, a killer app that demonstrates CQE principles to non-technical users
3. **Distribute at scale** — Package everything as an MCP Server that reaches all Claude Code users with a single install command
4. **Expand applications** — Add ThinkTank for multi-perspective decision support

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Zero Infrastructure** | Bash + Markdown + Claude Code. No databases, no external services, no cloud dependencies |
| **Sequential Execution** | Each phase builds on the previous. No phase starts until its prerequisites are met |
| **Circular Feedback** | Not a one-way pipeline — telemetry flows back to improve patterns, strategies, and tools |
| **Independence + Integration** | Each direction delivers standalone value, yet integrates into a unified ecosystem via CQ Benchmark |

---

## 2. Phase Overview

```
Phase 1 ✓             Phase 2 ✓             Phase 3 ✓             Phase 4
FOUNDATION             KILLER APP             DISTRIBUTION           EXPANSION
─────────────────────  ─────────────────────  ─────────────────────  ─────────────────────
CQE Patterns v0.1      MutaDoc v0.1           CQ MCP Server v0.1     ThinkTank v0.1
  8 patterns (GoF)       5 mutation strategies   6 MCP tools            8 personas
  Anti-Patterns          3 adversarial personas  3 hooks                3-Wave pipeline
cqlint v0.1              Mutation-Driven Repair  Telemetry baseline     Anchoring Visibility
  5 rules (Bash)         12 document presets     Feedback loop v1       Contradiction Heatmap
CQ Benchmark v0.1        CQ Benchmark applied                          MCP integration
  4-axis spec                                                          Feedback loop v2

Milestones: 7          Milestones: 6          Milestones: 7          Milestones: 11
Tasks: ~25             Tasks: 40              Tasks: 18              Tasks: 30
Size: M                Size: L                Size: L                Size: L

✓ COMPLETE             ✓ COMPLETE             ✓ COMPLETE             ◀── NEXT
───────────────────────────────────────────────────────────────────────────────────────────
                                  ▲
                        CQ Benchmark (cross-cutting: defined in Phase 1, applied from Phase 2)

                        Phase 5 (CONDITIONAL): CTL — Cognitive Task Language
                        Revival checkpoint at Phase 3. Milestones: 7, Tasks: 10
```

### CTL (Cognitive Task Language) — Cross-Cutting Consideration

CTL was explored as a dedicated DSL for describing cognitive tasks with type-safe syntax and static analysis. It was **deferred** (not rejected) during the sharpening phase due to high learning cost. The cqlint approach delivers equivalent quality assurance with zero learning curve.

**CTL positioning in this roadmap:**
- **Phase 1**: CTL concepts are absorbed into cqlint rules (budget checking, gate validation, persona verification)
- **Phase 3**: Revival checkpoint — if 4 quantitative criteria are met, CTL proceeds to Phase 5
- **Rationale**: "Tools first, language later" — users experience cqlint, understand why it catches what it catches, and only then might want the expressiveness of a dedicated language

> **Full detail**: [phases/phase-5-ctl.md](phases/phase-5-ctl.md)

---

## 3. Phase Details

### Phase 1: Foundation

> *"Pattern naming has the highest leverage. A foundation without which killer apps are just 'useful tools.'"*

**Purpose**: Define the vocabulary of Cognitive Quality Engineering. Name the unnamed concepts, formalize them as patterns, build the first automated verifier, and specify the measurement framework.

> **Full detail**: [phase-1-foundation.md](phases/phase-1-foundation.md)

**Implementation Status**: ✓ COMPLETE
- 8 patterns written (GoF format), indexed with relationship diagram
- cqlint v0.1: cqlint.sh (527 lines) + 5 rules (CQ001-CQ005) + 10 test fixtures
- CQ Benchmark v0.1: 4-axis specification complete
- Anti-pattern index: 34 entries across 8 patterns
- Total: 33 files, ~5,139 lines
- Commit: 31ad10c

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **CQE Patterns v0.1** | 8 core patterns in GoF format (Problem / Context / Solution / Anti-Pattern / Evidence Level / Known Uses / Related) |
| 2 | **cqlint v0.1** | 5 lint rules (CQ001–CQ005) implemented in Bash + Claude Code |
| 3 | **CQ Benchmark v0.1** | Specification document for the 4-axis measurement framework (no implementation yet) |

**8 Core Patterns**:

| # | Pattern | Weight | Evidence | Effort |
|---|---------|--------|----------|--------|
| 01 | Attention Budget | Foundational | B | M |
| 02 | Context Gate | Foundational | B | M |
| 03 | Cognitive Profile | Foundational | B | M |
| 04 | Wave Scheduler | Situational | B | S |
| 05 | Assumption Mutation | Situational | B | L |
| 06 | Experience Distillation | Advanced | B | M |
| 07 | File-Based I/O | Foundational | B | S |
| 08 | Template-Driven Role | Situational | B | S |

Each pattern includes Anti-Pattern section, Failure Catalog, Interaction Catalog, and Evidence Level (A/B/C/D).

**5 cqlint Rules**:

| Rule | Name | Detects | Severity |
|------|------|---------|----------|
| CQ001 | attention-budget-missing | Task definition lacks token budget | WARNING |
| CQ002 | context-contamination-risk | No filtering between agent stages | ERROR |
| CQ003 | generic-persona | Persona undefined or too generic | WARNING |
| CQ004 | no-mutation-critical | High-risk task without mutation step | ERROR |
| CQ005 | learning-disabled | Learning mechanism absent | WARNING |

**CQ Benchmark v0.1 — 4-Axis Specification**:

| Axis | Sub-metrics |
|------|-------------|
| Context Health Score | Information density, contamination level, freshness |
| Decision Quality Score | Perspective diversity, anchoring exclusion, blind-spot coverage |
| Document Integrity Score | Mutation Kill rate, contradiction count, ambiguity score |
| Evolution Score | Pattern compliance rate, learning accumulation rate, recurring issue rate |

#### Tasks

| Task ID | Task | Effort | Dependencies |
|---------|------|:------:|-------------|
| Patterns 01-04 | Write 4 Foundational patterns | 2M + 1S = ~1,100 lines | None |
| Patterns 05-08 | Write 4 Situational/Advanced patterns | 1L + 2M + 1S = ~1,700 lines | Patterns 01-04 |
| Pattern index | `patterns/README.md` with relationship diagram | S | All patterns |
| cqlint scaffold | Entry point, parser, output modules | S | None |
| cqlint rules | 5 rules + test fixtures | 3S + 2M | Patterns 01-04, scaffold |
| cqlint adapters | crew YAML + generic YAML adapters | 2S | scaffold |
| Benchmark spec | 4-axis specification with formulas | 2S + 2M | Patterns 01-04 |
| Integration | Cross-references, integration test | S | All above |

**Estimated total**: ~5,700 lines (Markdown + Bash)

#### Milestones

| # | Milestone | Definition of Done | Depends On |
|---|-----------|-------------------|------------|
| **M1.1** | Pattern catalog core | 4 Foundational patterns written and reviewed | None |
| **M1.2** | Pattern catalog complete | All 8 patterns + index with relationship diagram | M1.1 |
| **M1.3** | cqlint scaffold | Entry point, parser, output modules working | None |
| **M1.4** | cqlint rules implemented | All 5 rules detecting violations in test fixtures | M1.1, M1.3 |
| **M1.5** | cqlint 30-second experience | `cqlint check .` produces useful output in < 30s | M1.4 |
| **M1.6** | CQ Benchmark spec | 4-axis specification complete with formulas and worked examples | M1.1 |
| **M1.7** | Phase 1 integration test | All components work together, README updated | M1.2, M1.5, M1.6 |

**Parallel Execution**: M1.1 and M1.3 can start simultaneously (no dependencies).

#### Completion Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| P1-1 | 8 pattern files pass all completion criteria (PC-1 through PC-8) | Checklist review per pattern |
| P1-2 | `cqlint check .` runs on any directory and produces output | Manual test on 3 project types |
| P1-3 | All 5 cqlint rules pass their test fixtures | `run_tests.sh` exits 0 |
| P1-4 | 30-second experience validated | Timed test: clone → run → useful output in < 30s |
| P1-5 | CQ Benchmark spec covers all 4 axes with formulas | Review for completeness |
| P1-6 | All documentation in English, arXiv-compatible format | Review for publishability |
| P1-7 | No placeholder text remaining | `grep -r "TODO\|TBD\|PLACEHOLDER"` returns zero |

#### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pattern misuse epidemic (Strategy Hell) | Undermines CQE credibility | Anti-Patterns + Failure Catalog + Weight classification from v0.1 |
| "8 patterns = too many" | Slows adoption | Weight classification: "Start with 3 Foundational, grow to 8" |
| Evidence Level B only (no quantitative validation) | Academic skepticism | Disclose Evidence Levels; define upgrade path to A; arXiv-compatible format |
| cqlint false positives | Tool rejection | Conservative defaults (WARNING not ERROR for uncertain detections) |
| Scope creep delays Phase 2 | Schedule slip | Strict Phase 1 = specification + tooling scaffold. No application-layer code |

> **Full risk table with likelihood**: [phases/phase-1-foundation.md §4.5](phases/phase-1-foundation.md)

**Dependencies**: None (this is the foundation)

**Estimated Size**: **M** (Medium)

**Entry Criteria**: None

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | Pattern vocabulary improves design discussions | 5 AI engineers review with/without catalog | 30% faster OR 50% more issues found |
| H2 | cqlint detects quality issues pre-execution | Analyze 50 past execution logs | 40%+ failures pre-detectable |
| H3 | Patterns apply across frameworks | Test on LangGraph, CrewAI, raw Task tool | Quality improves on all 3 |
| H4 | Anti-Patterns reduce pattern misuse by 50%+ | Compare misuse rates with/without docs | 50%+ reduction |

---

### Phase 2: Killer App (MutaDoc)

> *"Document mutation testing is a category that does not exist on Earth."*

**Purpose**: Build MutaDoc — the first tool that applies software mutation testing to documents. Prove that CQE principles create value beyond the AI engineering community by reaching lawyers, researchers, and quality managers.

> **Full detail**: [phase-2-mutadoc.md](phases/phase-2-mutadoc.md)

**Implementation Status**: ✓ COMPLETE
- MutaDoc v0.1: mutadoc.sh (1,096 lines)
- 5 mutation strategies implemented
- 3 adversarial personas defined
- Mutation-Driven Repair with 5 repair templates
- 4 document type presets (contract, api_spec, academic_paper, policy)
- 3 test fixtures with intentional vulnerabilities
- Total: 23 files, ~6,921 lines
- Commit: 47bcf23

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **MutaDoc v0.1** | Document mutation testing engine with 5 strategies + Mutation-Driven Repair + Regression Mutation |
| 2 | **12 document type presets** | Strategy presets for contracts, API specs, academic papers, policy docs, and 8 more |
| 3 | **CQ Benchmark applied** | First application of CQ Benchmark to validate MutaDoc hypotheses |

**5 Mutation Strategies**:

| Strategy | Description | Size |
|----------|-------------|:----:|
| Contradiction | Alter a clause and detect cascading contradictions | M |
| Ambiguity | Replace vague modifiers with extremes to expose meaninglessness | M |
| Deletion | Remove a clause and measure structural impact (zero = dead clause) | S |
| Inversion | Reverse assumptions/claims and measure argument robustness | M |
| Boundary | Mutate parameters (numbers, deadlines) to test conclusion robustness | S |

**Key Innovation — Mutation-Driven Repair**:
- **Repair Draft**: Auto-generate fix suggestions for each Critical finding
- **Repair Impact Analysis**: Predict cascading effects of proposed fixes
- **Regression Mutation**: Re-apply mutation to repaired text to verify no new vulnerabilities
- Mirrors ESLint's auto-fix revolution: "detect + repair" achieves 10x adoption over "detect only"

**3 Adversarial Personas**:

| Persona | Role | Strategy Affinity |
|---------|------|-------------------|
| `adversarial_reader` | Malicious reader seeking exploitable ambiguity | Ambiguity, Boundary |
| `opposing_counsel` | Opposing lawyer seeking contract weaknesses | Contradiction, Deletion |
| `naive_implementer` | Developer who implements everything literally | Ambiguity, Inversion |

#### Tasks

| Area | Task Count | Size |
|------|:----------:|:----:|
| Strategy S1 (Contradiction) | 4 tasks | M |
| Strategy S2 (Ambiguity) | 4 tasks | M |
| Strategy S3 (Deletion) | 4 tasks | S |
| Strategy S4 (Inversion) | 4 tasks | M |
| Strategy S5 (Boundary) | 4 tasks | S |
| Persona P1 (Adversarial Reader) | 3 tasks | M |
| Persona P2 (Opposing Counsel) | 3 tasks | M |
| Persona P3 (Naive Implementer) | 3 tasks | M |
| Mutation-Driven Repair | 6 tasks | L |
| Document Type Presets | 5 tasks | M |
| **Total** | **40 tasks** | **L** |

> **Full task breakdown**: [phases/phase-2-mutadoc.md §1–4](phases/phase-2-mutadoc.md)

#### Milestones

| # | Milestone | Definition of Done | Depends On |
|---|-----------|-------------------|------------|
| **M2.1** | 5 strategies implemented | All 5 produce mutation test reports on sample documents; 2+ test fixtures each | Phase 1 M1.1 |
| **M2.2** | Mutation-Driven Repair functional | Repair drafts for Critical findings; regression mutation validates repairs; diff view renders | M2.1 |
| **M2.3** | "30-second experience" working | `mutadoc test README.md` returns findings within 30 seconds | M2.1 |
| **M2.4** | 12 document type presets | All presets functional; auto-detection works for core 4 types | M2.1 |
| **M2.5** | CQ Benchmark validation | Hypotheses H1-H5 validated using CQ Benchmark metrics | M2.1, M2.2, Phase 1 M1.6 |
| **M2.6** | Mutation Kill Score | Numerical document quality score calculated and displayed | M2.1 |

#### Completion Criteria

| # | Criterion | Validation |
|---|-----------|-----------|
| 1 | All 5 strategies produce correct reports on test fixtures | Automated test runner |
| 2 | All 3 personas produce actionable analysis | Human review per persona |
| 3 | Repair drafts generated for 100% of Critical findings | Automated check |
| 4 | Regression Mutation detects ≥ 1 repair-introduced issue | Automated detection |
| 5 | 10+ presets available and functional | Automated run on sample inputs |
| 6 | "30-second experience" within 30s on 100-line document | Timed test |
| 7 | Mutation Kill Score displayed in output | Automated check |
| 8 | CQ Benchmark validation complete for H1-H5 | Review validation report |

#### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| "Just ask ChatGPT to review" perception | Dismissed as unnecessary | "30-second experience" shows result ChatGPT missed |
| Repair suggestions unusable | Seen as noise | Target 30%+ "use as-is" rate; diff view for evaluation |
| Document type coverage too narrow | Perceived as niche | Launch with 12 presets + custom preset capability |
| Slow execution (5+ minutes) | UX indistinguishable from ChatGPT | Progress in 5s; Critical first-report in 2 minutes |
| High false positive rate | User trust erodes | Per-preset severity calibration; confidence scores |

> **Full risk table**: [phases/phase-2-mutadoc.md §5.7](phases/phase-2-mutadoc.md)

**Dependencies**: Phase 1 (CQE Patterns provide theoretical foundation)

**Estimated Size**: **L** (Large)

**Entry Criteria**:
- CQE Patterns v0.1 published (M1.1)
- cqlint v0.1 functional (M1.2)

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | MutaDoc detects issues human reviewers miss | 5 contracts with known issues, compare with 2 lawyers | 50%+ of missed issues detected |
| H2 | Strategies generalize across document types | Same 5 strategies on contracts, specs, papers | 1+ Critical in all 3 types |
| H3 | Mutation mechanism ports from code to docs | Script adversarial approach, apply to new docs | Quality matches manual review |
| H4 | 30%+ of repair suggestions directly usable | Human evaluation of 20 repair drafts | 30%+ "use as-is" rate |
| H5 | Regression Mutation catches new vulnerabilities | Re-mutate 10 repaired documents | 15%+ detection rate |

---

### Phase 3: Distribution (CQ MCP Server)

> *"The best product, if it can't reach anyone, is the same as not existing."*

**Purpose**: Package CQE Patterns, cqlint, and MutaDoc as an MCP Server that any Claude Code user can install with a single command. Add telemetry to create a self-improving ecosystem.

> **Full detail**: [phase-3-mcp-server.md](phases/phase-3-mcp-server.md)

**Implementation Status**: ✓ COMPLETE
- CQ MCP Server v0.1: server.py (110 lines, FastMCP)
- 6 MCP tools: decompose, gate, persona, cqlint, mutate, learn
- 3 MCP resources: patterns, learned, health
- 3 Claude Code hooks: cognitive_hygiene_check, auto_mutation, auto_learn
- Telemetry collector: local JSONL, no network
- Total: 23 files, ~3,178 lines
- Commit: 870eeb1

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **CQ MCP Server v0.1** | MCP server with 6 core tools + MutaDoc wrapper |
| 2 | **Hooks integration** | PreToolUse / PostToolUse / Notification hooks |
| 3 | **Telemetry baseline** | Local-only usage data collection + CQ Health Dashboard |

**6 MCP Tools**:

| Tool | Function | Effort | Priority |
|------|----------|:------:|:--------:|
| `cq_engine__decompose` | Task decomposition within attention budgets | M | High |
| `cq_engine__gate` | Context filtering for subtasks | M | High |
| `cq_engine__persona` | Optimal persona selection | S | Medium |
| `cq_engine__mutate` | Mutation testing for robustness | L | High |
| `cq_engine__learn` | Knowledge accumulation across sessions | M | Medium |
| `cq_engine__cqlint` | MCP wrapper for cqlint | S | High |

**Additional wrapper tools**: `cq_engine__mutadoc` (Phase 2 integration), `cq_engine__benchmark` (measurement)

**3 Hooks**:

| Hook | Trigger | Action |
|------|---------|--------|
| PreToolUse | Before Edit/Write | Context hygiene check via `gate` |
| PostToolUse | After Task completion | Auto-mutation via `mutate` |
| Notification | Task outcome | Auto-learning via `learn` |

**Telemetry** (All Local, Privacy-First): Usage frequency, failure patterns, quality improvement data, task correlation. Storage: `~/.cq-engine/telemetry/` (JSONL, auto-rotated, 90-day retention).

#### Tasks

| Area | Task Count | Effort |
|------|:----------:|:------:|
| MCP Tools (6 core) | 6 | 2S + 3M + 1L |
| Hooks | 5 | 4S + 1M |
| Telemetry | 7 | 3S + 3M |
| **Total** | **18 tasks** | **L** |

> **Full task breakdown**: [phases/phase-3-mcp-server.md §2–4](phases/phase-3-mcp-server.md)

#### Milestones

| # | Milestone | Definition of Done | Depends On |
|---|-----------|-------------------|------------|
| **M3.1** | MCP server installable | `claude mcp add cq-engine` works; all 6 core tools respond | Phase 1 (M1.1, M1.2) |
| **M3.2** | Core tools functional | All 6 tools pass test suites; Bash/CLI fallbacks work for every tool | M3.1 |
| **M3.3** | MutaDoc integration | `cq_engine__mutadoc` wraps MutaDoc v0.1 | Phase 2 (M2.1, M2.2) |
| **M3.4** | Hooks auto-trigger | PreToolUse and PostToolUse hooks installed and functioning | M3.2 |
| **M3.5** | Telemetry collecting | Local data accumulating; all tools emit events; aggregation pipeline operational | M3.2 |
| **M3.6** | CQ Health Dashboard | `cq_engine://health` returns 4-axis scores; CLI `cq-engine report` generates report | M3.5 |
| **M3.7** | Feedback loop v1 | First telemetry-driven update: identify most violated pattern → update Anti-Pattern → adjust rule threshold | M3.5, M3.6 |

**Parallelization**: After M3.2, hooks (M3.4), telemetry (M3.5), and MutaDoc integration (M3.3) can proceed in parallel.

**CTL Revival Checkpoint**: Evaluated after M3.4, before M3.7. See [Phase 5 (CTL)](#phase-5-cross-cutting-ctl--cognitive-task-language).

#### Completion Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| 1 | `claude mcp add cq-engine` installs successfully | Clean environment test |
| 2 | All 6 core tools + mutadoc wrapper pass tests | 30+ test cases |
| 3 | Bash/CLI fallback exists for every MCP tool | Each tool testable without MCP |
| 4 | Hooks auto-trigger on Edit/Write/Task | Integration test |
| 5 | Telemetry accumulates with zero network calls | Network monitor verification |
| 6 | CQ Health Dashboard returns 4-axis scores | Report generation test |
| 7 | First feedback loop cycle completed | At least 1 telemetry-driven rule update |
| 8 | No Python dependency leaks outside mcp-server/ | Dependency audit |

#### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python dependency contradicts zero-infra | Philosophy inconsistency | Bash/CLI fallback for every MCP tool; document exception |
| Telemetry privacy concerns | User distrust | All telemetry strictly local; no network calls; opt-out mechanism |
| MCP SDK API changes | Server breaks on update | Pin to stable SDK version; compatibility test suite |
| Hook performance overhead | Slows sessions | Strict timeouts (5s PreToolUse, 30s PostToolUse) |
| Agent Teams competition | Direct competitor | Prepare CQE as Agent Teams CLAUDE.md injection path |

> **Full risk table**: [phases/phase-3-mcp-server.md §5.5](phases/phase-3-mcp-server.md)

**Dependencies**: Phase 1 (patterns + cqlint) and Phase 2 (MutaDoc)

**Estimated Size**: **L** (Large)

**Entry Criteria**:
- CQE Patterns v0.1 stable
- cqlint v0.1 validated
- MutaDoc v0.1 functional (M2.1 + M2.2)

**Note on Infrastructure Exception**: CQ MCP Server is the **only** component requiring Python (MCP SDK). A Bash/CLI fallback must always exist for every MCP tool.

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | MCP delivery reaches 10x more users | Compare installs vs framework users | 5x+ install ratio |
| H2 | Claude Code autonomously uses CQ tools | 10 task types autonomous usage test | 70%+ on complex tasks |
| H3 | MCP improves quality for non-cq-engine users | Same-task quality comparison | 20%+ improvement |
| H4 | Telemetry recommendations outperform static rules | Compare adoption rates | 30%+ higher adoption |

---

### Phase 4: Expansion (ThinkTank)

> *"What ChatGPT cannot do by principle: truly independent multi-perspective analysis."*

**Purpose**: Build ThinkTank — an anti-anchoring decision engine that uses independent-context parallel analysis to produce genuinely diverse perspectives. Integrate it into the CQ MCP Server to complete the ecosystem.

> **Full detail**: [phases/phase-4-thinktank.md](phases/phase-4-thinktank.md)

**Implementation Status**: Not Started

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **ThinkTank v0.1** | 8-persona, 3-Wave decision engine with Anchoring Visibility Score |
| 2 | **MCP integration** | ThinkTank added as `cq_engine__thinktank` tool |
| 3 | **Feedback loop activation** | First telemetry → pattern evolution cycle |

**3-Wave Process**:

| Wave | Name | Description |
|------|------|-------------|
| Wave 1 | Independent Analysis | 8 personas analyze in isolated contexts (parallel, zero cross-contamination) |
| Wave 2 | Cross-Critique | Each persona critiques others' analyses; generates Contradiction Heatmap data |
| Wave 3 | Synthesis | Integrate into Decision Brief with risk matrix + Anchoring Visibility Score |

**8 Personas**:

| # | Persona | Category | Key Concern |
|---|---------|----------|-------------|
| P1 | CFO | Business | Financial viability, ROI, cost structure |
| P2 | CTO | Business | Technical feasibility, scalability, tech debt |
| P3 | CMO | Business | Market fit, competitive positioning |
| P4 | Investor | Business | Valuation, exit potential, capital efficiency |
| P5 | Customer | Stakeholder | Usability, value perception, pain points |
| P6 | Employee | Stakeholder | Workload impact, skill requirements, morale |
| P7 | Regulator | Stakeholder | Legal compliance, data privacy, liability |
| P8 | Devil's Advocate | Meta | Assumptions challenged, worst-case scenarios |

**Key Innovations**:
- **Anchoring Visibility Score (AVS)**: `(PSS_sequential - PSS_parallel) / PSS_sequential × 100` — quantifies bias eliminated by parallel execution
- **Contradiction Heatmap**: 8×8 matrix visualizing inter-persona disagreements
- **Parameter Mutation Test**: Sensitivity analysis on decision parameters
- **Decision Replay**: Re-analyze past decisions for continuous improvement
- **Quick Mode**: 3-persona subset (CFO + CTO + Devil's Advocate) for rapid analysis

#### Tasks

| Area | Task Count | Size |
|------|:----------:|:----:|
| Persona templates (8 + custom + quick mode) | 10 | 9S + 1M |
| Wave 1 design + orchestration | 2 | 2M |
| Wave 2 design + heatmap + orchestration | 3 | 2M + 1S |
| Wave 3 synthesis + brief format + orchestration | 3 | 1L + 2M |
| AVS specification + calculator + visualization | 5 | 3M + 2S |
| MCP integration + CLI + telemetry + tests | 5 | 2L + 1M + 2S |
| **Total** | **30 tasks** | **(12S + 13M + 5L)** |

> **Full task breakdown**: [phases/phase-4-thinktank.md §1–4](phases/phase-4-thinktank.md)

#### Milestones

| # | Milestone | Definition of Done | Depends On |
|---|-----------|-------------------|------------|
| **M4.1** | 3-Wave pipeline functional | Wave 1→2→3 produces a complete Decision Brief | M3.1 |
| **M4.2** | 8 persona templates complete | All 8 produce domain-appropriate analyses on 3 test decisions | None (internal) |
| **M4.3** | AVS implemented | Calculator produces valid scores; sequential baseline works | M4.1 |
| **M4.4** | Contradiction Heatmap functional | 8×8 heatmap renders in Decision Brief | M4.1 |
| **M4.5** | Parameter Mutation operational | Sensitivity analysis for numeric parameter variations | M4.1 |
| **M4.6** | Quick mode (3-persona) functional | Decision Brief in < 2 minutes | M4.1, M4.2 |
| **M4.7** | MCP integration complete | `cq_engine__thinktank` available via MCP Server | M3.1, M4.1 |
| **M4.8** | Bash/CLI fallback validated | `thinktank.sh` produces output equivalent to MCP tool | M4.7 |
| **M4.9** | Decision Replay functional | Re-analysis of past decisions produces improved quality | M4.1 |
| **M4.10** | Feedback loop operational | Telemetry drives ≥ 1 pattern/persona update | M3.5, M4.7 |
| **M4.11** | "30-second experience" working | 8 independent perspectives within 30 seconds | M4.1, M4.6 |

#### Completion Criteria

| # | Criterion | Validation |
|---|-----------|-----------|
| 1 | All 11 milestones achieved | Checklist review |
| 2 | Full mode produces valid Decision Briefs for 5 test decisions | Quality review |
| 3 | Quick mode in < 2 minutes | Timing measurement |
| 4 | AVS > 0% on all test decisions | Automated calculation |
| 5 | `cq_engine__thinktank` callable via MCP | Integration tests |
| 6 | CLI produces equivalent output to MCP tool | Diff comparison |
| 7 | H1 validated: parallel diversity ≥ 1.5× sequential | Statistical test (p < 0.05) |
| 8 | H2 validated: Wave 2 reduces blind spots ≥ 30% | Before/after comparison |
| 9 | ≥ 1 feedback-loop cycle completed | Audit trail |

#### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| "Multi-perspective = SWOT/Six Hats" perception | Dismissed as derivative | Position as "Anti-Anchoring Engine"; lead with AVS, not "8 perspectives" |
| 8 personas too expensive (API costs) | Prohibitive for casual use | 3-persona quick mode; full mode for important decisions |
| AVS methodology unvalidated | Core differentiator unproven | Validate with statistical rigor (20+ decisions) before marketing |
| Slow execution (>5 min full mode) | UX issue | Progress display in 30s; quick mode for immediacy |
| Wave 2 degenerates into agreement | Lost value | Devil's Advocate mandatory; critique template requires ≥ 2 disagreements |

> **Full risk table**: [phases/phase-4-thinktank.md §5.6](phases/phase-4-thinktank.md)

**Dependencies**: Phase 3 (MCP Server provides distribution channel)

**Estimated Size**: **L** (Large)

**Entry Criteria**:
- CQ MCP Server v0.1 operational (M3.1 + M3.2)
- Distribution channel validated

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | Parallel analysis more diverse than sequential | ThinkTank vs ChatGPT "8 perspectives" | 1.5×+ diversity score |
| H2 | Wave 2 cross-critique improves quality | Wave 1 only vs Wave 1+2 | 30%+ blind spot reduction |
| H3 | Retroactively detects past decision failures | Analyze Kodak, Nokia, WeWork, etc. | 3/5+ factors detected |
| H4 | Sequential shows anchoring; parallel shows zero | Similarity vs generation order | Positive (sequential), zero (parallel) |

---

### Phase 5 (Cross-Cutting): CTL — Cognitive Task Language

> **Status**: Conditional — activated only if revival conditions are met at Phase 3

**Purpose**: If the CQE ecosystem outgrows YAML-based cqlint, provide a dedicated type-safe language for describing cognitive tasks with static analysis capabilities beyond what YAML rules can express.

> **Full detail**: [phases/phase-5-ctl.md](phases/phase-5-ctl.md)

**Revival Conditions** (ALL must be met at Phase 3 checkpoint):

| # | Criterion | Threshold |
|---|-----------|-----------|
| RC-1 | CQE Patterns maturity | v0.2+ with ≥ 12 patterns, ≥ 3 at Evidence Level A |
| RC-2 | cqlint rule saturation | ≥ 15 rules AND ≥ 3 "can't express in YAML" complaints |
| RC-3 | Community demand | ≥ 10 unique users requesting DSL features |
| RC-4 | Reproducibility gap | ≥ 5 documented cases of quality inconsistency from informal task definition |

**Revival Decision**: All 4 met → REVIVE | 3/4 → CONDITIONAL (MVP grammar only) | ≤ 2 → DEFER

**MVP Grammar**: 5 keywords (`task`, `wave`, `gate`, `persona`, `invariant`), formal BNF/PEG specification.

**CTL-Only Capabilities** (what YAML rules cannot do):

| Rule | Name | Description |
|------|------|-------------|
| CQ006 | budget-overflow | Total subtask budgets exceed parent task budget |
| CQ007 | gate-inconsistency | Downstream references data excluded by upstream gate |
| CQ008 | dependency-cycle | Circular dependency in wave definitions |
| CQ009 | unused-invariant | Invariant condition trivially satisfied |

**Milestones** (conditional, post-revival):

| # | Milestone | Depends On |
|---|-----------|------------|
| **M5.1** | Grammar spec complete + 20 retrospective `.ctl` files | Revival GO decision |
| **M5.2** | Parser and type checker functional | M5.1 |
| **M5.3** | cqlint CTL adapter integrated | M5.2 |
| **M5.4** | Runtime functional | M5.2 |
| **M5.5** | Sample library + documentation | M5.4 |
| **M5.6** | Usability validated (3 devs productive in 30 min) | M5.5 |
| **M5.7** | YAML-to-CTL converter | M5.2 |

**Key design decision**: YAML and CTL coexist. CTL is opt-in for power users. Both produce the same execution plan — the difference is in pre-execution verification depth.

---

## 4. Cross-Phase Sections

### 4.1 Cross-Phase Dependency Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CQ BENCHMARK (Cross-Cutting)                             │
│                  Defined in Phase 1 → Applied from Phase 2                       │
└────────────┬──────────────────────┬──────────────────────┬──────────────────────┘
             │                      │                      │
             ▼                      ▼                      ▼
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│    PHASE 1         │  │    PHASE 2         │  │    PHASE 3         │  │    PHASE 4         │
│    Foundation      │─▶│    Killer App      │─▶│    Distribution    │─▶│    Expansion       │
│                    │  │                    │  │                    │  │                    │
│ M1.1 Patterns core │  │ M2.1 5 strategies  │  │ M3.1 MCP install   │  │ M4.1 3-Wave pipe   │
│ M1.2 Patterns full │  │ M2.2 Repair engine │  │ M3.2 Core tools    │  │ M4.2 8 personas    │
│ M1.3 cqlint scaff  │  │ M2.3 30-sec exp    │  │ M3.3 MutaDoc integ │  │ M4.3 AVS           │
│ M1.4 cqlint rules  │  │ M2.4 12 presets    │  │ M3.4 Hooks         │  │ M4.4-M4.6 Features │
│ M1.5 30-sec exp    │  │ M2.5 Benchmark val │  │ M3.5 Telemetry     │  │ M4.7 MCP integ     │
│ M1.6 Benchmark spec│  │ M2.6 Kill Score    │  │ M3.6 Dashboard     │  │ M4.8-M4.9 CLI+Rep  │
│ M1.7 Integration   │  │                    │  │ M3.7 Feedback v1   │  │ M4.10 Feedback v2  │
│                    │  │                    │  │                    │  │ M4.11 30-sec exp   │
└────────────────────┘  └────────────────────┘  └─────────┬──────────┘  └────────────────────┘
     │                                                     │
     │                  CTL Revival Checkpoint ◇            │
     │                  (after M3.4, before M3.7)          │
     │                         │ GO                        │
     │                         ▼                           │
     │              ┌────────────────────┐                 │
     │              │   PHASE 5 (Cond.)  │                 │
     │              │   CTL/DSL          │                 │
     │              │   M5.1-M5.7       │                 │
     └─────────────▶│   (if revived)     │◀────────────────┘
                    └────────────────────┘
```

### 4.2 Technical Dependency Flow

```
KNOWLEDGE LAYER
  CQE Patterns ──────── defines vocabulary for all directions
       │
       ├── implements ──▶ cqlint (pattern verification rules)
       ├── applies ─────▶ MutaDoc (Assumption Mutation → document mutation)
       ├── applies ─────▶ ThinkTank (Cognitive Profile + Wave Scheduler + Mutation)
       └── measured by ─▶ CQ Benchmark (unified metrics)

VERIFICATION LAYER
  cqlint ◀──────────── rules derived from patterns
       └── integrated ─▶ CQ MCP Server (as cq_engine__cqlint)

APPLICATION LAYER
  MutaDoc ────────────── standalone killer app
       ├── shares core ─▶ ThinkTank (devil's advocate = document mutation)
       └── integrated ──▶ CQ MCP Server (as cq_engine__mutadoc)
  ThinkTank ──────────── standalone decision engine
       └── integrated ──▶ CQ MCP Server (as cq_engine__thinktank)

DISTRIBUTION LAYER
  CQ MCP Server ─────── bundles all + telemetry
       └── feedback ───▶ CQE Patterns (telemetry → pattern evolution)

MEASUREMENT LAYER (Cross-Cutting)
  CQ Benchmark ──────── validates hypotheses for all directions

OPTIONAL LAYER (Conditional)
  CTL ─────────────────  type-safe task definition + static analysis
       └── extends ────▶ cqlint (CQ006-CQ009 rules)
```

### 4.3 Circular Feedback Structure

```
CQE Patterns ──▶ MutaDoc / ThinkTank / cqlint ──▶ CQ MCP Server ──▶ Users
      ▲                                                                 │
      │                                                                 │
      └──── Pattern Evolution ◀── Telemetry ◀── CQ Benchmark ◀─────────┘
```

Feedback paths:
1. **CQ MCP → CQE Patterns**: Most violated patterns → Anti-Pattern reinforcement
2. **CQ MCP → MutaDoc**: Most detected vulnerability types → Strategy preset optimization
3. **CQ MCP → ThinkTank**: Decision Replay data → Persona weighting auto-adjustment
4. **CQ Benchmark → All**: Standardized measurement unifies hypothesis validation

### 4.4 Master Milestone Timeline

```
PHASE 1 (Foundation) ✓ COMPLETE                                Size: M
─────────────────────────────────────────────────────────────────────
  M1.1  ──▶  M1.2  ──────────────────────────────────────▶  M1.7
  M1.3  ──▶  M1.4  ──▶  M1.5  ──────────────────────────▶  M1.7
              M1.6  ──────────────────────────────────────▶  M1.7

PHASE 2 (MutaDoc) ✓ COMPLETE                                   Size: L
─────────────────────────────────────────────────────────────────────
  M2.1  ──▶  M2.2  ──────────────────────────────────────▶  M2.5
  M2.1  ──▶  M2.3
  M2.1  ──▶  M2.4
  M2.1  ──▶  M2.6

PHASE 3 (Distribution) ✓ COMPLETE                              Size: L
─────────────────────────────────────────────────────────────────────
  M3.1  ──▶  M3.2  ──▶  M3.3
                    ──▶  M3.4  ──── CTL Checkpoint ◇
                    ──▶  M3.5  ──▶  M3.6  ──▶  M3.7

PHASE 4 (ThinkTank) — NOT STARTED                              Size: L
─────────────────────────────────────────────────────────────────────
  M4.2  ──▶  M4.1  ──▶  M4.3
                    ──▶  M4.4
                    ──▶  M4.5
                    ──▶  M4.6
                    ──▶  M4.7  ──▶  M4.8  ──▶  M4.10
                    ──▶  M4.9
                                              ──▶  M4.11

PHASE 5 (CTL, Conditional)                                    Size: L
─────────────────────────────────────────────────────────────────────
  M5.1  ──▶  M5.2  ──▶  M5.3
                    ──▶  M5.4  ──▶  M5.5  ──▶  M5.6
                    ──▶  M5.7

Total milestones: 38 (7 + 6 + 7 + 11 + 7 conditional)
```

### 4.5 Phase Transition Criteria

| Transition | Required Milestones | Rationale |
|------------|-------------------|-----------|
| **Phase 1 → Phase 2** | M1.1 (4 Foundational patterns) + M1.3 (cqlint scaffold) | MutaDoc needs Assumption Mutation pattern + cqlint validation. Full Phase 1 completion NOT required — M1.2, M1.5 can overlap with early Phase 2 |
| **Phase 2 → Phase 3** | M2.1 (strategies) + M2.2 (repair) | MCP wraps MutaDoc — functional strategies + repair required. Presets (M2.4) and benchmark (M2.5) can continue in parallel |
| **Phase 3 → Phase 4** | M3.1 (MCP installable) + M3.2 (core tools) | ThinkTank needs MCP distribution channel. Telemetry (M3.5) and dashboard (M3.6) can overlap with early Phase 4 |
| **Phase 3 → Phase 5** | CTL Revival Checkpoint (after M3.4) | All 4 revival conditions (RC-1 through RC-4) must be met. See [phases/phase-5-ctl.md §1](phases/phase-5-ctl.md) |

**Key insight**: Phases overlap. The transition criterion is the minimum required to *start* the next phase, not full completion of the current phase. This allows pipeline parallelism.

---

## 5. Direction Overviews

### 5.1 CQE Patterns — The Vocabulary

| Attribute | Detail |
|-----------|--------|
| **One-liner** | GoF Design Patterns for LLM agent systems — naming the unnamed concepts of cognitive quality |
| **Key Features** | 8 core patterns with Anti-Patterns, Evidence Levels, Failure Catalogs, and Interaction Catalogs |
| **Target Users** | AI engineers, Claude Code users, LLM agent system designers |
| **Tech Stack** | Pure documentation (Markdown). No code required for the catalog itself |
| **MVP** | 8 pattern files in GoF format + index with relationship diagram |

### 5.2 cqlint — The Verifier

| Attribute | Detail |
|-----------|--------|
| **One-liner** | A linter for cognitive quality — catches pattern violations before execution |
| **Key Features** | 5 rules (CQ001–CQ005), Bash + Claude Code, CI/CD gate capability, crew + generic YAML adapters |
| **Target Users** | AI engineers, DevOps teams integrating quality gates |
| **Tech Stack** | Bash + Claude Code (zero infrastructure) |
| **MVP** | `cqlint.sh` + 5 rule implementations + 2 adapters + test fixtures |

### 5.3 MutaDoc — The Killer App

| Attribute | Detail |
|-----------|--------|
| **One-liner** | Software mutation testing applied to documents — find hidden contradictions, ambiguities, and vulnerabilities by intentionally breaking text |
| **Key Features** | 5 mutation strategies, 3 adversarial personas, Mutation-Driven Repair, Regression Mutation, 12 document presets, Mutation Kill Score |
| **Target Users** | Lawyers, API engineers, researchers, quality managers (including non-technical users) |
| **Tech Stack** | Bash + Markdown templates + Claude Code Task tool (zero infrastructure) |
| **MVP** | `mutadoc.sh` + 5 strategies + 3 personas + repair engine + 12 presets |

### 5.4 ThinkTank — The Decision Engine

| Attribute | Detail |
|-----------|--------|
| **One-liner** | An anti-anchoring decision engine — 8 personas analyze independently in parallel, then cross-critique, producing genuinely diverse perspectives |
| **Key Features** | 3-Wave process, Anchoring Visibility Score, Contradiction Heatmap, Parameter Mutation, Decision Replay, Quick Mode (3-persona) |
| **Target Users** | Executives, policymakers, individuals — including non-technical users |
| **Tech Stack** | Bash + Markdown persona templates + Claude Code Task tool (zero infrastructure) |
| **MVP** | `thinktank.sh` + 8 personas + 3 Wave templates + AVS calculator |

### 5.5 CQ MCP Server — The Distribution Platform

| Attribute | Detail |
|-----------|--------|
| **One-liner** | One command to bring cognitive quality management to every Claude Code session: `claude mcp add cq-engine` |
| **Key Features** | 8 MCP tools, 3 MCP resources, 3 Hooks, local telemetry, CQ Health Dashboard |
| **Target Users** | All Claude Code users (zero learning cost — Claude autonomously uses CQ tools) |
| **Tech Stack** | Python MCP SDK (sole infrastructure exception) + Bash/CLI fallback for every tool |
| **MVP** | `server.py` + 6 core tools + hooks + telemetry collector |

### 5.6 CQ Benchmark — The Measurement Framework

| Attribute | Detail |
|-----------|--------|
| **One-liner** | A unified measurement framework for cognitive quality — you cannot call it "engineering" without measurement |
| **Key Features** | 4-axis scoring (Context Health, Decision Quality, Document Integrity, Evolution), standardized metrics |
| **Target Users** | AI engineers using any CQE direction (internal validation tool) |
| **Tech Stack** | Specification (Phase 1) + measurement scripts (Phase 2+) |
| **MVP** | Spec document with 4 axes, 12 sub-metrics, formulas, and worked examples |

---

## 6. Risks & Prerequisites

### 6.1 Phase-Specific Risks

See each Phase section above for detailed risk tables. Summary of top risks per phase:

| Phase | Top Risk | Mitigation |
|-------|----------|------------|
| Phase 1 | Evidence Level B only — academic skepticism | arXiv-compatible format; define upgrade path to Level A |
| Phase 2 | "Just ask ChatGPT" perception | "30-second experience" shows result ChatGPT missed |
| Phase 3 | Python dependency contradicts zero-infra | Bash/CLI fallback for every MCP tool |
| Phase 4 | "Multi-perspective = SWOT" perception | Position as Anti-Anchoring Engine; lead with AVS |
| Phase 5 | Revival conditions never met | No implementation effort until GO; design doc serves as reference |

### 6.2 Cross-Cutting Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hypothesis baselines are vague | Cannot validate success | 5-element framework (IV/DV/Baseline/Effect/Sample) for all hypotheses |
| "Engineering discipline" claim without academic backing | Credibility challenge | Phase 1 patterns in arXiv-compatible format; pursue publication |
| Community building not addressed | Ecosystem stalls | GitHub Discussions post Phase 3 MCP launch |
| Revenue model undefined | Sustainability unclear | Explicitly out of scope — focus on value creation first |
| Competitor analysis incomplete | Positioning blind spots | Schedule competitive analysis before Phase 2 |

### 6.3 Prerequisites

| Prerequisite | Applies To | Description |
|--------------|-----------|-------------|
| Zero-infrastructure principle | All Phases | Bash + Markdown + Claude Code. Python only for MCP Server |
| Sequential execution | All Phases | Each phase's entry criteria must be met (with overlap allowed) |
| Hypothesis validation framework | All Phases | 5-element framework for every hypothesis |
| arXiv-compatible writing | Phase 1 | Pattern catalog publishable as academic paper |
| 30-second experience design | Phase 1–4 | Every direction has an instant "aha moment" |
| Circular feedback architecture | Phase 3+ | Telemetry → pattern evolution from day one |
| Privacy-first telemetry | Phase 3+ | All data strictly local. Non-negotiable |

### 6.4 Deferred Directions (Revival Conditions)

| Direction | Revival Condition | Timing |
|-----------|-------------------|--------|
| CTL (Cognitive Task Language) | 4 quantitative criteria (RC-1 through RC-4) | Phase 3 checkpoint |
| Cognitive Quality Protocol (CQP) | Patterns v0.2+, inter-framework interoperability need | Phase 3+ |
| Personal CQ Assistant | Personal mode in CQ MCP Server | Phase 3 |
| ContextOS concepts | Incorporated into gate tool internals | Phase 3 gate implementation |
| Academic citations | arXiv-publishable format for patterns | Phase 1 (built-in) |
| Community building | GitHub Discussions after MCP launch | Phase 3+ |

---

## 7. Repository Structure

```
cq-engine/
├── README.md                          # Project entry point
├── LICENSE                            # MIT License
├── CLAUDE.md                          # Claude Code integration settings
├── CONTRIBUTING.md                    # Contribution guide
├── .github/workflows/                 # CI/CD
│
├── patterns/                          # CQE Patterns catalog (Phase 1)
│   ├── README.md                      #   Index + relationship diagram
│   ├── 01_attention_budget.md         #   8 pattern files
│   ├── ...
│   └── anti-patterns/
│
├── cqlint/                            # CQ Linter (Phase 1)
│   ├── cqlint.sh                      #   Entry point
│   ├── lib/                           #   Parser, output, utilities
│   ├── rules/                         #   CQ001-CQ005 (.sh + .md)
│   ├── adapters/                      #   crew_yaml.sh, generic_yaml.sh
│   └── tests/                         #   Fixtures + test runner
│
├── benchmark/                         # CQ Benchmark (Phase 1)
│   ├── spec.md                        #   Full specification
│   └── measures/                      #   Per-axis detail
│
├── mutadoc/                           # MutaDoc (Phase 2)
│   ├── mutadoc.sh                     #   Entry point
│   ├── strategies/                    #   5 strategy templates
│   ├── personas/                      #   3 adversarial personas
│   ├── repair/templates/              #   Repair templates per strategy
│   ├── presets/                       #   12 document type presets
│   └── test_fixtures/                 #   Test documents
│
├── thinktank/                         # ThinkTank (Phase 4)
│   ├── thinktank.sh                   #   Entry point
│   ├── personas/                      #   8 personas (business/stakeholder/meta/custom)
│   ├── waves/                         #   3 Wave templates + formats
│   └── mutation/                      #   AVS calculator + sequential baseline
│
├── mcp-server/                        # CQ MCP Server (Phase 3)
│   ├── server.py                      #   MCP server entry point
│   ├── tools/                         #   8 MCP tool implementations
│   ├── resources/                     #   patterns, learned, health
│   ├── telemetry/                     #   Collector + aggregation
│   └── hooks/                         #   3 hook scripts
│
├── docs/                              # Documentation
│   ├── roadmap.md                     #   This file
│   ├── architecture.md
│   ├── glossary.md
│   └── guides/
│
└── examples/                          # Usage examples
```

---

## Appendix A: Ecosystem Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CQE ECOSYSTEM (cq-engine)                      │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │ KNOWLEDGE LAYER                                              │     │
│  │  CQE Patterns (8 patterns + Anti-Patterns + Evidence Levels) │     │
│  └────────────────────────┬────────────────────────────────────┘     │
│                           │                                          │
│  ┌────────────────────────▼────────────────────────────────────┐     │
│  │ APPLICATION LAYER                                            │     │
│  │  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │     │
│  │  │  cqlint   │  │   MutaDoc    │  │     ThinkTank         │  │     │
│  │  │ (verify)  │  │ (doc mutate) │  │ (anti-anchor decide)  │  │     │
│  │  └──────────┘  └──────────────┘  └───────────────────────┘  │     │
│  └────────────────────────┬────────────────────────────────────┘     │
│                           │                                          │
│  ┌────────────────────────▼────────────────────────────────────┐     │
│  │ MEASUREMENT LAYER                                            │     │
│  │  CQ Benchmark (4-axis: Context / Decision / Document / Evo)  │     │
│  └────────────────────────┬────────────────────────────────────┘     │
│                           │                                          │
│  ┌────────────────────────▼────────────────────────────────────┐     │
│  │ DISTRIBUTION LAYER                                           │     │
│  │  CQ MCP Server (Tools + Resources + Hooks + Telemetry)       │     │
│  └────────────────────────┬────────────────────────────────────┘     │
│                           │                                          │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
                            ▼
                   Claude Code Users
                            │
                            │ telemetry (local-only)
                            ▼
                   Feedback → Pattern Evolution
```

## Appendix B: Uniqueness Scores

| Direction | Uniqueness (30%) | Crew Fit (25%) | Impact (20%) | Feasibility (15%) | Synergy (10%) | Weighted | Rank |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| MutaDoc | 10 | 9 | 9 | 8 | 7 | 9.0 | 1 |
| CQE Patterns + cqlint | 9 | 10 | 9 | 7 | 9 | 8.9 | 2 |
| ThinkTank | 8 | 9 | 9 | 7 | 8 | 8.3 | 3 |
| CQ MCP Server | 7 | 8 | 8 | 6 | 10 | 7.7 | 4 |
| CQ Benchmark | 6 | 8 | 7 | 8 | 10 | 7.5 | 5 |

**Note**: Uniqueness rank ≠ implementation order. MutaDoc ranks #1 but is Phase 2, because the foundation (CQE Patterns) must exist first.

## Appendix C: cq-engine Extension vs Standalone Product

| Classification | Directions | Criteria |
|---------------|-----------|----------|
| **cq-engine Extension** | CQE Patterns, cqlint, CQ MCP Server, CQ Benchmark | Target: AI engineers. Runs on Claude Code. Distribution: MCP/Skills/Hooks |
| **Standalone Product** | MutaDoc, ThinkTank | Target: includes non-technical users. Valuable without Claude Code. Independent CLI or Web |

## Appendix D: Effort Summary

| Phase | Tasks | Milestones | Estimated Lines | Actual Lines | Size | Status |
|-------|:-----:|:----------:|:---------------:|:------------:|:----:|:------:|
| Phase 1 | ~25 | 7 | ~5,700 | 5,139 | M | ✓ Complete |
| Phase 2 | 40 | 6 | ~8,000+ | 6,921 | L | ✓ Complete |
| Phase 3 | 18 | 7 | ~4,000+ | 3,178 | L | ✓ Complete |
| Phase 4 | 30 | 11 | ~6,000+ | — | L | Not Started |
| Phase 5 | 10 | 7 | ~3,000+ | — | L | Conditional |
| **Total** | **~123** | **38** | **~26,700+** | **15,238** | | |
