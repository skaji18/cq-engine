# Phase 2: MutaDoc — Detailed Implementation Plan

> **Version**: 1.0.0
> **Parent**: cq-engine roadmap Phase 2
> **Purpose**: Break down Phase 2 (MutaDoc) into actionable implementation tasks
> **Prerequisite**: Phase 1 complete (CQE Patterns v0.1 + cqlint v0.1 + CQ Benchmark v0.1 spec)

---

## 1. Mutation Strategies

### 1.1 Strategy Overview

MutaDoc implements 5 mutation strategies. Each strategy is a template-driven analysis that intentionally alters the target document to expose hidden vulnerabilities.

| # | Strategy | Description | Estimated Size |
|---|----------|-------------|:-:|
| S1 | Contradiction | Alter a clause and detect if other clauses become contradictory | M |
| S2 | Ambiguity | Replace vague modifiers with extreme values to expose meaninglessness | M |
| S3 | Deletion | Remove a clause and measure structural impact (zero impact = dead clause) | S |
| S4 | Inversion | Reverse assumptions/claims and measure argument robustness | M |
| S5 | Boundary | Mutate parameters (numbers, deadlines) to estimate conclusion robustness | S |

### 1.2 Strategy S1: Contradiction

**Purpose**: Detect hidden contradictions between document sections by altering one clause and observing cascading inconsistencies.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| S1-T1 | Strategy template | Write `strategies/contradiction.md` — the prompt template that instructs the LLM how to identify clauses, generate contradictory mutations, and evaluate cross-clause impact | S |
| S1-T2 | Clause extraction logic | Implement clause/section identification in `mutadoc.sh` — parse document structure (headings, numbered items, paragraphs) to identify discrete testable units | M |
| S1-T3 | Cross-reference detection | Implement logic to identify which clauses reference or depend on each other (e.g., "as defined in Section 3.2") | M |
| S1-T4 | Test fixtures | Create 3 test documents with known contradictions (contract, API spec, policy doc) and expected detection results | S |

**Input/Output Specification**:

| Field | Specification |
|-------|---------------|
| **Input** | Document path (Markdown/text), clause identification mode (auto/manual) |
| **Output** | Contradiction report: mutated clause, affected clauses, contradiction description, severity (Critical/Major/Minor), original vs mutated text diff |
| **Severity Criteria** | Critical: legal/logical impossibility; Major: significant inconsistency; Minor: stylistic tension |

**Test Cases**:

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| S1-TC1 | Contract with conflicting termination clauses (Section 5 says 30 days, Section 12 says "immediately") | Detect Critical contradiction between Section 5 and Section 12 |
| S1-TC2 | API spec where PUT endpoint response schema contradicts GET response schema | Detect Major contradiction in response schemas |
| S1-TC3 | Document with no contradictions | Report zero contradictions (false positive check) |

### 1.3 Strategy S2: Ambiguity

**Purpose**: Expose vague modifiers ("reasonable", "appropriate", "timely") by replacing them with extreme values, revealing that the original text is effectively meaningless.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| S2-T1 | Strategy template | Write `strategies/ambiguity.md` — prompt template for identifying vague modifiers and generating extreme-value mutations | S |
| S2-T2 | Vague modifier catalog | Build a catalog of common vague modifiers with their extreme-value replacements (e.g., "reasonable" → "unlimited" / "zero") | S |
| S2-T3 | Impact assessment logic | Implement scoring for how much the document's meaning changes under extreme-value replacement (high change = ambiguity is load-bearing) | M |
| S2-T4 | Test fixtures | Create 3 test documents with known ambiguous language and expected detection results | S |

**Input/Output Specification**:

| Field | Specification |
|-------|---------------|
| **Input** | Document path, ambiguity sensitivity level (strict/normal/lenient) |
| **Output** | Ambiguity report: original phrase, extreme-value mutations (min/max), impact score (0-100), recommendation (define precisely / accept ambiguity / remove), location in document |
| **Severity Criteria** | Critical: ambiguity in obligation/rights/deadline; Major: ambiguity in scope/definition; Minor: ambiguity in description/context |

