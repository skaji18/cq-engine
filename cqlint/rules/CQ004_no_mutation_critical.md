# CQ004: no-mutation-on-critical

> **Severity**: ERROR
> **Pattern**: [#05 Assumption Mutation](../../patterns/05_assumption_mutation.md)
> **Since**: cqlint v0.1

## Description

Detects tasks or documents marked as high-risk or critical that have no mutation, review, or verification step. Critical outputs that bypass adversarial testing are the highest-risk category of cognitive quality failures — the stakes are high and the safety net is absent.

## Detection Logic

Scan task definitions for risk-level indicators:

- `danger_level: high` or `danger_level: critical`
- `priority: critical`
- `risk: high`
- `criticality: high`

When a high-risk indicator is found, check for the presence of any verification mechanism:

- `mutation`, `mutate`, `mutation_test`
- `review`, `peer_review`
- `verify`, `verification`
- `test`, `adversarial`
- `gate_required: true`
- A `depends_on` reference to a task containing "review", "verify", "test", or "mutation"

## Conditions

| Condition | Result |
|-----------|--------|
| High-risk task with mutation/review/verify step | PASS |
| High-risk task with `gate_required: true` | PASS |
| High-risk task with no verification mechanism | ERROR |
| Low/medium-risk task with no verification | SKIP (not required) |
| No risk level specified | SKIP (assume low risk) |

## Output Format

```
ERROR CQ004: <file>:<line> — High-risk task "<name>" has no mutation or verification step.
  → Apply Pattern #05 (Assumption Mutation): Add mutation testing or adversarial review for critical outputs.
```

## Test Cases

| Case | Input | Expected |
|------|-------|----------|
| Critical with mutation | `danger_level: critical` + `mutation: true` | PASS |
| High with review dep | `danger_level: high` + depends_on includes "review" | PASS |
| Critical, no verify | `danger_level: critical`, no mutation/review/verify | ERROR |
| High, no verify | `danger_level: high`, no verification step | ERROR |
| Low risk | `danger_level: low`, no mutation | SKIP |
| No risk level | No danger_level field | SKIP |

## Anti-Pattern Reference

This rule detects the precondition for **[F001] Mutation Theater** — but catches the even worse case where mutation/review is entirely absent, not merely performative.

## Rationale

The Assumption Mutation pattern states: "High-risk outputs require systematic adversarial testing." This rule enforces that principle by requiring at least one verification mechanism for any task marked as critical or high-risk.
