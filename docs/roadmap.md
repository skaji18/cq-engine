# Cognitive Quality Engineering — Implementation Roadmap

> **Version**: 1.1.0
> **Repository**: `cq-engine`
> **License**: MIT
> **Origin**: Initial exploration (5 Directions + DSL/CTL analysis)
> **Purpose**: Public GitHub repository roadmap for the CQE ecosystem

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
Phase 1                Phase 2                Phase 3                Phase 4
FOUNDATION             KILLER APP             DISTRIBUTION           EXPANSION
─────────────────────  ─────────────────────  ─────────────────────  ─────────────────────
CQE Patterns v0.1      MutaDoc v0.1           CQ MCP Server v0.1     ThinkTank v0.1
cqlint v0.1            + Mutation-Driven       + mutadoc/cqlint       + 8 personas
CQ Benchmark v0.1        Repair                 as MCP tools         + 3-Wave pipeline
(spec only)            + Regression Mutation   + Hooks integration    + Anchoring Visibility
                       + CQ Benchmark applied  + Telemetry baseline   + MCP integration
                                                                     + Feedback loop start

Size: M                Size: L                Size: L                Size: L
───────────────────────────────────────────────────────────────────────────────────────────
                                  ▲
                        CQ Benchmark (cross-cutting: defined in Phase 1, applied from Phase 2)
