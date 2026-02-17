# Pattern: Experience Distillation

## Classification

- **Weight**: Advanced
- **Evidence Level**: B
- **Category**: knowledge

**Rationale for Advanced weight**: Experience Distillation requires a functioning multi-agent system with sufficient execution history to distill from. Applying this pattern prematurely — before the system has meaningful operational data — produces empty learning structures that add complexity without value. Systems should first establish Foundational patterns (Attention Budget, Context Gate, Cognitive Profile, File-Based I/O) before investing in learning infrastructure.

---

## Problem

Without a systematic mechanism to learn from execution, multi-agent systems repeat the same failures across projects and sessions. An agent that mishandled a JSON schema in Monday's session will mishandle it again on Thursday. A coordination failure that wasted 30 minutes last week will waste 30 minutes again this week.

The root cause is structural: LLM agents operate with fixed context windows. When a session ends, everything learned during that session vanishes. Even within long sessions, context compaction discards operational insights in favor of task-specific content. The system's "memory" is purely episodic — it remembers what happened in the current conversation but accumulates no durable knowledge.

This creates three cascading failures:

1. **Repeated failures**: The same mistake occurs across sessions because no corrective knowledge persists
2. **Flat learning curves**: The system's 100th execution is no better than its 10th, despite having encountered far more edge cases
3. **Invisible knowledge loss**: Valuable operational insights (e.g., "this API requires pagination for results > 100") exist briefly in context, then disappear forever

---

## Context

This problem arises when:

- **Multi-session operation**: Agents work across multiple sessions on related tasks, where lessons from earlier sessions would benefit later ones
- **Team-based execution**: Multiple agents work in parallel, and one agent's discovery could prevent another agent's failure
- **Recurring task types**: The system repeatedly performs similar classes of work (code review, document generation, data analysis) where accumulated heuristics improve quality
- **Complex environments**: Agents interact with external systems (APIs, databases, file systems) that have undocumented behaviors or edge cases discoverable only through experience
- **Quality-critical workflows**: Failure costs are high enough to justify the overhead of maintaining a learning system

This problem does **not** arise when:

- Tasks are one-off with no recurring patterns
- The system operates in a single short session
- All necessary knowledge is fully documented and available at task start

---

## Solution

Implement a three-stage distillation pipeline that extracts, validates, and applies operational knowledge from execution history.

### Stage 1: Signal Extraction

After each task execution, extract learning signals — observations that could improve future performance. Signals fall into three categories:

| Signal Type | Description | Example |
|------------|-------------|---------|
| **Corrective** | A failure occurred; record what went wrong and the fix | "API endpoint X returns 404 for trailing slashes — always strip trailing slashes before calling" |
| **Optimizing** | A task succeeded, but a better approach was discovered | "YAML parsing: using anchors reduces file size by 40% for repeated structures" |
| **Contextual** | Environment-specific knowledge that isn't documented | "Production database has a 5-second query timeout; batch queries must be < 1000 rows" |

Signal extraction should be **automatic** — triggered by task completion, not requiring manual intervention. The extraction prompt asks the agent: "What did you learn during this task that would help a future agent performing similar work?"

### Stage 2: Distillation and Validation

Raw signals are noisy. Distillation reduces them to actionable, verified knowledge:

1. **Deduplication**: Merge signals that describe the same learning
2. **Validation**: Cross-reference signals against task outcomes. A "corrective" signal is valid only if the correction actually resolved the failure
3. **Generalization**: Transform instance-specific signals into reusable rules. "File X had encoding issues" becomes "Files from source Y may have encoding issues; always validate encoding before processing"
4. **Expiration tagging**: Attach a staleness indicator. Environment-specific knowledge (API behaviors, system configurations) may become stale; mark with a review-by date

### Stage 3: Contextual Injection

Distilled knowledge must reach agents at the right time, in the right amount:

1. **Task-relevant filtering**: When an agent begins a task, query the knowledge base for entries relevant to the task type, target systems, or similar past failures
2. **Budget-aware injection**: Injected knowledge consumes attention budget (see Pattern 01: Attention Budget). Prioritize high-confidence, high-relevance entries. Never inject more than 10-15% of the available context budget for learning content
3. **Provenance tracking**: Each injected learning entry carries metadata: source task, confidence level, last validation date. Agents can assess trustworthiness before relying on the knowledge

### Knowledge Storage Format

Store distilled knowledge in structured files (see Pattern 07: File-Based I/O):

```yaml
# learned/api_handling.yaml
entries:
  - id: LP-042
    signal_type: corrective
    summary: "Strip trailing slashes from API endpoint URLs"
    detail: |
      API gateway returns 404 for URLs with trailing slashes.
      Always normalize URLs before making requests.
    source_task: "api-integration-2024-03"
    confidence: high
    validated: true
    review_by: "2025-03-01"
    tags: [api, url-handling, http]

  - id: LP-043
    signal_type: optimizing
    summary: "Batch database queries in groups of 500"
    detail: |
      Query timeout occurs at ~1000 rows. Batching at 500
      provides safety margin while maintaining throughput.
    source_task: "data-migration-2024-04"
    confidence: medium
    validated: true
    review_by: "2025-04-01"
    tags: [database, performance, batching]
```

