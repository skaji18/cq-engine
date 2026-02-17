<p align="center">
  <h1 align="center">cq-engine</h1>
  <p align="center">
    <strong>Cognitive Quality Engineering for LLM Agents</strong>
  </p>
  <p align="center">
    <!-- Badges: replace URLs once repository is public -->
    <img src="https://img.shields.io/badge/phase-1%20%2F%204-blue" alt="Phase">
    <img src="https://img.shields.io/badge/status-conceptual-orange" alt="Status">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/infra-zero--dependency-brightgreen" alt="Zero Infra">
  </p>
</p>

---

## Why This Project Exists

LLM-based agent systems suffer from invisible quality failures: attention budgets silently overflow, context gets contaminated across agent boundaries, and design assumptions go untested. These problems have no shared vocabulary, no measurement, and no tooling.

**Cognitive Quality Engineering (CQE)** is a new engineering discipline that names these problems, provides patterns to solve them, and builds tools to enforce quality automatically. This project is the reference implementation.

> Think of it this way: GoF gave Object-Oriented Programming its *Design Patterns*. We give LLM agent design its *Cognitive Quality Patterns* — and the linter, mutation tester, and decision engine to go with them.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Knowledge Layer                                               │
│   ┌───────────────────────────────────┐                         │
│   │  CQE Patterns                     │  8 core patterns that   │
│   │  Name concepts. Define the field. │  give vocabulary to     │
│   └──────────────┬────────────────────┘  cognitive quality      │
│                  │                                               │
│   Application Layer                                             │
│   ┌──────────────┼────────────────────────────────────┐         │
│   │              ▼                                    │         │
│   │  ┌────────────────┐  ┌────────────┐  ┌─────────┐ │         │
│   │  │    MutaDoc      │  │  ThinkTank │  │ cqlint  │ │         │
│   │  │  Break docs to  │  │  Parallel  │  │  Lint   │ │         │
│   │  │  find weakness  │  │  multi-POV │  │  agent  │ │         │
│   │  │  & auto-repair  │  │  decisions │  │  config │ │         │
│   │  └────────┬────────┘  └─────┬──────┘  └────┬────┘ │         │
│   └───────────┼─────────────────┼──────────────┼──────┘         │
│               │                 │              │                 │
│   Measurement Layer             │              │                 │
│   ┌───────────┼─────────────────┼──────────────┼──────┐         │
│   │           ▼                 ▼              ▼      │         │
│   │        CQ Benchmark — unified metrics for all     │         │
│   └───────────────────────────┬────────────────────────┘         │
│                               │                                 │
│   Distribution Layer          │                                 │
│   ┌───────────────────────────┼────────────────────────┐         │
│   │                           ▼                        │         │
│   │     CQ MCP Server                                  │         │
│   │     claude mcp add cq-engine  →  every Claude Code │         │
│   │     user gets CQE for free                         │         │
│   └────────────────────────────────────────────────────┘         │
│                               │                                 │
│                               ▼                                 │
│                    Telemetry feedback loop                       │
│                    Usage data → Pattern evolution                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### :books: CQE Patterns — The Foundation

> Name the unnamed. Define the field.

Eight core patterns for LLM agent cognitive quality, written in GoF format (Problem / Context / Solution / Anti-Pattern / Evidence Level).

| # | Pattern | Problem It Solves | Weight |
|---|---------|-------------------|--------|
| 1 | **Attention Budget** | LLM attention is finite but unmanaged | Foundational |
| 2 | **Context Gate** | Passing all info between agents contaminates attention | Foundational |
| 3 | **Cognitive Profile** | Generic agents underperform specialized ones | Foundational |
| 4 | **Wave Scheduler** | Launching everything at once degrades quality | Situational |
| 5 | **Assumption Mutation** | Untested assumptions hide vulnerabilities | Situational |
| 6 | **Experience Distillation** | Without learning, the same failures repeat | Advanced |
| 7 | **File-Based I/O** | Agent communication lacks reliability and transparency | Foundational |
| 8 | **Template-Driven Role** | Implicit roles cause inconsistent quality | Situational |