```

### CTL (Cognitive Task Language) — Cross-Cutting Consideration

CTL was explored as a dedicated DSL for describing cognitive tasks with type-safe syntax and static analysis. It was **deferred** (not rejected) during the sharpening phase due to high learning cost. The cqlint approach delivers equivalent quality assurance with zero learning curve.

**CTL positioning in this roadmap:**
- **Phase 1**: CTL concepts are absorbed into cqlint rules (budget checking, gate validation, persona verification)
- **Phase 3**: If CQE Patterns reach v0.2+ and community demand exists, CTL may be revived as an optional power-user layer on top of cqlint
- **Rationale**: "Tools first, language later" — users experience cqlint, understand why it catches what it catches, and only then might want the expressiveness of a dedicated language

---

## 3. Phase Details

### Phase 1: Foundation

> *"Pattern naming has the highest leverage. A foundation without which killer apps are just 'useful tools.'"*

**Purpose**: Define the vocabulary of Cognitive Quality Engineering. Name the unnamed concepts, formalize them as patterns, build the first automated verifier, and specify the measurement framework.

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **CQE Patterns v0.1** | 8 core patterns in GoF format (Problem / Context / Solution / Anti-Pattern / Evidence Level / Known Uses / Related) |
| 2 | **cqlint v0.1** | 5 lint rules (CQ001–CQ005) implemented in Bash + Claude Code |
| 3 | **CQ Benchmark v0.1** | Specification document for the 4-axis measurement framework (no implementation yet) |

**8 Core Patterns**:

| # | Pattern | Problem | Weight | Evidence |
|---|---------|---------|--------|----------|
| 1 | Attention Budget | LLM attention is finite but unmanaged | Foundational | B |
| 2 | Context Gate | Passing all information between agents contaminates attention | Foundational | B |
| 3 | Cognitive Profile | Generic agents underperform specialized ones | Foundational | B |
| 4 | Wave Scheduler | Simultaneous deployment degrades quality | Situational | B |
| 5 | Assumption Mutation | Unverified assumptions hide vulnerabilities | Situational | B |
| 6 | Experience Distillation | Without learning from execution, failures repeat | Advanced | B |
| 7 | File-Based I/O | Agent communication needs reliability and transparency | Foundational | B |
| 8 | Template-Driven Role | Implicit roles cause quality variance | Situational | B |

Each pattern includes:
- **Anti-Pattern** section (learning from GoF's weakness of not explaining "when NOT to use")
- **Failure Catalog** with real examples
- **Interaction Catalog** documenting how patterns combine
- **Evidence Level** (A: quantitatively verified, B: multi-project confirmed, C: theoretical, D: hypothesis)

**5 cqlint Rules**:

| Rule | Name | Detects |
|------|------|---------|
| CQ001 | attention-budget-missing | Task definition lacks token budget |
| CQ002 | context-contamination-risk | No filtering between agent stages (Context Gate violation) |
| CQ003 | generic-persona | Persona undefined or too generic |
| CQ004 | no-mutation-critical | High-risk task without mutation step |
| CQ005 | learning-disabled | Learning mechanism absent |

**CQ Benchmark v0.1 — 4-Axis Specification**:

| Axis | Sub-metrics |
|------|-------------|
| Context Health Score | Information density, contamination level, freshness |
| Decision Quality Score | Perspective diversity, anchoring exclusion, blind-spot coverage |
| Document Integrity Score | Mutation Kill rate, contradiction count, ambiguity score |
| Evolution Score | Pattern compliance rate, learning accumulation rate, recurring issue rate |

**Milestones**:

| # | Milestone | Definition of Done |
|---|-----------|-------------------|
| M1.1 | Pattern catalog published | 8 patterns documented in GoF format with Anti-Patterns and Evidence Levels |
| M1.2 | cqlint functional | `cqlint check .` runs on any project directory and reports violations |
| M1.3 | "30-second experience" working | A new user can run `cqlint check .` and see actionable output within 30 seconds |
| M1.4 | Benchmark spec complete | 4-axis measurement specification documented with calculation methods |

**Dependencies**: None (this is the foundation)

**Estimated Size**: **M** (Medium) — primarily documentation + scripting

**Entry Criteria**: None

**Success Criteria**:
- 8 patterns fully documented with Anti-Patterns
- cqlint detects all 5 rule violations in test fixtures
- CQ Benchmark specification reviewed and baselined

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | Pattern vocabulary improves design discussions | 5 AI engineers review with/without catalog | 30% faster discussion OR 50% more issues found |
| H2 | cqlint detects quality issues pre-execution | Analyze 50 past execution logs | 40%+ of failures were pre-detectable |
| H3 | Patterns apply across frameworks | Test on LangGraph, CrewAI, raw Task tool | Quality improves on all 3 |
| H4 | Anti-Patterns reduce pattern misuse by 50%+ | Compare misuse rates with/without Anti-Pattern docs | 50%+ reduction |

---

### Phase 2: Killer App (MutaDoc)

> *"Document mutation testing is a category that does not exist on Earth."*

**Purpose**: Build MutaDoc — the first tool that applies software mutation testing to documents. Prove that CQE principles create value beyond the AI engineering community by reaching lawyers, researchers, and quality managers.

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **MutaDoc v0.1** | Document mutation testing engine with 5 strategies + Mutation-Driven Repair + Regression Mutation |
| 2 | **CQ Benchmark applied** | First application of CQ Benchmark to validate MutaDoc hypotheses |

**5 Mutation Strategies**:

| Strategy | Description |
|----------|-------------|
| Contradiction | Alter a clause and detect if other clauses become contradictory |
| Ambiguity | Replace vague modifiers with extreme values to expose meaninglessness |
| Deletion | Remove a clause and measure structural impact (zero impact = dead clause) |
| Inversion | Reverse assumptions/claims and measure argument robustness |
| Boundary | Mutate parameters (numbers, deadlines) to estimate conclusion robustness |

**Key Innovation — Mutation-Driven Repair**:
- **Repair Draft**: Auto-generate fix suggestions for each Critical finding
- **Repair Impact Analysis**: Predict cascading effects of proposed fixes
- **Regression Mutation**: Re-apply mutation to repaired text to verify no new vulnerabilities were introduced
- This mirrors ESLint's auto-fix revolution: "detect + repair" achieves 10x adoption over "detect only"

**3 Adversarial Personas**:

| Persona | Role |
|---------|------|
| `adversarial_reader` | Malicious reader looking for exploitable ambiguity |
| `opposing_counsel` | Opposing lawyer seeking contract weaknesses |
| `naive_implementer` | Developer who implements everything literally |

**Milestones**:

| # | Milestone | Definition of Done |
|---|-----------|-------------------|
| M2.1 | 5 strategies implemented | Each strategy produces a mutation test report on sample documents |
| M2.2 | Mutation-Driven Repair functional | Repair drafts generated for Critical findings with regression mutation |
| M2.3 | "30-second experience" working | Feed a README → get "3 ambiguous expressions found" within 30 seconds |
| M2.4 | 10+ document type presets | Strategy presets for contracts, API specs, academic papers, policy docs, and 6+ more |
| M2.5 | CQ Benchmark validation | MutaDoc hypotheses validated using CQ Benchmark metrics |

**Dependencies**: Phase 1 (CQE Patterns provide the theoretical foundation — especially the Assumption Mutation pattern)

**Estimated Size**: **L** (Large) — multiple strategies, repair engine

**Entry Criteria**:
- CQE Patterns v0.1 published (M1.1 complete)
- cqlint v0.1 functional (M1.2 complete)

**Success Criteria**:
- Detects issues in contracts, specs, and papers that human reviewers miss
- Mutation-Driven Repair generates actionable fix suggestions
- Non-technical users (lawyers, researchers) can use it without AI knowledge

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | MutaDoc detects issues human reviewers miss | Test set of 5 contracts with known issues, compare with 2 lawyers | 50%+ of missed issues detected |
| H2 | Strategies generalize across document types | Apply same 5 strategies to contracts, specs, and papers | 1+ Critical found in all 3 types |
| H3 | Mutation mechanism ports from code to documents | Script adversarial review approach, apply to new docs | Quality matches manual adversarial review |
| H4 | 30%+ of repair suggestions are directly usable | Human evaluation of repair drafts | 30%+ "use as-is" rate |
| H5 | Regression Mutation catches new vulnerabilities | Re-mutate repaired documents | 15%+ detection rate of new issues |

---

### Phase 3: Distribution (CQ MCP Server)

> *"The best product, if it can't reach anyone, is the same as not existing."*

**Purpose**: Package CQE Patterns, cqlint, and MutaDoc as an MCP Server that any Claude Code user can install with a single command. Add telemetry to create a self-improving ecosystem.

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **CQ MCP Server v0.1** | MCP server providing mutadoc + cqlint + learn as tools |
| 2 | **Hooks integration** | PreToolUse / TaskCompleted hooks for automatic CQ checks |
| 3 | **Telemetry baseline** | Local-only usage data collection for ecosystem evolution |

**MCP Tools**:

| Tool | Function |
|------|----------|
| `cq_engine__decompose` | Auto-decompose tasks within cognitive budget |
| `cq_engine__gate` | Pass only needed files to each subtask (context hygiene) |
| `cq_engine__persona` | Select optimal persona for subtask characteristics |
| `cq_engine__mutate` | Auto-mutation test on refactoring results |
| `cq_engine__cqlint` | Static cognitive quality verification |
| `cq_engine__mutadoc` | Document mutation testing (Phase 2 integration) |
| `cq_engine__learn` | Accumulate learning from execution |
| `cq_engine__benchmark` | Run CQ Benchmark measurements |

**MCP Resources**:

| Resource | Content |
|----------|---------|
| `cq_engine://patterns` | Pattern catalog (read-only) |
| `cq_engine://learned` | Accumulated learning data |

