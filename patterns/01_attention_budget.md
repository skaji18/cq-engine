# Pattern: Attention Budget

## Classification

- **Weight**: Foundational
- **Evidence Level**: B — Confirmed across multiple production multi-agent systems
- **Category**: knowledge

Attention Budget is a foundational pattern. Every other pattern in the CQE catalog references "budget" as a core resource model. Apply this pattern first when designing any multi-agent system.

---

## Problem

LLM attention is a finite, non-renewable resource within a single execution context, yet most multi-agent systems treat it as unlimited. Developers launch tasks without specifying how much context each task may consume, leading to **silent quality degradation** — the agent continues to produce output, but the output quality drops as context grows beyond the model's effective attention window.

The failure is insidious because:

1. **No hard crash occurs.** The agent does not throw an error when context overflows — it quietly loses coherence.
2. **Quality degradation is non-linear.** Performance holds steady up to a threshold, then drops sharply, making the cliff invisible until it is too late.
3. **Developers blame the model.** "The LLM hallucinated" is often misattributed to model weakness when the true cause is attention exhaustion from unmanaged context growth.

Without explicit budgets, teams have no vocabulary for discussing attention allocation, no mechanism for detecting overflows before they happen, and no way to right-size tasks to the available cognitive resources.

---

## Context

This problem arises when:

- A system runs **multiple tasks sequentially or in parallel** within shared or growing contexts.
- Tasks vary in **complexity** but receive uniform resource allocation.
- **Inter-agent communication** passes large payloads without filtering (see Context Gate pattern).
- The system operates under **cost constraints** where wasted tokens translate directly to wasted budget.
- **Quality is critical** — the system's output feeds into downstream decisions, documents, or code.

Typical environments include multi-agent orchestration frameworks, autonomous coding assistants, document processing pipelines, and any system where an LLM performs multiple distinct tasks within a session.

---

## Solution

Assign an **explicit token budget** to every task before execution begins. The budget defines the maximum context size the task may consume, including input tokens, retrieved context, and generated output.

### Core Principles

1. **Budget Before Execution**: No task starts without a declared budget. The budget is part of the task specification, not an afterthought.

2. **Complexity-Proportional Allocation**: Budgets scale with task complexity. A simple formatting task receives a smaller budget than a multi-file analysis task.

3. **Budget = Ceiling, Not Floor**: A task that completes in 30% of its budget should direct the remaining capacity toward quality verification, not consume it for the sake of spending.

4. **Dual-Track Monitoring**: Track both token consumption (quantity) AND output quality indicators (effectiveness). Budget utilization without quality correlation is meaningless.

5. **Overflow Prevention**: When a task approaches its budget limit, the system must take explicit action — summarize and continue, checkpoint and spawn a sub-task, or escalate to a human operator.

### Budget Specification Format

```yaml
task:
  name: "Analyze requirements document"
  attention_budget:
    max_context_tokens: 50000
    max_output_tokens: 8000
    overflow_strategy: "summarize_and_continue"
    quality_checkpoint_at: 0.7  # Check quality at 70% budget consumption
  complexity: high
  priority: 1
```

### Overflow Strategies

| Strategy | When to Use | Trade-off |
|----------|------------|-----------|
| `summarize_and_continue` | Long-running analysis tasks | Loses some detail but preserves coherence |
| `checkpoint_and_spawn` | Tasks that can be decomposed | Adds coordination overhead but prevents degradation |
| `hard_stop` | Safety-critical tasks where partial output is dangerous | May leave task incomplete |
| `escalate` | Tasks where human judgment is needed at the boundary | Blocks execution until human responds |

### Budget Sizing Heuristic

| Task Complexity | Recommended Budget Range | Examples |
|----------------|------------------------|----------|
| Low | 5K–15K tokens | Formatting, simple lookups, template filling |
| Medium | 15K–50K tokens | Single-file analysis, code review, summarization |
| High | 50K–120K tokens | Multi-file analysis, architectural decisions, report generation |
| Critical | 120K+ tokens (with checkpoints) | System-wide refactoring, cross-repository analysis |