Each pattern includes Anti-Patterns, a Failure Catalog, and an Evidence Level (A: quantitatively verified — D: hypothesis).

**Status:** `Planned`

---

### :boom: MutaDoc — Document Mutation Testing

> Break documents to find what human reviewers miss — then auto-repair.

The world has grammar checkers (Grammarly), contract extractors (ContractPodAi), and plagiarism detectors (Turnitin). Nobody *intentionally breaks* documents to discover hidden vulnerabilities. MutaDoc does.

**Key capabilities:**
- **5 mutation strategies** — contradiction, ambiguity, deletion, inversion, boundary
- **Mutation-Driven Repair** — auto-generates fix proposals for every Critical finding
- **Regression mutation** — re-mutates the repaired version to catch new weaknesses
- **Mutation Kill Score** — a quantified document quality metric that doesn't exist yet
- **10+ document-type presets** — contracts, API specs, academic papers, policy docs, and more

**Target users:** Lawyers (M&A stress-testing), API engineers (spec verification), researchers (logic validation) — including non-technical users.

```
mutadoc test contract.md --strategies all --personas adversarial_reader
```

**Status:** `Planned`

---

### :crystal_ball: ThinkTank — Anti-Anchoring Decision Engine

> Truly independent multi-perspective analysis. Structurally impossible with ChatGPT alone.

When you ask ChatGPT to "analyze from 8 perspectives," each perspective is generated sequentially in the same context — earlier perspectives anchor later ones. ThinkTank runs each perspective in an **independent context in parallel**, producing genuinely independent viewpoints.

**3-Wave Process:**

| Wave | What Happens |
|------|-------------|
| Wave 1: Independent Analysis | 8 personas analyze in isolated contexts |
| Wave 2: Cross-Critique | Each persona critiques the others |
| Wave 3: Synthesis | Unified judgment with risk matrix |

**Unique outputs:**
- **Anchoring Visibility Score** — quantifies how much bias was eliminated vs. sequential analysis
- **Contradiction Heatmap** — 8x8 matrix showing where personas disagree
- **Decision Replay** — re-analyze past decisions to improve future judgment quality

**Status:** `Planned`

---

### :straight_ruler: CQ Benchmark — The Shared Measuring Stick

> If you can't measure it, you can't call it engineering.

A unified measurement framework for cognitive quality, ensuring all components speak the same metrics language.

| Axis | What It Measures |
|------|-----------------|
| **Context Health** | Information density, contamination level, freshness |
| **Decision Quality** | Perspective diversity, anchoring elimination, blind-spot coverage |
| **Document Integrity** | Mutation Kill rate, contradiction count, ambiguity score |
| **Evolution** | Pattern conformance, learning accumulation rate, recurrence rate |

**Status:** `Planned`

---

### :electric_plug: CQ MCP Server — The Distribution Layer

> `claude mcp add cq-engine` — one line to bring cognitive quality to every Claude Code session.

An MCP server that bundles all components into tools that Claude Code can call automatically. Not just distribution — it collects local telemetry to evolve the patterns themselves.

**Tools provided:**

| Tool | Function |
|------|----------|
| `cq_engine__decompose` | Break tasks into cognitively-budgeted subtasks |
| `cq_engine__gate` | Filter context to only what each subtask needs |
| `cq_engine__persona` | Select the right cognitive profile for each subtask |
| `cq_engine__mutadoc` | Run document mutation tests |
| `cq_engine__thinktank` | Multi-perspective decision analysis |
| `cq_engine__cqlint` | Static analysis for cognitive quality |
| `cq_engine__learn` | Accumulate experience from execution |
| `cq_engine__benchmark` | Measure cognitive quality metrics |

**Status:** `Planned`

---

### :mag: cqlint — The Linter

> Catch cognitive quality issues before execution, not after.

A static analysis tool for agent configurations. Five initial rules:

