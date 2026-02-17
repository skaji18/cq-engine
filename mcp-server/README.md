# CQ Engine MCP Server

Cognitive Quality Engineering tools as an MCP Server for Claude Code.

> **Version**: 0.1.0
> **License**: MIT
> **Requirements**: Python >= 3.10, mcp >= 1.0.0

---

## Overview

CQ Engine MCP Server packages the full Cognitive Quality Engineering toolkit — patterns, linting, mutation testing, persona selection, and learning — into an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that integrates directly with Claude Code.

With a single command, every Claude Code user gets access to:

- **6 MCP Tools** — decompose tasks within attention budgets, filter context, select personas, run mutation tests, lint agent configurations, and accumulate learning
- **3 MCP Resources** — browse CQE patterns, query accumulated learnings, and check cognitive health
- **3 Claude Code Hooks** — automated context hygiene checks, mutation testing on modified files, and learning signal capture

This is the **distribution layer** for CQ Engine. Phase 1 (CQE Patterns + cqlint + CQ Benchmark) and Phase 2 (MutaDoc) provide the engineering foundations; this MCP Server makes them accessible to all Claude Code users.

---

## Quick Start

### Install

```bash
cd mcp-server
pip install -r requirements.txt
```

### Register with Claude Code

```bash
# One-line registration
claude mcp add cq-engine -- python server.py
```

Or manually add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "cq-engine": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/cq-engine/mcp-server"
    }
  }
}
```

### Verify

Once registered, CQ Engine tools appear as `mcp__cq_engine__<tool>` in Claude Code:

```
mcp__cq_engine__decompose
mcp__cq_engine__gate
mcp__cq_engine__persona
mcp__cq_engine__mutate
mcp__cq_engine__learn
mcp__cq_engine__cqlint
```

---

## Available Tools

| Tool | Description | CQE Pattern |
|------|-------------|-------------|
| `decompose` | Decompose a task into budget-aware subtasks | Attention Budget (01) |
| `gate` | Filter and rank files by relevance within a token budget | Context Gate (02) |
| `persona` | Select the best-fit cognitive persona for a task | Cognitive Profile (03) |
| `mutate` | Run mutation testing on documents to detect vulnerabilities | Assumption Mutation (05) |
| `learn` | Record and accumulate learning observations | Experience Distillation (06) |
| `cqlint` | Lint agent configurations against CQE rules (CQ001-CQ005) | All patterns |

### decompose

Splits a complex task into subtasks, each with an estimated token budget and dependency information.

```
Use mcp__cq_engine__decompose with:
  task_description: "Review authentication module for security vulnerabilities and performance issues"
  budget: 80000
  max_subtasks: 5
```

### gate

Filters available files to select the most relevant context within a token budget, preventing context contamination.

```
Use mcp__cq_engine__gate with:
  task_description: "Fix the login timeout bug"
  available_files: ["src/auth.py", "src/session.py", "src/utils.py", "docs/api.md", "tests/test_auth.py"]
  max_files: 3
  max_tokens: 30000
```

### persona

Selects the optimal cognitive persona from a built-in registry of 6 personas, with support for custom persona directories.

```
Use mcp__cq_engine__persona with:
  task_description: "Audit the API endpoint for SQL injection vulnerabilities"
  task_type: "auto"
```

### mutate

Applies 5 mutation strategies (contradiction, ambiguity, deletion, inversion, boundary) to a document to discover hidden vulnerabilities.

```
Use mcp__cq_engine__mutate with:
  target_path: "docs/api_spec.md"
  strategies: "contradiction,ambiguity"
  preset: "api_spec"
```

### learn

Records a learning observation from agent execution, with duplicate detection and CQE pattern mapping.

```
Use mcp__cq_engine__learn with:
  observation: "API endpoint /users returns 404 for trailing slashes — always strip trailing slashes"
  category: "failure"
  confidence: 0.9
  project: "api-integration"
```

### cqlint

Runs the cognitive quality linter on agent configuration files, checking for CQ001-CQ005 violations.

```
Use mcp__cq_engine__cqlint with:
  target_path: "./my-agent-project/"
  rules: "all"
  output_format: "json"
```

---

## MCP Resources

| Resource | URI | Description |
|----------|-----|-------------|
| **Patterns** | `cq_engine://patterns` | CQE Pattern catalog — all 8 patterns with names, summaries, and classification |
| **Learned** | `cq_engine://learned` | Accumulated learning entries from `~/.cq-engine/learned/` with category aggregation |
| **Health** | `cq_engine://health` | CQ Health Dashboard — telemetry summary and pattern usage statistics |

Resources are read-only and provide context that Claude Code agents can access during task execution.

---

