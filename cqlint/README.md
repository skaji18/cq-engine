# cqlint

> A cognitive quality linter for LLM agent configurations.

**Version**: 0.1.0
**Status**: Phase 1 — Functional

## Overview

cqlint is a static analysis tool that checks LLM agent configurations against CQE Patterns. It detects common cognitive quality issues before they cause problems in production, similar to how ESLint catches JavaScript issues before runtime.

Built with zero infrastructure: pure Bash + standard UNIX tools, runs anywhere.

## Quick Start

```bash
# Check a project directory
./cqlint.sh check your-project/

# Check a single file
./cqlint.sh check task.yaml

# Run a specific rule only
./cqlint.sh check . --rule CQ001

# Output as JSON
./cqlint.sh check . --format json
```

Example output:
```
cqlint v0.1.0 — Cognitive Quality Linter
Checking: ./my-project/

  WARNING CQ001: task.yaml:2 — Task has no attention budget defined.
    → Pattern #01 (Attention Budget): Set an explicit token budget before execution.
  ERROR CQ004: critical_task.yaml:5 — High-risk task has no mutation or verification step.
    → Pattern #05 (Assumption Mutation): Add mutation testing or adversarial review.

─── cqlint summary ───
  1 error(s), 1 warning(s), 3 passed, 5 skipped
```

## Rules (v0.1)

| Rule | Name | Severity | Pattern | Description |
|------|------|----------|---------|-------------|
| CQ001 | attention-budget-missing | WARNING | [#01 Attention Budget](../patterns/01_attention_budget.md) | Task definition lacks token budget specification |
| CQ002 | context-contamination-risk | ERROR | [#02 Context Gate](../patterns/02_context_gate.md) | Multi-stage pipeline has no filtering between stages |
| CQ003 | generic-persona | WARNING | [#03 Cognitive Profile](../patterns/03_cognitive_profile.md) | Agent persona is generic, too short, or missing |
| CQ004 | no-mutation-on-critical | ERROR | [#05 Assumption Mutation](../patterns/05_assumption_mutation.md) | High-risk task has no mutation or review step |
| CQ005 | learning-disabled | WARNING | [#06 Experience Distillation](../patterns/06_experience_distillation.md) | No learning/experience accumulation mechanism |

Each rule links to a CQE Pattern. See `rules/` for detailed rule documentation including detection logic, conditions, and test cases.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed (warnings are allowed) |
| 1 | One or more ERROR-severity issues found |
| 2 | Invalid arguments or target not found |

## Options

| Option | Description |
|--------|-------------|
| `--help` | Show usage information |
| `--version` | Show version |
| `--rule <ID>` | Run only the specified rule (e.g., `CQ001`) |
| `--format <fmt>` | Output format: `text` (default) or `json` |

## Architecture

```
cqlint/
├── cqlint.sh                          # Entry point (Bash, zero-infrastructure)
├── README.md                          # This file
├── rules/                             # Rule definitions (Markdown documentation)
│   ├── CQ001_budget_missing.md
│   ├── CQ002_context_contamination.md
│   ├── CQ003_generic_persona.md
│   ├── CQ004_no_mutation_critical.md
│   └── CQ005_learning_disabled.md
└── tests/                             # Test fixtures
    ├── pass/                          # Configurations that should pass
    │   ├── task_with_budget.yaml      # CQ001 pass
    │   ├── pipeline_with_gate.yaml    # CQ002 pass
    │   ├── agent_specific_persona.yaml # CQ003 pass
    │   ├── critical_with_mutation.yaml # CQ004 pass
    │   └── project_with_learning.yaml # CQ005 pass
    └── fail/                          # Configurations that should trigger issues
        ├── task_no_budget.yaml        # CQ001 fail
        ├── pipeline_no_gate.yaml      # CQ002 fail
        ├── agent_generic_persona.yaml # CQ003 fail
        ├── critical_no_mutation.yaml  # CQ004 fail
        └── project_no_learning.yaml   # CQ005 fail
```

## Running Tests

```bash
# Run against pass fixtures (should exit 0)
./cqlint.sh check tests/pass/
# Expected: warnings allowed, no errors

# Run against fail fixtures (should exit 1)
./cqlint.sh check tests/fail/
# Expected: errors detected

# Test individual rules
./cqlint.sh check tests/fail/task_no_budget.yaml --rule CQ001
./cqlint.sh check tests/fail/pipeline_no_gate.yaml --rule CQ002
./cqlint.sh check tests/fail/agent_generic_persona.yaml --rule CQ003
./cqlint.sh check tests/fail/critical_no_mutation.yaml --rule CQ004
./cqlint.sh check tests/fail/project_no_learning.yaml --rule CQ005
```

## Design Principles

- **Zero infrastructure**: Bash + grep/awk/sed only. No Python, Node.js, or other runtime required.
- **Pattern-backed**: Every rule maps to a CQE Pattern. No arbitrary style checks.
- **Evidence-linked**: Each rule references its evidence level from the pattern catalog.
- **Severity-stratified**: ERROR = must fix before deployment. WARNING = should fix. SKIP = rule not applicable.
