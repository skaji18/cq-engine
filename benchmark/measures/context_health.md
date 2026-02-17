# Axis 1: Context Health Score

> **Purpose**: Measure the quality of information flowing through LLM agents.
> **CQE Pattern Link**: Attention Budget (#01), Context Gate (#02)
> **Effort**: M

---

## 1. Definition

Context Health measures how well an agent system manages the information fed to LLM agents. High context health means agents receive relevant, uncontaminated, fresh information. Low context health means agents are drowning in irrelevant data, stale references, or cross-contaminated context from unrelated tasks.

**Why it matters**: LLM attention is finite. Every irrelevant token in the context window displaces a relevant one. Context Health directly predicts whether the agent can produce quality output — garbage in, garbage out.

---

## 2. Sub-Metrics

### 2.1 Information Density (CH-1)

**Definition**: Ratio of task-relevant tokens to total tokens in the agent's context window.

**Formula**:

```
InformationDensity = relevant_tokens / total_tokens
```

Where:
- `relevant_tokens`: Tokens that directly contribute to the current task (determined by semantic overlap with task description keywords)
- `total_tokens`: Total tokens in the agent's context window at execution time

**Normalization**: Already in [0.0, 1.0] range.

**Measurement Method**:
1. Capture the full context window content at agent execution time
2. Extract task description keywords (top-N TF-IDF terms from the task definition)
3. For each sentence in the context, compute semantic similarity to task keywords
4. Sentences with similarity > threshold (default: 0.3) are classified as "relevant"
5. Sum relevant sentence tokens / total tokens

**Edge Cases**:
- Empty context: InformationDensity = 0.0 (no information at all is not healthy)
- All-relevant context: InformationDensity = 1.0 (ideal, but rare in practice)
- Very short context (< 100 tokens): Flag as "insufficient context" rather than high density

**Worked Example**:

```
Task: "Review the authentication module for security vulnerabilities"
Context window (500 tokens):
  - Auth module source code (300 tokens) → relevant
  - Database schema for user table (80 tokens) → relevant
  - Marketing roadmap notes (100 tokens) → irrelevant
  - Build system configuration (20 tokens) → irrelevant

InformationDensity = (300 + 80) / 500 = 380 / 500 = 0.76
```

**Baseline Target**: Measure on 10 representative task executions. Expected naive baseline: 0.4-0.6 (typical agent systems pass too much context).

---

### 2.2 Contamination Level (CH-2)

**Definition**: Proportion of context that originated from unrelated prior tasks or agent stages.

**Formula**:

```
ContaminationLevel_raw = unrelated_tokens / total_tokens
ContaminationScore = 1.0 - ContaminationLevel_raw
```

Where:
- `unrelated_tokens`: Tokens in the current context that belong to a different task/stage and were not explicitly passed through a Context Gate
- The score is inverted so that 1.0 = no contamination (healthy)

**Normalization**: Inverted to [0.0, 1.0] where 1.0 = best.

**Measurement Method**:
1. Track context provenance: tag each context chunk with its origin (task_id, stage_id)
2. For the current task, identify chunks whose origin does not match the current task
3. Among those, exclude chunks that were explicitly passed through a gate (intentional cross-task reference)
4. Remaining untagged/unrelated chunks are "contamination"
5. Compute ratio

**Edge Cases**:
- No provenance tracking available: ContaminationScore = null (unmeasurable, not 1.0)
- Intentional cross-task reference: Not counted as contamination if passed through a gate
- First task in a session: ContaminationScore = 1.0 (no prior tasks to contaminate)

**Worked Example**:

```
Task: task_003 (code review)
Context window (1000 tokens):
  - task_003 code diff (600 tokens) → current task, not contamination
  - task_003 review guidelines (150 tokens) → current task, not contamination
  - task_001 summary (100 tokens) → gated cross-reference, not contamination
  - task_002 debug logs (150 tokens) → NO gate, contamination

ContaminationLevel_raw = 150 / 1000 = 0.15
ContaminationScore = 1.0 - 0.15 = 0.85
```

**Baseline Target**: Measure on 10 executions with/without Context Gate. Expected naive baseline (no gate): 0.5-0.7. Expected with gate: 0.85-0.95.

---

### 2.3 Freshness (CH-3)

**Definition**: How current the information in context is, relative to the task's requirements.

**Formula**:

```
Freshness = 1.0 - weighted_avg(staleness_i)

staleness_i = min(1.0, (current_time - info_timestamp_i) / task_lifetime)
```

Where:
- `info_timestamp_i`: When information chunk `i` was last updated
- `current_time`: When the agent executes the task
- `task_lifetime`: Expected duration of the task or project (normalization factor)
- `staleness_i`: Per-chunk staleness, capped at 1.0
- Weighted average uses importance weights (task-critical info weighted higher)

**Normalization**: [0.0, 1.0] where 1.0 = all information is fresh.

**Measurement Method**:
1. For each information chunk in context, determine its last-modified timestamp
2. Compute staleness for each chunk relative to current time
3. Assign importance weights (critical files = 1.0, reference files = 0.5, boilerplate = 0.1)
4. Compute weighted average staleness
5. Freshness = 1.0 - weighted_avg_staleness

**Edge Cases**:
- No timestamps available: Freshness = null (unmeasurable)
- Real-time data (age = 0): staleness = 0.0, Freshness contribution = 1.0
- Very old reference material (e.g., language spec): Weight as low-importance, not as "stale"

**Worked Example**:

```
Task lifetime: 7 days
Current time: Day 7

Context chunks:
  - Source code (modified Day 6, importance 1.0)
    staleness = (7-6)/7 = 0.14
  - Requirements doc (modified Day 1, importance 0.8)
    staleness = (7-1)/7 = 0.86
  - API reference (modified Day 5, importance 0.5)
    staleness = (7-5)/7 = 0.29

weighted_avg_staleness = (0.14*1.0 + 0.86*0.8 + 0.29*0.5) / (1.0 + 0.8 + 0.5)
                       = (0.14 + 0.688 + 0.145) / 2.3
                       = 0.973 / 2.3
                       = 0.423

Freshness = 1.0 - 0.423 = 0.577
```

**Baseline Target**: Measure staleness across 10 multi-step tasks. Expected naive baseline: 0.5-0.7.

---

## 3. Axis Score Aggregation

```
ContextHealthScore = w1 * InformationDensity + w2 * ContaminationScore + w3 * Freshness
```

**Default weights**: w1 = 0.40, w2 = 0.35, w3 = 0.25

**Weight rationale**:
- Information Density (0.40): Most directly impacts agent output quality
- Contamination Level (0.35): Cross-contamination causes unpredictable failures
- Freshness (0.25): Staleness is less immediately harmful than irrelevance or contamination

---

## 4. CQE Pattern Correspondence

| CQE Pattern | Context Health Impact | Sub-Metric Affected |
|-------------|----------------------|---------------------|
| **#01 Attention Budget** | Budget enforcement prevents context overflow | CH-1 Information Density |
| **#02 Context Gate** | Filtering prevents cross-task contamination | CH-2 Contamination Level |
| **#07 File-Based I/O** | File boundaries provide natural context partitioning | CH-1, CH-2 |
| **#04 Wave Scheduler** | Wave boundaries limit temporal contamination | CH-2, CH-3 |

---

## 5. Baseline Measurement Plan

| Step | Action | Sample Size | Data Source |
|------|--------|-------------|-------------|
| 1 | Select representative tasks | 10 tasks | Agent execution logs |
| 2 | Capture context windows at execution time | 10 snapshots | Agent runtime instrumentation |
| 3 | Compute CH-1 (Information Density) for each | 10 values | Semantic similarity analysis |
| 4 | Compute CH-2 (Contamination Level) for each | 10 values | Provenance tracking |
| 5 | Compute CH-3 (Freshness) for each | 10 values | Timestamp analysis |
| 6 | Compute axis scores and statistics | Mean, SD | Aggregation formula |
| 7 | Record as baseline | 1 record | `baseline_context_health.json` |
