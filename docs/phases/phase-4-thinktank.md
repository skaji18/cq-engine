# Phase 4: Expansion (ThinkTank) — Detailed Implementation Plan

> **timestamp**: 2026-02-17

---

## 1. 8 Persona Design Tasks

### 1.1 Persona Overview

ThinkTank uses 8 specialized personas across 4 categories. Each persona analyzes decisions from an independent context, ensuring zero anchoring contamination between perspectives.

| # | Persona | Category | Domain | Key Concern |
|---|---------|----------|--------|-------------|
| P1 | **CFO** | Business | Finance & Capital | Financial viability, cash flow, ROI, cost structure |
| P2 | **CTO** | Business | Technology & Engineering | Technical feasibility, scalability, tech debt, architecture |
| P3 | **CMO** | Business | Marketing & Growth | Market fit, competitive positioning, user acquisition, brand |
| P4 | **Investor** | Business | Investment & Returns | Valuation, exit potential, market timing, capital efficiency |
| P5 | **Customer** | Stakeholder | End-User Experience | Usability, value perception, switching costs, pain points |
| P6 | **Employee** | Stakeholder | Workforce & Operations | Workload impact, skill requirements, morale, retention |
| P7 | **Regulator** | Stakeholder | Compliance & Governance | Legal compliance, data privacy, regulatory risk, liability |
| P8 | **Devil's Advocate** | Meta | Adversarial Analysis | Assumptions challenged, worst-case scenarios, hidden risks |

### 1.2 Persona Template Design Tasks

Each persona requires a Markdown prompt template that defines its cognitive profile, analysis framework, and output format.

| Task ID | Task | Persona | Deliverable | Size |
|---------|------|---------|-------------|:----:|
| T4.1.1 | Design CFO persona template | CFO | `personas/business/cfo.md` | S |
| T4.1.2 | Design CTO persona template | CTO | `personas/business/cto.md` | S |
| T4.1.3 | Design CMO persona template | CMO | `personas/business/cmo.md` | S |
| T4.1.4 | Design Investor persona template | Investor | `personas/business/investor.md` | S |
| T4.1.5 | Design Customer persona template | Customer | `personas/stakeholders/customer.md` | S |
| T4.1.6 | Design Employee persona template | Employee | `personas/stakeholders/employee.md` | S |
| T4.1.7 | Design Regulator persona template | Regulator | `personas/stakeholders/regulator.md` | S |
| T4.1.8 | Design Devil's Advocate persona template | Devil's Advocate | `personas/meta/devils_advocate.md` | M |
| T4.1.9 | Design custom persona specification | User-defined | `personas/custom/TEMPLATE.md` | S |
| T4.1.10 | Design 3-persona quick mode subset | CFO + CTO + Devil's Advocate | `personas/presets/quick_3.md` | S |

### 1.3 Persona Template Structure

Each persona template must follow this structure:

```markdown
# Persona: [Name]

## Identity
- Role and expertise domain
- Years of experience / seniority level
- Primary concerns and evaluation criteria

## Analysis Framework
- Key questions this persona always asks
- Metrics and indicators this persona prioritizes
- Decision heuristics and mental models

## Output Format
- Structured analysis sections
- Risk assessment criteria
- Recommendation format

## Anti-Anchoring Directive
- "You are analyzing this decision INDEPENDENTLY."
- "You have NOT seen any other analysis."
- "Your perspective must be grounded solely in your expertise domain."
```

### 1.4 Independence Guarantees

The structural mechanism that ensures perspective independence:

| Mechanism | Description |
|-----------|-------------|
| **Isolated Context** | Each persona runs as a separate Claude Code Task (subagent) with its own context window |
| **No Shared State** | No persona receives output from any other persona during Wave 1 |
| **Anti-Anchoring Directive** | Each template includes an explicit directive that the persona has not seen other analyses |
| **Parallel Execution** | All 8 personas launch simultaneously via Task tool, eliminating sequential contamination |
| **File-Based I/O** | Each persona writes its analysis to a separate file (`output/wave1/persona_{name}.md`), preventing cross-read |

---

## 2. 3-Wave Execution Template Design Tasks