## Claude Code Hooks

CQ Engine provides 3 hooks that integrate into Claude Code's hook system for automated cognitive quality monitoring.

### PreToolUse: cognitive_hygiene_check.sh

Runs before Edit/Write tool execution. Computes a lightweight Context Health Score based on file count, file size, and freshness. **Never blocks** — warnings only.

### PostToolUse: auto_mutation.sh

Runs after Task tool completion. Automatically detects modified files and runs MutaDoc quick-check on each. Reports surviving mutations as informational findings. **Never blocks.**

### Notification: auto_learn.sh

Runs on task completion notifications. Automatically extracts learning signals, classifies them by category (failure, optimization, pattern_usage, preference), and persists them to `~/.cq-engine/learned/global.jsonl`. **Silent operation** — no stdout output.

### Hook Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "/path/to/cq-engine/mcp-server/hooks/cognitive_hygiene_check.sh"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Task",
        "command": "/path/to/cq-engine/mcp-server/hooks/auto_mutation.sh"
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "command": "/path/to/cq-engine/mcp-server/hooks/auto_learn.sh"
      }
    ]
  }
}
```

---

## Telemetry

All telemetry is **100% local**. No data is sent to any remote server.

- **Storage**: `~/.cq-engine/telemetry/`
- **Format**: Daily JSONL files (`YYYY-MM-DD.jsonl`)
- **Retention**: 90 days (configurable via `purge_old_events()`)
- **Features**:
  - Daily and weekly summaries
  - Pattern usage statistics (mapped to CQE Patterns)
  - Trend comparison (week-over-week)

Telemetry data feeds back into CQE pattern evolution — identifying which patterns are most frequently used and which violations are most common.

---

## Architecture

```
mcp-server/
├── server.py                          # MCP Server entry point (FastMCP)
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
├── tools/                             # 6 MCP tools
│   ├── decompose.py                   # Task decomposition (Attention Budget)
│   ├── gate.py                        # Context filtering (Context Gate)
│   ├── persona.py                     # Persona selection (Cognitive Profile)
│   ├── cqlint_tool.py                 # Configuration linter (CQ001-CQ005)
│   ├── mutate.py                      # Document mutation testing (Assumption Mutation)
│   └── learn.py                       # Learning accumulation (Experience Distillation)
├── resources/                         # MCP resources
│   ├── patterns.py                    # cq_engine://patterns
│   └── learned.py                     # cq_engine://learned
├── telemetry/                         # Local telemetry
│   └── collector.py                   # Event collection + aggregation
└── hooks/                             # Claude Code hooks
    ├── cognitive_hygiene_check.sh     # PreToolUse: Context Health monitoring
    ├── auto_mutation.sh               # PostToolUse: Auto mutation check
    └── auto_learn.sh                  # Notification: Auto learning capture
```

---

## Requirements

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | >= 3.10 | Runtime for MCP server and tools |
| mcp | >= 1.0.0 | MCP SDK for server implementation |
| Claude Code | latest | Client for hooks integration |
| Bash | >= 4.0 | Runtime for hooks and cqlint.sh |

All tool implementations use **Python standard library only** (json, pathlib, re, asyncio, subprocess). The only external dependency is the `mcp` package for the server framework.

---

## Relationship to CQ Engine

CQ MCP Server is Phase 3 of the CQ Engine project — the distribution layer that makes Phase 1 and Phase 2 outputs accessible to all Claude Code users.

```
Phase 1: Foundation          Phase 2: MutaDoc          Phase 3: MCP Server
─────────────────           ──────────────            ────────────────────
../patterns/                ../mutadoc/               ./  (this directory)
  8 CQE Patterns              5 mutation strategies     6 tools
  Anti-pattern catalog         3 adversarial personas    3 resources
../cqlint/                    Mutation-Driven Repair    3 hooks
  5 lint rules (CQ001-005)    4 document presets        Local telemetry
../benchmark/
  4-axis measurement
  12 sub-metrics
```

Each MCP tool maps to one or more CQE Patterns:

| CQE Pattern | MCP Tool | Integration |
|-------------|----------|-------------|
| 01 Attention Budget | `decompose` | Budget-aware task splitting |
| 02 Context Gate | `gate` | Relevance filtering within token limits |
| 03 Cognitive Profile | `persona` | Best-fit persona selection |
| 05 Assumption Mutation | `mutate` | Document mutation testing via MutaDoc |
| 06 Experience Distillation | `learn` | Learning signal capture and persistence |
| 07 File-Based I/O | All tools | JSON-based inter-tool communication |
| 08 Template-Driven Role | `persona` | Template-driven persona prompts |
| CQ001-CQ005 | `cqlint` | Automated configuration linting |
