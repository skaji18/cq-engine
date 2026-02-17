# CQ001: attention-budget-missing

> **Severity**: WARNING
> **Pattern**: [#01 Attention Budget](../../patterns/01_attention_budget.md)
> **Since**: cqlint v0.1

## Description

Detects task definitions that lack an explicit token budget specification. Without a declared budget, agents operate without resource constraints, leading to silent quality degradation when context windows overflow.

## Detection Logic

Scan YAML and Markdown task definition files for any of the following budget-related fields:

- `attention_budget`
- `token_budget`
- `budget`
- `max_tokens`
- `token_limit`
- `context_limit`

A task definition is identified by the presence of a `task` key (YAML) or a task heading pattern (Markdown).

## Conditions

| Condition | Result |
|-----------|--------|
| Budget field present with a numeric value > 0 | PASS |
| Budget field present but set to `null`, `0`, or empty | WARNING |
| No budget field found in a task definition | WARNING |
| No task definitions found in file | SKIP (not applicable) |

## Output Format

```
WARNING CQ001: <file>:<line> — Task "<name>" has no attention budget defined.
  → Apply Pattern #01 (Attention Budget): Set an explicit token budget before execution.
```

## Test Cases

| Case | Input | Expected |
|------|-------|----------|
| Budget present | `attention_budget: 4000` | PASS |
| Max tokens present | `max_tokens: 8000` | PASS |
| Budget null | `attention_budget: null` | WARNING |
| No budget field | Task YAML with no budget-related field | WARNING |
| Not a task file | Generic YAML config | SKIP |

## Anti-Pattern Reference

This rule detects the precondition for **[F001] Budget Illusion** — having no budget at all is even worse than having a budget that is not enforced.

## Rationale

The Attention Budget pattern states: "No task starts without a declared budget." This rule enforces that principle at the configuration level, catching missing budgets before execution begins.
