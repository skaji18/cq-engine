# CQ Benchmark v0.1 — Full Specification

> **Version**: 0.1.0
> **Status**: Phase 1 — Specification
> **Principle**: Quantitative, Composable, Tool-Agnostic, Evidence-Driven

---

## 1. Overview

CQ Benchmark defines a standardized measurement framework for **Cognitive Quality** (CQ) in LLM agent systems. It provides a common language for evaluating whether agents manage attention, make decisions, produce reliable documents, and improve over time.

An engineering discipline requires measurement. CQ Benchmark is the measurement layer for Cognitive Quality Engineering (CQE).

### 1.1 Why 4 Axes?

LLM agent quality cannot be captured by a single metric. Four orthogonal axes cover the full lifecycle of cognitive work:

```
                    ┌─────────────────────┐
                    │   Context Health    │  INPUT quality
                    │   "What goes in"    │  (before execution)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Decision Quality   │  PROCESS quality
                    │  "How it reasons"   │  (during execution)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Document Integrity  │  OUTPUT quality
                    │  "What comes out"   │  (after execution)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │     Evolution       │  IMPROVEMENT quality
                    │ "How it gets better"│  (across executions)
                    └─────────────────────┘
```

Each axis has 3 sub-metrics (12 total), ensuring granularity without overwhelming complexity.

### 1.2 Axis Summary

| # | Axis | Purpose | Sub-Metrics | CQE Pattern Link |
|---|------|---------|-------------|------------------|
| 1 | **Context Health** | Measure quality of information flowing through agents | Information Density, Contamination Level, Freshness | Attention Budget, Context Gate |
| 2 | **Decision Quality** | Measure quality of agent decision-making | Perspective Diversity, Anchoring Elimination, Blind-Spot Coverage | Cognitive Profile, Assumption Mutation, Wave Scheduler |
| 3 | **Document Integrity** | Measure quality of produced documents | Mutation Kill Rate, Contradiction Count, Ambiguity Score | Assumption Mutation, Template-Driven Role |
| 4 | **Evolution** | Measure system's ability to learn and improve | Pattern Conformance, Learning Accumulation Rate, Recurrence Rate | Experience Distillation, File-Based I/O |

---

## 2. Measurement Framework Design

### 2.1 Score Computation

Each sub-metric produces a **normalized score** in the range [0.0, 1.0], where:
- **1.0** = perfect (e.g., zero contamination, all mutations killed)
- **0.0** = worst possible (e.g., entirely irrelevant context, no mutations detected)

**Axis Score** = weighted average of its 3 sub-metrics:

```
AxisScore = w1 * SubMetric1 + w2 * SubMetric2 + w3 * SubMetric3
where w1 + w2 + w3 = 1.0
```

Default weights are equal (1/3 each). Users may customize weights based on their priorities.

**Overall CQ Score** = weighted average of 4 axis scores:

```
CQScore = wCH * ContextHealth + wDQ * DecisionQuality
        + wDI * DocumentIntegrity + wEV * Evolution
where wCH + wDQ + wDI + wEV = 1.0
```

Default weights: CH=0.25, DQ=0.30, DI=0.25, EV=0.20

Decision Quality receives the highest default weight because reasoning quality is the most impactful factor for agent-based systems, while Evolution receives the lowest because it measures long-term improvement and is less critical for individual task assessment.

### 2.2 Score Interpretation

| CQ Score Range | Grade | Interpretation |
|---------------|-------|----------------|
| 0.80 - 1.00 | **A** | Excellent — systematic cognitive quality management |
| 0.60 - 0.79 | **B** | Good — most quality aspects addressed |
| 0.40 - 0.59 | **C** | Fair — significant gaps in quality management |
| 0.20 - 0.39 | **D** | Poor — minimal quality practices in place |
| 0.00 - 0.19 | **F** | Failing — no meaningful quality management |

### 2.3 Measurement Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Snapshot** | Measure a single execution at a point in time | Ad-hoc quality check |
| **Comparative** | Measure before/after an intervention | Evaluating a change |
| **Trending** | Measure over multiple executions over time | Monitoring improvement |

---

## 3. Axis Relationships and Data Flow

```
┌──────────────────────────────────────────────────────────┐
│                    DATA SOURCES                          │
├────────────┬────────────┬────────────┬───────────────────┤
│ Agent      │ Execution  │ Output     │ Historical        │
│ Config     │ Logs       │ Documents  │ Records           │
│ (YAML/MD)  │ (traces)   │ (MD/text)  │ (past runs)       │
└─────┬──────┴─────┬──────┴─────┬──────┴────────┬──────────┘
      │            │            │               │
      ▼            ▼            ▼               ▼
┌──────────┐ ┌──────────┐ ┌──────────┐  ┌──────────┐
│ Context  │ │ Decision │ │ Document │  │Evolution │
│ Health   │ │ Quality  │ │ Integrity│  │          │
│          │ │          │ │          │  │          │
│ 3 subs   │ │ 3 subs   │ │ 3 subs   │  │ 3 subs   │
└─────┬────┘ └─────┬────┘ └─────┬────┘  └────┬─────┘
      │            │            │             │
      └────────────┼────────────┼─────────────┘
                   ▼
          ┌────────────────┐
          │  CQ Score      │
          │  (composite)   │
          └────────────────┘
```

