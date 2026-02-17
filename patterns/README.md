# CQE Patterns

> Cognitive Quality Engineering pattern catalog for LLM agent systems.

**Status**: Phase 1 - In Development

## Overview

CQE Patterns defines a structured vocabulary for designing cognitive quality into LLM agent systems. Inspired by GoF Design Patterns, each pattern captures a recurring problem in agent design and provides a proven solution, along with anti-patterns and failure catalogs to prevent misuse.

## Core Patterns (8)

| # | Pattern | Problem |
|---|---------|---------|
| 01 | Attention Budget | Uncontrolled token consumption degrades output quality |
| 02 | Context Gate | Irrelevant context contaminates agent reasoning |
| 03 | Cognitive Profile | Generic personas produce shallow, undifferentiated analysis |
| 04 | Wave Scheduler | Sequential analysis creates anchoring bias between perspectives |
| 05 | Assumption Mutation | Untested assumptions propagate through document chains |
| 06 | Experience Distillation | Valuable operational knowledge is lost between sessions |
| 07 | File-Based I/O | Direct inter-agent communication creates race conditions and coupling |
| 08 | Template-Driven Role | Ad-hoc role definitions lead to inconsistent agent behavior |

## Pattern Format

Each pattern follows a structured format:

```
# Pattern: [Name]
## Problem
## Solution
## Anti-Pattern: [Name]
## Failure Catalog
## Evidence Level (A/B/C/D)
## Interaction Catalog
## Weight Classification (Foundational/Situational/Advanced)
```

### Evidence Levels

| Level | Definition |
|-------|-----------|
| A | Quantitatively verified (A/B test results available) |
| B | Confirmed across multiple projects (inductively derived) |
| C | Theoretical reasoning (design principle) |
| D | Hypothesis stage (verification needed) |

### Weight Classification

| Weight | When to Apply |
|--------|--------------|
| Foundational | Every LLM agent system should implement these |
| Situational | Apply under specific conditions |
| Advanced | Effective only in mature systems |

## Directory Structure

```
patterns/
├── README.md                       # This file
├── 01_attention_budget.md
├── 02_context_gate.md
├── 03_cognitive_profile.md
├── 04_wave_scheduler.md
├── 05_assumption_mutation.md
├── 06_experience_distillation.md
├── 07_file_based_io.md
├── 08_template_driven_role.md
└── anti-patterns/
    └── README.md
```
