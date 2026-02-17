# Pattern: Wave Scheduler

## Classification

- **Weight**: Situational
- **Evidence Level**: B — Confirmed across multiple production multi-agent systems
- **Category**: application

Wave Scheduler is a situational pattern. It provides the most value when a system runs multiple parallel agents with shared resources or interdependent outputs. Systems with only sequential, independent tasks may not need wave-based scheduling. However, any system that deploys more than 3 agents concurrently should evaluate this pattern.

---

## Problem

Launching all tasks simultaneously degrades quality because of resource contention, dependency violations, and coordination failures. The "all-at-once" deployment strategy treats parallelism as free, but in LLM-based systems, parallelism has real costs.

The failure manifests in three ways:

1. **Resource contention.** Parallel agents compete for shared resources — total available attention budget, access to shared files, human review bandwidth. When 8 agents run simultaneously but only enough attention budget exists for 4, all 8 produce degraded output rather than 4 producing excellent output.

2. **Dependency violations.** Tasks have implicit and explicit dependencies. Agent B needs Agent A's output as input. If both launch simultaneously, Agent B either blocks (wasting resources) or proceeds with stale/missing data (producing incorrect output). Without wave sequencing, dependency management becomes each agent's responsibility — and agents handle it inconsistently.

3. **Coordination collapse.** As concurrency increases, the coordination overhead grows non-linearly. Status tracking, conflict resolution, and output integration all become harder. Beyond a critical concurrency threshold, the system spends more effort coordinating than producing.

The counter-intuition is key: **reducing parallelism often increases total throughput.** A system running 3 waves of 3 agents typically outperforms 9 agents running at once, because each wave produces clean inputs for the next.

---

## Context

This problem arises when:

- A system deploys **more than 3 agents concurrently** with any shared resources or interdependencies.
- Tasks have **data dependencies** — some tasks produce outputs that others consume.
- **Total attention budget** is finite and must be shared across agents (see Pattern 01: Attention Budget).
- **Output integration** is required — individual agent outputs must be combined into a coherent result.
- **Quality is prioritized over speed** — a 20% slower but 40% higher-quality result is preferred.

This problem does **not** arise when:

- All tasks are fully independent with no shared resources or dependencies
- The system runs only 1-2 agents at a time
- Speed is the only metric and quality degradation is acceptable
- Tasks are trivially parallelizable (e.g., formatting 100 independent files)

---

## Solution

Organize task execution into sequenced **waves** — groups of tasks that run in parallel within a wave, with synchronization barriers between waves. Each wave's completion provides clean, verified inputs for the next wave.

### Core Principles

1. **Wave as Synchronization Primitive**: A wave is a batch of tasks that start together, run in parallel, and must all complete before the next wave begins. The wave boundary is a hard synchronization point — no task in wave N+1 starts until all tasks in wave N are complete.

2. **Dependency-Driven Wave Assignment**: Tasks that produce outputs consumed by other tasks must execute in an earlier wave. The wave structure is derived from the task dependency graph, not assigned arbitrarily.

3. **Budget-Constrained Wave Sizing**: The number of tasks per wave is limited by the total available attention budget. If 4 tasks each need 50K tokens and total budget is 150K, the wave holds 3 tasks, not 4.

4. **Wave-Boundary Quality Gates**: Between waves, verify that the current wave's outputs meet quality thresholds before proceeding. A failed quality gate triggers rework within the current wave rather than propagating errors to the next wave.

5. **Minimize Wave Count**: Fewer waves means less synchronization overhead. Within the dependency constraints, pack as many independent tasks into each wave as the budget allows.

### Wave Structure Format

