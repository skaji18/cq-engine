# Axis 3: Document Integrity Score

> **Purpose**: Measure the structural and logical quality of produced documents.
> **CQE Pattern Link**: Assumption Mutation (#05), Template-Driven Role (#08)
> **Effort**: S

---

## 1. Definition

Document Integrity measures how well an agent system produces reliable, internally consistent, and unambiguous documents. High integrity means documents withstand adversarial scrutiny — mutations are detected, contradictions are absent, and ambiguous language is minimized. Low integrity means documents contain hidden flaws that will surface in production.

**Why it matters**: LLM-generated documents (contracts, specifications, reports, code documentation) are increasingly used as authoritative sources. Without integrity measurement, flawed documents propagate errors downstream. Document Integrity is the output-side counterpart to Context Health's input-side measurement.

---

## 2. Sub-Metrics

### 2.1 Mutation Kill Rate (DI-1)

**Definition**: Proportion of intentionally injected document mutations that are detected as problems during review.

**Formula**:

```
MutationKillRate = detected_mutations / total_injected_mutations
```

Where:
- `total_injected_mutations`: Number of deliberate modifications applied to the document (e.g., inverting a claim, deleting a clause, changing a number)
- `detected_mutations`: Number of those mutations that were flagged by the review process

**Normalization**: Already in [0.0, 1.0] range. No baseline needed — this is an absolute measure.

**Mutation Strategy Set**:

| Strategy | Description | Example |
|----------|-------------|---------|
| **Inversion** | Reverse a claim or condition | "must" → "must not" |
| **Deletion** | Remove a clause or section | Delete error handling section |
| **Substitution** | Replace a specific term with a related but incorrect one | "PostgreSQL" → "MySQL" in a PostgreSQL-specific guide |
| **Boundary** | Change numeric values to boundary conditions | "30 days" → "0 days" or "365 days" |
| **Contradiction** | Add a statement that contradicts an existing one | Add "API is stateless" when "session management" is described |

**Measurement Method**:
1. Select a document to evaluate
2. Create a copy and apply N mutations using the strategy set (minimum N=10)
3. Submit the mutated document for review (human or automated)
4. Count how many mutations were detected
5. Compute kill rate

**Edge Cases**:
- Trivial mutations (obvious typos): Exclude from count — only semantically meaningful mutations qualify
- Cascading mutations (one mutation causes another to be detected): Count each independently
- Self-contradicting mutations: Exclude mutations that contradict each other (only inject independent mutations)

**Worked Example**:

```
Document: API specification (50 sections)
Mutations applied: 10
  M1: Inversion — "GET endpoint returns JSON" → "GET endpoint returns XML" → Detected
  M2: Deletion — Removed authentication section → Detected
  M3: Substitution — "rate limit: 100/min" → "rate limit: 100/hour" → NOT detected
  M4: Boundary — "timeout: 30s" → "timeout: 0s" → Detected
  M5: Contradiction — Added "stateless API" when sessions are used → Detected
  M6: Inversion — "required field" → "optional field" → Detected
  M7: Deletion — Removed one error code from error table → NOT detected
  M8: Substitution — Changed endpoint path in one location → Detected
  M9: Boundary — "max payload: 10MB" → "max payload: 10KB" → Detected
  M10: Contradiction — Added conflicting versioning statement → NOT detected

MutationKillRate = 7 / 10 = 0.70
```

**Target**: A well-reviewed document should achieve kill rate > 0.80.

---

### 2.2 Contradiction Count (DI-2)

**Definition**: Number of internal contradictions in the document, normalized by document size.

**Formula**:

```
ContradictionDensity = contradiction_count / section_count
ContradictionScore = max(0.0, 1.0 - ContradictionDensity * penalty_factor)
```

Where:
- `contradiction_count`: Number of pairs of statements that make incompatible claims
- `section_count`: Number of logical sections in the document
- `penalty_factor`: Scaling factor (default: 5.0 — each contradiction per section reduces score by 0.2)

**Normalization**: [0.0, 1.0] where 1.0 = zero contradictions (healthy).

**Contradiction Types**:

| Type | Description | Example |
|------|-------------|---------|
| **Direct** | Two statements explicitly contradict | "API is RESTful" vs. "API uses GraphQL" |
| **Implicit** | Logical implication creates contradiction | "All endpoints require auth" + "Public health check endpoint" |
| **Temporal** | Statements true at different times but presented as simultaneous | "v2.0 removed feature X" + "Feature X configuration guide" |
| **Cross-reference** | References point to contradictory content | Section 3 references "see Table 2" but Table 2 contradicts Section 3 |

**Measurement Method**:
1. Parse document into logical sections
2. Extract claims/assertions from each section
3. For each pair of claims, evaluate compatibility (LLM-based semantic analysis)
4. Claims classified as incompatible are contradictions
5. Count contradictions and compute density

**Edge Cases**:
- Intentional contradictions (e.g., "pro/con" analysis): Exclude sections explicitly marked as comparative
- Versioned information: Contradictions between versions are not counted if versioning is clear
- Very short documents (< 3 sections): Report raw count instead of density

**Worked Example**:

```
Document: Software Design Specification (20 sections)

Contradictions found:
  C1: Section 2 says "microservices architecture"
      Section 8 says "monolithic deployment"
      → Direct contradiction

  C2: Section 5 says "all data encrypted at rest"
      Section 12 says "cache stored in plaintext for performance"
      → Implicit contradiction

ContradictionDensity = 2 / 20 = 0.10
ContradictionScore = max(0.0, 1.0 - 0.10 * 5.0) = 1.0 - 0.5 = 0.50
```

**Baseline Target**: Measure on 5 sample documents. Expected naive baseline: 0.5-0.7.

---

### 2.3 Ambiguity Score (DI-3)

**Definition**: Density of ambiguous terms or statements that could be interpreted in multiple valid ways, normalized to a quality score.

**Formula**:

```
AmbiguityDensity = ambiguous_statements / total_statements
AmbiguityScore = 1.0 - AmbiguityDensity
```

Where:
- `ambiguous_statements`: Statements containing terms or phrasing that admit multiple valid interpretations
- `total_statements`: Total assertive statements in the document (excluding headings, boilerplate)

**Ambiguity Indicators**:

| Indicator | Examples | Risk Level |
|-----------|----------|------------|
| **Vague quantifiers** | "several", "many", "some", "few", "various" | Medium |
| **Undefined references** | "as appropriate", "as needed", "when necessary" | High |
| **Passive without agent** | "the data will be processed", "errors are handled" | Medium |
| **Hedge words** | "should", "may", "might", "could", "generally" | Low-Medium |
| **Relative terms** | "fast", "large", "significant", "reasonable" | High |

**Measurement Method**:
1. Parse document into individual assertive statements
2. For each statement, scan for ambiguity indicators (pattern matching + LLM analysis)
3. Classify each flagged statement: truly ambiguous vs. appropriately flexible
4. Count truly ambiguous statements
5. Compute density and score

**Edge Cases**:
- Legal hedging (intentional "may"/"should"): Context-dependent — legal documents use these deliberately
- Requirements documents: "shall" is unambiguous, "should" is intentionally weaker per RFC 2119
- Early drafts: Higher ambiguity is expected and acceptable

**Worked Example**:

```
Document: Deployment Runbook (30 statements)

Ambiguous statements found:
  A1: "Wait for a reasonable time before retrying" → "reasonable" undefined
  A2: "Deploy to several staging servers" → "several" undefined
  A3: "Handle errors appropriately" → "appropriately" undefined
  A4: "The system should be fast enough" → "fast enough" undefined
  A5: "Data may be cached for performance" → intentional flexibility, NOT ambiguous

Truly ambiguous: 4 (A5 excluded as intentional)
AmbiguityDensity = 4 / 30 = 0.133
AmbiguityScore = 1.0 - 0.133 = 0.867
```

**Baseline Target**: Measure on 5 sample documents. Expected naive baseline: 0.6-0.8.

---

## 3. Axis Score Aggregation

```
DocumentIntegrityScore = w1 * MutationKillRate + w2 * ContradictionScore + w3 * AmbiguityScore
```

**Default weights**: w1 = 0.45, w2 = 0.30, w3 = 0.25

**Weight rationale**:
- Mutation Kill Rate (0.45): Most rigorous and comprehensive measure — subsumes aspects of the other two
- Contradiction Count (0.30): Internal contradictions are high-severity defects
- Ambiguity Score (0.25): Ambiguity is context-dependent and sometimes intentional

---

## 4. CQE Pattern Correspondence

| CQE Pattern | Document Integrity Impact | Sub-Metric Affected |
|-------------|--------------------------|---------------------|
| **#05 Assumption Mutation** | Direct foundation — mutation testing applied to documents | DI-1 Mutation Kill Rate |
| **#08 Template-Driven Role** | Structured templates reduce ambiguity and contradictions | DI-2, DI-3 |
| **#03 Cognitive Profile** | Adversarial reviewer personas detect more mutations | DI-1 Mutation Kill Rate |
| **#01 Attention Budget** | Budget prevents attention fatigue that causes overlooked contradictions | DI-2 Contradiction Count |

---

## 5. Connection to MutaDoc (Phase 2)

Document Integrity is the primary measurement axis for MutaDoc. The relationship:

| MutaDoc Feature | Document Integrity Sub-Metric |
|----------------|------------------------------|
| Mutation strategies (inversion, deletion, etc.) | DI-1 Mutation Kill Rate |
| Contradiction detection | DI-2 Contradiction Count |
| Ambiguity analysis | DI-3 Ambiguity Score |
| Mutation-Driven Repair | All three (repair targets all defect types) |

MutaDoc is both a **measurement tool** (computing DI scores) and a **remediation tool** (fixing detected issues). CQ Benchmark defines what to measure; MutaDoc provides automated measurement and repair.

---

## 6. Baseline Measurement Plan

| Step | Action | Sample Size | Data Source |
|------|--------|-------------|-------------|
| 1 | Select representative documents | 5 documents | Agent-generated outputs |
| 2 | Apply mutation strategies (10 mutations each) | 50 total mutations | Manual or automated injection |
| 3 | Submit mutated documents for review | 5 review sessions | Human or LLM-based review |
| 4 | Compute DI-1 (Mutation Kill Rate) | 5 values | Detection count / injection count |
| 5 | Extract claims and check for contradictions | 5 documents | LLM-based claim extraction |
| 6 | Compute DI-2 (Contradiction Count) | 5 values | Contradiction density formula |
| 7 | Scan for ambiguity indicators | 5 documents | Pattern matching + LLM analysis |
| 8 | Compute DI-3 (Ambiguity Score) | 5 values | Ambiguity density formula |
| 9 | Compute axis scores and record baseline | Mean, SD | Aggregation formula |