---

## Anti-Pattern

What happens when Attention Budget is misapplied or partially applied:

- **[F001] Budget Illusion** — Setting a budget number but never monitoring it or acting on overflows. The budget exists in the configuration but has no enforcement mechanism. Teams believe they are managing attention because a number is written down, while in practice the system ignores it entirely. The budget is a "ceiling" on paper but a suggestion in practice.

- **[F002] Uniform Budget** — Assigning the same budget to every task regardless of complexity. A simple file rename receives the same 100K token budget as a full codebase analysis. This wastes resources on trivial tasks and starves complex tasks that need more headroom. The root cause is treating budgeting as a checkbox ("we have budgets") rather than an engineering decision.

- **[F003] Budget-Only Monitoring** — Tracking token consumption without correlating it to output quality. A task that uses 100% of its budget is flagged as "completed" even when the output quality degraded sharply in the last 20%. The team celebrates high budget utilization while quality silently collapses. Budget monitoring without quality monitoring is like measuring engine RPM without checking if the car is moving forward.

- **[F004] Budget Hoarding** — Over-allocating budgets "just in case," resulting in system-wide underutilization. When every task requests 3x its actual need, the system's effective parallelism drops because the scheduler believes resources are scarce. This is the attention equivalent of memory leaks — allocated but unused capacity that blocks other work.

- **[F005] Post-Hoc Budgeting** — Adding budget specifications after tasks are already designed and running, rather than using budgets to inform task decomposition from the start. Budgets should drive design decisions (how to split tasks, what to filter), not merely annotate existing designs.

---

## Failure Catalog

Real examples drawn from production multi-agent system execution history.

| ID | Failure | Root Cause | Detection Point | Impact |
|----|---------|-----------|-----------------|--------|
| FC-01 | Agent produced 12,000-line report when 500 lines were requested | No output budget specified; agent expanded to fill available context | Output exceeded 20x the expected size | 4 hours of human review wasted; downstream agents choked on oversized input |
| FC-02 | Quality of code review degraded sharply after reviewing file #7 of 12 | All 12 files loaded into context simultaneously; budget for entire review not decomposed per file | Quality metrics dropped 60% in files 8–12 compared to files 1–3 | Critical bugs in later files went undetected |
| FC-03 | Task completed using only 8% of allocated budget, but output was superficial | Budget set to "maximum available" rather than complexity-appropriate level; no minimum quality threshold | Output lacked depth despite available capacity | Rework required; 2x total cost |
| FC-04 | Parallel agents all requested maximum budget, causing sequential execution | Scheduler could not run 4 agents in parallel because each claimed 200K tokens | System throughput dropped to 25% of capacity | 3x wall-clock time for task completion |
| FC-05 | Agent hallucinated references in final section of a long document | Context window exceeded effective attention at ~80K tokens; no checkpoint triggered | Factual accuracy audit found 7 fabricated citations in the last 3 pages | Published document required emergency retraction |

---

## Interaction Catalog

How Attention Budget interacts with other CQE patterns.

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **Context Gate** | requires | Budget is meaningless if context is contaminated with irrelevant information. Context Gate filters what enters the attention window; Budget constrains how much total attention is available. Apply both together. |
| **Wave Scheduler** | enables | Budget determines wave capacity — how many tasks can run in parallel within total available attention. Wave sizing without budget awareness leads to either underutilization or overflow. |
| **File-Based I/O** | complements | File boundaries create natural budget checkpoints. Each file read/write is a measurable attention expenditure. File-based architectures make budget tracking easier than in-memory communication. |
| **Cognitive Profile** | informs | Different cognitive profiles (personas) have different budget requirements. An analytical profile needs more context than a formatting profile. Budget should be profile-aware. |
| **Experience Distillation** | feeds | Historical budget consumption data (which tasks exceeded budget, which underutilized) feeds back into better budget estimation for future tasks. |
| **Assumption Mutation** | constrains | Mutation testing consumes additional budget by design (generating adversarial variants). Budget must account for the mutation overhead explicitly, or mutation steps get silently skipped. |
| **Template-Driven Role** | structures | Templates can embed default budget ranges for specific role types, providing budget guidance as part of role definition. |