**Hooks Integration**:

| Hook | Trigger | Action |
|------|---------|--------|
| PreToolUse | Before Edit/Write | Context hygiene check |
| TaskCompleted | After Task completion | Auto-mutation test |

**Telemetry (All Local, Privacy-First)**:

| Data Collected | Purpose |
|---------------|---------|
| Usage frequency | Identify most valuable patterns |
| Failure patterns | Measure rule effectiveness |
| Quality improvement data | Measure mutation strategy effectiveness |
| Task characteristic correlation | Improve automatic recommendations |

**CTL Revival Checkpoint**: If by Phase 3, CQE Patterns have reached v0.2+ and community feedback indicates demand for a declarative task language, evaluate reviving CTL as an optional layer. CTL's static analysis capabilities (budget overflow detection, gate inconsistency detection) could complement cqlint for power users.

**Milestones**:

| # | Milestone | Definition of Done |
|---|-----------|-------------------|
| M3.1 | MCP server installable | `claude mcp add cq-engine` works and provides all tools |
| M3.2 | Hooks auto-trigger | CQ checks run automatically on Edit/Write and Task completion |
| M3.3 | Telemetry collecting | Local usage data accumulating for ecosystem feedback |
| M3.4 | Feedback loop v1 | First telemetry-driven pattern/rule update cycle completed |

**Dependencies**: Phase 1 (patterns + cqlint) and Phase 2 (MutaDoc)

**Estimated Size**: **L** (Large) — Python MCP SDK, hooks integration, telemetry

**Entry Criteria**:
- CQE Patterns v0.1 stable
- cqlint v0.1 validated
- MutaDoc v0.1 functional (M2.1 + M2.2 complete)

**Success Criteria**:
- MCP installs exceed direct framework users by 5x
- Claude Code autonomously uses CQ tools on 70%+ of complex tasks
- Telemetry-to-pattern-update feedback loop operational

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | MCP delivery reaches 10x more users than framework adoption | Compare MCP installs vs framework users | 5x+ install ratio |
| H2 | Claude Code autonomously uses CQ tools appropriately | Test 10 task types for autonomous usage | 70%+ autonomous usage on complex tasks |
| H3 | MCP integration improves quality for non-cq-engine users | Same-task quality comparison with/without cq-engine | 20%+ quality improvement |
| H4 | Telemetry-based recommendations outperform static rules | Compare adoption rates | 30%+ higher adoption |

