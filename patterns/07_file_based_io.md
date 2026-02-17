# Pattern: File-Based I/O

## Classification

- **Weight**: Foundational
- **Evidence Level**: B
- **Category**: knowledge

**Rationale for Foundational weight**: File-Based I/O is infrastructure. Nearly every other CQE pattern depends on file-system persistence for state transfer, audit trails, or configuration storage. Without reliable inter-agent communication, higher-level patterns like Context Gate, Wave Scheduler, and Experience Distillation cannot function correctly. This pattern should be adopted from day one of any multi-agent system.

---

## Problem

In-memory agent communication — passing data through function arguments, shared variables, or API responses — lacks three critical properties for production multi-agent systems:

1. **Reliability**: If an agent crashes mid-task, in-memory state is lost. The next agent in the pipeline receives nothing, or worse, receives partial state that it cannot distinguish from complete state
2. **Transparency**: When debugging a multi-agent failure, developers cannot inspect what one agent passed to another. The communication is invisible — it existed only in RAM during execution
3. **Auditability**: Compliance-sensitive workflows (legal, financial, medical) require a record of what information each agent received and produced. In-memory communication leaves no audit trail

These three gaps create a cascading trust problem: developers cannot verify agent behavior, cannot reproduce failures, and cannot prove correctness to stakeholders.

### The Coupling Problem

In-memory communication also creates tight coupling between agents. Agent B must be running when Agent A produces output. If Agent A finishes before Agent B starts (common in wave-based execution), the output must be buffered somewhere. Without files, this buffer is ad-hoc — a queue, a database, a shared memory segment — each introducing its own failure modes and operational complexity.

---

## Context

This problem arises when:

- **Multiple agents collaborate**: Two or more agents must exchange information to complete a workflow
- **Asynchronous execution**: Agents do not run simultaneously; output from one must persist until the next agent consumes it
- **Debugging is non-trivial**: The system is complex enough that "print the output" is insufficient for understanding failures
- **Reproducibility matters**: Developers need to re-run agent pipelines with identical inputs to diagnose issues
- **Audit requirements exist**: The organization needs records of agent inputs, outputs, and decisions

This problem does **not** arise when:

- A single agent performs all work in one session
- Agent communication is purely synchronous and always succeeds
- The system is simple enough that debugging requires no tooling

---

## Solution

Use the file system as the primary communication channel between agents. Every inter-agent data transfer is written to a file before being read by the recipient.

### Core Principles

1. **Write-then-read**: The producing agent writes output to a file. The consuming agent reads from that file. No direct memory sharing
2. **Structured formats**: Use YAML or Markdown with consistent schemas. Avoid unstructured text dumps
3. **Conventional paths**: File locations follow a predictable naming convention, enabling agents and developers to find artifacts without configuration

### Communication Flow

```
Agent A                    File System                  Agent B
   │                          │                           │
   ├── Execute task ──────────┤                           │
   │                          │                           │
   ├── Write output ─────────▶│ tasks/task_a_output.yaml  │
   │                          │                           │
   │                          │◀── Read input ────────────┤
   │                          │                           │
   │                          │    tasks/task_b_output.yaml│◀── Write output
   │                          │                           │
```

### File Organization

Organize inter-agent files by function:

```
project/
├── queue/
│   ├── tasks/           # Task assignments (manager → worker)
│   │   ├── worker_1.yaml
│   │   └── worker_2.yaml
│   ├── reports/         # Task results (worker → manager)
│   │   ├── worker_1_report.yaml
│   │   └── worker_2_report.yaml
│   └── gate/            # Review requests and decisions
│       ├── request.yaml
│       └── decision.yaml
├── config/
│   ├── settings.yaml    # System configuration
│   └── projects.yaml    # Project registry
├── learned/             # Experience Distillation storage
│   └── corrections.yaml
└── status/
    └── dashboard.md     # Human-readable status summary
```

### Schema Discipline

Every file type has a defined schema. Example for a task assignment:

```yaml
# queue/tasks/worker_1.yaml
task:
  task_id: "task_042"
  description: |
    Review the API integration module for error handling gaps.
  depends_on: []
  status: assigned        # assigned | in_progress | done
  timestamp: "2025-03-15T10:30:00"
```

Example for a task report:

```yaml
# queue/reports/worker_1_report.yaml
worker_id: worker_1
task_id: "task_042"
timestamp: "2025-03-15T11:15:00"
status: done
result:
  summary: "Found 3 error handling gaps in api_client.py"
  details: |
    1. Line 42: HTTP 429 not handled (retry logic missing)
    2. Line 87: Timeout exception caught but not logged
    3. Line 103: Empty response body treated as success
  files_modified: []
```

### Notification Mechanism

Files provide persistence but not notification. Pair file writes with a lightweight signal to wake the consuming agent. Options:

| Mechanism | Pros | Cons |
|-----------|------|------|
| Polling (periodic file check) | Simple | Wastes resources; latency |
| File watcher (inotify/fswatch) | Efficient | Platform-dependent |
| External signal (tmux send-keys, IPC) | Immediate | Requires coordination layer |

**Recommended**: Use an external signal for notification and files for data. The signal says "something changed"; the file contains what changed.

---

## Anti-Pattern

### [F001] File Sprawl

**Description**: Creating a new file for every micro-interaction. A 10-agent system running 50 tasks generates hundreds of tiny files with no organizational structure. Developers cannot find relevant artifacts; agents waste attention budget parsing file listings.

**Symptoms**:
- Hundreds of files accumulate in flat directories
- Naming conventions are inconsistent or absent
- Developers resort to `grep` to find anything
- File cleanup becomes a task in itself

**Root cause**: No file organization convention. Each agent creates files ad-hoc.

**Fix**: Establish a directory structure convention before the first agent runs. Use purpose-based directories (`queue/tasks/`, `queue/reports/`, `learned/`). Implement file rotation or archiving for completed tasks.

### [F002] Schema Drift

**Description**: File formats change without coordination. Agent A writes a report with `result.summary`, but Agent B expects `result.findings`. The consuming agent fails silently — it reads the file successfully but gets null for the field it needs.

**Symptoms**:
- Agents produce correct output that downstream agents cannot parse
- "It worked yesterday" failures after one agent's prompt is updated
- Field names vary across files (`status` vs `state` vs `current_status`)

**Root cause**: No shared schema definition. Each agent defines its own output format.

**Fix**: Define schemas in a central location (e.g., `config/schemas/`). Validate files against schemas before reading. Use consistent field names across all file types. When a schema must change, update all producers and consumers simultaneously.

### [F003] Lock Contention

**Description**: Multiple agents write to the same file simultaneously. One agent's write overwrites another's, causing data loss. Or agents read a file mid-write, receiving partial content.

**Symptoms**:
- Intermittent data corruption in shared files
- "Phantom" entries that appear and disappear
- Race conditions that only manifest under parallel execution

**Root cause**: Treating files as shared mutable state without concurrency control.

**Fix**: Assign each file a single writer. If multiple agents need to contribute to a shared state, each writes to its own file (e.g., `reports/worker_1_report.yaml`, `reports/worker_2_report.yaml`), and a coordinator agent merges them. For truly shared state, use atomic write operations (write to temp file, then rename).

---

## Failure Catalog

| ID | Failure | Root Cause | Detection Point |
|----|---------|-----------|-----------------|
| FC-01 | Agent crash mid-task lost 20 minutes of work; no recovery possible | All intermediate state was in memory. No file checkpoints written during the task | Post-crash: nothing to recover from. Would have been mitigable with periodic file checkpoints |
| FC-02 | Debugging a 5-agent pipeline required 2 hours; inter-agent data was not inspectable | Agents passed data through function arguments. No files written between stages | Developer attempted to add logging retroactively; still could not reproduce the original failure conditions |
| FC-03 | Two agents wrote to `status.yaml` simultaneously; one agent's status update was silently lost | Lock Contention (F003). Shared file with multiple writers and no concurrency control | Detected when dashboard showed stale status. Root cause traced to overwritten file |
| FC-04 | Report format changed from `summary` to `findings`; downstream agent processed empty results for 2 days | Schema Drift (F002). No validation of file content against expected schema | Detected when human reviewed output quality. Silent failure — no error, just empty results |

---