**Test Cases**:

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| S2-TC1 | Contract with "reasonable efforts" in 5 locations | Detect 5 ambiguous phrases, at least 2 Critical (in obligation clauses) |
| S2-TC2 | Technical spec with "appropriate security measures" | Detect Critical ambiguity — "appropriate" is undefined |
| S2-TC3 | Document using precise quantitative language only | Report zero ambiguities (false positive check) |

### 1.4 Strategy S3: Deletion

**Purpose**: Remove a clause/section entirely and measure structural impact. Zero impact means a "dead clause" — text that exists but contributes nothing.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| S3-T1 | Strategy template | Write `strategies/deletion.md` — prompt template for systematic clause deletion and impact measurement | S |
| S3-T2 | Structural impact scorer | Implement a scoring system that measures how many other sections reference, depend on, or are affected by the deleted section | S |
| S3-T3 | Dead clause identifier | Flag clauses with zero structural impact as "dead clauses" and suggest removal or justification | S |
| S3-T4 | Test fixtures | Create 2 test documents — one with dead clauses, one with tightly interconnected clauses | S |

**Input/Output Specification**:

| Field | Specification |
|-------|---------------|
| **Input** | Document path, deletion mode (section-level / clause-level / paragraph-level) |
| **Output** | Deletion impact report: deleted unit, impact score (0-100), affected sections list, classification (dead clause / low impact / critical dependency), visualization of dependency graph |
| **Severity Criteria** | Dead clause (impact 0): suggest removal; Low impact (<20): review necessity; Critical dependency (>80): document is fragile if this section is wrong |

**Test Cases**:

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| S3-TC1 | Contract with a boilerplate clause that nothing references | Detect dead clause (impact score 0) |
| S3-TC2 | API spec where deleting the auth section cascades to 8 endpoints | Report Critical dependency (impact score >80) |

### 1.5 Strategy S4: Inversion

**Purpose**: Reverse assumptions, claims, or conditions and measure how well the surrounding argument structure holds up. Weak arguments collapse under inversion.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| S4-T1 | Strategy template | Write `strategies/inversion.md` — prompt template for identifying invertible claims and measuring argument robustness | S |
| S4-T2 | Claim extraction | Implement logic to identify claims, assumptions, and conditions that can be meaningfully inverted | M |
| S4-T3 | Robustness scorer | Score how well the surrounding text (discussion, conclusion, dependent sections) withstands inversion of each claim | M |
| S4-T4 | Test fixtures | Create 3 test documents — academic paper with weak methodology, policy doc with unsupported claims, spec with untested assumptions | S |

**Input/Output Specification**:

| Field | Specification |
|-------|---------------|
| **Input** | Document path, inversion target (all claims / specific sections / hypotheses only) |
| **Output** | Inversion report: original claim, inverted claim, robustness score (0-100), dependent sections that collapse, evidence gaps exposed |
| **Severity Criteria** | Critical: conclusion depends on uninverted assumption with no evidence; Major: argument weakened but not destroyed; Minor: stylistic preference |

**Test Cases**:

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| S4-TC1 | Paper claiming "X improves performance" with no control group | Inversion "X degrades performance" reveals zero counter-evidence → Critical |
| S4-TC2 | Contract assuming "market conditions remain stable" | Inversion reveals 3 clauses that have no contingency → Major |
| S4-TC3 | Well-structured argument with cited evidence for each claim | Report low severity (robustness score >80 for all claims) |

### 1.6 Strategy S5: Boundary

**Purpose**: Mutate numerical parameters (dates, amounts, percentages, counts) to extreme values and observe whether conclusions, obligations, or logic still hold.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| S5-T1 | Strategy template | Write `strategies/boundary.md` — prompt template for parameter identification, boundary generation, and impact analysis | S |
| S5-T2 | Parameter extractor | Identify all numerical parameters in the document (dates, amounts, percentages, counts, durations) | S |
| S5-T3 | Boundary value generator | For each parameter, generate boundary values: zero, minimum viable, maximum reasonable, extreme, negative (where applicable) | S |
| S5-T4 | Test fixtures | Create 2 test documents with parameters that have unexplored boundary conditions | S |

**Input/Output Specification**:

| Field | Specification |
|-------|---------------|
| **Input** | Document path, parameter scope (all / specific sections) |
| **Output** | Boundary report: parameter name, original value, boundary values tested, impact at each boundary, sensitivity classification (robust / sensitive / fragile) |
| **Severity Criteria** | Critical: obligation/logic breaks at realistic boundary values; Major: logic breaks at extreme but plausible values; Minor: logic breaks only at unrealistic extremes |

**Test Cases**:

| Test ID | Input | Expected Result |
|---------|-------|-----------------|
| S5-TC1 | Contract with "30 days notice" — test with 0, 1, 365, 3650 days | Detect that 0 days creates legal impossibility (Critical); 365 days is unreasonable but contract has no upper bound (Major) |
| S5-TC2 | Budget doc with cost projections — test with 0%, 50%, 200%, 1000% inflation | Identify which projections are fragile (break at realistic 50% deviation) |

---

## 2. Adversarial Personas

### 2.1 Persona Overview

Each persona is a prompt template that instructs the LLM to adopt a specific adversarial reading posture. Personas are orthogonal to strategies — any persona can be combined with any strategy for a unique analysis perspective.

| # | Persona | Role | Primary Strategy Affinity | Size |
|---|---------|------|---------------------------|:----:|
| P1 | `adversarial_reader` | Malicious reader seeking exploitable ambiguity | Ambiguity, Boundary | M |
| P2 | `opposing_counsel` | Opposing lawyer seeking contract weaknesses | Contradiction, Deletion | M |
| P3 | `naive_implementer` | Developer who implements everything literally | Ambiguity, Inversion | M |

### 2.2 Persona P1: Adversarial Reader

**Role**: A sophisticated bad-faith actor who reads the document looking for loopholes, exploitable ambiguities, and passages that can be interpreted in self-serving ways.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| P1-T1 | Persona template | Write `personas/adversarial_reader.md` — system prompt defining the adversarial reader's objectives, reading style, and analysis framework | S |
| P1-T2 | Exploitation catalog | Build a catalog of common exploitation patterns (ambiguity exploitation, scope creep, implied vs explicit rights) | S |
| P1-T3 | Output format | Define the structured output format: exploitable passage, exploitation method, risk level, recommended defense | S |

**Evaluation Criteria**:

| Criterion | Threshold |
|-----------|-----------|
| Identifies at least 1 exploitable passage per 5 pages of text | Required |
| False positive rate below 30% (human evaluation) | Required |
| Exploitation methods are specific and actionable (not generic "this is vague") | Required |

**Completion Criteria**: Adversarial reader persona produces actionable exploitation reports on 3 different document types (contract, spec, policy) with false positive rate < 30%.

### 2.3 Persona P2: Opposing Counsel

**Role**: A skilled opposing lawyer specifically seeking to invalidate, weaken, or exploit the document in a legal or contractual dispute.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| P2-T1 | Persona template | Write `personas/opposing_counsel.md` — system prompt with legal adversarial analysis framework | S |
| P2-T2 | Legal attack pattern catalog | Build catalog of common legal attack patterns (vagueness challenges, severability attacks, force majeure gaps, jurisdiction conflicts) | M |
| P2-T3 | Output format | Define structured output: vulnerable clause, legal attack vector, precedent risk, recommended fortification | S |

**Evaluation Criteria**:

| Criterion | Threshold |
|-----------|-----------|
| Identifies structural legal vulnerabilities (not just grammatical issues) | Required |
| Attack vectors are specific enough that a lawyer can evaluate them | Required |
| Covers both offensive (attack) and defensive (what opponent could argue) perspectives | Required |

**Completion Criteria**: Opposing counsel persona identifies at least 3 distinct legal attack vectors on a sample M&A contract with human lawyer validation.

### 2.4 Persona P3: Naive Implementer

**Role**: A developer who reads the document with zero assumed context and implements exactly what the text says — no more, no less. Exposes gaps between intent and literal text.