**Note on Infrastructure Exception**: CQ MCP Server is the **only component** requiring Python (via Python MCP SDK). All other components follow the zero-infrastructure principle. A Bash/CLI fallback must always be available for every MCP tool.

---

### Phase 4: Expansion (ThinkTank)

> *"What ChatGPT cannot do by principle: truly independent multi-perspective analysis."*

**Purpose**: Build ThinkTank — an anti-anchoring decision engine that uses independent-context parallel analysis to produce genuinely diverse perspectives. Integrate it into the CQ MCP Server to complete the ecosystem.

**Deliverables**:

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **ThinkTank v0.1** | 8-persona, 3-Wave decision engine with Anchoring Visibility Score |
| 2 | **MCP integration** | ThinkTank added as `cq_engine__thinktank` tool |
| 3 | **Feedback loop activation** | First telemetry → pattern evolution cycle |

**3-Wave Process**:

| Wave | Name | Description |
|------|------|-------------|
| Wave 1 | Independent Analysis | 8 personas analyze in isolated contexts (parallel) |
| Wave 2 | Cross-Critique | Each persona critiques others' analyses |
| Wave 3 | Synthesis | Integrate all analyses into final judgment + risk matrix |

**Persona Framework**:

| Category | Personas |
|----------|---------|
| Business | CFO, CTO, CMO, Investor |
| Stakeholders | Customer, Employee, Regulator |
| Meta | Devil's Advocate (mandatory) |
| Custom | User-defined personas |

**Key Innovations**:
- **Anchoring Visibility Score**: Estimates how much anchoring bias would have affected a sequential analysis, quantifying the value of parallel execution
- **Contradiction Heatmap**: 8x8 matrix visualizing inter-persona disagreements — structurally identifying where debate is needed
- **Parameter Mutation Test**: Mutate decision parameters for sensitivity analysis ("What if 10%? 20%? Over 3 years?")
- **Decision Replay**: Re-analyze past decisions to continuously improve judgment quality

**Milestones**:

| # | Milestone | Definition of Done |
|---|-----------|-------------------|
| M4.1 | 3-Wave pipeline functional | Wave 1 → Wave 2 → Wave 3 produces a Decision Brief |
| M4.2 | Anchoring Visibility Score implemented | Score quantifies parallel vs sequential bias difference |
| M4.3 | MCP integration complete | `cq_engine__thinktank` tool available via MCP Server |
| M4.4 | Feedback loop operational | Telemetry data drives pattern catalog and strategy updates |

**Dependencies**: Phase 3 (MCP Server provides the distribution channel)

**Estimated Size**: **L** (Large) — 8 personas, 3-Wave pipeline, MCP integration

**Entry Criteria**:
- CQ MCP Server v0.1 operational (M3.1 + M3.2 complete)
- Distribution channel validated

**Success Criteria**:
- Parallel analysis produces 1.5x+ more diverse perspectives than sequential
- Wave 2 cross-critique reduces blind spots by 30%+
- ThinkTank detects major failure factors in 3/5 historical case studies (Kodak, Nokia, WeWork, etc.)

**Hypotheses to Validate**:

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H1 | Parallel analysis is more diverse than sequential | ThinkTank (parallel) vs ChatGPT ("analyze from 8 perspectives") | 1.5x+ perspective diversity score |
| H2 | Wave 2 cross-critique improves quality | Wave 1 only vs Wave 1+2 comparison | 30%+ blind spot reduction |
| H3 | ThinkTank retroactively detects past decision failures | Analyze Kodak, Nokia, WeWork, etc. | 3/5+ major factors detected |
| H4 | Sequential analysis shows anchoring correlated with generation order; parallel shows zero | Measure perspective similarity vs generation order | Positive correlation (sequential), zero (parallel) |

---

## 4. Dependency Diagram

### Phase Dependencies