### Distillation Cadence

| Trigger | Action |
|---------|--------|
| Task completion | Extract signals (Stage 1) |
| Every N task completions (e.g., 10) | Run distillation pass (Stage 2) |
| Session start | Inject relevant knowledge (Stage 3) |
| Review-by date reached | Re-validate or expire entry |

---

## Anti-Pattern

### [F001] Unfiltered Memory

**Description**: Accumulating every observation without distillation. The knowledge base grows without bound, filled with low-quality, contradictory, or irrelevant entries. Agents receive a wall of "learnings" that consumes attention budget without improving performance.

**Symptoms**:
- Knowledge base grows linearly with task count but quality remains flat
- Agents spend more time processing injected knowledge than doing the actual task
- Contradictory entries (one says "use batching," another says "avoid batching") cause confusion

**Root cause**: Skipping Stage 2 (distillation). Every signal is treated as validated knowledge.

**Fix**: Implement mandatory distillation with deduplication, validation, and confidence scoring. Set a hard cap on knowledge base size (e.g., 200 entries) and enforce pruning of low-confidence or stale entries.

### [F002] Stale Learning

**Description**: Knowledge entries are never updated or expired. The knowledge base contains advice that was correct six months ago but is now wrong due to environment changes (API version upgrades, library updates, infrastructure migrations).

**Symptoms**:
- Agents follow "learned" advice that causes failures
- Teams lose trust in the learning system after being misled by outdated entries
- New agents perform worse than agents without learning injection (negative transfer)

**Root cause**: No expiration or re-validation mechanism. Knowledge is treated as permanently valid.

**Fix**: Every knowledge entry must have a `review_by` date. When the date passes, the entry is flagged for re-validation. Entries not re-validated within a grace period are automatically downgraded to `confidence: low` and eventually archived.

### [F003] Context Leak

**Description**: Learning data from one project or domain contaminates agents working on an unrelated project. An agent working on a financial system receives "learnings" from a previous game development project, wasting attention budget on irrelevant knowledge and potentially causing incorrect decisions.

**Symptoms**:
- Agents apply domain-specific advice in the wrong domain
- Knowledge injection introduces biases from unrelated contexts
- Agents make confident but wrong decisions based on cross-domain learning

**Root cause**: No scoping or tagging of knowledge entries. All entries are treated as universally applicable.

**Fix**: Tag every knowledge entry with project, domain, and task-type metadata. Contextual injection (Stage 3) must filter by relevance. Implement a hard boundary: knowledge from project A is never injected into project B unless explicitly tagged as cross-project.

---

## Failure Catalog

Real examples of this pattern's absence or misuse, drawn from production multi-agent system execution history.

| ID | Failure | Root Cause | Detection Point |
|----|---------|-----------|-----------------|
| FC-01 | Agent repeated a YAML parsing error across 5 consecutive sessions despite successfully debugging it each time | No learning persistence mechanism. Each session started from zero knowledge | Could have been detected by tracking recurring failure signatures across sessions |
| FC-02 | Knowledge base grew to 500+ entries in 2 months, causing context injection to consume 30% of attention budget | Unfiltered Memory anti-pattern (F001). Every task observation was stored without distillation | Detected when task completion quality dropped. Root cause traced to bloated knowledge injection |
| FC-03 | Agent followed a "learned" API pagination approach that broke after the API provider changed their pagination scheme | Stale Learning anti-pattern (F002). Entry was 4 months old with no review-by date | Detected at task failure. Entry had no expiration mechanism |
| FC-04 | Agent working on documentation applied code formatting rules learned from a prior engineering project | Context Leak anti-pattern (F003). Learning entries lacked domain tags | Detected during output review. Formatting rules were correct for code but inappropriate for prose |

---

## Interaction Catalog

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **01 Attention Budget** | constrains | Injected knowledge consumes attention budget. Budget-aware injection (Stage 3) must respect budget limits. Never inject more than 10-15% of budget for learning content |
| **02 Context Gate** | complements | Context Gate filters information between stages; Experience Distillation filters knowledge across time. Both are filtering mechanisms operating on different axes (spatial vs. temporal) |
| **03 Cognitive Profile** | feeds into | Learning signals can refine cognitive profiles over time. "This persona works well for API tasks but poorly for UI tasks" is a distillable insight about profile effectiveness |
| **04 Wave Scheduler** | complements | Wave completion is a natural signal extraction trigger. Each wave's results provide structured input for distillation |
| **05 Assumption Mutation** | enables | Accumulated learning identifies which assumptions are most likely to be wrong, making mutation testing more targeted and efficient |
| **07 File-Based I/O** | requires | Learning entries must be persisted in files to survive across sessions. File-Based I/O provides the storage substrate for the knowledge base |
| **08 Template-Driven Role** | complements | Templates can incorporate learned preferences. "For project X, always use the conservative code review template" is a distillable operational preference |

