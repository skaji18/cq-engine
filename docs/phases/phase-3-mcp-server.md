# Phase 3: Distribution — CQ MCP Server Detailed Plan

> **Version**: 1.0.0
> **Status**: Draft
> **Purpose**: Break down Phase 3 (CQ MCP Server) into actionable implementation tasks

---

## Table of Contents

1. [Phase 3 Overview](#1-phase-3-overview)
2. [MCP Tool Implementation Tasks](#2-mcp-tool-implementation-tasks)
3. [Hooks Integration Tasks](#3-hooks-integration-tasks)
4. [Telemetry Foundation Tasks](#4-telemetry-foundation-tasks)
5. [Phase 3 Overall](#5-phase-3-overall)

---

## 1. Phase 3 Overview

**Mission**: Package CQE Patterns, cqlint, and MutaDoc as an MCP Server that any Claude Code user can install with a single command. Add local telemetry to create a self-improving ecosystem.

**One-liner**: `claude mcp add cq-engine` brings cognitive quality management to every Claude Code session.

**Infrastructure Exception**: CQ MCP Server is the **only** component requiring Python (via Python MCP SDK). All other cq-engine components follow the zero-infrastructure principle (Bash + Markdown). A Bash/CLI fallback **must** exist for every MCP tool.

---

## 2. MCP Tool Implementation Tasks

### 2.1 `cq_engine__decompose` — Task Decomposition Tool

**Function Overview**:
Automatically decomposes a complex task into subtasks that fit within cognitive attention budgets. Applies the Attention Budget pattern to prevent quality degradation from overloaded contexts.

**Input/Output Specification**:

| Direction | Format | Description |
|-----------|--------|-------------|
| **Input** | `task_description: str` | Natural language description of the task |
| **Input** | `budget: int` (optional) | Max token budget per subtask (default: 50000) |
| **Input** | `max_subtasks: int` (optional) | Maximum number of subtasks (default: 8) |
| **Output** | `subtasks: list[dict]` | List of subtasks with `id`, `description`, `estimated_tokens`, `dependencies` |
| **Output** | `total_budget: int` | Sum of all subtask budgets |
| **Output** | `dependency_graph: str` | ASCII dependency graph |

**Implementation Approach**:

```python
# tools/decompose.py
from mcp.server import Server
from mcp.types import Tool, TextContent

@server.tool()
async def decompose(task_description: str, budget: int = 50000, max_subtasks: int = 8) -> list[TextContent]:
    """Decompose a task into attention-budget-aware subtasks."""
    # 1. Read patterns/01_attention_budget.md for budget guidelines
    # 2. Analyze task complexity (token estimation heuristic)
    # 3. Split into subtasks with dependency tracking
    # 4. Validate each subtask fits within budget
    # 5. Return structured subtask list + dependency graph
    # 6. Log to telemetry (task_type, subtask_count, budget_allocation)
```

**Bash/CLI Fallback**: `cqlint.sh decompose --task "description" --budget 50000`

**Test Cases**:

| # | Test Case | Input | Expected Output |
|---|-----------|-------|-----------------|
| T1 | Simple task | "Fix a typo in README" | 1 subtask, no decomposition needed |
| T2 | Medium task | "Add authentication to API" | 3-5 subtasks with dependencies |
| T3 | Complex task | "Refactor entire payment system" | 6-8 subtasks with dependency graph |
| T4 | Budget overflow | Task exceeding budget by 3x | Splits until each subtask fits budget |
| T5 | Circular dependency detection | Task with implicit circular deps | Error with explanation |

**Estimated Effort**: **M** (Medium)

---

### 2.2 `cq_engine__gate` — Quality Gate Tool

**Function Overview**:
Filters context to pass only relevant files/information to each subtask. Implements the Context Gate pattern to prevent context contamination. Incorporates ContextOS design concepts (quality-weighted LRU, context paging) internally.

**Input/Output Specification**:

| Direction | Format | Description |
|-----------|--------|-------------|
| **Input** | `task_description: str` | Description of the current subtask |
| **Input** | `available_files: list[str]` | List of file paths in scope |
| **Input** | `max_files: int` (optional) | Maximum files to pass through (default: 5) |
| **Input** | `max_tokens: int` (optional) | Maximum total token budget for context (default: 30000) |
| **Output** | `selected_files: list[dict]` | Files selected with `path`, `relevance_score`, `estimated_tokens` |
| **Output** | `excluded_files: list[dict]` | Files excluded with `path`, `reason` |
| **Output** | `context_health: dict` | Context Health Score sub-metrics (density, contamination, freshness) |

**Implementation Approach**:

```python
# tools/gate.py
@server.tool()
async def gate(task_description: str, available_files: list[str],
               max_files: int = 5, max_tokens: int = 30000) -> list[TextContent]:
    """Filter context to relevant files only (Context Gate pattern)."""
    # 1. Score each file for relevance to task_description
    # 2. Apply quality-weighted ranking (ContextOS concept)
    # 3. Select top-N files within token budget
    # 4. Calculate Context Health Score
    # 5. Return selected + excluded with reasons
    # 6. Log to telemetry (files_offered, files_selected, health_score)
```

**Bash/CLI Fallback**: `cqlint.sh gate --task "description" --files "file1,file2,..." --max 5`

**Test Cases**:

| # | Test Case | Input | Expected Output |
|---|-----------|-------|-----------------|
| T1 | Relevant subset | 10 files, 3 relevant | 3 files selected, 7 excluded with reasons |
| T2 | All relevant | 3 files, all relevant | All 3 selected |
| T3 | Token overflow | 5 relevant files exceeding budget | Top files within budget, overflow excluded |
| T4 | No relevant files | 5 files, none relevant | Empty selection with warning |
| T5 | Context health check | Mixed relevance files | Health score with density/contamination metrics |

**Estimated Effort**: **M** (Medium)

---

### 2.3 `cq_engine__persona` — Persona Management Tool

**Function Overview**:
Selects or generates the optimal cognitive profile (persona) for a given subtask. Implements the Cognitive Profile pattern to ensure specialized, high-quality analysis.

**Input/Output Specification**:

| Direction | Format | Description |
|-----------|--------|-------------|
| **Input** | `task_description: str` | Description of the subtask |
| **Input** | `task_type: str` (optional) | Category: `code`, `document`, `analysis`, `review` |
| **Input** | `custom_personas: list[str]` (optional) | User-defined persona file paths |
| **Output** | `selected_persona: dict` | Persona with `name`, `expertise`, `cognitive_style`, `template` |
| **Output** | `alternatives: list[dict]` | Other candidate personas with fit scores |
| **Output** | `persona_prompt: str` | Ready-to-use persona instruction text |

**Implementation Approach**:

```python
# tools/persona.py
@server.tool()
async def persona(task_description: str, task_type: str = "auto",
                  custom_personas: list[str] = None) -> list[TextContent]:
    """Select optimal cognitive persona for a task."""
    # 1. Read available personas from patterns/personas/ and user custom dir
    # 2. Match task characteristics to persona expertise
    # 3. Score fit for each candidate
    # 4. Return best match + alternatives
    # 5. Generate ready-to-use persona prompt
    # 6. Log to telemetry (task_type, persona_selected, fit_score)
```

**Bash/CLI Fallback**: `cqlint.sh persona --task "description" --type code`

**Test Cases**:

| # | Test Case | Input | Expected Output |
|---|-----------|-------|-----------------|
| T1 | Code task | "Optimize database query" | Senior DB Engineer persona |
| T2 | Document task | "Review contract terms" | Legal Analyst persona |
| T3 | Analysis task | "Analyze market opportunity" | Strategy Analyst persona |
| T4 | Custom persona | Task + custom persona path | Custom persona loaded and applied |
| T5 | Generic detection | "Do stuff" (vague) | Warning: CQ003 generic persona risk |

**Estimated Effort**: **S** (Small)

---

### 2.4 `cq_engine__mutate` — Mutation Testing Tool

**Function Overview**:
Applies mutation testing to code changes, refactoring results, or configuration modifications. Tests robustness by intentionally introducing controlled mutations and checking if quality mechanisms detect them. Implements the Assumption Mutation pattern.

**Input/Output Specification**:

| Direction | Format | Description |
|-----------|--------|-------------|
| **Input** | `target_path: str` | File or directory to mutate |
| **Input** | `strategies: list[str]` (optional) | Mutation strategies: `contradiction`, `deletion`, `inversion`, `boundary`, `assumption` (default: all) |
| **Input** | `severity_threshold: str` (optional) | Minimum severity to report: `info`, `minor`, `major`, `critical` (default: `minor`) |
| **Output** | `mutations: list[dict]` | Each mutation with `id`, `strategy`, `location`, `original`, `mutated`, `detected`, `severity` |
| **Output** | `kill_rate: float` | Mutation Kill Rate (detected / total) |
| **Output** | `surviving_mutations: list[dict]` | Mutations that survived (potential vulnerabilities) |

**Implementation Approach**:

```python
# tools/mutate.py
@server.tool()
async def mutate(target_path: str, strategies: list[str] = None,
                 severity_threshold: str = "minor") -> list[TextContent]:
    """Apply mutation testing to verify output robustness."""
    # 1. Read target file(s)
    # 2. Apply selected mutation strategies
    # 3. For each mutation: check if existing tests/checks detect it
    # 4. Calculate kill rate
    # 5. Flag surviving mutations as potential vulnerabilities
    # 6. Log to telemetry (file_type, strategies_used, kill_rate)
```

**Bash/CLI Fallback**: `cqlint.sh mutate --target path --strategies all`

**Test Cases**:

| # | Test Case | Input | Expected Output |
|---|-----------|-------|-----------------|
| T1 | YAML mutation | Agent config YAML | Mutations in budget/gate/persona fields |
| T2 | Markdown mutation | Documentation file | Contradiction/ambiguity mutations |
| T3 | High kill rate | Well-tested config | Kill rate > 80% |
| T4 | Low kill rate | Untested config | Kill rate < 50%, surviving mutations listed |
| T5 | Strategy selection | Single strategy only | Only that strategy's mutations applied |

**Estimated Effort**: **L** (Large)

---

### 2.5 `cq_engine__learn` — Learning & Knowledge Accumulation Tool

**Function Overview**:
Captures and accumulates learned preferences, execution insights, and pattern observations from agent sessions. Implements the Experience Distillation pattern to prevent knowledge loss between sessions.

**Input/Output Specification**:

| Direction | Format | Description |
|-----------|--------|-------------|
| **Input** | `observation: str` | What was learned (natural language) |
| **Input** | `category: str` | Category: `pattern_usage`, `failure`, `preference`, `optimization` |
| **Input** | `confidence: float` (optional) | Confidence level 0.0-1.0 (default: 0.5) |
| **Input** | `project: str` (optional) | Project context for scoped learning |
| **Output** | `learning_id: str` | Unique ID for the stored learning |
| **Output** | `related_learnings: list[dict]` | Previously stored learnings related to this observation |
| **Output** | `pattern_suggestion: str or null` | If observation maps to a known CQE pattern, suggest it |

**MCP Resource**: `cq_engine://learned` exposes accumulated learnings as a read-only resource.

**Implementation Approach**:

```python
# tools/learn.py
@server.tool()
async def learn(observation: str, category: str,
                confidence: float = 0.5, project: str = None) -> list[TextContent]:
    """Store a learned observation for future reference."""
    # 1. Validate category
    # 2. Search for related existing learnings (dedup)
    # 3. Store in local JSON/YAML file (~/.cq-engine/learned/)
    # 4. If confidence > 0.8 and repeated 3+ times, flag as candidate pattern
    # 5. Return learning_id + related learnings
    # 6. Log to telemetry (category, confidence, is_duplicate)
```

**Bash/CLI Fallback**: `cqlint.sh learn --observation "text" --category pattern_usage`

**Test Cases**:

| # | Test Case | Input | Expected Output |
|---|-----------|-------|-----------------|
| T1 | New learning | Novel observation | Stored with unique ID |
| T2 | Duplicate detection | Same observation twice | Related learning found, dedup warning |
| T3 | Pattern suggestion | Observation matching Attention Budget | Suggestion: "Related to Pattern 01" |
| T4 | Project-scoped | Learning with project context | Stored in project-specific scope |
| T5 | High-confidence repeat | Same pattern 3+ times, confidence 0.9 | Flagged as candidate pattern |

**Estimated Effort**: **M** (Medium)

---

### 2.6 `cq_engine__cqlint` — Linter MCP Wrapper

**Function Overview**:
MCP wrapper around the Bash-based cqlint tool. Provides cognitive quality linting as an MCP tool, checking agent configurations against CQE Patterns.

**Input/Output Specification**:

| Direction | Format | Description |
|-----------|--------|-------------|
| **Input** | `target_path: str` | File or directory to lint |
| **Input** | `rules: list[str]` (optional) | Specific rules to check: `CQ001`-`CQ005` (default: all) |
| **Input** | `format: str` (optional) | Output format: `text`, `json`, `markdown` (default: `text`) |
| **Output** | `violations: list[dict]` | Each violation with `rule`, `severity`, `file`, `line`, `message`, `suggestion` |
| **Output** | `summary: dict` | Total counts by severity: `errors`, `warnings`, `info` |
| **Output** | `passed: bool` | Whether the check passed (no errors) |

**Implementation Approach**:

```python
# tools/cqlint.py
@server.tool()
async def cqlint(target_path: str, rules: list[str] = None,
                 format: str = "text") -> list[TextContent]:
    """Run cognitive quality linting on agent configurations."""
    # 1. Delegate to cqlint.sh (Bash implementation) via subprocess
    # 2. Parse output into structured format
    # 3. Format as requested (text/json/markdown)
    # 4. Return violations + summary
    # 5. Log to telemetry (rules_checked, violations_found, pass_rate)
```

**Bash/CLI Fallback**: `cqlint.sh check path/ --rules CQ001,CQ003`

**Test Cases**:

| # | Test Case | Input | Expected Output |
|---|-----------|-------|-----------------|
| T1 | Clean config | Fully compliant YAML | `passed: true`, no violations |
| T2 | Budget missing | YAML without attention budget | CQ001 violation |
| T3 | Generic persona | YAML with vague persona | CQ003 warning |
| T4 | Multiple violations | Config with 3 issues | 3 violations, correct severities |
| T5 | JSON output | Same input, format=json | Structured JSON output |

**Estimated Effort**: **S** (Small) — wraps existing Bash implementation

---

### Tool Implementation Summary

| Tool | Function | Effort | Priority | Dependencies |
|------|----------|:------:|:--------:|-------------|
| `cq_engine__decompose` | Task decomposition within attention budgets | M | High | patterns/01_attention_budget.md |
| `cq_engine__gate` | Context filtering for subtasks | M | High | patterns/02_context_gate.md |
| `cq_engine__persona` | Optimal persona selection | S | Medium | patterns/03_cognitive_profile.md |
| `cq_engine__mutate` | Mutation testing for robustness | L | High | patterns/05_assumption_mutation.md, mutadoc/ |
| `cq_engine__learn` | Knowledge accumulation across sessions | M | Medium | patterns/06_experience_distillation.md |
| `cq_engine__cqlint` | MCP wrapper for cqlint | S | High | cqlint/cqlint.sh |

**Additional Phase 2 Integration Tools** (not detailed here — implemented as wrappers):

| Tool | Wraps | Added In |
|------|-------|----------|
| `cq_engine__mutadoc` | mutadoc/mutadoc.sh | Phase 3 (after MutaDoc v0.1 is stable) |
| `cq_engine__benchmark` | benchmark/ measurement scripts | Phase 3 (after Benchmark spec is baselined) |

---

## 3. Hooks Integration Tasks

### 3.1 Claude Code Hooks Integration Points

CQ MCP Server integrates with Claude Code via the Hooks system, providing automatic cognitive quality checks without user intervention.

**Supported Hook Types**:

| Hook Type | Trigger | CQ Action |
|-----------|---------|-----------|
| `PreToolUse` | Before `Edit`, `Write`, `Task` | Context hygiene check via `gate` |
| `PostToolUse` | After `Edit`, `Write` | Mutation spot-check via `mutate` |
| `Notification` | On task completion messages | Auto-learning via `learn` |

### 3.2 PreToolUse Hook Design

**File**: `hooks/cognitive_hygiene_check.sh`

**Trigger**: Before `Edit` or `Write` tool invocations.

**Behavior**:
1. Capture the list of files currently in context
2. Run `cq_engine__gate` to check context relevance
3. If Context Health Score < threshold (default: 0.6):
   - Return warning message to Claude Code
   - Suggest removing irrelevant files from context
4. If score >= threshold: pass through silently

**Configuration** (in `.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": { "tool_name": "Edit|Write" },
        "command": "~/.cq-engine/hooks/cognitive_hygiene_check.sh",
        "timeout": 5000
      }
    ]
  }
}
```

**Completion Criteria**:
- Hook triggers on every Edit/Write invocation
- Context Health Score calculated within 3 seconds
- Warning displayed when score is below threshold
- No false positives on clean contexts (< 5% false positive rate)

### 3.3 PostToolUse Hook Design

**File**: `hooks/auto_mutation.sh`

**Trigger**: After `Task` tool completion.

**Behavior**:
1. Identify files modified during the task
2. Run `cq_engine__mutate` with `strategies: [assumption, contradiction]` on modified files
3. If surviving mutations found:
   - Report surviving mutations as potential quality risks
   - Suggest review of flagged areas
4. Store results in telemetry

**Configuration**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": { "tool_name": "Task" },
        "command": "~/.cq-engine/hooks/auto_mutation.sh",
        "timeout": 30000
      }
    ]
  }
}
```

**Completion Criteria**:
- Hook triggers after every Task tool completion
- Mutation check completes within 30 seconds
- Results stored in telemetry automatically

### 3.4 Notification Hook Design

**File**: `hooks/auto_learn.sh`

**Trigger**: On notification messages indicating task completion.

**Behavior**:
1. Parse notification for task outcome (success/failure/partial)
2. If failure: extract error pattern, store via `cq_engine__learn` with `category: failure`
3. If success: extract successful patterns, store via `cq_engine__learn` with `category: optimization`
4. Increment session telemetry counters

**Completion Criteria**:
- Learning automatically captured from task outcomes
- Failure patterns stored for future prevention
- No user intervention required

### 3.5 Auto-Telemetry Collection via Hooks

All hooks automatically emit telemetry events:

| Hook | Telemetry Event | Data Captured |
|------|----------------|---------------|
| PreToolUse | `context_gate_check` | files_count, health_score, threshold_met |
| PostToolUse | `mutation_check` | files_checked, mutations_applied, kill_rate |
| Notification | `task_outcome` | task_type, outcome, duration, learnings_captured |

### Hooks Implementation Summary

| Task | Description | Effort | Priority |
|------|-------------|:------:|:--------:|
| H3.1 | Implement `cognitive_hygiene_check.sh` (PreToolUse) | S | High |
| H3.2 | Implement `auto_mutation.sh` (PostToolUse) | M | Medium |
| H3.3 | Implement `auto_learn.sh` (Notification) | S | Medium |
| H3.4 | Hook installer script (auto-configures `.claude/settings.json`) | S | High |
| H3.5 | Hook configuration documentation | S | Low |

---

## 4. Telemetry Foundation Tasks

### 4.1 Local Telemetry Storage Design

**Principle**: All telemetry data is **strictly local**. No data leaves the machine. Ever. This is non-negotiable.

**Storage Location**: `~/.cq-engine/telemetry/`

**Storage Format**: JSONL (JSON Lines) — one event per line, append-only.

**Directory Structure**:

```
~/.cq-engine/
├── telemetry/
│   ├── events/
│   │   ├── 2026-02-17.jsonl       # Daily event log (auto-rotated)
│   │   ├── 2026-02-18.jsonl
│   │   └── ...
│   ├── aggregates/
│   │   ├── weekly_summary.json    # Weekly aggregation
│   │   ├── monthly_summary.json   # Monthly aggregation
│   │   └── pattern_usage.json     # Pattern-specific usage stats
│   └── config.json                # Telemetry configuration
├── learned/
│   ├── global.jsonl               # Global learnings
│   └── projects/
│       └── {project_name}.jsonl   # Project-scoped learnings
└── cache/
    └── context_scores.json        # Cached context health scores
```

**Event Schema**:

```json
{
  "timestamp": "2026-02-17T21:30:00Z",
  "event_type": "tool_invocation",
  "tool": "cq_engine__gate",
  "data": {
    "files_offered": 10,
    "files_selected": 3,
    "context_health_score": 0.85,
    "task_type": "code_review"
  },
  "session_id": "abc123",
  "duration_ms": 1200
}
```

**Retention Policy**:
- Raw events: 90 days (auto-purge older files)
- Weekly aggregates: 1 year
- Monthly aggregates: indefinite
- Learnings: indefinite (user can manually clear)

### 4.2 Metrics Collection & Aggregation Pipeline

**Collection Layer**:
Every MCP tool call emits a telemetry event via a shared `TelemetryCollector` class.

```python
# telemetry/collector.py
class TelemetryCollector:
    def __init__(self, storage_path: str = "~/.cq-engine/telemetry"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def emit(self, event_type: str, tool: str, data: dict) -> None:
        """Append a telemetry event to today's log."""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "tool": tool,
            "data": data,
            "session_id": self._get_session_id(),
            "duration_ms": data.pop("_duration_ms", None)
        }
        daily_file = self.storage_path / "events" / f"{date.today()}.jsonl"
        with open(daily_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def aggregate_weekly(self) -> dict:
        """Aggregate last 7 days into weekly summary."""
        # Count tool invocations, average scores, failure rates
        ...

    def get_pattern_usage(self) -> dict:
        """Which patterns are most/least used."""
        ...
```

**Aggregation Layer**:

| Aggregation | Frequency | Content |
|-------------|-----------|---------|
| Daily | End of day (lazy, on next startup) | Tool call counts, avg scores |
| Weekly | Every 7 days | Trend analysis, most violated rules |
| Monthly | Every 30 days | Pattern usage evolution, learning accumulation rate |
| On-demand | User-triggered | Full CQ Health report |

**Metrics Collected**:

| Category | Metric | Description |
|----------|--------|-------------|
| Usage | `tool_invocation_count` | How often each tool is called |
| Usage | `tool_invocation_source` | Autonomous vs explicit invocation |
| Quality | `context_health_avg` | Average Context Health Score across sessions |
| Quality | `mutation_kill_rate_avg` | Average kill rate from mutation checks |
| Quality | `cqlint_violation_rate` | Violations per check over time |
| Learning | `learnings_per_session` | How many learnings captured per session |
| Learning | `duplicate_learning_rate` | How often the same thing is re-learned |
| Feedback | `rule_override_rate` | How often users dismiss cqlint warnings |
| Feedback | `gate_override_rate` | How often users include files gate recommended excluding |

### 4.3 CQ Benchmark Integration

Telemetry feeds directly into CQ Benchmark's 4-axis measurement:

| CQ Benchmark Axis | Telemetry Source | Metric Mapping |
|--------------------|-----------------|----------------|
| **Context Health Score** | `gate` tool data | `context_health_avg`, file filtering ratios |
| **Decision Quality Score** | `persona` + `decompose` data | Persona fit scores, decomposition quality |
| **Document Integrity Score** | `mutate` + `cqlint` data | `mutation_kill_rate_avg`, `cqlint_violation_rate` |
| **Evolution Score** | `learn` data | `learnings_per_session`, `duplicate_learning_rate`, pattern compliance trends |

**Benchmark Report Generation**:

```bash
# CLI command to generate CQ Benchmark report
cq-engine benchmark report

# Output:
# CQ Health Report — 2026-02-17
# =============================
# Context Health:     0.82 / 1.00  ████████░░
# Decision Quality:   0.75 / 1.00  ███████░░░
# Document Integrity: 0.91 / 1.00  █████████░
# Evolution:          0.60 / 1.00  ██████░░░░
# =============================
# Overall CQ Score:   0.77 / 1.00
#
# Top Issue: Evolution score low — only 2 learnings captured in last 7 sessions
# Recommendation: Enable auto_learn hook for automatic knowledge capture
```

### 4.4 Dashboard / Report Generation

**CQ Health Dashboard** (via MCP resource):

MCP Resource URI: `cq_engine://health`

Returns a real-time project health summary consumable by Claude Code.

**CLI Report** (via Bash fallback):

```bash
cq-engine report [--period weekly|monthly|all] [--format text|json|markdown]
```

**Report Sections**:
1. **CQ Score Summary** — 4-axis scores with trend arrows
2. **Tool Usage Breakdown** — Which tools used most/least
3. **Pattern Compliance** — Which CQE patterns are well-applied vs neglected
4. **Learning Insights** — Most valuable learnings accumulated
5. **Recommendations** — Actionable suggestions based on telemetry

### 4.5 Telemetry Completion Criteria

| Criterion | Measurement |
|-----------|------------|
| Events are captured for all 6 MCP tools | 100% tool coverage |
| Daily JSONL files are correctly rotated | No single file > 10MB |
| Weekly/monthly aggregation runs without errors | Aggregation success rate 100% |
| CQ Benchmark report generates from telemetry data | 4-axis scores calculated |
| Privacy: zero network calls from telemetry module | Verified by code review + network monitoring test |
| Report generation completes within 5 seconds | Performance benchmark |

### Telemetry Implementation Summary

| Task | Description | Effort | Priority |
|------|-------------|:------:|:--------:|
| T4.1 | Implement `TelemetryCollector` class | M | High |
| T4.2 | Add telemetry emission to all 6 tools | S | High |
| T4.3 | Implement daily/weekly/monthly aggregation | M | Medium |
| T4.4 | Implement CQ Benchmark report generation | M | Medium |
| T4.5 | Implement `cq_engine://health` MCP resource | S | Medium |
| T4.6 | Implement CLI `cq-engine report` command | S | Low |
| T4.7 | Implement retention policy (auto-purge) | S | Low |

---

## 5. Phase 3 Overall

### 5.1 Milestone Definitions

| # | Milestone | Definition of Done | Depends On |
|---|-----------|-------------------|------------|
| **M3.1** | MCP Server installable | `claude mcp add cq-engine -- python server.py` works. All 6 core tools respond to invocations. Server starts/stops cleanly | Phase 1 (M1.1, M1.2) |
| **M3.2** | Core tools functional | `decompose`, `gate`, `persona`, `mutate`, `learn`, `cqlint` all pass test suites. Bash/CLI fallbacks work for every tool | M3.1 |
| **M3.3** | MutaDoc integration | `cq_engine__mutadoc` wraps MutaDoc v0.1. Document mutation testing available via MCP | Phase 2 (M2.1, M2.2) |
| **M3.4** | Hooks auto-trigger | PreToolUse and PostToolUse hooks installed and functioning. CQ checks run automatically on Edit/Write and Task completion | M3.2 |
| **M3.5** | Telemetry collecting | Local usage data accumulating in `~/.cq-engine/telemetry/`. All tools emit events. Aggregation pipeline operational | M3.2 |
| **M3.6** | CQ Health Dashboard | `cq_engine://health` resource returns 4-axis CQ scores. CLI `cq-engine report` generates benchmark report | M3.5 |
| **M3.7** | Feedback loop v1 | First telemetry-driven update cycle: telemetry identifies most violated pattern → Anti-Pattern section updated → cqlint rule threshold adjusted | M3.5, M3.6 |

### 5.2 Dependencies on Phase 1 and Phase 2

**Phase 1 Dependencies (Required)**:

| Phase 1 Deliverable | Required By | Reason |
|---------------------|-------------|--------|
| CQE Patterns v0.1 (M1.1) | M3.1 | Patterns served via `cq_engine://patterns` resource |
| cqlint v0.1 (M1.2) | M3.1 | `cq_engine__cqlint` wraps cqlint.sh |
| CQ Benchmark spec (M1.4) | M3.6 | Telemetry → Benchmark mapping requires finalized spec |

**Phase 2 Dependencies (Partial — MutaDoc integration)**:

| Phase 2 Deliverable | Required By | Reason |
|---------------------|-------------|--------|
| MutaDoc v0.1 strategies (M2.1) | M3.3 | `cq_engine__mutadoc` wraps MutaDoc |
| Mutation-Driven Repair (M2.2) | M3.3 | Repair functionality exposed via MCP |

**Note**: M3.1 and M3.2 can begin as soon as Phase 1 is complete. M3.3 requires Phase 2 MutaDoc. This allows parallel work.

### 5.3 Dependency Diagram

```
PHASE 1 (Foundation)                    PHASE 2 (Killer App)
========================                ========================

M1.1 CQE Patterns v0.1 ──────────────────────────────────────┐
  │                                                           │
  │                                     M2.1 MutaDoc          │
  │                                     strategies ───┐       │
M1.2 cqlint v0.1 ───────┐              │             │       │
  │                      │              M2.2 Mutation  │       │
  │                      │              Driven Repair ─┤       │
M1.4 CQ Benchmark ──────┼──────────────────────────┐  │       │
  spec                   │                          │  │       │
                         │                          │  │       │
PHASE 3 (Distribution)  │                          │  │       │
======================== │                          │  │       │
                         │                          │  │       │
M3.1 MCP Server ◄────────┘                          │  │       │
  installable            │                          │  │       │
  │                      │                          │  │       │
  ▼                      │                          │  │       │
M3.2 Core tools ◄────────┘                          │  │       │
  functional                                        │  │       │
  │                                                 │  │       │
  ├───────────────────────────────────────────────────┘  │       │
  │                                                    │       │
  ▼                                                    │       │
M3.3 MutaDoc ◄──────────────────────────────────────────┘       │
  integration                                                  │
  │                                                            │
  ▼                                                            │
M3.4 Hooks ◄─── M3.2                                          │
  auto-trigger                                                 │
  │                                                            │
  ▼                                                            │
M3.5 Telemetry ◄─── M3.2                                      │
  collecting                                                   │
  │                                                            │
  ▼                                                            │
M3.6 CQ Health ◄─── M3.5 + M1.4                               │
  Dashboard                                                    │
  │                                                            │
  ▼                                                            │
M3.7 Feedback ◄─── M3.5 + M3.6 + M1.1 ◄──────────────────────┘
  loop v1

                         │
                         ▼
                    PHASE 4 (Expansion)
                    ========================
                    M4.1 ThinkTank
                    M4.2 Anchoring Score
                    M4.3 MCP integration
                    M4.4 Feedback loop v2
```

**Parallelization Opportunity**:

```
Timeline (sequential blocks shown, parallel where possible):

Block A: M3.1 → M3.2 (server skeleton + core tools)
Block B:              M3.4 (hooks) ──────────────┐
Block C:              M3.5 (telemetry) ──────────┼──→ M3.7
Block D:              M3.3 (MutaDoc integration)  │
Block E:                    M3.6 (dashboard) ◄────┘
```

Blocks B, C, D can run in parallel after M3.2 completes.

### 5.4 Phase 3 Completion Criteria

Phase 3 is complete when **all** of the following are true:

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | `claude mcp add cq-engine` installs successfully | Manual test on clean environment |
| 2 | All 6 core tools + mutadoc wrapper respond correctly | Automated test suite (30+ test cases) |
| 3 | Bash/CLI fallback exists for every MCP tool | Each tool testable without MCP |
| 4 | Hooks auto-trigger on Edit/Write/Task | Integration test with sample session |
| 5 | Telemetry accumulates locally with zero network calls | Network monitor verification |
| 6 | CQ Health Dashboard returns 4-axis scores | Report generation test |
| 7 | First feedback loop cycle completed | At least 1 telemetry-driven rule update |
| 8 | Documentation covers installation, configuration, and all tools | docs/guides/mcp-server.md exists |
| 9 | No Python dependency leaks outside mcp-server/ directory | Dependency audit |

### 5.5 Risks and Mitigations

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|:----------:|-----------|
| R1 | Python dependency contradicts zero-infrastructure principle | Philosophy inconsistency, user confusion | High | Always provide Bash/CLI fallback for every MCP tool. Document the exception clearly |
| R2 | Telemetry privacy concerns | User distrust, adoption resistance | Medium | All telemetry strictly local. No network calls. Privacy audit in code review. Opt-out mechanism |
| R3 | MCP SDK API changes break server | Server stops working on Claude Code update | Medium | Pin to stable MCP SDK version. Maintain compatibility test suite. Monitor MCP SDK changelog |
| R4 | Hook performance overhead | Slows down Claude Code sessions | Medium | Strict timeout enforcement (5s for PreToolUse, 30s for PostToolUse). Async where possible |
| R5 | Agent Teams competition | Claude Code's Agent Teams directly competes with multi-agent patterns | High | Prepare cq-engine as Agent Teams CLAUDE.md injection path. CQE patterns are framework-agnostic |
| R6 | Tool auto-selection inaccuracy | Claude uses wrong CQ tool or uses tools unnecessarily | Medium | Clear tool descriptions with explicit use-case examples. Telemetry tracks override rates for tuning |
| R7 | Telemetry storage grows unbounded | Disk space exhaustion | Low | Retention policy: 90 days raw, 1 year weekly, auto-purge. Max file size limits |
| R8 | Feedback loop produces incorrect pattern updates | Bad telemetry → bad rules | Low | Human review gate: feedback loop v1 generates *suggestions*, not auto-applied changes |

### 5.6 CTL Revival Checkpoint

**Evaluation Point**: Phase 3, after M3.5 (Telemetry collecting) is operational.

**Revival Conditions** (ALL must be true):
1. CQE Patterns have reached v0.2+ (at least one pattern revision cycle complete)
2. Community feedback indicates demand for declarative task definition beyond what cqlint provides
3. Telemetry shows users repeatedly constructing complex task configurations that a DSL would simplify

**Evaluation Criteria**:

| Question | Data Source | Revival Threshold |
|----------|-----------|-------------------|
| Do users need more expressive task definitions than YAML? | Telemetry: task complexity distribution | > 20% of tasks exceed cqlint's expressiveness |
| Is there community demand? | GitHub Issues / Discussions | 5+ independent requests for DSL-like features |
| Can CTL complement (not replace) cqlint? | Technical analysis | CTL as optional power-user layer, cqlint remains default |

**If Revived**: CTL would be added as `cq-engine/ctl/` directory with:
- `ctl/` — CTL parser and compiler (transpiles to YAML + cqlint rules)
- `cq_engine__ctl_check` — MCP tool for CTL validation
- Integration with existing cqlint rules (CTL checks compile to CQ001-CQ005 equivalents)

**If Not Revived**: CTL remains permanently deferred. cqlint continues as the sole verification layer.

---

## Appendix A: MCP Server Architecture

```
┌──────────────────────────────────────────────────────┐
│                  CQ MCP Server (server.py)             │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │ TOOLS                                            │  │
│  │  ┌──────────┐ ┌──────┐ ┌─────────┐ ┌────────┐  │  │
│  │  │decompose │ │ gate │ │ persona │ │ mutate │  │  │
│  │  └──────────┘ └──────┘ └─────────┘ └────────┘  │  │
│  │  ┌──────────┐ ┌────────┐ ┌──────────────────┐  │  │
│  │  │  learn   │ │ cqlint │ │ mutadoc (Ph2)    │  │  │
│  │  └──────────┘ └────────┘ └──────────────────┘  │  │
│  └────────────────────┬────────────────────────────┘  │
│                       │                                │
│  ┌────────────────────▼────────────────────────────┐  │
│  │ RESOURCES                                        │  │
│  │  cq_engine://patterns    cq_engine://learned     │  │
│  │  cq_engine://health                              │  │
│  └────────────────────┬────────────────────────────┘  │
│                       │                                │
│  ┌────────────────────▼────────────────────────────┐  │
│  │ TELEMETRY                                        │  │
│  │  TelemetryCollector → JSONL → Aggregator → Report│  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────┬───────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────────┐
    │ PreTool  │  │ PostTool │  │ Notification │
    │ Use Hook │  │ Use Hook │  │ Hook         │
    └──────────┘  └──────────┘  └──────────────┘
    cognitive_     auto_          auto_
    hygiene.sh     mutation.sh    learn.sh
```

## Appendix B: Effort Estimation Summary

| Category | Task Count | S | M | L | Total Effort |
|----------|:---------:|:-:|:-:|:-:|:------------:|
| MCP Tools | 6 | 2 | 3 | 1 | ~M-L |
| Hooks | 5 | 4 | 1 | 0 | ~S-M |
| Telemetry | 7 | 3 | 3 | 0 (1 included in tools) | ~M |
| **Phase 3 Total** | **18** | **9** | **7** | **1** | **L** |

Estimated total: **L** (Large), consistent with the roadmap's original estimation.

---

<!-- PHASE 3 DETAIL COMPLETE -->