```
                    ┌─────────────────────────────────────────────────┐
                    │         CQ Benchmark (Cross-Cutting)            │
                    │  Defined in Phase 1 → Applied from Phase 2      │
                    └──────┬──────────────────┬───────────────────────┘
                           │                  │
                           ▼                  ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   PHASE 1        │    │   PHASE 2        │    │   PHASE 3        │    │   PHASE 4        │
│   Foundation     │───▶│   Killer App     │───▶│   Distribution   │───▶│   Expansion      │
│                  │    │                  │    │                  │    │                  │
│ • CQE Patterns   │    │ • MutaDoc        │    │ • CQ MCP Server  │    │ • ThinkTank      │
│ • cqlint         │    │ • Repair Engine  │    │ • Hooks          │    │ • 3-Wave Engine  │
│ • Benchmark Spec │    │ • Benchmark Use  │    │ • Telemetry      │    │ • MCP Integration│
└──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
        │                                               │
        │          CTL Revival Checkpoint ◇              │
        │          (if Patterns v0.2+ &                  │
        └──────────  community demand)  ─────────────────┘
```

### Technical Dependencies Between Directions

```
KNOWLEDGE LAYER
  CQE Patterns ─────────── defines vocabulary for all directions
       │
       ├── implements ──▶ cqlint (automated pattern verification)
       │
       ├── applies ─────▶ MutaDoc (Assumption Mutation pattern → document mutation)
       │
       ├── applies ─────▶ ThinkTank (Cognitive Profile + Wave Scheduler + Assumption Mutation)
       │
       └── measured by ─▶ CQ Benchmark (unified metrics across all directions)

VERIFICATION LAYER
  cqlint ◀──────────────── rules derived from patterns
       │
       └── integrated ──▶ CQ MCP Server (as cq_engine__cqlint tool)

APPLICATION LAYER
  MutaDoc ──────────────── standalone killer app
       │
       ├── shares core ──▶ ThinkTank (devil's advocate = document mutation)
       │
       └── integrated ──▶ CQ MCP Server (as cq_engine__mutadoc tool)

  ThinkTank ────────────── standalone decision engine
       │
       └── integrated ──▶ CQ MCP Server (as cq_engine__thinktank tool)

DISTRIBUTION LAYER
  CQ MCP Server ─────────── bundles all above + telemetry
       │
       └── feedback ────▶ CQE Patterns (telemetry → pattern evolution)

MEASUREMENT LAYER (Cross-Cutting)
  CQ Benchmark ──────────── validates hypotheses for all directions
```

### Circular Feedback Structure

```
CQE Patterns ──▶ MutaDoc / ThinkTank / cqlint ──▶ CQ MCP Server ──▶ Users
      ▲                                                                 │
      │                                                                 │
      └──── Pattern Evolution ◀── Telemetry ◀── CQ Benchmark ◀─────────┘
```

Specific feedback paths:
1. **CQ MCP → CQE Patterns**: Most frequently violated patterns → Anti-Pattern section reinforcement
2. **CQ MCP → MutaDoc**: Most detected vulnerability types → Mutation strategy preset optimization
3. **CQ MCP → ThinkTank**: Decision Replay data → Persona weighting auto-adjustment
4. **CQ Benchmark → All**: Standardized measurement unifies hypothesis validation

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

```
cq-engine/patterns/
├── README.md
├── 01_attention_budget.md
├── 02_context_gate.md
├── 03_cognitive_profile.md
├── 04_wave_scheduler.md
├── 05_assumption_mutation.md
├── 06_experience_distillation.md
├── 07_file_based_io.md
├── 08_template_driven_role.md
└── anti-patterns/
    ├── README.md
    └── (anti-pattern files for each pattern)
```

### 5.2 cqlint — The Verifier

| Attribute | Detail |
|-----------|--------|
| **One-liner** | A linter for cognitive quality — catches pattern violations before execution |
| **Key Features** | 5 rules (CQ001–CQ005), Bash + Claude Code implementation, CI/CD gate capability |
| **Target Users** | AI engineers, DevOps teams integrating quality gates |
| **Tech Stack** | Bash + Claude Code (zero infrastructure) |
| **MVP** | `cqlint.sh` + 5 rule definitions + adapter for crew YAML and generic YAML |

```
cq-engine/cqlint/
├── README.md
├── cqlint.sh
├── rules/
│   ├── CQ001_budget_missing.md
│   ├── CQ002_context_contamination.md
│   ├── CQ003_generic_persona.md
│   ├── CQ004_no_mutation_critical.md
│   └── CQ005_learning_disabled.md
└── adapters/
    ├── crew_yaml.sh
    └── generic_yaml.sh
```

### 5.3 MutaDoc — The Killer App

