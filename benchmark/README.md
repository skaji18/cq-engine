# CQ Benchmark

> A standardized measurement framework for cognitive quality in LLM agent systems.

**Version**: 0.1.0
**Status**: Phase 1 — Specification Complete

## Overview

CQ Benchmark provides a common measurement foundation for evaluating cognitive quality across all CQE tools and patterns. Without standardized metrics, each tool would define its own success criteria, making cross-comparison impossible.

An engineering discipline requires measurement. CQ Benchmark is the measurement layer for Cognitive Quality Engineering.

## 4-Axis Metric Framework

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

### Axis Summary

| # | Axis | Purpose | Sub-Metrics |
|---|------|---------|-------------|
| 1 | **Context Health** | Measure quality of information fed to agents | Information Density, Contamination Level, Freshness |
| 2 | **Decision Quality** | Measure quality of agent reasoning | Perspective Diversity, Anchoring Elimination, Blind-Spot Coverage |
| 3 | **Document Integrity** | Measure quality of produced documents | Mutation Kill Rate, Contradiction Count, Ambiguity Score |
| 4 | **Evolution** | Measure ability to learn and improve | Pattern Conformance, Learning Accumulation Rate, Recurrence Rate |

**Total**: 4 axes x 3 sub-metrics = **12 quantitative indicators**

## Scoring

Each sub-metric produces a normalized score in [0.0, 1.0]. Axis scores are weighted averages of their sub-metrics. The overall CQ Score is a weighted average of axis scores.

| CQ Score | Grade | Interpretation |
|----------|-------|----------------|
| 0.80-1.00 | **A** | Excellent cognitive quality management |
| 0.60-0.79 | **B** | Good — most quality aspects addressed |
| 0.40-0.59 | **C** | Fair — significant gaps |
| 0.20-0.39 | **D** | Poor — minimal practices |
| 0.00-0.19 | **F** | No meaningful quality management |

## Directory Structure

```
benchmark/
├── README.md                          # This file
├── spec.md                            # Full 4-axis specification
└── measures/
    ├── context_health.md              # Axis 1: Context Health Score
    ├── decision_quality.md            # Axis 2: Decision Quality Score
    ├── document_integrity.md          # Axis 3: Document Integrity Score
    └── evolution.md                   # Axis 4: Evolution Score
```

## Quick Reference

### CQE Pattern → Benchmark Mapping

| CQE Pattern | Primary Axis | Primary Sub-Metric |
|-------------|-------------|-------------------|
| #01 Attention Budget | Context Health | Information Density |
| #02 Context Gate | Context Health | Contamination Level |
| #03 Cognitive Profile | Decision Quality | Perspective Diversity |
| #04 Wave Scheduler | Decision Quality | Anchoring Elimination |
| #05 Assumption Mutation | Document Integrity | Mutation Kill Rate |
| #06 Experience Distillation | Evolution | Learning Accumulation Rate |
| #07 File-Based I/O | Evolution | Pattern Conformance |
| #08 Template-Driven Role | Document Integrity | Ambiguity Score |

### CQE Tool → Benchmark Integration

| Tool | Benchmark Role |
|------|---------------|
| **cqlint** | Computes Pattern Conformance (EV-1) |
| **MutaDoc** | Computes Mutation Kill Rate (DI-1), Contradiction Count (DI-2) |
| **ThinkTank** | Computes Perspective Diversity (DQ-1), Anchoring Elimination (DQ-2) |
| **CQ MCP Server** | Collects telemetry for all axes |

## Quick Start (Future)

Once measurement tooling is available (v0.3+):

```bash
# Run a full CQ Benchmark assessment
cq-benchmark assess ./my-agent-project/

# Output:
# CQ Score: 0.67 (Grade B)
#   Context Health:     0.72  [██████████████░░░░░░]
#   Decision Quality:   0.65  [█████████████░░░░░░░]
#   Document Integrity: 0.70  [██████████████░░░░░░]
#   Evolution:          0.58  [███████████░░░░░░░░░]
```

## Design Principles

- **Quantitative**: Every metric has a formula. No subjective ratings.
- **Composable**: Use individual sub-metrics, axis scores, or overall CQ Score.
- **Tool-agnostic**: Metrics apply regardless of which CQE tool generates the data.
- **Evidence-driven**: Thresholds calibrated from real usage data, not arbitrary.