**Implementation Tasks**:

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| P3-T1 | Persona template | Write `personas/naive_implementer.md` — system prompt emphasizing literal interpretation and zero implicit knowledge | S |
| P3-T2 | Gap catalog | Build catalog of common intent-vs-literal gaps (undefined terms, missing edge cases, assumed context, implicit ordering) | S |
| P3-T3 | Output format | Define structured output: literal interpretation, likely intended interpretation, gap description, risk if implemented literally | S |

**Evaluation Criteria**:

| Criterion | Threshold |
|-----------|-----------|
| Identifies at least 1 intent-vs-literal gap per 3 pages of spec/requirements | Required |
| Literal interpretations are genuinely plausible (not absurd stretches) | Required |
| Gap descriptions are specific enough to write a clarifying amendment | Required |

**Completion Criteria**: Naive implementer persona identifies implementation-blocking gaps on 2 technical documents (API spec + requirements doc) that are validated by a developer as genuine ambiguities.

---

## 3. Mutation-Driven Repair

### 3.1 Overview

Mutation-Driven Repair extends MutaDoc from a "detection only" tool to a "detect + repair" tool, mirroring ESLint's auto-fix revolution. The core insight: "detect + repair" achieves 10x adoption over "detect only."

### 3.2 Pipeline Architecture

```
┌──────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  Detection   │────▶│   Repair Draft    │────▶│   Regression      │
│  (Strategies │     │   Generation      │     │   Mutation         │
│  + Personas) │     │                   │     │                   │
└──────────────┘     └───────────────────┘     └───────────────────┘
       │                     │                         │
       ▼                     ▼                         ▼
  Vulnerability         Repair Draft              Regression
  Report                + Impact Analysis         Report
  (findings)            (fixes + cascading        (new issues
                         effects)                  from fixes)
```

### 3.3 Implementation Tasks

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| R-T1 | Repair template engine | Build template system for generating repair drafts — each strategy type has a corresponding repair approach | M |
| R-T2 | Repair draft generator | For each Critical/Major finding, auto-generate a concrete fix suggestion with the repaired text | M |
| R-T3 | Repair impact analysis | For each repair draft, predict cascading effects on other sections ("fixing Section 5 may invalidate Section 12") | L |
| R-T4 | Regression mutation engine | Apply all 5 mutation strategies to the repaired document to verify no new vulnerabilities were introduced | M |
| R-T5 | Diff view output | Generate side-by-side original vs repaired text view (GitHub PR diff style) for human review | S |
| R-T6 | Repair confidence scoring | Score each repair suggestion: auto-applicable (high confidence) vs needs-human-review (low confidence) | S |

### 3.4 Repair Strategy Definitions

| Detection Strategy | Repair Approach |
|--------------------|----------------|
| Contradiction | Identify the dominant clause (by context/intent), suggest amendments to the subordinate clause to resolve conflict |
| Ambiguity | Replace vague modifier with a precise quantitative or qualitative definition, offering 2-3 options with different specificity levels |
| Deletion (dead clause) | Suggest removal with justification, or suggest adding cross-references to make the clause structurally relevant |
| Inversion | Strengthen the claim by adding evidence references, adding contingency clauses, or qualifying the scope |
| Boundary | Add explicit boundary constraints (minimum, maximum, default values) to parameters that lack them |

### 3.5 Auto-Repair vs Suggestion Criteria

| Criterion | Auto-Applicable | Needs Human Review |
|-----------|:-:|:-:|
| Fix is purely additive (adds precision without changing meaning) | Yes | — |
| Fix modifies an obligation or right | — | Yes |
| Fix involves choosing between 2+ valid alternatives | — | Yes |
| Fix removes text | — | Yes |
| Fix adds explicit boundary to an implicit parameter | Yes | — |
| Fix resolves a contradiction by choosing one interpretation | — | Yes |

**Target**: 30%+ of repair suggestions are directly usable ("use as-is" rate).

### 3.6 Completion Criteria

| Criterion | Threshold |
|-----------|-----------|
| Repair drafts generated for 100% of Critical findings | Required |
| Repair drafts generated for 80%+ of Major findings | Required |
| Repair impact analysis covers cascading effects on related sections | Required |
| Regression mutation detects at least 1 new issue introduced by repairs in test fixtures | Required (validates the regression engine works) |
| Diff view renders correctly for all test fixture repairs | Required |
| Auto-applicable vs needs-review classification accuracy > 80% | Required |