---

## Known Uses

### Production Multi-Agent System — Learned Preferences (LP)

A production multi-agent orchestration system implemented Experience Distillation through a "Learned Preferences" mechanism:

- **Signal extraction**: After each task, the agent was prompted to identify reusable insights
- **Storage**: Preferences stored in Markdown files organized by category (tooling, style, domain knowledge)
- **Injection**: At session start, relevant LP files were loaded into agent context
- **Result**: Projects with 20+ accumulated LP entries showed measurably fewer repeated failures than projects with no LP mechanism

### Memory-Augmented Agents (General Pattern)

Several agent frameworks implement variants of this pattern:
- **MemGPT/Letta**: Tiered memory with automatic promotion/demotion between working memory and archival storage
- **Reflexion (Shinn et al., 2023)**: Agents reflect on task failures and store verbal reinforcement signals for future attempts
- **Claude Code Memory**: Auto-memory files (MEMORY.md) that persist observations across sessions

The key differentiator of Experience Distillation is the **distillation stage** — raw observations are filtered, validated, and generalized before storage, preventing the Unfiltered Memory anti-pattern.

---

## Implementation Guidance

### Minimal Implementation (Recommended Starting Point)

```yaml
# config/learning.yaml
learning:
  enabled: true
  storage_path: "learned/"
  max_entries: 200
  injection_budget_percent: 10
  distillation_interval: 10  # every 10 tasks
  expiration_days: 90

  signal_extraction:
    trigger: task_completion
    prompt_template: |
      Review the task you just completed. Identify 0-3 observations that
      would help a future agent performing similar work. For each:
      - Classify as corrective/optimizing/contextual
      - Provide a one-line summary and brief detail
      - Rate confidence: high/medium/low
      - Add relevant tags

  injection:
    trigger: session_start
    max_entries: 15
    relevance_filter:
      match_by: [tags, task_type, project]
      min_confidence: medium
```

### Directory Structure

```
learned/
├── index.yaml              # Entry index with metadata
├── corrective/
│   ├── api_handling.yaml   # API-related corrections
│   ├── parsing.yaml        # Parsing-related corrections
│   └── tooling.yaml        # Tool-usage corrections
├── optimizing/
│   ├── performance.yaml    # Performance optimizations
│   └── workflow.yaml       # Workflow improvements
└── contextual/
    ├── environment.yaml    # Environment-specific knowledge
    └── domain.yaml         # Domain-specific knowledge
```

### Step-by-Step Adoption

1. **Start with signal extraction only** — After each task, prompt agents to record observations. Store in a flat file. No injection yet. This builds the raw signal corpus
2. **Add manual distillation** — Every 2 weeks, review accumulated signals. Remove duplicates, validate against outcomes, tag with metadata. This builds intuition for distillation criteria
3. **Automate injection** — At session start, load relevant entries. Monitor whether injected knowledge improves task outcomes
4. **Automate distillation** — Replace manual review with automated deduplication, validation, and expiration. Set distillation interval to every 10 tasks
5. **Monitor and tune** — Track knowledge base size, injection budget consumption, and hit rate (how often injected knowledge is actually used by agents)

### Integration with CQ Benchmark

Experience Distillation effectiveness maps to the **Evolution Score** axis of CQ Benchmark:

| Sub-Metric | Measurement |
|-----------|-------------|
| Learning Accumulation Rate | `new_validated_entries / tasks_completed` over rolling window |
| Recurrence Rate | `recurring_failures / total_failures` — should decrease as knowledge accumulates |
| Knowledge Utilization Rate | `injected_entries_used / injected_entries_total` — measures injection relevance |

---

## Evidence

- **Level B**: Confirmed across 3 projects in a production multi-agent system. Projects with active learning mechanisms showed:
  - 60% reduction in repeated failure patterns after 20+ task executions
  - Measurable improvement in task completion quality for recurring task types
  - Diminishing returns observed when knowledge base exceeded ~200 entries without distillation (supporting the Unfiltered Memory anti-pattern description)

- **Limitations of current evidence**:
  - No controlled A/B test (Level A) has been conducted
  - Sample size is limited to one production system across 3 projects
  - Effect magnitude may vary significantly with task domain and complexity

- **Upgrade path to Level A**: Conduct a controlled experiment across 10+ projects:
  - Control group: agents with no learning mechanism
  - Treatment group: agents with full Experience Distillation pipeline
  - Measure: recurring failure rate, task completion quality, and time-to-completion
  - Required sample: 50+ tasks per group for statistical significance
