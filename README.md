<p align="center">
  <h1 align="center">cq-engine</h1>
  <p align="center">
    <strong>Cognitive Quality Engineering for LLM Agents</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/phase-3%20%2F%204-blue" alt="Phase">
    <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status">
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

Each pattern includes Anti-Patterns (34 total), a Failure Catalog, an Interaction Catalog, and an Evidence Level (A: quantitatively verified — D: hypothesis). All 8 patterns are currently at Evidence Level B.

See [patterns/README.md](patterns/README.md) for the full catalog, dependency graph, and recommended reading order.

**Status:** `v0.1 — Implemented`

---

### :boom: MutaDoc — Document Mutation Testing

> Break documents to find what human reviewers miss — then auto-repair.

The world has grammar checkers (Grammarly), contract extractors (ContractPodAi), and plagiarism detectors (Turnitin). Nobody *intentionally breaks* documents to discover hidden vulnerabilities. MutaDoc does.

**Key capabilities:**
- **5 mutation strategies** — contradiction, ambiguity, deletion, inversion, boundary
- **Mutation-Driven Repair** — auto-generates fix proposals for every Critical finding
- **Regression mutation** — re-mutates the repaired version to catch new weaknesses
- **Mutation Kill Score** — a quantified document quality metric that doesn't exist yet
- **4 document-type presets** — contracts, API specs, academic papers, policy docs
- **3 adversarial personas** — opposing counsel, naive implementer, adversarial reader

**Target users:** Lawyers (M&A stress-testing), API engineers (spec verification), researchers (logic validation) — including non-technical users.

```bash
# Quick ambiguity scan
./mutadoc/mutadoc.sh quick your-document.md

# Full analysis with preset
./mutadoc/mutadoc.sh test contract.md --preset contract

# Just the Mutation Kill Score
./mutadoc/mutadoc.sh score document.md
```

See [mutadoc/README.md](mutadoc/README.md) for the full documentation.

**Status:** `v0.1 — Implemented`

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

**Status:** `Planned` (Phase 4)

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

**Status:** `v0.1 — Specification Complete`

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
| `cq_engine__mutate` | Run document mutation tests |
| `cq_engine__learn` | Accumulate experience from execution |
| `cq_engine__cqlint` | Static analysis for cognitive quality |

**Also includes:**
- 3 MCP Resources — patterns catalog, accumulated learnings, health dashboard
- 3 Claude Code Hooks — cognitive hygiene check, auto mutation, auto learn
- Local-only telemetry collector (JSONL, no network calls)

See [mcp-server/README.md](mcp-server/README.md) for the full documentation.

**Status:** `v0.1 — Implemented`

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
$ ./cqlint/cqlint.sh check .
WARNING CQ001: Task "deploy_service" has no attention budget defined.
ERROR   CQ002: Agent "reviewer" receives unfiltered output from "analyzer" (Context Gate missing).
```

**Status:** `v0.1 — Implemented`

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

  ✓ COMPLETE       ✓ COMPLETE       ✓ COMPLETE       ◀── NEXT

[████████████████████████████████░░░░░░░░░░] ~75%
```

**Phases 1–3 are complete.** The project has delivered 88 files and ~20,000 lines of implementation across CQE Patterns (8 patterns in GoF format), cqlint (5 rules), CQ Benchmark (4-axis specification), MutaDoc (5 strategies, 3 personas, 4 presets), and CQ MCP Server (6 tools, 3 resources, 3 hooks). Phase 4 (ThinkTank — anti-anchoring multi-perspective decision engine) is next.

---

## Getting Started

### cqlint — Check your agent configuration

```bash
# Clone the repository
git clone https://github.com/skaji18/cq-engine.git && cd cq-engine

# Scan your agent configuration for cognitive quality issues
./cqlint/cqlint.sh check path/to/your/agent-config/

# Check specific rules
./cqlint/cqlint.sh check my-crew.yaml --rules CQ001,CQ002
```

### MutaDoc — Break your documents to find weaknesses

```bash
# Run MutaDoc on a document
./mutadoc/mutadoc.sh test your-document.md

# Quick ambiguity scan
./mutadoc/mutadoc.sh quick contract.md

# Just the Mutation Kill Score
./mutadoc/mutadoc.sh score spec.md
```

### CQ MCP Server — Add cognitive quality to Claude Code

```bash
# Install dependencies
cd mcp-server && pip install -r requirements.txt

# Register with Claude Code
claude mcp add cq-engine -- python server.py
```

---

## Repository Statistics

| Component | Files | Lines | Phase |
|-----------|:-----:|:-----:|:-----:|
| CQE Patterns | 10 | ~2,900 | 1 |
| cqlint | 17 | ~1,000 | 1 |
| CQ Benchmark | 6 | ~1,300 | 1 |
| MutaDoc | 23 | ~6,900 | 2 |
| CQ MCP Server | 21 | ~3,200 | 3 |
| Docs & Config | 11 | ~4,700 | — |
| **Total** | **88** | **~20,000** | |

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

| Phase | Focus | Key Deliverables | Status |
|-------|-------|-----------------|--------|
| **1 — Foundation** | Name the concepts | CQE Patterns v0.1, cqlint v0.1, CQ Benchmark v0.1 | ✓ Complete |
| **2 — Killer App** | Prove the value | MutaDoc v0.1 with auto-repair, benchmark validation | ✓ Complete |
| **3 — Distribution** | Reach every user | CQ MCP Server, Hooks integration, telemetry | ✓ Complete |
| **4 — Expansion** | Complete the vision | ThinkTank v0.1, feedback loop, pattern evolution | Next |

### Design Principles

- **Zero Infrastructure** — Bash + Markdown + Claude Code. No databases, no external services.
- **Patterns First** — Name concepts before writing code. The naming has the highest leverage.
- **Feedback Loops** — Usage data flows back to evolve patterns. The system improves itself.
- **Honest Staging** — Every component shows its Evidence Level. Hypotheses are labeled as hypotheses.

---

<p align="center">
  <sub>Cognitive Quality Engineering is a new field. We're building it in the open.</sub>
</p>