---

## 4. Document Type Presets

### 4.1 Overview

Each preset is a configuration that adjusts strategy weights, persona selection, severity thresholds, and output format for a specific document type. MutaDoc ships with 10+ presets to ensure it is perceived as a general-purpose tool, not a niche application.

### 4.2 Preset List

| # | Preset Name | File | Target Document Type | Primary Strategies | Default Persona | Size |
|---|-------------|------|---------------------|-------------------|-----------------|:----:|
| 1 | `contract` | `presets/contract.md` | Legal contracts (M&A, SaaS, employment) | Contradiction, Ambiguity, Deletion | opposing_counsel | S |
| 2 | `api_spec` | `presets/api_spec.md` | API/technical specifications (OpenAPI, gRPC) | Contradiction, Boundary, Deletion | naive_implementer | S |
| 3 | `academic_paper` | `presets/academic_paper.md` | Research papers (pre-submission review) | Inversion, Ambiguity, Boundary | adversarial_reader | S |
| 4 | `policy` | `presets/policy.md` | Government/corporate policy documents | Ambiguity, Contradiction, Boundary | adversarial_reader | S |
| 5 | `requirements` | `presets/requirements.md` | Software requirements / PRDs | Ambiguity, Deletion, Boundary | naive_implementer | S |
| 6 | `rfc` | `presets/rfc.md` | RFCs and technical standards | Contradiction, Inversion, Boundary | naive_implementer | S |
| 7 | `terms_of_service` | `presets/terms_of_service.md` | Terms of Service / Privacy Policies | Ambiguity, Contradiction, Deletion | adversarial_reader | S |
| 8 | `grant_proposal` | `presets/grant_proposal.md` | Research grant applications | Inversion, Ambiguity, Deletion | adversarial_reader | S |
| 9 | `sla` | `presets/sla.md` | Service Level Agreements | Boundary, Ambiguity, Contradiction | opposing_counsel | S |
| 10 | `readme` | `presets/readme.md` | Open source README / documentation | Ambiguity, Deletion, Inversion | naive_implementer | S |
| 11 | `business_plan` | `presets/business_plan.md` | Business plans / pitch decks | Inversion, Boundary, Ambiguity | adversarial_reader | S |
| 12 | `compliance` | `presets/compliance.md` | Regulatory compliance documents | Contradiction, Ambiguity, Boundary | opposing_counsel | S |

### 4.3 Preset Implementation Tasks

| Task ID | Task | Description | Size |
|---------|------|-------------|:----:|
| PR-T1 | Preset template format | Define the YAML/Markdown format for presets (strategy weights, persona, severity thresholds, custom terminology) | S |
| PR-T2 | Core presets (4) | Implement contract, api_spec, academic_paper, policy presets — these are the primary validation targets | M |
| PR-T3 | Extended presets (8) | Implement remaining 8 presets | M |
| PR-T4 | Preset auto-detection | Implement heuristic to auto-detect document type from content/structure (optional override via CLI flag) | M |
| PR-T5 | Custom preset guide | Write guide for users to create their own presets | S |

### 4.4 Preset Configuration Format

```yaml
# presets/contract.md (front matter)
preset:
  name: contract
  description: "Legal contracts (M&A, SaaS, employment, NDA)"
  strategies:
    contradiction: { weight: 1.0, enabled: true }
    ambiguity: { weight: 1.0, enabled: true }
    deletion: { weight: 0.8, enabled: true }
    inversion: { weight: 0.5, enabled: true }
    boundary: { weight: 0.7, enabled: true }
  default_persona: opposing_counsel
  severity_overrides:
    ambiguity_in_obligation: Critical  # override default Major
    dead_clause: Minor                 # less critical in contracts
  domain_terminology:
    - "indemnify", "severability", "force majeure", "liquidated damages"
  output_format: full_report  # full_report | summary | ci_gate
```

### 4.5 Completion Criteria

| Criterion | Threshold |
|-----------|-----------|
| 4 core presets functional and tested | Required for M2.4 |
| 10+ total presets available | Required for M2.4 |
| Auto-detection correctly identifies document type for 3/4 core types | Required for M2.4 |
| Custom preset creation guide published | Required for M2.4 |