### 2.1 Wave Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  INPUT: Decision question + context documents                          │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ WAVE 1: Independent Analysis                                     │  │
│  │                                                                  │  │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌───┐│  │
│  │  │ CFO │ │ CTO │ │ CMO │ │ INV │ │ CUS │ │ EMP │ │ REG │ │ DA ││  │
│  │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └─┬─┘│  │
│  │     │       │       │       │       │       │       │       │   │  │
│  │     ▼       ▼       ▼       ▼       ▼       ▼       ▼       ▼   │  │
│  │  8 independent analysis files (parallel, zero cross-contamination)│  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
│                                 │                                      │
│  ┌──────────────────────────────▼───────────────────────────────────┐  │
│  │ INFORMATION GATE: Collect all 8 analyses                         │  │
│  │ (Context Gate pattern: structured summaries only, not raw output) │  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
│                                 │                                      │
│  ┌──────────────────────────────▼───────────────────────────────────┐  │
│  │ WAVE 2: Cross-Critique                                           │  │
│  │                                                                  │  │
│  │  Each persona receives ALL other analyses and critiques them      │  │
│  │  from its own domain expertise.                                   │  │
│  │  Output: Critique reports + Contradiction Heatmap data            │  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
│                                 │                                      │
│  ┌──────────────────────────────▼───────────────────────────────────┐  │
│  │ WAVE 3: Synthesis                                                │  │
│  │                                                                  │  │
│  │  Single synthesizer agent receives all analyses + all critiques   │  │
│  │  Output: Decision Brief (final judgment + risk matrix +           │  │
│  │          Anchoring Visibility Score + Contradiction Heatmap)      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  OUTPUT: Decision Brief (Markdown)                                     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Wave 1: Independent Analysis

| Attribute | Detail |
|-----------|--------|
| **Name** | Independent Analysis |
| **Purpose** | Generate 8 genuinely independent perspectives on the decision question, with zero anchoring contamination |
| **Execution** | 8 parallel Task tool invocations, each with its own persona template and anti-anchoring directive |

**Input/Output Specification:**

| Direction | Format | Content |
|-----------|--------|---------|
| **Input** | Decision question (text) + context documents (file paths) | The same input is provided to all 8 personas identically |
| **Output** | 8 separate Markdown files: `output/wave1/{persona_name}.md` | Each file contains: summary judgment, key arguments, risk assessment, confidence level (1-5), recommendation |

**Information Isolation:**

| Rule | Mechanism |
|------|-----------|
| No shared context | Each persona is a separate Task tool subagent |
| No cross-reading | Personas write to separate files; no file-read of other persona outputs during Wave 1 |
| Identical input | All personas receive exactly the same decision question and context |
| Anti-anchoring prompt | Template includes explicit directive: "You have NOT seen any other analysis" |