```yaml
wave_schedule:
  total_budget: 200000
  quality_gate: true

  waves:
    - wave_id: 1
      name: "Foundation"
      tasks:
        - task_id: "research_a"
          budget: 60000
          agent_profile: "analyst"
        - task_id: "research_b"
          budget: 60000
          agent_profile: "analyst"
        - task_id: "research_c"
          budget: 60000
          agent_profile: "analyst"
      gate:
        condition: "all_tasks_complete"
        quality_check: "output_completeness >= 0.8"

    - wave_id: 2
      name: "Analysis"
      depends_on: [1]
      tasks:
        - task_id: "cross_analysis"
          budget: 80000
          agent_profile: "synthesizer"
          inputs_from: ["research_a", "research_b", "research_c"]
        - task_id: "risk_assessment"
          budget: 50000
          agent_profile: "risk_assessor"
          inputs_from: ["research_a", "research_b", "research_c"]
      gate:
        condition: "all_tasks_complete"
        quality_check: "analysis_depth >= 0.7"

    - wave_id: 3
      name: "Integration"
      depends_on: [2]
      tasks:
        - task_id: "final_report"
          budget: 80000
          agent_profile: "technical_writer"
          inputs_from: ["cross_analysis", "risk_assessment"]
```

### Wave Sizing Algorithm

```
Input: task_list, dependency_graph, total_budget
Output: wave_schedule

1. Topological sort tasks by dependency_graph
2. Assign each task to the earliest wave where all dependencies are satisfied
3. For each wave:
   a. Sum task budgets
   b. If sum > total_budget: split wave (move lowest-priority tasks to next wave)
   c. If sum < total_budget * 0.5: consider merging with adjacent wave (if dependencies allow)
4. Add quality gates between waves
```

---

## Anti-Pattern

What happens when Wave Scheduler is misapplied or partially applied:

- **[F001] Wave Overload** — Packing too many tasks into a single wave, exceeding available resources. A wave with 8 tasks but budget for 4 produces the same degradation as all-at-once execution. The wave boundary provides no benefit if the wave itself is overcrowded. The root cause is treating wave boundaries as organizational labels rather than resource checkpoints. Fix: enforce budget constraints at wave construction time, not at execution time.

- **[F002] Sequential Fallback** — Overreacting to coordination complexity by running all tasks sequentially — one agent at a time. This eliminates all parallelism benefits and dramatically increases wall-clock time. The system regresses from "multi-agent" to "single-agent-many-tasks." The root cause is fear of coordination complexity. Fix: use dependency analysis to find tasks that genuinely can run in parallel, even if only 2-3 at a time. Some parallelism is vastly better than none.