---

## 5. Phase 2 Overall

### 5.1 Milestone Definitions

| Milestone | Definition of Done | Dependencies | Estimated Size |
|-----------|--------------------|-------------|:-:|
| **M2.1** — 5 strategies implemented | All 5 strategies produce mutation test reports on sample documents. Each has 2+ passing test fixtures. | Phase 1 M1.1 (patterns) | L |
| **M2.2** — Mutation-Driven Repair functional | Repair drafts generated for Critical findings. Regression mutation validates repairs. Diff view renders correctly. | M2.1 | L |
| **M2.3** — "30-second experience" working | `mutadoc test README.md` returns "N ambiguous expressions found" within 30 seconds. Progress indicator within 5 seconds. | M2.1 | M |
| **M2.4** — 10+ document type presets | 12 presets available. Auto-detection works for core 4 types. Custom preset guide published. | M2.1 | M |
| **M2.5** — CQ Benchmark validation | MutaDoc hypotheses H1-H5 validated using CQ Benchmark metrics. Results documented. | M2.1, M2.2, Phase 1 M1.4 | M |
| **M2.6** — Mutation Kill Score | Numerical document quality score (killed mutations / total mutations × 100%). Score calculation documented and implemented. | M2.1 | S |

### 5.2 Phase 1 Dependencies

Phase 2 requires the following Phase 1 outputs:

| Phase 1 Output | Why Needed | Milestone Gated |
|----------------|-----------|-----------------|
| CQE Patterns v0.1 (M1.1) | Assumption Mutation pattern provides theoretical foundation for all 5 strategies | M2.1 entry gate |
| cqlint v0.1 (M1.2) | Validates that MutaDoc's own configuration follows CQE patterns | M2.1 entry gate |
| CQ Benchmark v0.1 spec (M1.4) | Provides measurement framework for hypothesis validation | M2.5 |
| Pattern: Attention Budget | Guides token budget allocation for parallel strategy execution | M2.1 design input |
| Pattern: Context Gate | Guides isolation of each strategy's analysis context | M2.1 design input |
| Pattern: Cognitive Profile | Guides persona template design | M2.1 design input |

### 5.3 Dependency Diagram

```
PHASE 1 (Prerequisites)
════════════════════════════════════════════════════════════════════

  M1.1 CQE Patterns v0.1 ─────────────────────┐
  M1.2 cqlint v0.1 ───────────────────────────┐│
  M1.4 CQ Benchmark v0.1 spec ──────────────┐ ││
                                             │ ││
PHASE 2 (MutaDoc)                            │ ││
════════════════════════════════════════════════════════════════════

                                             │ ││
  ┌──────────────────────────────────────────┘ │└──── Entry Gate
  │                                            │
  │  ┌─────────────────────────────────────────┘
  │  │
  │  │   ┌──────────────────────────────────────────────────────┐
  │  │   │  M2.1 — 5 Strategies Implemented                    │
  │  │   │                                                      │
  │  │   │  S1 Contradiction ─┐                                 │
  │  │   │  S2 Ambiguity ─────┤                                 │
  │  └──▶│  S3 Deletion ──────┼──▶ All strategies functional    │
  │      │  S4 Inversion ─────┤                                 │
  │      │  S5 Boundary ──────┘                                 │
  │      │                                                      │
  │      │  P1 adversarial_reader ─┐                            │
  │      │  P2 opposing_counsel ───┼──▶ All personas functional │
  │      │  P3 naive_implementer ──┘                            │
  │      └─────────────┬────────────────────┬───────────────────┘
  │                    │                    │
  │         ┌──────────▼──────────┐        │
  │         │  M2.3 — 30-Second   │        │
  │         │  Experience         │        │
  │         └─────────────────────┘        │
  │                    │                   │
  │         ┌──────────▼──────────┐  ┌─────▼─────────────────┐
  │         │  M2.4 — 10+ Presets │  │ M2.6 — Mutation Kill  │
  │         │  (12 presets +      │  │ Score                  │
  │         │   auto-detection)   │  └─────┬─────────────────┘
  │         └─────────────────────┘        │
  │                                        │
  │                    ┌───────────────────▼┐
  │                    │  M2.2 — Mutation-  │
  │                    │  Driven Repair     │
  │                    │  (Repair + Regr.)  │
  │                    └─────────┬─────────┘
  │                              │
  └──────────────┐               │
                 │               │
          ┌──────▼───────────────▼──┐
          │  M2.5 — CQ Benchmark    │
          │  Validation (H1-H5)     │
          └─────────────────────────┘
```