| Attribute | Detail |
|-----------|--------|
| **One-liner** | Software mutation testing applied to documents — find hidden contradictions, ambiguities, and vulnerabilities by intentionally breaking text |
| **Key Features** | 5 mutation strategies, 3 adversarial personas, Mutation-Driven Repair, Regression Mutation, 10+ document type presets, Mutation Kill Score |
| **Target Users** | Lawyers (M&A contract stress testing), API engineers (spec consistency), researchers (paper logic verification), quality managers |
| **Tech Stack** | Bash + Markdown templates + Claude Code Task tool (zero infrastructure) |
| **MVP** | `mutadoc.sh` + 5 strategy templates + 3 persona definitions + repair engine |

```
cq-engine/mutadoc/
├── README.md
├── mutadoc.sh
├── strategies/
│   ├── contradiction.md
│   ├── ambiguity.md
│   ├── deletion.md
│   ├── inversion.md
│   └── boundary.md
├── personas/
│   ├── adversarial_reader.md
│   ├── opposing_counsel.md
│   └── naive_implementer.md
├── repair/
│   └── templates/
└── presets/
    ├── contract.md
    ├── api_spec.md
    ├── academic_paper.md
    └── policy.md
```

### 5.4 ThinkTank — The Decision Engine

| Attribute | Detail |
|-----------|--------|
| **One-liner** | An anti-anchoring decision engine — 8 personas analyze independently in parallel, then cross-critique, producing genuinely diverse perspectives that sequential analysis cannot achieve |
| **Key Features** | 3-Wave process (Independent → Cross-Critique → Synthesis), Anchoring Visibility Score, Contradiction Heatmap, Parameter Mutation, Decision Replay |
| **Target Users** | Executives (business decisions), policymakers (policy simulation), individuals (career decisions) — including non-technical users |
| **Tech Stack** | Bash + Markdown persona templates + Claude Code Task tool (zero infrastructure) |
| **MVP** | `thinktank.sh` + 8 persona definitions + 3 Wave templates + parameter mutation template |

```
cq-engine/thinktank/
├── README.md
├── thinktank.sh
├── personas/
│   ├── business/
│   │   ├── cfo.md, cto.md, cmo.md, investor.md
│   ├── stakeholders/
│   │   ├── customer.md, employee.md, regulator.md
│   ├── meta/
│   │   └── devils_advocate.md
│   └── custom/
├── waves/
│   ├── wave1_independent.md
│   ├── wave2_cross_critique.md
│   └── wave3_synthesis.md
└── mutation/
    └── parameter_mutation.md
```

### 5.5 CQ MCP Server — The Distribution Platform

| Attribute | Detail |
|-----------|--------|
| **One-liner** | One command to bring cognitive quality management to every Claude Code session: `claude mcp add cq-engine` |
| **Key Features** | 8 MCP tools, 2 MCP resources, Hooks integration, local telemetry for self-improvement |
| **Target Users** | All Claude Code users (zero learning cost — Claude autonomously decides when to use CQ tools) |
| **Tech Stack** | Python MCP SDK (sole infrastructure exception) + Bash/CLI fallback for every tool |
| **MVP** | `server.py` + tool implementations + hooks scripts + telemetry module |

```
cq-engine/mcp-server/
├── README.md
├── server.py
├── tools/
│   ├── decompose.py
│   ├── gate.py
│   ├── persona.py
│   ├── mutate.py
│   ├── learn.py
│   ├── cqlint.py
│   ├── mutadoc.py
│   └── thinktank.py
├── resources/
│   ├── patterns.py
│   └── learned.py
├── telemetry/
│   └── collector.py
└── hooks/
    ├── cognitive_hygiene_check.sh
    └── auto_mutation.sh
```

### 5.6 CQ Benchmark — The Measurement Framework

| Attribute | Detail |
|-----------|--------|
| **One-liner** | A unified measurement framework for cognitive quality — because you cannot call it "engineering" without measurement |
| **Key Features** | 4-axis scoring (Context Health, Decision Quality, Document Integrity, Evolution), standardized metrics across all directions |
| **Target Users** | AI engineers using any CQE direction (internal validation tool) |
| **Tech Stack** | Specification document (Phase 1) + measurement scripts (Phase 2+) |
| **MVP** | Specification document defining 4 axes, sub-metrics, and calculation methods |

**Cross-cutting nature**: CQ Benchmark is not a separate phase — it is defined in Phase 1 and applied progressively from Phase 2 onward. It serves as the common yardstick that prevents each direction from claiming success with incompatible metrics.

```
cq-engine/benchmark/
├── README.md
├── spec.md
└── measures/
    ├── context_health.md
    ├── decision_quality.md
    ├── document_integrity.md
    └── evolution.md
```

---

## 6. Risks & Prerequisites

### 6.1 Phase-Specific Risks