- **[F003] Dependency Blindness** — Assigning tasks to waves without analyzing dependencies. Two tasks that should be sequential (because one consumes the other's output) are placed in the same wave. The dependent task either fails, blocks, or works with stale data. The root cause is treating wave assignment as a scheduling problem (balance load across waves) rather than a dependency problem (respect data flow). Fix: always derive wave structure from the dependency graph first, then optimize for load balance within those constraints.

- **[F004] Wave Rigidity** — Defining wave structure statically at plan time and never adjusting during execution. When a wave-1 task fails or takes 3x longer than expected, the schedule cannot adapt — wave 2 either waits indefinitely or proceeds with incomplete inputs. Fix: implement wave-level timeout and fallback policies. If a task exceeds its time budget, the scheduler can reassign, retry, or proceed without the stalled task's output (with appropriate quality warnings).

---

## Failure Catalog

Real examples drawn from production multi-agent system execution history.

| ID | Failure | Root Cause | Detection Point | Impact |
|----|---------|-----------|-----------------|--------|
| FC-01 | 7 agents launched simultaneously; 3 produced outputs that conflicted with each other because they read the same source files and made incompatible assumptions | No wave structure; all tasks launched at once regardless of shared-resource conflicts | Detected during output integration — conflicting modifications to the same files | 2 hours of rework to reconcile conflicts; 3 agents' work discarded |
| FC-02 | Agent needed another agent's output as input but both were in the same wave; dependent agent used an empty file as input and produced garbage | Dependency Blindness (F003): dependency was implicit (not declared in task spec) and missed during wave planning | Detected at output review — output contained references to "undefined" data | Entire task had to be re-run after the dependency was satisfied |
| FC-03 | Team switched from 5-agent parallel execution to fully sequential after experiencing coordination issues | Sequential Fallback (F002): reaction to FC-01 eliminated all parallelism | Wall-clock time for the task set tripled | Team concluded "multi-agent doesn't work" when the real issue was wave design |
| FC-04 | Wave 1 had 6 tasks with a total budget exceeding available capacity; all 6 produced lower-quality output | Wave Overload (F001): wave sizing ignored budget constraints | Quality scores for wave 1 outputs averaged 30% lower than when the same tasks were run in 2 waves of 3 | Downstream waves received degraded inputs, compounding the quality loss |

---

## Interaction Catalog

How Wave Scheduler interacts with other CQE patterns.

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **01 Attention Budget** | requires | Budget determines wave capacity. Without budget information, the scheduler cannot determine how many tasks fit in a wave. Budget-unaware wave scheduling leads to Wave Overload (F001). |
| **02 Context Gate** | complements | Wave boundaries are natural context gate points. Between waves, apply Context Gate to filter the current wave's outputs before passing them to the next wave. This prevents context contamination across wave boundaries. |
| **03 Cognitive Profile** | interacts with | Profile assignment influences wave composition. A wave combining complementary profiles (researcher + critic) produces better outputs than a wave with duplicate profiles. The scheduler should consider profile diversity when assigning tasks to waves. |
| **05 Assumption Mutation** | sequences with | Mutation testing naturally fits as a dedicated wave after the primary work wave. Wave 1: produce the artifact. Wave 2: mutate and test the artifact. Wave 3: repair based on mutation results. This three-wave pattern is a recurring idiom in CQE systems. |
| **06 Experience Distillation** | feeds into | Wave completion is a natural signal extraction trigger. Each wave provides structured execution data (task outcomes, budget utilization, quality scores) that feeds into experience distillation. Historical wave performance data improves future wave sizing. |
| **07 File-Based I/O** | requires | Wave boundaries need reliable state transfer. When wave 1 completes, its outputs must be reliably available to wave 2. File-based communication provides the persistence, auditability, and concurrency safety that wave boundaries demand. In-memory state transfer across wave boundaries is fragile and un-auditable. |
| **08 Template-Driven Role** | complements | Templates can encode wave-aware output formats. A wave-1 research template specifies output format that a wave-2 analysis template expects as input. This creates a contract between waves that prevents integration failures. |

---

## Known Uses

### 1. Production Multi-Agent Development System — Hierarchical Wave Execution

A production multi-agent system implemented Wave Scheduler to coordinate 7 parallel agents:

- **Wave 1 (Exploration)**: 4 agents independently researched different aspects of a problem domain. Each agent had a distinct cognitive profile and operated in an isolated context
- **Wave 2 (Analysis)**: 1 agent synthesized the 4 exploration outputs; 1 agent performed adversarial critique. The synthesis agent received filtered outputs via Context Gate
- **Wave 3 (Integration)**: 1 agent produced the final deliverable incorporating analysis and critique
- **Result**: The 3-wave approach produced significantly higher quality output than the previous approach of launching all 7 agents at once. The key improvement was that wave 2 received clean, complete inputs from wave 1, rather than racing against still-running exploration tasks

### 2. Multi-Perspective Decision Analysis

A decision analysis framework used waves to prevent anchoring bias:

- **Wave 1**: Independent perspective agents (each with a distinct Cognitive Profile) analyzed the decision in parallel, isolated from each other
- **Wave 2**: A cross-critique agent received all wave-1 outputs and identified contradictions, blind spots, and areas of agreement
- **Wave 3**: A synthesis agent produced a Decision Brief incorporating all perspectives and the critique

The wave structure was essential for preventing anchoring — if perspective agents could see each other's outputs during analysis (as in a single-wave design), later perspectives would anchor to earlier ones.

### 3. Document Processing Pipeline

A document analysis pipeline used waves to manage dependency chains:

- **Wave 1**: Extract structure, identify sections, classify content
- **Wave 2**: Analyze each section in parallel (with budget proportional to section complexity)
- **Wave 3**: Cross-reference findings across sections, identify contradictions
- **Wave 4**: Generate final report with integrated findings

Each wave's quality gate prevented low-quality extractions from wave 1 from corrupting downstream analysis.

---

## Implementation Guidance

### Step 1: Map Task Dependencies

Before designing waves, create a dependency graph:

```yaml
# Identify task dependencies
dependency_map:
  research_a: []                    # No dependencies — wave 1 candidate
  research_b: []                    # No dependencies — wave 1 candidate
  research_c: []                    # No dependencies — wave 1 candidate
  analysis:   [research_a, research_b, research_c]  # Depends on all research
  critique:   [research_a, research_b, research_c]  # Depends on all research
  report:     [analysis, critique]  # Depends on analysis and critique
```

### Step 2: Assign Tasks to Waves

```yaml
# Derive wave structure from dependency graph
wave_schedule:
  wave_1:
    tasks: [research_a, research_b, research_c]
    total_budget: 180000
    rationale: "All independent; can run in parallel"

  wave_2:
    tasks: [analysis, critique]
    depends_on: [wave_1]
    total_budget: 130000
    rationale: "Both depend on wave 1 outputs; independent of each other"

  wave_3:
    tasks: [report]
    depends_on: [wave_2]
    total_budget: 80000
    rationale: "Depends on wave 2 outputs"
```

### Step 3: Add Quality Gates

```yaml
# Quality gates between waves
gates:
  wave_1_to_2:
    check: "All research outputs exist and are non-empty"
    action_on_fail: "Re-run failed research task; do not proceed to wave 2"

  wave_2_to_3:
    check: "Analysis covers all research themes; critique identifies at least 3 issues"
    action_on_fail: "Flag for human review before proceeding"
```

### Step 4: Monitor and Adjust

Track wave-level metrics to improve future scheduling:

```yaml
# Wave execution metrics
wave_metrics:
  wave_id: 1
  planned_tasks: 3
  completed_tasks: 3
  total_budget_allocated: 180000
  total_budget_consumed: 142000
  utilization: 0.79
  wall_clock_time: "12m"
  quality_gate_passed: true
  notes: "research_b finished in 40% of budget — consider reducing allocation"
```

---

## Evidence

- **Level B**: Confirmed across 2 projects in a production multi-agent system. Wave-based scheduling showed:
  - Higher output quality compared to all-at-once execution, particularly for tasks with data dependencies
  - Reduction in rework caused by dependency violations (agents consuming incomplete inputs)
  - Improved resource utilization — wave sizing based on attention budget reduced both overallocation and quality crashes
  - The most dramatic improvement was in integration quality — when wave boundaries ensured clean inputs, the final integration step produced significantly more coherent output

- **Limitations of current evidence**:
  - No controlled A/B test (Level A) comparing wave-based vs. all-at-once for identical task sets
  - Optimal wave sizing is still determined by heuristic rather than formal analysis
  - Observed improvements may partly reflect better task decomposition (which wave planning forces) rather than wave scheduling per se

- **Upgrade path to Level A**: Run controlled experiments comparing:
  - Treatment A: all-at-once execution (all tasks launched simultaneously)
  - Treatment B: wave-based execution (dependency-derived waves with quality gates)
  - Treatment C: fully sequential execution (one task at a time)
  - Measure: output quality, wall-clock time, rework rate, resource utilization
  - Required sample: 30+ comparable task sets for statistical significance
  - This would quantify the trade-off between parallelism and coordination overhead
