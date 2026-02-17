# CQE Anti-Pattern Index

> A cross-pattern catalog of failure modes in LLM agent systems.
>
> Use this index to diagnose problems by symptom — find the anti-pattern
> that matches your failure, then follow the link to the corrective pattern.

**Version**: 0.1.0
**Total Anti-Patterns**: 34

---

## Anti-Pattern Summary

| Pattern | ID | Anti-Pattern Name | One-Line Description |
|---------|----|-------------------|---------------------|
| [01 Attention Budget](../01_attention_budget.md) | F001 | Budget Illusion | Set a budget number but never enforce it |
| [01 Attention Budget](../01_attention_budget.md) | F002 | Uniform Budget | Same budget for every task regardless of complexity |
| [01 Attention Budget](../01_attention_budget.md) | F003 | Budget-Only Monitoring | Track tokens without correlating to output quality |
| [01 Attention Budget](../01_attention_budget.md) | F004 | Budget Hoarding | Over-allocate budgets, blocking system parallelism |
| [01 Attention Budget](../01_attention_budget.md) | F005 | Post-Hoc Budgeting | Add budgets after design instead of using them to drive design |
| [02 Context Gate](../02_context_gate.md) | F001 | Gate Bypass | Route information around the gate for "efficiency" |
| [02 Context Gate](../02_context_gate.md) | F002 | Over-Filtering | Remove too much context, starving downstream agents |
| [02 Context Gate](../02_context_gate.md) | F003 | Stale Gate | Filter rules not updated as the system evolves |
| [02 Context Gate](../02_context_gate.md) | F004 | Symmetric Gate | Same filter for both directions of bidirectional communication |
| [02 Context Gate](../02_context_gate.md) | F005 | Filter-Without-Format | Filter content but leave it unstructured |
| [03 Cognitive Profile](../03_cognitive_profile.md) | F001 | Profile Bloat | Overload a single profile with contradictory traits |
| [03 Cognitive Profile](../03_cognitive_profile.md) | F002 | Profile Drift | Persona degrades over time without maintenance |
| [03 Cognitive Profile](../03_cognitive_profile.md) | F003 | Shallow Profile | Name-only persona with no behavioral specification |
| [03 Cognitive Profile](../03_cognitive_profile.md) | F004 | Profile Cargo Cult | Copy profiles between domains without adaptation |
| [03 Cognitive Profile](../03_cognitive_profile.md) | F005 | Profile Rigidity | Refuse to update profiles based on execution feedback |
| [04 Wave Scheduler](../04_wave_scheduler.md) | F001 | Wave Overload | Too many tasks in a single wave, exceeding resources |
| [04 Wave Scheduler](../04_wave_scheduler.md) | F002 | Sequential Fallback | Abandon all parallelism out of coordination fear |
| [04 Wave Scheduler](../04_wave_scheduler.md) | F003 | Dependency Blindness | Ignore task dependencies in wave assignment |
| [04 Wave Scheduler](../04_wave_scheduler.md) | F004 | Wave Rigidity | Static wave structure that cannot adapt during execution |
| [05 Assumption Mutation](../05_assumption_mutation.md) | F001 | Mutation Theater | Run mutations but ignore results |
| [05 Assumption Mutation](../05_assumption_mutation.md) | F002 | Weak Mutation | Only test trivial assumptions, miss critical ones |
| [05 Assumption Mutation](../05_assumption_mutation.md) | F003 | Mutation Fatigue | Generate too many findings, burying critical signals |
| [05 Assumption Mutation](../05_assumption_mutation.md) | F004 | Self-Mutation | Same agent creates and tests its own work |
| [05 Assumption Mutation](../05_assumption_mutation.md) | F005 | Mutation Without Repair | Detect vulnerabilities without providing fix proposals |
| [05 Assumption Mutation](../05_assumption_mutation.md) | F006 | One-Shot Mutation | Mutation testing once, never revisiting as system evolves |
| [06 Experience Distillation](../06_experience_distillation.md) | F001 | Unfiltered Memory | Accumulate everything without distillation or prioritization |
| [06 Experience Distillation](../06_experience_distillation.md) | F002 | Stale Learning | Never update or prune accumulated knowledge |
| [06 Experience Distillation](../06_experience_distillation.md) | F003 | Context Leak | Learning data from unrelated tasks contaminates current work |
| [07 File-Based I/O](../07_file_based_io.md) | F001 | File Sprawl | Too many unstructured files without organization |
| [07 File-Based I/O](../07_file_based_io.md) | F002 | Schema Drift | File formats change without coordination between agents |
| [07 File-Based I/O](../07_file_based_io.md) | F003 | Lock Contention | Multiple agents write to the same file simultaneously |
| [08 Template-Driven Role](../08_template_driven_role.md) | F001 | Template Rigidity | Templates too strict to adapt to novel tasks |
| [08 Template-Driven Role](../08_template_driven_role.md) | F002 | Template Sprawl | Too many overlapping templates with unclear boundaries |
| [08 Template-Driven Role](../08_template_driven_role.md) | F003 | Undocumented Deviation | Agents silently deviate from templates without recording why |

---

## Reverse Index: Symptom → Anti-Pattern → Pattern

Use this when you observe a symptom and want to find the relevant pattern.

### Resource & Performance Symptoms

