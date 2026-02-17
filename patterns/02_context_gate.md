# Pattern: Context Gate

## Classification

- **Weight**: Foundational
- **Evidence Level**: B — Confirmed across multiple production multi-agent systems
- **Category**: knowledge

Context Gate is a foundational pattern that controls information flow between agent stages. It is the attention-conservation counterpart to Attention Budget — while Budget constrains *how much* attention is available, the Gate controls *what enters* the attention window.

---

## Problem

In multi-agent systems, the default behavior is to pass **all** information from one stage to the next. The output of Agent A becomes the full input of Agent B, which becomes the full input of Agent C, and so on. This creates an **attention contamination cascade**:

1. **Irrelevant context accumulates.** Each stage adds its own output to the growing context, including intermediate reasoning, debug information, and metadata that downstream agents do not need.
2. **Signal-to-noise ratio degrades.** The information that Agent C actually needs from Agent A may be 5% of Agent A's output, but Agent C receives 100% and must waste attention separating signal from noise.
3. **Hallucination amplifies.** When an LLM receives a large context with mixed relevance, it is more likely to confuse irrelevant context fragments with relevant ones, producing outputs that blend unrelated information.
4. **Budget is wasted on filtering.** Without an explicit gate, each downstream agent implicitly performs its own filtering — spending tokens to decide what to ignore rather than focusing on the task.

The result is that the system's effective capacity decreases with each stage, even when the raw token budget appears sufficient. The problem is not insufficient context — it is **unfiltered context**.

---

## Context

This problem arises when:

- A system has **sequential agent stages** where output from one stage feeds into the next.
- Agents have **different information needs** — what is relevant to the code reviewer is different from what is relevant to the test generator.
- The system produces **intermediate artifacts** (reasoning chains, debug logs, draft versions) that are valuable for auditing but harmful for downstream processing.
- **Context windows are shared or constrained** — running on models with limited effective attention, or running multiple tasks in parallel with a shared budget.
- The system handles **sensitive information** that should not propagate beyond its intended stage (security credentials, personal data, internal metadata).

Context Gate is particularly critical in hierarchical multi-agent architectures where commands flow down and reports flow up through multiple layers. Without gates at each layer boundary, the top-level agent receives the accumulated noise of every layer below it.

---

## Solution

Insert an **explicit filtering mechanism** at every boundary between agent stages. The gate examines the output of the upstream agent and produces a filtered, structured summary that contains only what the downstream agent needs.

### Core Principles

1. **Explicit Over Implicit**: Every stage boundary must have a declared gate policy. "Pass everything" is a valid policy, but it must be a conscious choice, not a default.

2. **Receiver-Defined Filtering**: The gate's filter rules are defined by the **downstream** agent's needs, not the upstream agent's output format. Ask "what does the receiver need?" not "what did the sender produce?"

3. **Structured Handoff**: Gate output should follow a defined schema — not free-form text that the receiver must parse. Structured handoffs (YAML, JSON, typed Markdown sections) reduce downstream parsing overhead.

4. **Audit Trail Preservation**: Filtering does not mean deletion. The full unfiltered output is preserved in a file or log for debugging, while only the filtered version enters the downstream context.

5. **Dynamic Gate Adjustment**: Gate rules evolve as the system matures. What was relevant early in a project may become noise later, and vice versa. Gates should be reviewed and updated periodically.

### Gate Specification Format

```yaml
context_gate:
  name: "analysis_to_review"
  upstream: "analysis_agent"
  downstream: "review_agent"
  filter_rules:
    include:
      - "summary"
      - "findings"
      - "risk_assessment"
      - "file_list"
    exclude:
      - "debug_log"
      - "intermediate_reasoning"
      - "raw_data"
    max_tokens: 5000
    format: "structured_yaml"
  audit:
    preserve_full_output: true
    audit_path: "logs/gate_audit/"
```

### Gate Types

| Gate Type | Description | Use Case |
|-----------|------------|----------|
| **Whitelist Gate** | Only pass explicitly listed fields/sections | High-security boundaries, narrow downstream needs |
| **Blacklist Gate** | Pass everything except explicitly excluded items | Broad downstream needs, few known irrelevant fields |
| **Summary Gate** | Generate a compressed summary of upstream output | Large upstream outputs feeding into constrained downstream contexts |
| **Schema Gate** | Transform upstream output into a predefined downstream schema | Cross-format boundaries (e.g., free-text → structured YAML) |
| **Conditional Gate** | Apply different filters based on upstream output content | Variable-complexity tasks where filtering needs vary |

### File-Based Gate Implementation

Files provide natural gate boundaries in systems using file-based communication:

```
upstream_agent/
├── full_output.md          # Complete output (preserved for audit)
├── gate_output.yaml        # Filtered output (this is what downstream reads)
└── gate_manifest.yaml      # What was filtered and why
```

The downstream agent reads **only** `gate_output.yaml`. The full output and manifest exist for debugging and compliance but never enter the downstream context.

---

## Anti-Pattern

What happens when Context Gate is misapplied or omitted:

- **[F001] Gate Bypass** — Routing information around the gate "for efficiency" or "because this one is urgent." Once a single bypass is permitted, the gate's value collapses. Other agents learn that bypasses are possible and begin requesting them routinely. Within weeks, the gate exists in the architecture diagram but not in practice. The root cause is treating the gate as an optimization (skippable when inconvenient) rather than a structural boundary (always enforced).

- **[F002] Over-Filtering** — Removing too much context, causing the downstream agent to produce incomplete or incorrect work because it lacked necessary information. This typically occurs when gate rules are designed by the upstream agent's developer (who knows what their agent produces) rather than the downstream agent's developer (who knows what their agent needs). The receiver's perspective must drive filter design.

- **[F003] Stale Gate** — Gate filter rules that were correct when designed but have not been updated as the system evolved. New fields are added to upstream output but never added to the gate's include list. New downstream requirements emerge but the gate still filters based on the original design. Stale gates silently starve downstream agents of information they now need.

- **[F004] Symmetric Gate** — Applying the same filter in both directions of a bidirectional communication channel. Upward reports (agent → manager) need different filtering than downward commands (manager → agent). Commands need precision and context; reports need brevity and actionability. A symmetric gate optimizes for neither.

- **[F005] Filter-Without-Format** — Filtering the content but not structuring it. A gate that passes the right fields but in free-text format forces the downstream agent to parse and extract, spending attention on structural interpretation rather than substantive reasoning. Filtering and formatting are inseparable gate responsibilities.

---

## Failure Catalog

Real examples drawn from production multi-agent system execution history.

| ID | Failure | Root Cause | Detection Point | Impact |
|----|---------|-----------|-----------------|--------|
| FC-01 | Manager agent received 15,000-token reports from each of 7 workers, exceeding its context window | No gate between worker output and manager input; full reports passed upstream | Manager's responses became incoherent after processing worker #4's report | Manager made incorrect prioritization decisions based on partial comprehension of later reports |
| FC-02 | Worker agent included internal system metadata (task IDs, timestamps, routing info) in its public-facing output | No gate between internal processing and external output; internal identifiers leaked | External reviewer noticed system-internal terminology in published document | Required manual scrubbing of all outputs; delayed delivery by one day |
| FC-03 | Downstream agent produced work that contradicted upstream findings | Gate removed the "caveats" and "limitations" section from upstream output, passing only "findings" | Quality review found downstream conclusions ignored critical qualifications | Rework required; 2x cost |
| FC-04 | Code review agent reviewed files that were not actually changed in the pull request | Full repository file list passed to reviewer without filtering to only changed files | Reviewer spent 80% of its budget reviewing unchanged files | Critical bugs in actually-changed files went undetected due to budget exhaustion |
| FC-05 | Agent communication channel grew to 200K tokens over a 4-hour session | No periodic gate/summarization between turns; full conversation history accumulated | System hit context limit and lost early-session context to truncation | Early task requirements were forgotten; agent produced work inconsistent with original instructions |

---

## Interaction Catalog

How Context Gate interacts with other CQE patterns.

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **Attention Budget** | requires | Gate filtering criteria depend on budget constraints. A gate that passes 50K tokens to an agent with a 20K budget is useless. Gate token limits should be derived from downstream budget allocations. Budget sets the ceiling; Gate ensures only valuable content reaches that ceiling. |
| **File-Based I/O** | complements | Files are natural gate boundaries. The upstream agent writes to a file; the gate reads the file, filters it, and writes a filtered version for the downstream agent. File-based gates are inspectable, auditable, and debuggable — you can read the gate's input and output files to verify correctness. |
| **Cognitive Profile** | informs | Different cognitive profiles need different information. An adversarial reviewer needs the full argument to critique; a summarizer needs only the key points. Gate rules should be profile-aware — the same upstream output should be filtered differently for different downstream profiles. |
| **Wave Scheduler** | structures | Wave boundaries are natural gate points. Between Wave 1 (independent analysis) and Wave 2 (cross-critique), the gate aggregates and structures Wave 1 outputs into a format suitable for cross-referencing. |
| **Template-Driven Role** | enables | Templates can specify what information a role expects to receive, which directly defines the gate's output schema. Template + Gate together ensure that agents receive exactly the information their role requires, in the format their template expects. |
| **Experience Distillation** | protects | Learning data (accumulated experience) should pass through a gate before entering task contexts to prevent context leak — where historical information about unrelated tasks contaminates the current task. |
| **Assumption Mutation** | guides | Mutation results are filtered before reaching downstream consumers. Raw mutation output (dozens of adversarial variants) is distilled through a gate into actionable findings (the 3-5 mutations that actually revealed vulnerabilities). |

---

## Known Uses

### 1. Hierarchical Multi-Agent Command System

A production system with a three-layer hierarchy (commander → manager → workers). Each layer boundary has an explicit gate:

- **Command Gate (downward)**: Filters high-level strategy into specific task assignments. Workers receive only their task specification, not the full strategic context or other workers' assignments.
- **Report Gate (upward)**: Filters detailed worker reports into structured summaries. The manager receives a standardized report (status, findings, blockers) rather than the worker's full execution log.
- **Audit Gate (lateral)**: A separate audit agent receives unfiltered data for compliance purposes, but through a dedicated audit channel that does not enter the operational context.

**Outcome**: Context contamination incidents dropped dramatically after gate introduction. Manager decision quality improved because reports were standardized and digestible rather than raw and overwhelming.

### 2. YAML-Based Inter-Agent Communication Protocol

A multi-agent system where all communication flows through structured YAML files rather than raw text. Each YAML file serves as both a gate and a communication record:

```yaml
# Worker report (gate output - filtered for manager)
report:
  worker_id: "agent_3"
  status: done
  summary: "Completed analysis of 5 files"
  findings:
    - "3 issues found in authentication module"
  blockers: []
  # Note: full analysis details are in worker's local output file,
  # not in this report. Manager sees summary only.
```

The YAML schema itself enforces the gate — workers can only report fields defined in the schema. Extraneous information has no place to go.

### 3. Document Review Pipeline

A multi-stage document review system where each stage (extraction → analysis → recommendation → formatting) has a stage-specific gate:

- Extraction → Analysis gate: passes only extracted entities and relationships, not raw document text.
- Analysis → Recommendation gate: passes only findings and severity ratings, not analysis methodology.
- Recommendation → Formatting gate: passes only approved recommendations, not rejected alternatives.

Each gate reduces context size by 60-80%, allowing downstream stages to operate within tight budgets.

---

## Implementation Guidance

### Step 1: Map Information Flow

Identify every boundary where information passes between agents:

```
Agent A ──[?]──→ Agent B ──[?]──→ Agent C
                                      │
Agent D ──[?]──→ Agent E ──────[?]────┘
```

For each `[?]`, determine: What does the downstream agent **actually need**?

### Step 2: Define Gate Policies

For each boundary, create a gate specification:

```yaml
# Example: Worker-to-Manager gate
gates:
  - name: "worker_report_gate"
    boundary: "worker → manager"
    type: "schema_gate"
    downstream_needs:
      - task_status        # Did the task complete?
      - key_findings       # What was discovered?
      - blockers           # What prevents progress?
      - quality_score      # Self-assessed output quality
    explicitly_excluded:
      - intermediate_reasoning
      - debug_output
      - raw_data
      - internal_metadata
    max_output_tokens: 2000
```

### Step 3: Implement File-Based Gates

```bash
# Gate implementation pattern (Bash)
# 1. Worker writes full output
worker_output="outputs/worker_3_full.md"

# 2. Gate script filters output
gate_script="gates/worker_to_manager.sh"
gate_output="queue/reports/worker_3_report.yaml"

# 3. Manager reads only the gate output
# Full output preserved at $worker_output for audit
```

### Step 4: Validate Gate Effectiveness

Periodically verify that gates are neither too permissive nor too restrictive:

```yaml
gate_health_check:
  gate: "worker_report_gate"
  metrics:
    pass_through_ratio: 0.15    # Only 15% of upstream tokens reach downstream
    downstream_completeness: 0.95  # Downstream reports no missing info 95% of time
    filter_staleness: 30         # Days since last gate rule review
  thresholds:
    pass_through_ratio_max: 0.30   # If >30%, gate is too permissive
    downstream_completeness_min: 0.90  # If <90%, gate is over-filtering
    filter_staleness_max: 60      # Review gate rules at least every 60 days
```

### Step 5: Connect Gates to Attention Budget

Ensure gate output sizes align with downstream budgets:

```yaml
# Gate output must fit within downstream budget
downstream_budget: 50000
gate_max_output: 5000    # Gate output is 10% of downstream budget
# This leaves 90% of budget for the downstream agent's actual work
# Rule of thumb: Gate output should consume <20% of downstream budget
```

---

## Evidence

- **Level B**: Confirmed across 100+ inter-agent communication events in production multi-agent systems. Systems with explicit gates showed significantly fewer context contamination incidents compared to systems with pass-everything communication.

- **Specific observations**:
  - Introducing gates between hierarchical layers reduced upstream context size reaching the manager by an average of 70-85%, while maintaining downstream task completeness above 95%.
  - The most impactful gate type was the Schema Gate (structured YAML), which simultaneously filtered content and standardized format. Systems using Schema Gates showed faster downstream processing than those using raw text filtering.
  - Gate Bypass ([F001]) was the most common anti-pattern, occurring in approximately 1 in 5 early deployments. Every instance eventually led to context contamination incidents that required system-wide remediation.
  - Over-Filtering ([F002]) was the second most common anti-pattern, typically caused by upstream-defined (rather than downstream-defined) filter rules.

- **Upgrade path to Level A**: Conduct controlled experiments measuring downstream agent output quality with and without gates across 200+ task executions. Measure attention utilization efficiency (useful tokens / total tokens in context) as a quantitative metric. Publish results with statistical significance testing comparing gated vs. ungated architectures.