### 5.4 Task Summary Table

| Area | Task Count | Total Size |
|------|:----------:|:----------:|
| Strategy S1 (Contradiction) | 4 tasks | M |
| Strategy S2 (Ambiguity) | 4 tasks | M |
| Strategy S3 (Deletion) | 4 tasks | S |
| Strategy S4 (Inversion) | 4 tasks | M |
| Strategy S5 (Boundary) | 4 tasks | S |
| Persona P1 (Adversarial Reader) | 3 tasks | M |
| Persona P2 (Opposing Counsel) | 3 tasks | M |
| Persona P3 (Naive Implementer) | 3 tasks | M |
| Mutation-Driven Repair | 6 tasks | L |
| Presets | 5 tasks | M |
| **Total** | **40 tasks** | **L** |

### 5.5 Completion Criteria (Phase 2 Done)

Phase 2 is complete when **all** of the following are met:

| # | Criterion | Validation Method |
|---|-----------|-------------------|
| 1 | All 5 mutation strategies produce correct reports on test fixtures | Automated: run all test fixtures, verify expected findings detected |
| 2 | All 3 personas produce actionable analysis on their target document types | Human review: evaluate 1 output per persona for actionability |
| 3 | Mutation-Driven Repair generates repair drafts for 100% of Critical findings | Automated: verify repair draft exists for each Critical |
| 4 | Regression Mutation detects at least 1 repair-introduced issue in test fixtures | Automated: verify regression detection on intentionally flawed repair |
| 5 | 10+ document type presets available and functional | Automated: verify each preset runs without error on sample input |
| 6 | "30-second experience" delivers result within 30 seconds on a 100-line document | Manual timing test |
| 7 | Mutation Kill Score is calculated and displayed in output | Automated: verify score appears in report |
| 8 | CQ Benchmark validation completed for hypotheses H1-H5 | Manual: review validation report |
| 9 | `mutadoc/` directory structure matches cq-engine repo design | Automated: verify file structure |

### 5.6 Repository Structure (Phase 2 Addition)

```
cq-engine/mutadoc/
├── README.md                     # MutaDoc overview + quick start
├── mutadoc.sh                    # Entry point (Bash, zero infrastructure)
├── strategies/
│   ├── contradiction.md          # S1: Contradiction detection
│   ├── ambiguity.md              # S2: Ambiguity attack
│   ├── deletion.md               # S3: Deletion test
│   ├── inversion.md              # S4: Inversion test
│   └── boundary.md               # S5: Boundary mutation
├── personas/
│   ├── adversarial_reader.md     # P1: Malicious reader
│   ├── opposing_counsel.md       # P2: Opposing lawyer
│   └── naive_implementer.md      # P3: Literal implementer
├── repair/
│   └── templates/                # Repair draft templates per strategy
│       ├── contradiction_repair.md
│       ├── ambiguity_repair.md
│       ├── deletion_repair.md
│       ├── inversion_repair.md
│       └── boundary_repair.md
├── presets/
│   ├── contract.md
│   ├── api_spec.md
│   ├── academic_paper.md
│   ├── policy.md
│   ├── requirements.md
│   ├── rfc.md
│   ├── terms_of_service.md
│   ├── grant_proposal.md
│   ├── sla.md
│   ├── readme.md
│   ├── business_plan.md
│   └── compliance.md
├── test_fixtures/
│   ├── contracts/                # Test contracts with known issues
│   ├── specs/                    # Test specs with known issues
│   └── papers/                   # Test papers with known issues
└── output/
    └── (generated reports)
```

### 5.7 Risks and Mitigations