## Interaction Catalog

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **01 Attention Budget** | enables | File-based communication allows precise measurement of inter-agent data volume, informing budget allocation for downstream agents |
| **02 Context Gate** | enables | Files are natural gate boundaries. A Context Gate reads an upstream file, filters it, and writes a reduced file for the downstream agent. Without files, there is no inspectable artifact to filter |
| **03 Cognitive Profile** | complements | Profile definitions stored as files enable version control, sharing, and reuse across agents and projects |
| **04 Wave Scheduler** | enables | Wave boundaries require persistent state transfer. Wave 1 agents write results to files; Wave 2 agents read those files. Without files, wave execution requires all agents to be co-resident in memory |
| **05 Assumption Mutation** | complements | Mutation strategies and results stored as files create a reproducible audit trail. "What mutations were applied?" is answerable by reading the mutation report file |
| **06 Experience Distillation** | enables | Learning entries must persist across sessions. File-Based I/O provides the storage substrate. Without files, distilled knowledge vanishes with the session |
| **08 Template-Driven Role** | complements | Role templates are files. File-Based I/O conventions ensure templates are versioned, discoverable, and consistently structured |

---

## Known Uses

### Production Multi-Agent System — YAML Communication

A production orchestration system uses YAML files as the sole communication channel between 9 agents:

- **Task assignment**: Manager writes `queue/tasks/worker_N.yaml`; worker reads it
- **Task reporting**: Worker writes `queue/reports/worker_N_report.yaml`; manager reads it
- **Review gate**: Manager writes `queue/gate/request.yaml`; reviewer reads and writes `queue/gate/decision.yaml`
- **Result**: Complete audit trail of every inter-agent interaction. Debugging time reduced from hours to minutes by inspecting file history

### Unix Philosophy

The Unix philosophy of "everything is a file" and "programs communicate through pipes (byte streams)" is the philosophical ancestor of this pattern. Files provide:
- Universal interface (every tool can read/write files)
- Composability (any producer can connect to any consumer)
- Inspectability (developers can `cat`, `grep`, and `diff` inter-process data)

### Infrastructure-as-Code

Tools like Terraform, Ansible, and Kubernetes use file-based configuration as the source of truth. State files (e.g., `terraform.tfstate`) persist infrastructure state across sessions, enabling collaboration, versioning, and audit.

---

## Implementation Guidance

### Minimal Implementation (Recommended Starting Point)

```yaml
# config/file_io.yaml
file_io:
  base_path: "queue/"
  schemas:
    task: "config/schemas/task.yaml"
    report: "config/schemas/report.yaml"
  conventions:
    task_file: "queue/tasks/{worker_id}.yaml"
    report_file: "queue/reports/{worker_id}_report.yaml"
  rotation:
    archive_completed: true
    archive_path: "queue/archive/"
    retention_days: 30
```

### Step-by-Step Adoption

1. **Define directory structure** — Before any agent runs, create the directory layout. Document the purpose of each directory in a README
2. **Define schemas** — For each file type (task, report, config), write a schema with required and optional fields. Keep it minimal — 5-10 fields maximum
3. **Single-writer rule** — Assign each file exactly one writer. If two agents need to write status, give each its own file
4. **Add validation** — Before reading a file, validate its schema. Log and fail gracefully on schema violations rather than silently processing malformed data
5. **Implement rotation** — Completed task and report files should be archived (moved to `archive/`) to prevent directory bloat
6. **Add notification** — Pair file writes with a signal mechanism. Start with a simple approach (tmux send-keys, inotify) and upgrade if needed

### Common File Format Template

```yaml
# Standard header for all inter-agent files
metadata:
  created_by: "{agent_id}"
  created_at: "{ISO 8601 timestamp}"
  schema_version: "1.0"

# Payload (file-type-specific)
payload:
  # ... file-specific content ...
```

---

## Evidence

- **Level B**: Confirmed across 3 projects in a production multi-agent system over 6 months of operation:
  - Debugging time reduced by approximately 70% compared to prior in-memory communication approach (measured by time-to-diagnosis for inter-agent failures)
  - Zero data loss incidents after adopting single-writer convention (compared to ~2 incidents/month with shared-file approach)
  - Complete audit trail enabled compliance review that was previously impossible

- **Limitations of current evidence**:
  - Performance overhead of file I/O vs. in-memory communication not quantified
  - Evidence comes from systems with 5-10 agents; scaling behavior to 50+ agents unknown
  - File system used was local (SSD); networked file systems may introduce different failure modes

- **Upgrade path to Level A**: Conduct a controlled comparison:
  - Two identical agent pipelines, one using File-Based I/O and one using in-memory communication
  - Measure: debugging time, data loss rate, reproducibility rate, and throughput
  - Run for 100+ tasks to achieve statistical significance