#### Phase 1 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pattern misuse epidemic (Strategy hell, Factory of Factories) | Undermines CQE credibility | Anti-Patterns + Failure Catalog + Weight classification (Foundational/Situational/Advanced) included from v0.1 |
| "8 patterns = too many to adopt" pressure | Slows adoption | Weight classification lets users start with 3 Foundational patterns only |
| Evidence Level B for all patterns (no quantitative validation yet) | Academic skepticism | Explicitly disclose Evidence Levels; upgrade to A as quantitative data becomes available |

#### Phase 2 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| "Just ask ChatGPT to review" perception | MutaDoc dismissed as unnecessary | "30-second experience" design — show a result ChatGPT review missed within 30 seconds |
| Repair suggestions are unusable | Mutation-Driven Repair seen as noise | Target 30%+ "use as-is" rate; show diff view for easy evaluation |
| Document type coverage too narrow (only 3 types) | Perceived as niche tool | Launch with 10+ document type presets |
| Slow execution (5+ minutes) | UX indistinguishable from ChatGPT | Progress display within 30s, Critical first-report within 2 minutes |

#### Phase 3 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python dependency contradicts zero-infrastructure principle | Philosophy inconsistency | Always provide Bash/CLI fallback for every MCP tool |
| Telemetry privacy concerns | User distrust | All telemetry strictly local. No data leaves the machine. Ever |
| Agent Teams competition | Claude Code's Agent Teams directly competes with crew | Prepare crew templates as Agent Teams CLAUDE.md injection path |
| Claude Code API changes | MCP server breaks on Claude Code updates | Pin to stable MCP SDK version; maintain compatibility test suite |

#### Phase 4 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| "Multi-perspective = SWOT/Six Hats" perception | ThinkTank dismissed as derivative | Position as "Anti-Anchoring Engine," not "multi-perspective tool." Quantify anchoring elimination |
| 8 personas too expensive (API costs) | Prohibitive for casual use | Provide 3-persona quick mode; 8-persona for important decisions |
| Anchoring Visibility Score methodology unvalidated | Core differentiator is unproven | Validate in Phase 4 H4 with statistical rigor before marketing the score |

### 6.2 Cross-Cutting Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hypothesis baselines are vague | Cannot validate success | Apply 5-element framework (IV / DV / Baseline / Effect Size / Sample Size) to all hypotheses before testing |
| "Engineering discipline" claim without academic backing | Credibility challenge | Phase 1 patterns written in arXiv-compatible format; pursue academic publication track |
| Community building not addressed | Ecosystem stalls at solo developer | Post Phase 3 MCP launch: open GitHub Discussions, build contributor onboarding |
| Revenue model undefined | Long-term sustainability unclear | Explicitly out of scope — focus on value creation first |
| Competitor analysis incomplete (LangGraph, CrewAI) | Blind spots in positioning | Schedule competitive analysis as a dedicated task before Phase 2 |

### 6.3 Prerequisites

| Prerequisite | Applies To | Description |
|--------------|-----------|-------------|
| Zero-infrastructure principle | All Phases | Bash + Markdown + Claude Code as default. Python only for MCP Server, with CLI fallback |
| Sequential execution | All Phases | No phase skipping. Each phase's entry criteria must be met |
| Hypothesis validation framework | All Phases | 5-element framework applied to every hypothesis before testing |
| arXiv-compatible writing | Phase 1 | Pattern catalog must be publishable as academic paper |
| 30-second experience design | Phase 1–4 | Every direction must have an instant "aha moment" for new users |
| Circular feedback architecture | Phase 3+ | Design telemetry → pattern evolution loops into the MCP Server from day one |
| Privacy-first telemetry | Phase 3+ | All data collection strictly local. No remote transmission. Non-negotiable |

### 6.4 Deferred Directions (Revival Conditions)

These directions were not selected but have explicit revival conditions:

| Direction | Revival Condition | Timing |
|-----------|-------------------|--------|
| CTL (Cognitive Task Language) | CQE Patterns v0.2+ AND community demand for declarative task definition | Phase 3+ |
| Cognitive Quality Protocol (CQP) | CQE Patterns reach 2+ versions, need for inter-framework interoperability | Phase 3+ |
| Personal CQ Assistant | Add personal mode to CQ MCP Server | Phase 3 |
| ContextOS concepts | Incorporate into CQ MCP Server gate tool internals | Phase 3 gate tool implementation |
| Academic citations | Adopt arXiv-publishable format for patterns | Phase 1 (built-in) |
| Community building | GitHub Discussions after MCP public launch | Phase 3+ |