---

## Known Uses

### 1. Production Multi-Agent Development System

A hierarchical multi-agent system managing parallel software development tasks. Each task in the work queue includes an explicit `attention_budget` field specifying maximum context tokens. The system's task decomposer uses complexity analysis to set budgets proportional to task difficulty, and the scheduler uses budget declarations to determine how many agents can run in parallel.

**Outcome**: After introducing explicit budgets, the system saw a measurable reduction in "silent quality degradation" incidents — tasks that completed but produced substandard output.

### 2. Document Processing Pipeline

An automated document analysis pipeline where each stage (extraction, analysis, summarization, quality check) receives a stage-specific budget. When the extraction stage discovers a document is larger than expected, it triggers `checkpoint_and_spawn` to split processing rather than exceeding its budget.

### 3. Multi-File Code Review System

A code review system that reviews files individually rather than loading all files into a single context. Each file receives a budget proportional to its size and complexity (measured by cyclomatic complexity and change density). Files exceeding budget trigger a human escalation flag.

---

## Implementation Guidance

### Step 1: Audit Current Context Usage

Before introducing budgets, measure current attention consumption:

```bash
# Scan task definitions for existing budget specifications
grep -r "budget\|max_tokens\|token_limit\|context_size" config/ tasks/

# If no results, every task is running with implicit unlimited budgets
```

### Step 2: Add Budget Fields to Task Definitions

```yaml
# Before: Implicit unlimited budget
task:
  name: "Review pull request"
  description: "Review all changed files"

# After: Explicit attention budget
task:
  name: "Review pull request"
  description: "Review all changed files"
  attention_budget:
    max_context_tokens: 80000
    max_output_tokens: 5000
    overflow_strategy: "checkpoint_and_spawn"
    quality_checkpoint_at: 0.7
  complexity: high
```

### Step 3: Implement Budget Monitoring

Track budget consumption at execution time:

```yaml
# Budget consumption report (generated per task)
budget_report:
  task: "Review pull request"
  allocated: 80000
  consumed: 62000
  utilization: 0.775
  quality_score: 0.88
  overflow_triggered: false
  notes: "Quality checkpoint at 70% passed. Output within expected parameters."
```

### Step 4: Calibrate Budget Sizes

Use historical execution data to refine budget estimates:

1. Run 10+ tasks with generous budgets and record actual consumption.
2. Compute mean and standard deviation per task complexity class.
3. Set budgets to `mean + 1.5σ` as initial targets.
4. Adjust based on overflow frequency — target < 5% overflow rate.

### Step 5: Connect to Wave Scheduler

Once budgets are calibrated, feed them into wave scheduling:

```yaml
wave_config:
  total_budget: 200000          # Total attention available per wave
  tasks:
    - name: "Task A"
      budget: 50000             # Can run in parallel
    - name: "Task B"
      budget: 80000             # Can run in parallel (total: 130K < 200K)
    - name: "Task C"
      budget: 90000             # Must wait for next wave (130K + 90K > 200K)
```

---

## Evidence

- **Level B**: Confirmed across 100+ task executions in a production multi-agent system. Tasks with explicit budgets showed significantly fewer "silent degradation" incidents compared to tasks running with implicit unlimited budgets. The most dramatic improvement was in multi-file analysis tasks, where per-file budgeting reduced quality variance by an estimated 60% across the file set.

- **Specific observations**:
  - Tasks exceeding ~80K tokens of accumulated context showed measurable quality drops in output coherence and factual accuracy.
  - Complexity-proportional budgets reduced both overallocation (budget hoarding) and underallocation (quality crashes).
  - The `quality_checkpoint_at: 0.7` threshold proved effective — catching degradation before it became unrecoverable while minimizing false alarms.

- **Upgrade path to Level A**: Run controlled A/B experiments comparing budget-managed vs. unmanaged task execution across 200+ tasks, measuring output quality via automated scoring (factual accuracy, completeness, coherence) and human review. Publish quantitative results with statistical significance testing.