| # | Risk | Impact | Probability | Mitigation |
|---|------|--------|:-----------:|------------|
| R1 | "Just ask ChatGPT to review" perception | MutaDoc dismissed as unnecessary | High | "30-second experience" design — show a result that ChatGPT review missed within 30 seconds |
| R2 | Repair suggestions are unusable | Mutation-Driven Repair seen as noise | Medium | Target 30%+ "use as-is" rate; diff view for easy evaluation; auto/manual classification |
| R3 | Document type coverage too narrow | Perceived as niche tool | Medium | Launch with 12 presets (not just 3) + custom preset capability |
| R4 | Slow execution (5+ minutes) | UX indistinguishable from ChatGPT | Medium | Progress display within 5 seconds; Critical first-report within 2 minutes; use parallel Task tool execution |
| R5 | High false positive rate | User trust erodes | High | Calibrate severity thresholds per preset; include confidence score; test on known-good documents |
| R6 | Strategy overlap (redundant findings across strategies) | Reports feel bloated | Medium | Implement deduplication: if two strategies detect the same issue, merge into a single finding with multiple evidence sources |
| R7 | Phase 1 delays block Phase 2 start | Schedule slip | Low | M2.1 only requires M1.1 (patterns) and M1.2 (cqlint). Benchmark spec (M1.4) only needed for M2.5 |

### 5.8 Hypotheses to Validate

| # | Hypothesis | IV | DV | Baseline | Effect Size | Sample Size | Method |
|---|-----------|----|----|----------|-------------|-------------|--------|
| H1 | MutaDoc detects issues human reviewers miss | MutaDoc (present/absent) | Issues detected | Human-only review (2 lawyers) | 50%+ of missed issues detected | 5 contracts with known issues | Controlled comparison |
| H2 | Strategies generalize across document types | Document type (contract/spec/paper) | Critical findings count | Zero (no existing tool) | 1+ Critical per type | 3 document types × 2 samples | Cross-type application |
| H3 | Mutation mechanism ports from code to docs | Automation level (manual/auto) | Review quality score | Manual adversarial review | Equivalent quality | 3 documents | Quality comparison |
| H4 | 30%+ of repair suggestions are directly usable | Repair engine (present/absent) | "Use as-is" rate | N/A (new capability) | 30%+ | 20 repair suggestions | Human evaluation |
| H5 | Regression Mutation catches new vulnerabilities | Regression mutation (present/absent) | New issues detected | Zero (repairs assumed safe) | 15%+ detection rate | 10 repaired documents | Automated detection |

---

## Appendix A: CLI Interface Design

```bash
# Basic usage (auto-detect document type)
mutadoc test document.md

# Specify preset
mutadoc test contract.md --preset contract

# Specify strategies
mutadoc test spec.md --strategies contradiction,ambiguity

# Specify persona
mutadoc test contract.md --persona opposing_counsel

# Full options
mutadoc test document.md \
  --preset contract \
  --strategies all \
  --persona opposing_counsel \
  --repair \
  --regression \
  --output report.md

# Quick mode (30-second experience — ambiguity only, no repair)
mutadoc quick document.md

# Score only (just the Mutation Kill Score)
mutadoc score document.md
```

## Appendix B: Output Report Structure

```markdown
# MutaDoc Report: contract.md

> Preset: contract | Persona: opposing_counsel
> Mutation Kill Score: 72% (18 killed / 25 applied)
> Generated: 2026-MM-DD

## Summary
- Critical: 3
- Major: 7
- Minor: 8
- Dead Clauses: 2

## Critical Findings

### [C1] Contradiction: Termination clauses conflict
- **Location**: Section 5.1 vs Section 12.3
- **Strategy**: Contradiction
- **Mutation**: Changed "30 days" to "immediately" in Section 5.1
- **Impact**: Section 12.3 becomes impossible to fulfill
- **Repair Suggestion**: [View Diff]
  ```diff
  - Section 12.3: "Following the notice period defined in Section 5..."
  + Section 12.3: "Following the 30-day notice period defined in Section 5.1..."
  ```
- **Repair Confidence**: High (auto-applicable)
- **Regression Check**: PASS (no new issues introduced)

...
```
