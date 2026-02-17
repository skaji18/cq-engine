# CQ002: context-contamination-risk

> **Severity**: ERROR
> **Pattern**: [#02 Context Gate](../../patterns/02_context_gate.md)
> **Since**: cqlint v0.1

## Description

Detects multi-stage agent configurations where output from one stage flows to the next without explicit filtering or scoping. Unfiltered context transfer is the primary cause of attention contamination — irrelevant information from prior stages consuming budget in downstream stages.

## Detection Logic

Scan YAML pipeline/workflow definitions for multi-stage configurations. For each stage transition, check for the presence of filtering directives:

- `context_filter`
- `context_gate`
- `gate`
- `filter`
- `output_scope`
- `input_scope`
- `select`
- `include_only`

A stage transition is identified when one stage references another stage's output (e.g., `input: stage_a.output`, `depends_on: stage_a`).

## Conditions

| Condition | Result |
|-----------|--------|
| Stage transition has explicit filter/gate/scope | PASS |
| Stage transition with no filtering directive | ERROR |
| Single-stage configuration (no transitions) | SKIP (not applicable) |
| Stage references a file path (file-based I/O acts as natural gate) | PASS |

## Output Format

```
ERROR CQ002: <file>:<line> — Stage "<name>" receives unfiltered output from "<source>". Context Gate missing.
  → Apply Pattern #02 (Context Gate): Add explicit filtering between stages.
```

## Test Cases

| Case | Input | Expected |
|------|-------|----------|
| Gate present | Stage with `context_gate: [summary, findings]` | PASS |
| Filter present | Stage with `input_scope: relevant_files` | PASS |
| No filtering | Stage B input references Stage A output directly | ERROR |
| File-based handoff | Stage B reads from a specific file path | PASS |
| Single stage | No multi-stage pipeline | SKIP |

## Anti-Pattern Reference

This rule detects the precondition for **[F001] Gate Bypass** — if no gate exists in the configuration, bypass is guaranteed.

## Rationale

The Context Gate pattern states: "Every stage transition must include explicit filtering." This rule catches missing gates at the configuration level, before any context contamination can occur at runtime.