### 3.1 Cross-Axis Dependencies

| Upstream Axis | Downstream Axis | Relationship |
|---------------|-----------------|-------------|
| Context Health | Decision Quality | Poor input quality degrades decision quality |
| Decision Quality | Document Integrity | Flawed reasoning produces flawed documents |
| Context Health + Decision Quality + Document Integrity | Evolution | All three axes feed data into evolution tracking |
| Evolution | Context Health | Learned experience improves context filtering over time |

---

## 4. Baseline Definition Method

### 4.1 Baseline Types

| Type | Description | When to Use |
|------|-------------|-------------|
| **Naive Baseline** | Score with no CQE practices applied | First-time adoption |
| **Pre-intervention Baseline** | Score before a specific change | A/B testing |
| **Industry Baseline** | Average score across comparable systems | Benchmarking |

### 4.2 Baseline Measurement Protocol

1. **Select sample**: Choose N representative task executions (minimum N=10)
2. **Measure each axis**: Compute all 12 sub-metrics for each execution
3. **Compute statistics**: Mean, median, standard deviation for each sub-metric
4. **Record baseline**: Store as `baseline_YYYY-MM-DD.json`
5. **Define targets**: Set improvement goals (e.g., "Improve Context Health from 0.45 to 0.65")

### 4.3 Minimum Sample Sizes

| Purpose | Minimum N | Rationale |
|---------|-----------|-----------|
| Snapshot assessment | 5 | Quick directional check |
| Comparative study | 10 per condition | Statistical significance |
| Trending analysis | 20+ over time | Detect meaningful trends |

---

## 5. Integration Points

### 5.1 CQE Tool Integration

| CQE Tool | Feeds Data To | Axis | Mechanism |
|----------|--------------|------|-----------|
| **cqlint** | Pattern Conformance | Evolution | `cqlint check .` output → conformance score |
| **MutaDoc** | Mutation Kill Rate, Contradiction Count | Document Integrity | MutaDoc report → kill rate and contradiction data |
| **ThinkTank** | Perspective Diversity, Anchoring Elimination | Decision Quality | ThinkTank output analysis → diversity and independence metrics |
| **CQ MCP Server** | All axes | All | Telemetry collection from MCP tool usage |

### 5.2 Hypothesis Validation Mapping

CQ Benchmark metrics serve as the primary validation instrument for hypotheses defined in all roadmap phases:

| Phase | Hypothesis Domain | Relevant CQ Benchmark Axis |
|-------|-------------------|---------------------------|
| Phase 1 | Pattern effectiveness | Evolution (Pattern Conformance) |
| Phase 2 | MutaDoc detection accuracy | Document Integrity (Mutation Kill Rate) |
| Phase 2 | ThinkTank diversity gain | Decision Quality (Perspective Diversity, Anchoring Elimination) |
| Phase 3 | MCP distribution effectiveness | All axes (before/after MCP adoption) |
| Phase 4 | ThinkTank production readiness | Decision Quality (all 3 sub-metrics) |

---

## 6. Detailed Axis Specifications

Each axis has a dedicated specification document with:
- Formal definitions and formulas
- Worked examples
- Edge cases and limitations
- Baseline measurement plan
- CQE Pattern correspondence

| Axis | Specification File |
|------|--------------------|
| Context Health | [measures/context_health.md](measures/context_health.md) |
| Decision Quality | [measures/decision_quality.md](measures/decision_quality.md) |
| Document Integrity | [measures/document_integrity.md](measures/document_integrity.md) |
| Evolution | [measures/evolution.md](measures/evolution.md) |

---

## 7. Limitations and Future Work

### 7.1 v0.1 Limitations

- **No automated measurement tooling**: v0.1 is specification-only. Measurement scripts are Phase 2+ deliverables.
- **Baselines are TBD**: Actual baseline values require measurement on real execution data.
- **Semantic analysis required**: Several sub-metrics (e.g., Information Density, Perspective Diversity) require LLM-based semantic analysis, not purely mechanical computation.
- **Single-system focus**: v0.1 assumes a single agent system. Multi-system comparison methodology is future work.

### 7.2 Evolution Path

| Version | Scope |
|---------|-------|
| v0.1 | Specification + formulas (this document) |
| v0.2 | Baseline measurements on real data |
| v0.3 | Automated measurement scripts |
| v1.0 | Full integration with cqlint, MutaDoc, ThinkTank |
