# Axis 2: Decision Quality Score

> **Purpose**: Measure the quality of agent reasoning and decision-making.
> **CQE Pattern Link**: Cognitive Profile (#03), Assumption Mutation (#05), Wave Scheduler (#04)
> **Effort**: M

---

## 1. Definition

Decision Quality measures how well an agent system reasons about problems and makes judgments. High decision quality means decisions are informed by diverse perspectives, free from anchoring bias, and cover relevant stakeholder concerns. Low decision quality means decisions are narrow, biased by generation order, and blind to critical viewpoints.

**Why it matters**: The most common failure mode in LLM agent systems is not incorrect computation but flawed reasoning — anchoring on the first perspective, missing stakeholder concerns, or failing to challenge assumptions. Decision Quality captures these failure modes quantitatively.

---

## 2. Sub-Metrics

### 2.1 Perspective Diversity (DQ-1)

**Definition**: Number of genuinely independent viewpoints considered before a decision, normalized against the expected number for the decision's complexity.

**Formula**:

```
PerspectiveDiversity = independent_perspectives / expected_perspectives

independent_perspectives = count(perspectives where pairwise_similarity < threshold)
```

Where:
- `perspectives`: Set of distinct analytical viewpoints generated during the decision process
- `pairwise_similarity`: Cosine similarity between perspective embedding vectors
- `threshold`: Independence threshold (default: 0.65 — perspectives with cosine similarity below this are considered independent)
- `expected_perspectives`: Expected number of perspectives for the decision's complexity class

**Complexity Classes and Expected Perspectives**:

| Complexity | Criteria | Expected Perspectives |
|------------|----------|----------------------|
| Low | Single-domain, reversible decision | 2-3 |
| Medium | Cross-domain or significant impact | 4-5 |
| High | Strategic, irreversible, multi-stakeholder | 6-8 |

**Normalization**: Capped at 1.0 (more perspectives than expected = 1.0, not > 1.0).

**Measurement Method**:
1. Collect all analytical perspectives generated during the decision process
2. Embed each perspective using a text embedding model
3. Compute pairwise cosine similarity matrix
4. Count perspectives where ALL pairwise similarities to other perspectives are below threshold
5. Classify decision complexity and determine expected perspectives
6. Divide independent count by expected count, cap at 1.0

**Worked Example**:

```
Decision: "Should we migrate from PostgreSQL to DynamoDB?"
Complexity: Medium (cross-domain) → Expected: 4-5 perspectives

Generated perspectives:
  P1: Performance analysis (latency, throughput projections)
  P2: Cost analysis (licensing, operational costs)
  P3: Developer experience (learning curve, tooling)
  P4: Data model compatibility (relational → NoSQL mapping)
  P5: Vendor lock-in risk assessment

Pairwise similarity matrix (cosine):
     P1    P2    P3    P4    P5
P1  1.00  0.25  0.30  0.45  0.20
P2  0.25  1.00  0.35  0.15  0.40
P3  0.30  0.35  1.00  0.28  0.22
P4  0.45  0.15  0.28  1.00  0.18
P5  0.20  0.40  0.22  0.18  1.00

All pairwise similarities < 0.65 → All 5 are independent.
PerspectiveDiversity = 5 / 5 = 1.0
```

**Baseline Target**: Measure on 10 decision cases. Expected naive baseline (single-agent sequential): 0.3-0.5. Expected with ThinkTank: 0.7-0.9.

---

### 2.2 Anchoring Elimination (DQ-2)

**Definition**: Degree to which later-generated analyses are independent of earlier ones, measuring freedom from generation-order bias.

**Formula**:

```
AnchoringElimination = 1.0 - |correlation(generation_order, similarity_to_first)|
```

Where:
- `generation_order`: Sequence number of each perspective (1st, 2nd, 3rd, ...)
- `similarity_to_first`: Cosine similarity of each perspective to the first-generated perspective
- `correlation`: Pearson correlation coefficient
- A positive correlation means later perspectives drift toward the first one (anchoring)
- The score is inverted so that 1.0 = no anchoring (healthy)

**Normalization**: [0.0, 1.0] where 1.0 = no anchoring effect detected.

**Measurement Method**:
1. Record the generation order of all perspectives
2. Compute cosine similarity of each perspective to the first-generated perspective
3. Compute Pearson correlation between generation order and similarity-to-first
4. If correlation is significantly positive (> 0.3), anchoring is present
5. Score = 1.0 - |correlation| (stronger correlation = lower score)

**Edge Cases**:
- Only 1 perspective generated: AnchoringElimination = null (insufficient data)
- Only 2 perspectives: Use direct similarity comparison instead of correlation
- Parallel generation (same timestamp): All perspectives have "order 1" → score = 1.0 by design (parallel generation eliminates anchoring by construction)

**Worked Example**:

```
Sequential generation (ChatGPT-style "list 5 perspectives"):
  P1 (order 1): similarity_to_P1 = 1.00
  P2 (order 2): similarity_to_P1 = 0.72
  P3 (order 3): similarity_to_P1 = 0.68
  P4 (order 4): similarity_to_P1 = 0.75
  P5 (order 5): similarity_to_P1 = 0.80

correlation(order, similarity) = 0.15 (weak positive — later ones drift back)
AnchoringElimination = 1.0 - |0.15| = 0.85

---

Parallel generation (ThinkTank-style independent contexts):
  P1 (order 1): similarity_to_P1 = 1.00 (excluded as self-reference)
  P2 (order 1): similarity_to_P1 = 0.31
  P3 (order 1): similarity_to_P1 = 0.28
  P4 (order 1): similarity_to_P1 = 0.42
  P5 (order 1): similarity_to_P1 = 0.19

All generated in parallel → correlation undefined → AnchoringElimination = 1.0
```

**Baseline Target**: Measure sequential (ChatGPT-style) generation as baseline. Expected: 0.5-0.7. Parallel generation should achieve 0.9-1.0.

---

### 2.3 Blind-Spot Coverage (DQ-3)

**Definition**: Proportion of relevant stakeholder concerns addressed in the final analysis.

**Formula**:

```
BlindSpotCoverage = addressed_concerns / total_relevant_concerns
```

Where:
- `total_relevant_concerns`: Predefined set of concerns relevant to the decision domain
- `addressed_concerns`: Subset of concerns that are explicitly discussed in the analysis output

**Concern Taxonomies** (predefined per domain):

| Domain | Concern Categories |
|--------|-------------------|
| **Technology Decision** | Performance, Cost, Security, Scalability, Maintainability, Developer Experience, Vendor Lock-in, Migration Risk |
| **Business Strategy** | Revenue Impact, Cost Impact, Competitive Position, Customer Impact, Employee Impact, Regulatory Risk, Timeline, Reversibility |
| **Policy Decision** | Economic Impact, Social Impact, Environmental Impact, Legal Compliance, Implementation Feasibility, Public Perception, Equity/Fairness, Unintended Consequences |

**Measurement Method**:
1. Classify the decision domain
2. Load the corresponding concern taxonomy
3. For each concern in the taxonomy, search the analysis output for explicit discussion
4. A concern is "addressed" if the output contains a substantive statement about it (not just mention)
5. Compute ratio

**Edge Cases**:
- Unknown domain: Use the union of all concern categories
- Custom concerns: Users can extend the taxonomy for their domain
- Partial address: A concern mentioned but not analyzed counts as 0.5

**Worked Example**:

```
Decision: "Adopt Kubernetes for production deployment"
Domain: Technology Decision
Total concerns: 8 (Performance, Cost, Security, Scalability,
                    Maintainability, Dev Experience, Vendor Lock-in, Migration Risk)

Analysis output addresses:
  - Performance: Yes (latency benchmarks discussed) → 1.0
  - Cost: Yes (infrastructure cost comparison) → 1.0
  - Security: Mentioned but not analyzed ("security should be considered") → 0.5
  - Scalability: Yes (horizontal scaling analysis) → 1.0
  - Maintainability: Not discussed → 0.0
  - Developer Experience: Yes (learning curve analysis) → 1.0
  - Vendor Lock-in: Not discussed → 0.0
  - Migration Risk: Yes (rollback plan outlined) → 1.0

BlindSpotCoverage = (1.0+1.0+0.5+1.0+0.0+1.0+0.0+1.0) / 8 = 5.5 / 8 = 0.6875
```

**Baseline Target**: Measure on 5 decision cases with predefined concern lists. Expected naive baseline: 0.4-0.6. Expected with ThinkTank: 0.7-0.9.

---

## 3. Axis Score Aggregation

```
DecisionQualityScore = w1 * PerspectiveDiversity + w2 * AnchoringElimination + w3 * BlindSpotCoverage
```

**Default weights**: w1 = 0.35, w2 = 0.30, w3 = 0.35

**Weight rationale**:
- Perspective Diversity (0.35): Foundational — diversity of viewpoints is prerequisite for quality decisions
- Anchoring Elimination (0.30): Important but less actionable — mainly addressed by architectural choice (parallel vs. sequential)
- Blind-Spot Coverage (0.35): Directly actionable — missing concerns can be systematically identified and addressed

---

## 4. CQE Pattern Correspondence

| CQE Pattern | Decision Quality Impact | Sub-Metric Affected |
|-------------|------------------------|---------------------|
| **#03 Cognitive Profile** | Specialized personas generate more diverse perspectives | DQ-1 Perspective Diversity |
| **#05 Assumption Mutation** | Challenging premises reveals blind spots | DQ-3 Blind-Spot Coverage |
| **#04 Wave Scheduler** | Parallel execution in Wave 1 eliminates anchoring | DQ-2 Anchoring Elimination |
| **#02 Context Gate** | Independent contexts prevent cross-perspective contamination | DQ-2 Anchoring Elimination |
| **#08 Template-Driven Role** | Structured roles ensure systematic concern coverage | DQ-3 Blind-Spot Coverage |

---

## 5. Baseline Measurement Plan

| Step | Action | Sample Size | Data Source |
|------|--------|-------------|-------------|
| 1 | Select representative decision tasks | 10 tasks | Past decision records |
| 2 | For sequential baseline: generate perspectives in single context | 10 runs | Single-agent LLM output |
| 3 | For parallel baseline: generate perspectives in independent contexts | 10 runs | Multi-agent parallel output |
| 4 | Embed all perspectives | N perspectives per run | Text embedding model |
| 5 | Compute DQ-1 (Perspective Diversity) | 10 values per condition | Pairwise similarity analysis |
| 6 | Compute DQ-2 (Anchoring Elimination) | 10 values per condition | Order-similarity correlation |
| 7 | Compute DQ-3 (Blind-Spot Coverage) | 10 values per condition | Concern taxonomy matching |
| 8 | Compare conditions and record baselines | Mean, SD per condition | Statistical comparison |
