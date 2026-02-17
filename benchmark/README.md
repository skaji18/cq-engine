# CQ Benchmark

> A standardized measurement framework for cognitive quality in LLM agent systems.

**Status**: Phase 1 - In Development

## Overview

CQ Benchmark provides a common measurement foundation for evaluating cognitive quality across all CQE tools and patterns. Without standardized metrics, each tool would define its own success criteria, making cross-comparison impossible.

An engineering discipline requires measurement. CQ Benchmark is the measurement layer for Cognitive Quality Engineering.

## 4-Axis Metric Framework

### 1. Context Health Score

Measures the quality of information fed to LLM agents.

| Metric | Description |
|--------|-------------|
| Information Density | Relevant information per token |
| Contamination Rate | Proportion of irrelevant information |
| Freshness | How current the information is |

### 2. Decision Quality Score

Measures the quality of agent reasoning and judgment.

| Metric | Description |
|--------|-------------|
| Perspective Diversity | Number of truly independent viewpoints |
| Anchoring Elimination | Degree of bias removal in multi-perspective analysis |
| Blind Spot Coverage | Proportion of potential blind spots identified |

### 3. Document Integrity Score

Measures the structural and logical quality of generated documents.

| Metric | Description |
|--------|-------------|
| Mutation Kill Rate | Proportion of injected mutations detected by review |
| Contradiction Count | Number of internal contradictions |
| Ambiguity Score | Degree of ambiguous or vague statements |

### 4. Evolution Score

Measures the system's ability to learn and improve over time.

| Metric | Description |
|--------|-------------|
| Pattern Compliance | Adherence to CQE patterns |
| Learning Accumulation Rate | Speed of experience distillation |
| Recurrence Rate | Frequency of previously-solved problems reappearing |

## Directory Structure

```
benchmark/
├── README.md                    # This file
├── spec.md                      # Full 4-axis specification
└── measures/                    # Individual metric definitions
    ├── context_health.md
    ├── decision_quality.md
    ├── document_integrity.md
    └── evolution.md
```

## Design Principles

- **Quantitative**: Every metric must be measurable, not subjective.
- **Composable**: Individual metrics can be combined or used independently.
- **Tool-agnostic**: Metrics apply regardless of which CQE tool generates the data.
- **Evidence-driven**: Metric thresholds are calibrated from real usage data, not arbitrary.
