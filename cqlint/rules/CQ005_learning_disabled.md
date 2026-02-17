# CQ005: learning-disabled

> **Severity**: WARNING
> **Pattern**: [#06 Experience Distillation](../../patterns/06_experience_distillation.md)
> **Since**: cqlint v0.1

## Description

Detects project configurations that have no learning or experience accumulation mechanism. Without learning, the system treats every execution as if it were the first — repeating the same failures, unable to improve over time.

## Detection Logic

This is a **project-level** check (run once per project, not per file). Scan the project root for evidence of a learning mechanism:

### Directory-based detection
Check for the existence of any learning-related directory:
- `memory/`
- `learned/`
- `experience/`
- `knowledge/`
- `learnings/`
- `lp/` (Learned Preferences)

The directory must contain at least one file (an empty directory does not count).

### Configuration-based detection
Scan config files (YAML, JSON, TOML) for learning-related settings:
- `learning: true` or `learning: enabled`
- `experience_distillation: enabled`
- `memory: enabled`
- `feedback: enabled`

## Conditions

| Condition | Result |
|-----------|--------|
| Learning directory exists with content | PASS |
| Learning config setting enabled | PASS |
| Learning directory exists but empty | WARNING |
| Learning explicitly disabled (`learning: false`) | WARNING |
| No learning directory and no learning config | WARNING |

## Output Format

```
WARNING CQ005: Project has no learning mechanism. Experience Distillation pattern not implemented.
  → Apply Pattern #06 (Experience Distillation): Add a memory/ or learned/ directory and configure experience accumulation.
```

## Test Cases

| Case | Input | Expected |
|------|-------|----------|
| Memory directory with files | `memory/` dir containing `.md` files | PASS |
| Config with learning enabled | `learning: enabled` in config file | PASS |
| Empty memory directory | `memory/` dir with no files | WARNING |
| Learning disabled | `learning: false` in config | WARNING |
| No mechanism | No learning directory or config | WARNING |

## Anti-Pattern Reference

This rule detects the precondition for **[F001] Unfiltered Memory** — but catches the even more fundamental issue where no memory exists at all.

## Rationale

The Experience Distillation pattern states: "Without learning from execution, systems repeat the same failures across projects and sessions." This rule catches the complete absence of a learning mechanism at the project level.