| Rule | What It Catches |
|------|----------------|
| CQ001 | Missing attention budget in task definitions |
| CQ002 | Context contamination risk (no Context Gate) |
| CQ003 | Generic or undefined persona |
| CQ004 | No mutation step for high-risk tasks |
| CQ005 | Learning mechanism disabled |

```bash
$ cqlint check .
WARNING CQ001: Task "deploy_service" has no attention budget defined.
ERROR   CQ002: Agent "reviewer" receives unfiltered output from "analyzer" (Context Gate missing).
```

**Status:** `Planned`

---

## Current Phase

```
Phase 1          Phase 2          Phase 3          Phase 4
Foundation       Killer App       Distribution     Expansion
─────────────    ─────────────    ─────────────    ─────────────
CQE Patterns     MutaDoc v0.1     CQ MCP Server    ThinkTank v0.1
+ cqlint v0.1    + Auto-Repair    + Telemetry      + 8 Personas
+ CQ Benchmark   + Benchmark      + Hooks           + 3-Wave Pipe
  v0.1             applied          Integration      + Feedback Loop

  ◀── YOU ARE HERE

[████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] ~10%
```

**What's happening now:** Defining the 8 core patterns, designing the cqlint rule set, and specifying the CQ Benchmark axes. No code yet — we're naming concepts first, because naming is the highest-leverage activity at this stage.

---

## Getting Started

> This section will be populated once Phase 1 delivers working tools. Here's what to expect:

### cqlint (first tool available)

```bash
# Install (planned)
# git clone https://github.com/skaji18/cq-engine.git && cd cq-engine
# ./install.sh

# Scan your agent configuration for cognitive quality issues
cqlint check path/to/your/agent-config/

# Check a specific file
cqlint check my-crew.yaml --rules CQ001,CQ002
```

### MCP Server (Phase 3)

```bash
# One-line install into Claude Code (planned)
claude mcp add cq-engine
```

---

## Contributing

We welcome contributions across all components. Here's how to get involved:

### Guidelines

- **Patterns:** Propose new patterns or refine existing ones via Issues. Each pattern needs: Problem, Context, Solution, Anti-Pattern, Evidence Level.
- **cqlint rules:** New rules should map to a specific CQE Pattern and include test cases (passing + failing examples).
- **MutaDoc strategies:** New mutation strategies should work across at least 2 document types.
- **Bug reports:** Include the component name, input that triggered the issue, and expected vs. actual behavior.

### Process

1. Open an Issue describing the change
2. Fork and create a feature branch (`feature/your-change`)
3. Submit a Pull Request referencing the Issue
4. All PRs require one review approval before merge

### Code of Conduct

Be constructive. This project applies mutation testing to documents — channel that adversarial energy into making things better, not tearing people down.

---

## License

[MIT](LICENSE)

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the detailed plan.

### Quick Overview

| Phase | Focus | Key Deliverables | Timeframe |
|-------|-------|-----------------|-----------|
| **1 — Foundation** | Name the concepts | CQE Patterns v0.1, cqlint v0.1, CQ Benchmark v0.1 | Current |
| **2 — Killer App** | Prove the value | MutaDoc v0.1 with auto-repair, benchmark validation | Next |
| **3 — Distribution** | Reach every user | CQ MCP Server, Hooks integration, telemetry | Upcoming |
| **4 — Expansion** | Complete the vision | ThinkTank v0.1, feedback loop, pattern evolution | Future |

### Design Principles

- **Zero Infrastructure** — Bash + Markdown + Claude Code. No databases, no external services.
- **Patterns First** — Name concepts before writing code. The naming has the highest leverage.
- **Feedback Loops** — Usage data flows back to evolve patterns. The system improves itself.
- **Honest Staging** — Every component shows its Evidence Level. Hypotheses are labeled as hypotheses.

---

<p align="center">
  <sub>Cognitive Quality Engineering is a new field. We're building it in the open.</sub>
</p>
