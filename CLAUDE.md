# CQE: Cognitive Quality Engineering for LLM Agents

> A pattern catalog, linter, and benchmark suite for designing high-quality LLM agent systems.

## Project Overview

CQE (Cognitive Quality Engineering) establishes a new engineering discipline for managing cognitive quality in LLM agent systems. It provides named patterns, automated verification tools, and standardized measurement to ensure LLM agents produce reliable, high-quality outputs.

The project draws inspiration from GoF Design Patterns: just as GoF gave software engineers a shared vocabulary for object-oriented design, CQE gives AI engineers a shared vocabulary for cognitive quality in agent design.

## Repository Structure

```
cq-engine/
├── patterns/       # CQE Patterns catalog (8 core patterns + anti-patterns)
├── cqlint/         # CQ Linter (static analysis for cognitive quality)
├── benchmark/      # CQ Benchmark (standardized measurement framework)
├── examples/       # Usage examples
└── docs/           # Documentation
```

### Directory Descriptions

| Directory | Purpose | Phase |
|-----------|---------|-------|
| `patterns/` | Core pattern catalog. Each pattern follows a structured format: Problem, Solution, Anti-Pattern, Failure Catalog, Evidence Level. | Phase 1 |
| `cqlint/` | Bash-based linter that checks agent configurations against CQE patterns. Zero-infrastructure design. | Phase 1 |
| `benchmark/` | Standardized metrics for measuring cognitive quality across 4 axes: Context Health, Decision Quality, Document Integrity, Evolution. | Phase 1 |
| `examples/` | Practical usage examples for different agent frameworks. | Phase 1 |
| `docs/` | Architecture docs, roadmap, glossary, and guides. | Phase 1 |

## Coding Conventions

### Zero-Infrastructure Principle

This project follows a strict zero-infrastructure approach:

- **Primary stack**: Bash + Markdown + Claude Code
- **No build tools**: No npm, webpack, vite, or similar
- **No compile step**: Everything runs directly
- **Single exception**: `mcp-server/` (Phase 3) uses Python with the MCP SDK

### Language and File Formats

- Pattern definitions: Markdown (`.md`)
- Linter rules: Markdown for definitions, Bash (`.sh`) for implementation
- Benchmark specifications: Markdown (`.md`)
- MCP Server (Phase 3 only): Python (`.py`)

### File Naming

| Type | Convention | Example |
|------|-----------|---------|
| Pattern files | `NN_snake_case.md` | `01_attention_budget.md` |
| Rule files | `CQNNN_snake_case.md` | `CQ001_budget_missing.md` |
| Shell scripts | `snake_case.sh` | `cqlint.sh` |
| Documentation | `kebab-case.md` | `quick-start.md` |

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Patterns | Markdown | Human-readable, version-controllable |
| cqlint | Bash | Zero-infrastructure, runs anywhere |
| Benchmark | Markdown + Bash | Specification in Markdown, measurement scripts in Bash |
| MCP Server | Python (MCP SDK) | Only exception to zero-infra; required by MCP protocol |

## Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

Types:
  feat:     New feature or pattern
  fix:      Bug fix
  docs:     Documentation changes
  refactor: Code restructuring
  test:     Adding or updating tests
  chore:    Maintenance tasks

Scopes:
  patterns, cqlint, benchmark, docs, examples
```

Examples:
```
feat(patterns): add Attention Budget pattern with anti-patterns
fix(cqlint): correct false positive in CQ003 persona check
docs(benchmark): clarify Context Health Score calculation
```

## Current Phase

**Phase 1: Foundation**

Phase 1 focuses on establishing the theoretical and tooling foundation:

- CQE Patterns v0.1 (8 core patterns in GoF-inspired format)
- cqlint v0.1 (5 initial rules, Bash implementation)
- CQ Benchmark v0.1 (4-axis metric specification)

Future phases (not yet started):
- Phase 2: Killer apps (MutaDoc)
- Phase 3: Distribution (CQ MCP Server)
- Phase 4: Expansion (ThinkTank)