**Completion Criteria:**
- All 8 persona output files exist and are non-empty
- Each output follows the structured format (summary, arguments, risks, confidence, recommendation)
- No evidence of cross-contamination (no references to other personas' analyses)

**Design Task:**

| Task ID | Task | Deliverable | Size |
|---------|------|-------------|:----:|
| T4.2.1 | Design Wave 1 execution template | `waves/wave1_independent.md` | M |
| T4.2.2 | Design Wave 1 orchestration script | `thinktank.sh` (Wave 1 section) | M |

### 2.3 Wave 2: Cross-Critique

| Attribute | Detail |
|-----------|--------|
| **Name** | Cross-Critique |
| **Purpose** | Each persona critiques all other analyses from its own domain expertise, identifying blind spots, invalid assumptions, and contradictions |
| **Execution** | 8 parallel Task tool invocations; each persona receives all 8 Wave 1 outputs |

**Input/Output Specification:**

| Direction | Format | Content |
|-----------|--------|---------|
| **Input** | All 8 Wave 1 output files + original decision question | Each persona reads all other analyses |
| **Output** | 8 critique files: `output/wave2/{persona_name}_critique.md` | Each file contains: per-persona critique, identified blind spots, contradictions found, revised confidence level |

**Information Gate (Wave 1 → Wave 2):**

| Aspect | Design |
|--------|--------|
| **What passes** | Structured summaries from Wave 1 (summary, key arguments, risks, recommendation) |
| **What is filtered** | Raw reasoning chains, intermediate drafts (Context Gate pattern applied) |
| **Anchoring risk** | Acceptable — Wave 2's purpose IS to read other analyses; independence was guaranteed in Wave 1 |

**Contradiction Heatmap Data Collection:**

During Wave 2, each persona records agreement/disagreement with every other persona on a 5-point scale:

```
             CFO  CTO  CMO  INV  CUS  EMP  REG  DA
CFO           -   +2   -1   +1   0    -2   +1   -3
CTO          +2    -   +1   0    -1   +1   -1   -2
...
```

Scale: -3 (strong disagreement) to +3 (strong agreement), 0 = neutral

**Completion Criteria:**
- All 8 critique files exist
- Each critique addresses every other persona's analysis
- Contradiction heatmap data matrix is complete (8x8, diagonal excluded)
- At least 3 blind spots identified across all critiques combined

**Design Task:**

| Task ID | Task | Deliverable | Size |
|---------|------|-------------|:----:|
| T4.2.3 | Design Wave 2 execution template | `waves/wave2_cross_critique.md` | M |
| T4.2.4 | Design contradiction heatmap data format | `waves/heatmap_format.md` | S |
| T4.2.5 | Design Wave 2 orchestration script | `thinktank.sh` (Wave 2 section) | M |

### 2.4 Wave 3: Synthesis

| Attribute | Detail |
|-----------|--------|
| **Name** | Synthesis |
| **Purpose** | Integrate all analyses and critiques into a single Decision Brief with final judgment, risk matrix, and quantified metrics |
| **Execution** | Single Task tool invocation with a dedicated synthesis persona |

**Input/Output Specification:**

| Direction | Format | Content |
|-----------|--------|---------|
| **Input** | All Wave 1 outputs (8 files) + all Wave 2 critiques (8 files) + contradiction heatmap data + original question | Full corpus of analysis |
| **Output** | Single Decision Brief: `output/decision_brief.md` | Contains all sections below |

**Decision Brief Structure:**

```markdown
# Decision Brief: [Question]

## Executive Summary
[2-3 paragraph synthesis of the decision]

## Recommendation
[GO / NO-GO / CONDITIONAL with conditions]

## Perspective Summary (8 rows)
| Persona | Position | Confidence | Key Argument |
|---------|----------|:----------:|-------------|
| CFO     | ...      | 4/5        | ...         |
| ...     | ...      | ...        | ...         |

## Contradiction Heatmap
[8x8 ASCII heatmap visualization]

## Key Debates
[Top 3-5 areas of strongest disagreement, with both sides]

## Blind Spots Identified
[Issues found during cross-critique that no single persona caught alone]

## Risk Matrix
| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| ...  | H/M/L      | H/M/L  | ...        |

## Parameter Sensitivity (if applicable)
[Results of parameter mutation tests]

## Anchoring Visibility Score
[Quantified score — see Section 3]

## Decision Replay Notes
[Guidance for future re-analysis]
```

**Completion Criteria:**
- Decision Brief contains all required sections
- Recommendation is clearly stated (GO / NO-GO / CONDITIONAL)
- Contradiction Heatmap is rendered
- Anchoring Visibility Score is calculated and included
- Risk matrix has at least 3 risks

**Design Task:**

| Task ID | Task | Deliverable | Size |
|---------|------|-------------|:----:|
| T4.2.6 | Design Wave 3 synthesis template | `waves/wave3_synthesis.md` | L |
| T4.2.7 | Design Decision Brief output format | `waves/decision_brief_format.md` | M |
| T4.2.8 | Design Wave 3 orchestration script | `thinktank.sh` (Wave 3 section) | M |

---

## 3. Anchoring Visibility Score Design Task

### 3.1 Definition

The **Anchoring Visibility Score (AVS)** quantifies how much anchoring bias would have affected a sequential analysis compared to ThinkTank's parallel analysis. It answers: "How much independent thinking did we gain by running perspectives in parallel?"

### 3.2 Calculation Method

**Step 1: Measure Perspective Diversity in Parallel Output (ThinkTank)**

For each pair of personas (i, j) in Wave 1, compute a **Perspective Similarity Score (PSS)**:

```
PSS(i, j) = similarity(analysis_i, analysis_j)
```

Where similarity is measured across 3 dimensions:
- **Conclusion similarity**: Do they reach the same recommendation? (0 = opposite, 1 = identical)
- **Argument overlap**: Jaccard similarity of key arguments cited
- **Risk overlap**: Jaccard similarity of risks identified

```
PSS(i, j) = 0.4 * conclusion_sim + 0.3 * argument_overlap + 0.3 * risk_overlap
```

**Average PSS (Parallel)**:
```
PSS_parallel = mean(PSS(i, j)) for all i ≠ j    (28 pairs from 8 personas)
```

**Step 2: Estimate Sequential Anchoring**

Run a **sequential baseline**: Generate the same 8 perspectives in a single context sequentially (simulating what ChatGPT does). Compute PSS for the sequential output:

```
PSS_sequential = mean(PSS(i, j)) for all i ≠ j in sequential output
```

**Step 3: Compute AVS**

```
AVS = (PSS_sequential - PSS_parallel) / PSS_sequential * 100
```

Interpretation:
- **AVS = 0%**: No anchoring detected (parallel = sequential). Parallel adds no value.
- **AVS = 30%**: Parallel analysis is 30% more diverse than sequential. Moderate anchoring eliminated.
- **AVS = 60%+**: Parallel analysis is dramatically more diverse. Strong anchoring was present in sequential.

**Step 4: Generation-Order Correlation (Supplementary)**

For the sequential baseline, measure correlation between generation order and perspective similarity to the first-generated perspective:

```
r = correlation(generation_order, similarity_to_first)
```

- Positive r in sequential = evidence of anchoring
- Zero r in parallel = evidence of independence

### 3.3 Visualization

```
Anchoring Visibility Score: 42%

Parallel (ThinkTank)              Sequential (Baseline)
┌────────────────────┐            ┌────────────────────┐
│ PSS = 0.31         │            │ PSS = 0.53         │
│ (low similarity =  │            │ (high similarity = │
│  diverse views)    │            │  anchored views)   │
│                    │            │                    │
│ ████░░░░░░ 31%     │            │ █████████░ 53%     │
└────────────────────┘            └────────────────────┘

Diversity gain: 42% more independent thinking
```

### 3.4 CQ Benchmark Integration

AVS maps to the **Decision Quality Score** axis of CQ Benchmark:

| CQ Benchmark Axis | AVS Mapping |
|-------------------|-------------|
| **Perspective Diversity** | Inverse of PSS_parallel (lower PSS = higher diversity) |
| **Anchoring Elimination** | AVS percentage directly |
| **Blind Spot Coverage** | Number of unique risks identified across all personas / total risks in Wave 2 |

### 3.5 Design Tasks

| Task ID | Task | Deliverable | Size |
|---------|------|-------------|:----:|
| T4.3.1 | Define PSS calculation methodology | `docs/avs_specification.md` | M |
| T4.3.2 | Implement sequential baseline generator | `mutation/sequential_baseline.sh` | M |
| T4.3.3 | Implement AVS calculator | `mutation/avs_calculator.sh` | M |
| T4.3.4 | Design AVS visualization format | `waves/avs_visualization.md` | S |
| T4.3.5 | Map AVS to CQ Benchmark Decision Quality axis | `benchmark/avs_mapping.md` | S |

### 3.6 Completion Criteria

- PSS calculation produces a float in [0.0, 1.0] for any persona pair
- AVS produces a percentage in [0%, 100%]
- Sequential baseline runs in the same environment as ThinkTank
- Visualization renders correctly in terminal and Markdown
- CQ Benchmark mapping is documented and validated against at least 3 test cases

---

## 4. MCP Integration Task

### 4.1 ThinkTank MCP Tool Design

ThinkTank integrates into the CQ MCP Server (Phase 3) as the `cq_engine__thinktank` tool.

**Tool Specification:**

| Attribute | Detail |
|-----------|--------|
| **Tool Name** | `cq_engine__thinktank` |
| **Description** | Run multi-perspective decision analysis with anti-anchoring parallel execution |
| **Input Schema** | `question` (string, required), `context_files` (string[], optional), `personas` (string[], optional, default: all 8), `mode` (enum: "full" / "quick", default: "full") |
| **Output** | Decision Brief (Markdown string) |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `question` | string | Yes | — | The decision question to analyze |
| `context_files` | string[] | No | [] | File paths providing context for the decision |
| `personas` | string[] | No | all 8 | Subset of personas to use (minimum 3) |
| `mode` | enum | No | "full" | "full" = 8 personas + 3 Waves; "quick" = 3 personas (CFO + CTO + Devil's Advocate) + 3 Waves |
| `include_avs` | boolean | No | true | Calculate and include Anchoring Visibility Score |
| `parameter_mutation` | object | No | null | Parameters to mutate for sensitivity analysis |

**Output Format:**

```json
{
  "decision_brief": "# Decision Brief: ...\n...",
  "anchoring_visibility_score": 42,
  "contradiction_count": 7,
  "recommendation": "CONDITIONAL",
  "personas_used": ["cfo", "cto", "cmo", "investor", "customer", "employee", "regulator", "devils_advocate"],
  "waves_completed": 3
}
```

### 4.2 Phase 3 Integration Points

| Integration Point | Description | Dependency |
|-------------------|-------------|------------|
| **MCP Server registration** | Add `cq_engine__thinktank` to `server.py` tool list | M3.1 (MCP server installable) |
| **Shared persona infrastructure** | ThinkTank personas use the same Cognitive Profile pattern as `cq_engine__persona` | Phase 1 (CQE Patterns) |
| **CQ Benchmark reporting** | Decision Quality Score from AVS feeds into `cq_engine__benchmark` | Phase 1 (Benchmark spec) |
| **Telemetry integration** | ThinkTank usage data feeds into local telemetry for pattern evolution | M3.3 (Telemetry collecting) |
| **Hooks integration** | Optional auto-trigger on complex decisions (TaskCompleted hook) | M3.2 (Hooks auto-trigger) |
| **MutaDoc shared core** | Devil's Advocate persona shares adversarial techniques with MutaDoc | Phase 2 (MutaDoc) |

### 4.3 MCP Tool Implementation Structure

```
mcp-server/tools/thinktank.py
├── ThinkTankTool class
│   ├── execute(question, context_files, personas, mode, ...)
│   │   ├── wave1_independent(question, context_files, personas)
│   │   ├── wave2_cross_critique(wave1_results, personas)
│   │   ├── wave3_synthesis(wave1_results, wave2_critiques)
│   │   └── calculate_avs(wave1_results)
│   └── validate_input(params)
├── Bash/CLI fallback: thinktank.sh
│   └── Same 3-Wave pipeline, file-based I/O
└── Tests
    ├── test_wave1_isolation.py
    ├── test_wave2_critique.py
    ├── test_wave3_synthesis.py
    └── test_avs_calculation.py
```

### 4.4 Design Tasks

| Task ID | Task | Deliverable | Size |
|---------|------|-------------|:----:|
| T4.4.1 | Design MCP tool input/output schema | `mcp-server/tools/thinktank_schema.md` | S |
| T4.4.2 | Implement ThinkTank MCP tool (Python) | `mcp-server/tools/thinktank.py` | L |
| T4.4.3 | Implement Bash/CLI fallback | `thinktank/thinktank.sh` | L |
| T4.4.4 | Design telemetry data points for ThinkTank | `mcp-server/telemetry/thinktank_metrics.md` | S |
| T4.4.5 | Write integration tests | `mcp-server/tools/tests/test_thinktank.py` | M |

### 4.5 Completion Criteria

- `cq_engine__thinktank` tool is callable via MCP protocol
- Full mode (8 personas, 3 Waves) produces a complete Decision Brief
- Quick mode (3 personas, 3 Waves) produces a valid Decision Brief
- Bash/CLI fallback (`thinktank.sh`) produces identical output to MCP tool
- AVS is calculated and included in output
- Telemetry data points are collected on each invocation

---

## 5. Phase 4 Overall

### 5.1 Milestone Definitions

| # | Milestone | Definition of Done | Dependencies |
|---|-----------|-------------------|--------------|
| **M4.1** | 3-Wave pipeline functional | Wave 1 → Wave 2 → Wave 3 produces a complete Decision Brief for a test decision | M3.1 |
| **M4.2** | 8 persona templates complete | All 8 personas produce domain-appropriate analyses on 3 test decisions | None (internal) |
| **M4.3** | Anchoring Visibility Score implemented | AVS calculator produces valid scores; sequential baseline generates comparison data | M4.1 |
| **M4.4** | Contradiction Heatmap functional | 8x8 heatmap renders in Decision Brief for all test decisions | M4.1 |
| **M4.5** | Parameter Mutation operational | Sensitivity analysis produces valid results for numeric parameter variations | M4.1 |
| **M4.6** | Quick mode (3-persona) functional | Quick mode produces a Decision Brief in <2 minutes | M4.1, M4.2 |
| **M4.7** | MCP integration complete | `cq_engine__thinktank` available via CQ MCP Server | M3.1, M4.1 |
| **M4.8** | Bash/CLI fallback validated | `thinktank.sh` produces output equivalent to MCP tool | M4.7 |
| **M4.9** | Decision Replay functional | Re-analysis of a past decision produces improved judgment quality | M4.1 |
| **M4.10** | Feedback loop operational | Telemetry data drives at least one pattern catalog or persona update | M3.3, M4.7 |
| **M4.11** | "30-second experience" working | A new user provides a decision question and sees 8 independent perspectives within 30 seconds | M4.1, M4.6 |

### 5.2 Dependencies on Phase 1-3

| Dependency | Source Phase | Required Deliverable | Why Needed |
|------------|:-----------:|---------------------|------------|
| CQE Patterns v0.1 | Phase 1 | 8 pattern catalog (especially #3 Cognitive Profile, #4 Wave Scheduler, #5 Assumption Mutation) | Theoretical foundation for persona design, wave scheduling, and parameter mutation |
| cqlint v0.1 | Phase 1 | CQ003 (generic-persona) rule | Validation that ThinkTank personas pass cognitive quality checks |
| CQ Benchmark v0.1 | Phase 1 | Decision Quality Score specification | AVS integration target; defines how ThinkTank quality is measured |
| MutaDoc v0.1 | Phase 2 | Adversarial analysis techniques | Devil's Advocate persona shares core techniques with MutaDoc's adversarial reader |
| CQ MCP Server v0.1 | Phase 3 | MCP server framework (M3.1) | Distribution channel for `cq_engine__thinktank` tool |
| Hooks integration | Phase 3 | PreToolUse / TaskCompleted hooks (M3.2) | Optional auto-trigger for complex decisions |
| Telemetry baseline | Phase 3 | Local telemetry infrastructure (M3.3) | Data collection for feedback loop (M4.10) |

### 5.3 Dependency Diagram

```
PHASE 1: FOUNDATION
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  CQE Patterns v0.1                                                 │
│  ├── #3 Cognitive Profile ──────────────┐                          │
│  ├── #4 Wave Scheduler ────────────┐    │                          │
│  └── #5 Assumption Mutation ──┐    │    │                          │
│                               │    │    │                          │
│  cqlint v0.1                  │    │    │                          │
│  └── CQ003 persona check ────┼────┼────┼──────────┐               │
│                               │    │    │          │               │
│  CQ Benchmark v0.1            │    │    │          │               │
│  └── Decision Quality spec ───┼────┼────┼──────────┼───┐           │
│                               │    │    │          │   │           │
└───────────────────────────────┼────┼────┼──────────┼───┼───────────┘
                                │    │    │          │   │
PHASE 2: KILLER APP             │    │    │          │   │
┌───────────────────────────────┼────┼────┼──────────┼───┼───────────┐
│                               │    │    │          │   │           │
│  MutaDoc v0.1                 │    │    │          │   │           │
│  └── Adversarial techniques ──┼────┼────┼──┐       │   │           │
│                               │    │    │  │       │   │           │
└───────────────────────────────┼────┼────┼──┼───────┼───┼───────────┘
                                │    │    │  │       │   │
PHASE 3: DISTRIBUTION           │    │    │  │       │   │
┌───────────────────────────────┼────┼────┼──┼───────┼───┼───────────┐
│                               │    │    │  │       │   │           │
│  CQ MCP Server v0.1           │    │    │  │       │   │           │
│  ├── M3.1 Server framework ───┼────┼────┼──┼───────┼───┼──┐        │
│  ├── M3.2 Hooks integration ──┼────┼────┼──┼───────┼───┼──┼──┐     │
│  └── M3.3 Telemetry ──────────┼────┼────┼──┼───────┼───┼──┼──┼──┐  │
│                               │    │    │  │       │   │  │  │  │  │
└───────────────────────────────┼────┼────┼──┼───────┼───┼──┼──┼──┼──┘
                                │    │    │  │       │   │  │  │  │
PHASE 4: EXPANSION              ▼    ▼    ▼  ▼       ▼   ▼  ▼  ▼  ▼
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ThinkTank v0.1                                                    │
│  ├── M4.2 8 Personas ◀──── Cognitive Profile + cqlint CQ003       │
│  ├── M4.1 3-Wave Pipeline ◀──── Wave Scheduler                    │
│  ├── M4.5 Parameter Mutation ◀──── Assumption Mutation + MutaDoc   │
│  ├── M4.3 AVS ◀──── CQ Benchmark Decision Quality spec            │
│  ├── M4.7 MCP Integration ◀──── M3.1 Server framework             │
│  ├── M4.8 CLI Fallback                                             │
│  └── M4.10 Feedback Loop ◀──── M3.3 Telemetry                     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 5.4 Internal Task Dependency Graph

```
T4.1.1-T4.1.8 (Persona templates)
      │
      ▼
T4.1.10 (Quick mode subset) ───────────────────────────────┐
      │                                                     │
      ▼                                                     │
T4.2.1 (Wave 1 template) ◀── T4.1.9 (Custom template)     │
      │                                                     │
      ▼                                                     │
T4.2.2 (Wave 1 script)                                     │
      │                                                     │
      ├─── T4.2.4 (Heatmap format)                          │
      │         │                                           │
      ▼         ▼                                           │
T4.2.3 (Wave 2 template)                                    │
      │                                                     │
      ▼                                                     │
T4.2.5 (Wave 2 script)                                     │
      │                                                     │
      ▼                                                     │
T4.2.6 (Wave 3 template) ◀── T4.2.7 (Brief format)        │
      │                                                     │
      ▼                                                     │
T4.2.8 (Wave 3 script) ══════════════ M4.1 (Pipeline)      │
      │                                    │                │
      ├──────────────────────┐             │                │
      ▼                      ▼             ▼                ▼
T4.3.1 (PSS method)    T4.4.1 (MCP schema)           M4.6 (Quick mode)
      │                      │
      ▼                      ▼
T4.3.2 (Seq baseline)  T4.4.2 (MCP tool)
      │                      │
      ▼                      ▼
T4.3.3 (AVS calc) ════ M4.3   T4.4.3 (CLI fallback) ═══ M4.8
      │                      │
      ▼                      ▼
T4.3.4 (AVS viz)       T4.4.4 (Telemetry)
      │                      │
      ▼                      ▼
T4.3.5 (Benchmark map)  T4.4.5 (Tests) ═══════════════ M4.7
                                                         │
                                                         ▼
                                                   M4.10 (Feedback)
```

### 5.5 Completion Criteria (Phase 4 Complete)

Phase 4 is considered complete when ALL of the following are met:

| # | Criterion | Validation Method |
|---|-----------|-------------------|
| 1 | All 11 milestones (M4.1–M4.11) are achieved | Milestone checklist review |
| 2 | Full mode produces valid Decision Briefs for 5 diverse test decisions | Manual quality review |
| 3 | Quick mode produces valid Decision Briefs in <2 minutes | Timing measurement |
| 4 | AVS > 0% on all test decisions (parallel is more diverse than sequential) | Automated AVS calculation |
| 5 | `cq_engine__thinktank` is callable via MCP and produces correct output | Integration test suite |
| 6 | `thinktank.sh` (CLI) produces equivalent output to MCP tool | Diff comparison |
| 7 | Hypothesis H1 validated: parallel diversity ≥ 1.5x sequential | Statistical test (p < 0.05) |
| 8 | Hypothesis H2 validated: Wave 2 reduces blind spots by ≥ 30% | Before/after comparison |
| 9 | At least one feedback-loop cycle completed (telemetry → pattern/persona update) | Audit trail |

### 5.6 Risks and Mitigations

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|:----------:|------------|
| R1 | **"Multi-perspective = SWOT/Six Hats" perception** | ThinkTank dismissed as derivative | High | Position as "Anti-Anchoring Engine." Lead with Anchoring Visibility Score, not "8 perspectives." Quantify bias elimination |
| R2 | **8 personas too expensive (API costs)** | Prohibitive for casual use | High | Provide 3-persona quick mode (CFO + CTO + Devil's Advocate). Full mode reserved for important decisions |
| R3 | **AVS methodology unvalidated** | Core differentiator is unproven | Medium | Validate with statistical rigor in H4 before marketing. Run on 20+ diverse decisions |
| R4 | **Sequential baseline is artificial** | AVS comparison may not reflect real ChatGPT behavior | Medium | Use actual ChatGPT sequential output as baseline, not simulated sequential |
| R5 | **Wave 2 cross-critique degenerates into agreement** | Personas agree after reading each other | Low | Devil's Advocate is mandatory and structurally adversarial. Critique template requires minimum 2 disagreements per persona |
| R6 | **Slow execution (>5 minutes for full mode)** | UX indistinguishable from manual review | Medium | Progress display within 30s. Quick mode for immediate results. Wave 1 results shown as they complete |
| R7 | **Custom personas are low quality** | User-defined personas produce shallow analysis | Low | Provide `TEMPLATE.md` with required fields. cqlint CQ003 checks persona quality |
| R8 | **Contradiction Heatmap is noisy** | Too many disagreements make the heatmap uninformative | Low | Threshold at ±2 for significance. Only display statistically meaningful contradictions |

### 5.7 Full Task Summary

| Task ID | Task | Section | Deliverable | Size | Depends On |
|---------|------|---------|-------------|:----:|------------|
| T4.1.1 | CFO persona template | 1 | `personas/business/cfo.md` | S | — |
| T4.1.2 | CTO persona template | 1 | `personas/business/cto.md` | S | — |
| T4.1.3 | CMO persona template | 1 | `personas/business/cmo.md` | S | — |
| T4.1.4 | Investor persona template | 1 | `personas/business/investor.md` | S | — |
| T4.1.5 | Customer persona template | 1 | `personas/stakeholders/customer.md` | S | — |
| T4.1.6 | Employee persona template | 1 | `personas/stakeholders/employee.md` | S | — |
| T4.1.7 | Regulator persona template | 1 | `personas/stakeholders/regulator.md` | S | — |
| T4.1.8 | Devil's Advocate persona template | 1 | `personas/meta/devils_advocate.md` | M | — |
| T4.1.9 | Custom persona specification | 1 | `personas/custom/TEMPLATE.md` | S | T4.1.1–T4.1.8 |
| T4.1.10 | Quick mode preset | 1 | `personas/presets/quick_3.md` | S | T4.1.1, T4.1.2, T4.1.8 |
| T4.2.1 | Wave 1 execution template | 2 | `waves/wave1_independent.md` | M | T4.1.1–T4.1.8 |
| T4.2.2 | Wave 1 orchestration script | 2 | `thinktank.sh` (Wave 1) | M | T4.2.1 |
| T4.2.3 | Wave 2 execution template | 2 | `waves/wave2_cross_critique.md` | M | T4.2.1 |
| T4.2.4 | Contradiction heatmap data format | 2 | `waves/heatmap_format.md` | S | — |
| T4.2.5 | Wave 2 orchestration script | 2 | `thinktank.sh` (Wave 2) | M | T4.2.3, T4.2.4 |
| T4.2.6 | Wave 3 synthesis template | 2 | `waves/wave3_synthesis.md` | L | T4.2.3 |
| T4.2.7 | Decision Brief output format | 2 | `waves/decision_brief_format.md` | M | T4.2.4 |
| T4.2.8 | Wave 3 orchestration script | 2 | `thinktank.sh` (Wave 3) | M | T4.2.6, T4.2.7 |
| T4.3.1 | PSS calculation methodology | 3 | `docs/avs_specification.md` | M | — |
| T4.3.2 | Sequential baseline generator | 3 | `mutation/sequential_baseline.sh` | M | T4.3.1 |
| T4.3.3 | AVS calculator | 3 | `mutation/avs_calculator.sh` | M | T4.3.1, T4.3.2 |
| T4.3.4 | AVS visualization format | 3 | `waves/avs_visualization.md` | S | T4.3.3 |
| T4.3.5 | CQ Benchmark AVS mapping | 3 | `benchmark/avs_mapping.md` | S | T4.3.3 |
| T4.4.1 | MCP tool input/output schema | 4 | `mcp-server/tools/thinktank_schema.md` | S | T4.2.7 |
| T4.4.2 | ThinkTank MCP tool (Python) | 4 | `mcp-server/tools/thinktank.py` | L | T4.4.1, M4.1 |
| T4.4.3 | Bash/CLI fallback | 4 | `thinktank/thinktank.sh` (complete) | L | M4.1 |
| T4.4.4 | Telemetry data points | 4 | `mcp-server/telemetry/thinktank_metrics.md` | S | T4.4.2 |
| T4.4.5 | Integration tests | 4 | `mcp-server/tools/tests/test_thinktank.py` | M | T4.4.2 |

**Total: 30 tasks** (S: 12, M: 13, L: 5)

**Estimated Effort Distribution:**

| Size | Count | Estimated Effort Each | Subtotal |
|:----:|:-----:|:---------------------:|:--------:|
| S | 12 | 1-2 hours | 12-24 hours |
| M | 13 | 3-5 hours | 39-65 hours |
| L | 5 | 8-12 hours | 40-60 hours |
| **Total** | **30** | | **91-149 hours** |