---

## 7. Repository Structure

The `cq-engine` repository follows a monorepo structure with phase-by-phase growth. Each phase adds new top-level directories while keeping the existing structure intact.

### Full Structure (All Phases Complete)

```
cq-engine/
├── README.md                          # Project entry point
├── LICENSE                            # MIT License
├── CLAUDE.md                          # Claude Code integration settings
├── CONTRIBUTING.md                    # Contribution guide
├── .github/
│   └── workflows/
│       ├── cqlint-check.yml           # PR cqlint check
│       └── test.yml                   # Full test suite
│
├── patterns/                          # CQE Patterns catalog (Phase 1)
│   ├── README.md
│   ├── 01_attention_budget.md
│   ├── 02_context_gate.md
│   ├── 03_cognitive_profile.md
│   ├── 04_wave_scheduler.md
│   ├── 05_assumption_mutation.md
│   ├── 06_experience_distillation.md
│   ├── 07_file_based_io.md
│   ├── 08_template_driven_role.md
│   └── anti-patterns/
│
├── cqlint/                            # CQ Linter (Phase 1)
│   ├── README.md
│   ├── cqlint.sh
│   ├── rules/
│   └── adapters/
│
├── benchmark/                         # CQ Benchmark (Phase 1)
│   ├── README.md
│   ├── spec.md
│   └── measures/
│
├── mutadoc/                           # MutaDoc (Phase 2)
│   ├── README.md
│   ├── mutadoc.sh
│   ├── strategies/
│   ├── personas/
│   ├── repair/
│   └── presets/
│
├── mcp-server/                        # CQ MCP Server (Phase 3)
│   ├── README.md
│   ├── server.py
│   ├── tools/
│   ├── resources/
│   ├── telemetry/
│   └── hooks/
│
├── thinktank/                         # ThinkTank (Phase 4)
│   ├── README.md
│   ├── thinktank.sh
│   ├── personas/
│   ├── waves/
│   └── mutation/
│
├── docs/                              # Documentation
│   ├── overview.md
│   ├── architecture.md
│   ├── roadmap.md
│   ├── glossary.md
│   └── guides/
│       ├── quick-start.md
│       ├── pattern-writing.md
│       └── cqlint-rules.md
│
└── examples/                          # Usage examples
    ├── crew-yaml/
    ├── claude-code/
    └── standalone/
```

### File Naming Conventions

| Target | Convention | Example |
|--------|-----------|---------|
| Pattern files | `NN_snake_case.md` | `01_attention_budget.md` |
| Rule files | `CQNNN_snake_case.md` | `CQ001_budget_missing.md` |
| Shell scripts | `snake_case.sh` | `cqlint.sh`, `mutadoc.sh` |
| Python modules | `snake_case.py` | `decompose.py`, `gate.py` |
| Persona files | `snake_case.md` | `adversarial_reader.md` |
| Strategy files | `snake_case.md` | `contradiction.md` |
| Documentation | `kebab-case.md` | `quick-start.md` |

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

Final evaluation matrix from initial exploration (sharpness ranking):

| Direction | Uniqueness (30%) | Crew Fit (25%) | Impact (20%) | Feasibility (15%) | Synergy (10%) | Weighted | Rank |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| MutaDoc | 10 | 9 | 9 | 8 | 7 | 9.0 | 1 |
| CQE Patterns + cqlint | 9 | 10 | 9 | 7 | 9 | 8.9 | 2 |
| ThinkTank | 8 | 9 | 9 | 7 | 8 | 8.3 | 3 |
| CQ MCP Server | 7 | 8 | 8 | 6 | 10 | 7.7 | 4 |
| CQ Benchmark | 6 | 8 | 7 | 8 | 10 | 7.5 | 5 |

**Note**: Uniqueness rank ≠ implementation order. MutaDoc ranks #1 in uniqueness but is Phase 2 in implementation, because the foundation (CQE Patterns) must exist first. Without named patterns, killer apps are just "useful tools."

## Appendix C: cq-engine Extension vs Standalone Product

| Classification | Directions | Criteria |
|---------------|-----------|----------|
| **cq-engine Extension** | CQE Patterns, cqlint, CQ MCP Server, CQ Benchmark | Target: AI engineers. Runs on Claude Code. Distribution: MCP/Skills/Hooks |
| **Standalone Product** | MutaDoc, ThinkTank | Target: includes non-technical users. Valuable without knowing Claude Code exists. Independent CLI or Web |
