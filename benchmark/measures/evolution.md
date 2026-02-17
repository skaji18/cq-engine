# Axis 4: Evolution Score

> **Purpose**: Measure the system's ability to learn and improve over time.
> **CQE Pattern Link**: Experience Distillation (#06), File-Based I/O (#07)
> **Effort**: S

---

## 1. Definition

Evolution measures whether an agent system gets better over time. High evolution means the system systematically captures learning, applies it to future tasks, and avoids repeating past failures. Low evolution means the system treats every execution as if it were the first — no memory, no improvement, no adaptation.

**Why it matters**: A one-shot system that performs well on a single task is valuable. A system that improves with every execution is transformative. Evolution is the long-term multiplier for all other CQ axes — even moderate Context Health and Decision Quality become excellent over time if the system learns from experience.

---

## 2. Sub-Metrics

### 2.1 Pattern Conformance (EV-1)

**Definition**: Proportion of agent configurations that comply with CQE Patterns, as measured by cqlint.

**Formula**:

```
PatternConformance = passing_rules / total_applicable_rules
```

Where:
- `passing_rules`: Number of cqlint rules that the configuration satisfies
- `total_applicable_rules`: Number of cqlint rules applicable to this configuration (some rules may not apply depending on system architecture)

**Normalization**: Already in [0.0, 1.0] range.

**Measurement Method**:
1. Run `cqlint check <project_path>` on the agent configuration
2. Count total rules checked and total rules passed
3. Compute ratio

**Rule Applicability**:

| Rule | When Applicable |
|------|-----------------|
| CQ001 (attention-budget-missing) | Always — all tasks should have budgets |
| CQ002 (context-contamination-risk) | Multi-stage pipelines only |
| CQ003 (generic-persona) | Agent definitions with persona fields |
| CQ004 (no-mutation-critical) | Tasks with danger_level: high/critical |
| CQ005 (learning-disabled) | Project-level check (once per project) |

**Edge Cases**:
- No cqlint rules applicable: PatternConformance = 1.0 (trivially compliant)
- cqlint not installed: PatternConformance = null (unmeasurable)
- New rules added: Re-baseline after rule additions

**Worked Example**:

```
$ cqlint check my-agent-project/
CQ001: PASS — attention_budget defined in 3/3 tasks
CQ002: PASS — context gates present between all stages
CQ003: WARNING — agent "helper" has generic persona
CQ004: PASS — high-risk task has mutation step
CQ005: WARNING — no learning directory found

Applicable rules: 5
Passing rules: 3
PatternConformance = 3 / 5 = 0.60
```

**Baseline Target**: Run cqlint on project before CQE adoption. Expected naive baseline: 0.1-0.3 (most projects don't follow CQE patterns initially).

---

### 2.2 Learning Accumulation Rate (EV-2)

**Definition**: Rate at which actionable learning is extracted from task executions, measured over a rolling window.

**Formula**:

```
LearningAccumulationRate = new_learnings / tasks_completed

Normalized: LearningAccumulationRate_norm = min(1.0, LearningAccumulationRate / target_rate)
```

Where:
- `new_learnings`: Number of new, actionable learning entries added to the knowledge base during the measurement window
- `tasks_completed`: Number of tasks completed in the same window
- `target_rate`: Expected learning rate (default: 0.3 learnings per task — not every task produces new learning)

**Learning Quality Criteria** — a learning entry counts as "actionable" if it:
1. Describes a specific failure or success pattern (not generic)
2. Includes a concrete recommendation (not vague)
3. Is applicable to future tasks (not one-off)

**Measurement Method**:
1. Define measurement window (e.g., last 20 tasks)
2. Count tasks completed in the window
3. Count new learning entries added in the window
4. Filter learnings by quality criteria (remove duplicates, generic entries)
5. Compute rate and normalize

**Edge Cases**:
- No learning mechanism: LearningAccumulationRate = 0.0 (system cannot learn)
- Very high rate (> 1.0 learning per task): Cap at 1.0 — may indicate noisy/low-quality learnings
- Early stage (< 5 tasks): Insufficient data for meaningful rate; report as provisional

**Worked Example**:

```
Measurement window: Last 20 tasks

Tasks completed: 20
Learning entries added: 8
  L1: "YAML anchors cause cqlint false positives" → Actionable ✓
  L2: "Large files should be split before review" → Actionable ✓
  L3: "Something went wrong" → NOT actionable (too vague) ✗
  L4: "Context Gate reduces error rate by ~30%" → Actionable ✓
  L5: "Never use sudo in scripts" → Actionable ✓
  L6: "Review all PRs" → NOT actionable (too generic) ✗
  L7: "Wave size >5 causes queue contention" → Actionable ✓
  L8: "Embed personas in separate files" → Actionable ✓

Actionable learnings: 6
LearningAccumulationRate = 6 / 20 = 0.30
LearningAccumulationRate_norm = min(1.0, 0.30 / 0.30) = 1.0
```

**Baseline Target**: Measure on 20 task executions. Expected naive baseline (no learning system): 0.0. Expected with Experience Distillation: 0.5-0.8.

---

### 2.3 Recurrence Rate (EV-3)

**Definition**: Proportion of failures that repeat a previously-encountered failure mode, inverted to a quality score.

**Formula**:

```
RecurrenceRate_raw = recurring_failures / total_failures
RecurrenceScore = 1.0 - RecurrenceRate_raw
```

Where:
- `recurring_failures`: Failures whose root cause matches a previously-documented failure mode (fingerprint match)
- `total_failures`: All failures in the measurement window
- Score is inverted so that 1.0 = no recurring failures (healthy)

**Failure Fingerprinting**:

A failure fingerprint consists of:
- **Category**: The type of failure (e.g., context overflow, persona drift, gate bypass)
- **Root Cause**: The underlying reason (e.g., budget not set, filter too permissive)
- **Detection Point**: Where in the pipeline the failure was detected

Two failures match if their category AND root cause match (detection point may differ).

**Measurement Method**:
1. Collect all failures from the measurement window (minimum 10 failures for statistical relevance)
2. For each failure, extract its fingerprint (category + root cause)
3. Check if the fingerprint matches any previously-documented failure
4. A match means the system failed to learn from a prior occurrence
5. Compute recurrence rate and invert

**Edge Cases**:
- No failures in window: RecurrenceScore = 1.0 (no failures = no recurrence, but flag as "insufficient failure data")
- All failures are novel: RecurrenceScore = 1.0 (system hasn't seen these before)
- Very few failures (< 3): Report as provisional — sample too small for meaningful rate

**Worked Example**:

```
Measurement window: Last 50 task executions

Total failures: 8
  F1: Context overflow in task decomposition → First occurrence
  F2: Generic persona caused low-quality output → Recurring (seen in execution #12)
  F3: Missing gate between stages → First occurrence
  F4: Budget exceeded without warning → Recurring (seen in execution #23)
  F5: Stale reference data → First occurrence
  F6: Missing gate between stages → Recurring (same as F3's root cause from execution #31)
  F7: Persona drift mid-task → First occurrence
  F8: Budget exceeded without warning → Recurring (same as F4)

Recurring failures: 3 (F2, F4, F8)  [F6 is recurring relative to F3 within window]
Wait — F6 recurs F3 which is in the same window. Recurrence = matches a PREVIOUSLY documented failure.
If F3 is the first occurrence in this window but was seen before (e.g., in prior window): F6 is recurring.
If F3 is truly novel: F6 is a within-window repeat, still counts as recurrence.

Recurring: F2, F4, F6, F8 = 4
RecurrenceRate_raw = 4 / 8 = 0.50
RecurrenceScore = 1.0 - 0.50 = 0.50
```

**Baseline Target**: Analyze 50 execution logs. Expected naive baseline (no learning): 0.3-0.5. Expected with Experience Distillation: 0.7-0.9.

---

## 3. Axis Score Aggregation

```
EvolutionScore = w1 * PatternConformance + w2 * LearningAccumulationRate_norm + w3 * RecurrenceScore
```

**Default weights**: w1 = 0.30, w2 = 0.30, w3 = 0.40

**Weight rationale**:
- Pattern Conformance (0.30): Measures adherence to known best practices
- Learning Accumulation Rate (0.30): Measures whether the system captures new knowledge
- Recurrence Rate (0.40): Highest weight because recurring failures are the clearest sign of failed evolution — the system had the information to prevent the failure but didn't use it

---

## 4. CQE Pattern Correspondence

| CQE Pattern | Evolution Impact | Sub-Metric Affected |
|-------------|-----------------|---------------------|
| **#06 Experience Distillation** | Core pattern — drives learning accumulation and failure prevention | EV-2 Learning Accumulation Rate, EV-3 Recurrence Rate |
| **#07 File-Based I/O** | Persistent storage enables learning retention across sessions | EV-2 Learning Accumulation Rate |
| **All Patterns** | Pattern adoption is directly measured by cqlint | EV-1 Pattern Conformance |
| **#01 Attention Budget** | Budget awareness prevents attention-related failure recurrence | EV-3 Recurrence Rate |
| **#02 Context Gate** | Gate configuration improvements reduce contamination recurrence | EV-3 Recurrence Rate |

---

## 5. Evolution as the Long-Term Multiplier

Evolution is unique among the 4 axes because it amplifies all others over time:

```
Time →
         Without Evolution          With Evolution
         ┌──────────────┐           ┌──────────────────────────┐
CH Score │ ~~~~~~~~~~~~ │           │ ~~~~~~~~~~~~/////////////│
         │   (flat)     │           │   (improving)            │
         └──────────────┘           └──────────────────────────┘

         ┌──────────────┐           ┌──────────────────────────┐
DQ Score │ ~~~~~~~~~~~~ │           │ ~~~~~~~~~~~~/////////////│
         │   (flat)     │           │   (improving)            │
         └──────────────┘           └──────────────────────────┘

         ┌──────────────┐           ┌──────────────────────────┐
DI Score │ ~~~~~~~~~~~~ │           │ ~~~~~~~~~~~~/////////////│
         │   (flat)     │           │   (improving)            │
         └──────────────┘           └──────────────────────────┘
```

A system with mediocre initial scores but high Evolution will eventually surpass a system with high initial scores but no Evolution.

---

## 6. Baseline Measurement Plan

| Step | Action | Sample Size | Data Source |
|------|--------|-------------|-------------|
| 1 | Run cqlint on project configuration | 1 scan | Agent config files |
| 2 | Compute EV-1 (Pattern Conformance) | 1 value | cqlint output |
| 3 | Collect task execution records | 20 tasks | Execution logs |
| 4 | Count and filter learning entries | 20 tasks | Knowledge base / memory files |
| 5 | Compute EV-2 (Learning Accumulation Rate) | 1 value | Learning count / task count |
| 6 | Collect failure records | 50 executions | Failure logs / post-mortems |
| 7 | Fingerprint failures and check recurrence | 50 executions | Fingerprint matching |
| 8 | Compute EV-3 (Recurrence Rate) | 1 value | Recurrence formula |
| 9 | Compute axis score and record baseline | 1 record | Aggregation formula |
