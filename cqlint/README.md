# cqlint

> A cognitive quality linter for LLM agent configurations.

**Status**: Phase 1 - In Development

## Overview

cqlint is a static analysis tool that checks LLM agent configurations against CQE Patterns. It detects common cognitive quality issues before they cause problems in production, similar to how ESLint catches JavaScript issues before runtime.

Built with zero infrastructure: pure Bash, no dependencies, runs anywhere.

## Quick Start

```bash
cqlint check your-project/
```

Example output:
```
[CQ001] No attention budget specified in task.yaml:5
[CQ003] Generic persona detected in agent.yaml:12
[CQ005] No learning mechanism configured in config.yaml:1

3 issues found (1 error, 2 warnings)
```

## Initial Rules (v0.1)

| Rule | Name | Severity | Description |
|------|------|----------|-------------|
| CQ001 | Budget Missing | error | No attention budget defined for agent task |
| CQ002 | Context Contamination | warning | Potentially irrelevant files included in context |
| CQ003 | Generic Persona | warning | Agent persona lacks domain-specific expertise definition |
| CQ004 | No Mutation on Critical | error | Critical-level output has no mutation/review step |
| CQ005 | Learning Disabled | info | No experience distillation mechanism configured |

## Architecture

```
cqlint/
├── README.md
├── cqlint.sh           # Entry point (Bash, zero-infrastructure)
├── rules/              # Rule definitions (Markdown + check logic)
│   ├── CQ001_budget_missing.md
│   ├── CQ002_context_contamination.md
│   ├── CQ003_generic_persona.md
│   ├── CQ004_no_mutation_critical.md
│   └── CQ005_learning_disabled.md
└── adapters/           # Input adapters for different config formats
    ├── crew_yaml.sh    # crew YAML adapter
    └── generic_yaml.sh # Generic YAML adapter
```

## Design Principles

- **Zero infrastructure**: Bash only. No Python, Node.js, or other runtime required.
- **Pattern-backed**: Every rule maps to a CQE Pattern. No arbitrary style checks.
- **Adapter-based**: Input adapters allow cqlint to work with any agent configuration format.
- **Evidence-linked**: Each rule references its evidence level from the pattern catalog.