| Symptom | Likely Anti-Pattern | Pattern to Apply |
|---------|-------------------|-----------------|
| Output quality drops in long tasks | Budget Illusion (01-F001) | [Attention Budget](../01_attention_budget.md) |
| Simple tasks consume excessive tokens | Uniform Budget (01-F002) | [Attention Budget](../01_attention_budget.md) |
| High token usage but low quality | Budget-Only Monitoring (01-F003) | [Attention Budget](../01_attention_budget.md) |
| System runs fewer parallel tasks than expected | Budget Hoarding (01-F004) | [Attention Budget](../01_attention_budget.md) |
| Parallel execution degrades all outputs | Wave Overload (04-F001) | [Wave Scheduler](../04_wave_scheduler.md) |
| System is slow despite having multiple agents | Sequential Fallback (04-F002) | [Wave Scheduler](../04_wave_scheduler.md) |

### Information Flow Symptoms

| Symptom | Likely Anti-Pattern | Pattern to Apply |
|---------|-------------------|-----------------|
| Downstream agent produces irrelevant output | Gate Bypass (02-F001) | [Context Gate](../02_context_gate.md) |
| Agent lacks necessary context to complete task | Over-Filtering (02-F002) | [Context Gate](../02_context_gate.md) |
| System worked before but now agents miss info | Stale Gate (02-F003) | [Context Gate](../02_context_gate.md) |
| Internal metadata leaks to external outputs | Filter-Without-Format (02-F005) | [Context Gate](../02_context_gate.md) |
| Multiple agents conflict writing same file | Lock Contention (07-F003) | [File-Based I/O](../07_file_based_io.md) |
| Agent cannot parse another agent's output | Schema Drift (07-F002) | [File-Based I/O](../07_file_based_io.md) |
| File system becomes unnavigable mess | File Sprawl (07-F001) | [File-Based I/O](../07_file_based_io.md) |

### Agent Behavior Symptoms

| Symptom | Likely Anti-Pattern | Pattern to Apply |
|---------|-------------------|-----------------|
| Agent output is generic and shallow | Shallow Profile (03-F003) | [Cognitive Profile](../03_cognitive_profile.md) |
| Agent behavior is contradictory or incoherent | Profile Bloat (03-F001) | [Cognitive Profile](../03_cognitive_profile.md) |
| Same role performs differently across sessions | Profile Drift (03-F002) | [Cognitive Profile](../03_cognitive_profile.md) |
| Agent ignores its defined role instructions | Undocumented Deviation (08-F003) | [Template-Driven Role](../08_template_driven_role.md) |
| Cannot adapt agents to new task types | Template Rigidity (08-F001) | [Template-Driven Role](../08_template_driven_role.md) |
| Too many similar templates, unclear which to use | Template Sprawl (08-F002) | [Template-Driven Role](../08_template_driven_role.md) |

### Quality Assurance Symptoms

| Symptom | Likely Anti-Pattern | Pattern to Apply |
|---------|-------------------|-----------------|
| Critical assumptions go unquestioned | Mutation Theater (05-F001) | [Assumption Mutation](../05_assumption_mutation.md) |
| Mutation reports are ignored by the team | Mutation Fatigue (05-F003) | [Assumption Mutation](../05_assumption_mutation.md) |
| Adversarial review misses obvious blind spots | Self-Mutation (05-F004) | [Assumption Mutation](../05_assumption_mutation.md) |
| Problems found but no path to resolution | Mutation Without Repair (05-F005) | [Assumption Mutation](../05_assumption_mutation.md) |
| Assumptions validated once but drift over time | One-Shot Mutation (05-F006) | [Assumption Mutation](../05_assumption_mutation.md) |

### Learning & Evolution Symptoms

| Symptom | Likely Anti-Pattern | Pattern to Apply |
|---------|-------------------|-----------------|
| System repeats the same failures across projects | Stale Learning (06-F002) | [Experience Distillation](../06_experience_distillation.md) |
| Memory grows but decisions don't improve | Unfiltered Memory (06-F001) | [Experience Distillation](../06_experience_distillation.md) |
| Unrelated historical data affects current tasks | Context Leak (06-F003) | [Experience Distillation](../06_experience_distillation.md) |
| Profile worked well before but no longer does | Profile Rigidity (03-F005) | [Cognitive Profile](../03_cognitive_profile.md) |

---

## Statistics

| Pattern | Anti-Patterns | Weight | Category |
|---------|:------------:|--------|----------|
| 01 Attention Budget | 5 | Foundational | knowledge |
| 02 Context Gate | 5 | Foundational | knowledge |
| 03 Cognitive Profile | 5 | Foundational | knowledge |
| 04 Wave Scheduler | 4 | Situational | application |
| 05 Assumption Mutation | 6 | Situational | verification |
| 06 Experience Distillation | 3 | Advanced | knowledge |
| 07 File-Based I/O | 3 | Foundational | knowledge |
| 08 Template-Driven Role | 3 | Situational | knowledge |
| **Total** | **34** | | |

Distribution by pattern weight:
- Foundational patterns: 18 anti-patterns (53%)
- Situational patterns: 13 anti-patterns (38%)
- Advanced patterns: 3 anti-patterns (9%)

---

## How to Use This Index

1. **Diagnosing a problem**: Find your symptom in the Reverse Index tables above. Follow the link to the corrective pattern.
2. **Reviewing a design**: Scan the Anti-Pattern Summary table. For each anti-pattern, ask: "Could this happen in our system?"
3. **Learning from failures**: When a failure occurs, check if it matches a known anti-pattern. If so, the parent pattern provides the fix.
4. **Building a checklist**: Extract the anti-patterns relevant to your system's Weight class and use them as a pre-deployment review checklist.
