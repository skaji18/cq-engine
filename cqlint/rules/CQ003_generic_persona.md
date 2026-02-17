# CQ003: generic-persona

> **Severity**: WARNING
> **Pattern**: [#03 Cognitive Profile](../../patterns/03_cognitive_profile.md)
> **Since**: cqlint v0.1

## Description

Detects agent definitions that use generic, undefined, or insufficiently specific personas. LLMs respond strongly to persona framing — a generic "helpful assistant" performs measurably worse than a domain-specialized persona on tasks requiring expertise.

## Detection Logic

Scan agent configuration files for persona-related fields:

- `persona`
- `role`
- `profile`
- `system_prompt`
- `cognitive_profile`

Then check the value against:

1. **Generic keyword list** (case-insensitive):
   - `assistant`, `helper`, `bot`, `ai`, `agent`, `general`, `default`
   - Common generic phrases: `"you are a helpful"`, `"you are an ai"`, `"you are a general-purpose"`

2. **Minimum specificity threshold**:
   - Persona description shorter than 20 characters is too vague
   - Exception: File path references (e.g., `profile: ./personas/security_expert.md`) are acceptable at any length

## Conditions

| Condition | Result |
|-----------|--------|
| Persona field with domain-specific content (>= 20 chars) | PASS |
| Persona references an external file | PASS |
| Persona matches a generic keyword | WARNING |
| Persona is shorter than 20 characters | WARNING |
| No persona field found | WARNING |
| File has no agent definitions | SKIP (not applicable) |

## Output Format

```
WARNING CQ003: <file>:<line> — Agent "<name>" has generic or undefined persona.
  → Apply Pattern #03 (Cognitive Profile): Define a domain-specific persona with expertise and behavioral traits.
```

## Test Cases

| Case | Input | Expected |
|------|-------|----------|
| Specific persona | `persona: "Senior security auditor specializing in contract review"` | PASS |
| File reference | `cognitive_profile: ./personas/security_expert.md` | PASS |
| Generic keyword | `persona: "assistant"` | WARNING |
| Generic phrase | `persona: "you are a helpful assistant"` | WARNING |
| Too short | `persona: "reviewer"` | WARNING |
| Missing | No persona field in agent definition | WARNING |

## Anti-Pattern Reference

This rule detects the precondition for **[F003] Shallow Profile** — a persona that exists in name only, with no behavioral specification.

## Rationale

The Cognitive Profile pattern states: "Define specialized cognitive personas rather than using generic agents." This rule catches the most common violation — agents that are deployed with default or minimal persona definitions.
