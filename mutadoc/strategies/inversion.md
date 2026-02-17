# Strategy: Inversion

## Overview

The Inversion strategy reverses assumptions, claims, and conditions in a document, then measures how well the surrounding argument structure withstands the reversal. **Weak arguments collapse under inversion; robust arguments survive because they are backed by evidence and logical structure.**

Inversion exposes:
- **Unsupported claims**: Assertions presented as fact with no evidence — inverting them reveals that neither the original nor its opposite can be justified
- **Hidden assumptions**: Premises the author treats as self-evident but which could reasonably be false
- **Evidence gaps**: Points where the argument would need evidence to survive challenge but has none
- **Fragile conclusions**: Final conclusions that depend on a single uninverted assumption — a single-point-of-failure in the argument chain

Unlike Contradiction (which alters one clause to detect cross-clause conflicts) or Deletion (which removes text to measure structural impact), Inversion tests the **epistemological strength** of individual claims — does this assertion hold up when challenged?

## When to Use

| Scenario | Suitability | Notes |
|----------|:-----------:|-------|
| Academic papers (pre-submission review) | High | Exposes methodology weaknesses and unsupported conclusions |
| Policy documents with stated assumptions | High | Reveals which policy foundations are untested |
| Business plans with market assumptions | High | Tests whether financial projections survive premise reversal |
| Contracts with conditional clauses | Medium | Tests contingency robustness ("if market conditions change...") |
| Purely descriptive/factual documents | Low | Factual statements have clear truth values; inversion is less revealing |
| Short memos or status updates | Low | Too few claims to justify systematic inversion |

## Prompt Template

### Single-Claim Inversion

```markdown
You are an argument analyst performing an Inversion Mutation Test.

## Your Task

A specific claim in the document has been INVERTED (reversed). Your job is to
analyze how well the surrounding argument structure withstands this inversion.

## Original Document

{full_document}

## Inverted Claim

**Location**: {claim_location}
**Original claim**: "{original_claim}"
**Inverted claim**: "{inverted_claim}"

## Analysis Instructions

1. **Claim classification**: What type of claim is this?
   - Empirical claim (testable with data)
   - Logical claim (follows from premises)
   - Assumption (treated as given, not argued)
   - Value judgment (normative, not empirical)
   - Condition (if-then statement)

2. **Evidence assessment**: What evidence supports the ORIGINAL claim?
   - Direct evidence cited in the document
   - Indirect evidence (implied but not cited)
   - No evidence (asserted without support)

3. **Inversion impact**: If the inverted claim were true instead:
   - Which other sections, arguments, or conclusions would be affected?
   - Would the document's main conclusion still hold?
   - Are there contingency plans or caveats that address this scenario?

4. **Robustness score**: Rate the claim's robustness on a scale of 0-100:
   - 0-20: Fragile — claim has no evidence and multiple sections collapse under inversion
   - 21-50: Weak — claim has some support but key dependent arguments fail
   - 51-80: Moderate — claim has evidence but inversion reveals gaps in contingency planning
   - 81-100: Robust — claim is well-supported, and the document addresses the inverted scenario

5. **Evidence gaps**: What evidence would be needed to make this claim robust
   against inversion?

## Output Format

```yaml
inversion_result:
  claim_location: "{claim_location}"
  original_claim: "{original_claim}"
  inverted_claim: "{inverted_claim}"
  claim_type: "<empirical | logical | assumption | value_judgment | condition>"
  evidence_for_original:
    direct: ["..."]
    indirect: ["..."]
    none: <true | false>
  robustness_score: <0-100>
  classification: "<fragile | weak | moderate | robust>"
  dependent_sections:
    - section_id: "..."
      impact: "<collapses | weakened | unaffected>"
      description: "..."
  conclusion_survives: <true | false>
  contingency_exists: <true | false>
  evidence_gaps:
    - "What evidence is missing that would strengthen this claim"
  recommendation: "<add_evidence | add_contingency | qualify_scope | accept_risk>"
```
```

### Systematic Inversion (All Claims)

```markdown
You are performing a systematic Inversion Mutation Test on a document.

## Your Task

Identify ALL invertible claims, assumptions, and conditions in the document,
then evaluate each for robustness under inversion.

## Document

{full_document}

## Inversion Target: {inversion_target}
(Options: all_claims / hypotheses_only / assumptions_only / specific_sections)

## Instructions

1. **Claim extraction**: Identify all statements that can be meaningfully inverted.
   Skip purely factual statements (dates, names, defined terms) and focus on:
   - Causal claims ("X leads to Y")
   - Comparative claims ("X is better than Y")
   - Existence claims ("There is a market for X")
   - Conditional claims ("If X, then Y")
   - Assumptions ("Assuming market stability...")

2. **For each invertible claim**, produce:
   - Original text and inverted text
   - Claim type
   - Robustness score (0-100)
   - Whether the document's conclusion survives inversion
   - Key evidence gaps

3. **Prioritize**: Sort by robustness score (lowest first — most fragile claims first).

## Output Format

```yaml
inversion_sweep:
  document: "{document_name}"
  inversion_target: "{inversion_target}"
  total_claims_found: <N>
  total_invertible: <N>
  results:
    - claim_location: "..."
      original_claim: "..."
      inverted_claim: "..."
      claim_type: "..."
      robustness_score: <0-100>
      classification: "..."
      conclusion_survives: <true | false>
      evidence_gaps: ["..."]
  summary:
    fragile_claims: <count>
    weak_claims: <count>
    moderate_claims: <count>
    robust_claims: <count>
    weakest_link: "The claim with the lowest robustness score"
    overall_argument_robustness: <0-100>
```
```

## Input Specification

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `document_path` | string | Yes | Path to the target document (Markdown or plain text) |
| `inversion_target` | enum | No | `all_claims` (default), `hypotheses_only`, `assumptions_only`, specific section identifiers |
| `include_evidence_gaps` | boolean | No | If true, generates evidence gap recommendations (default: true) |
| `min_robustness_alert` | integer | No | Only report claims below this robustness threshold (default: 50) |

### Inversion Target Definitions

| Target | What Gets Inverted | When to Use |
|--------|-------------------|-------------|
| `all_claims` | Every invertible statement | Comprehensive analysis; use for important documents |
| `hypotheses_only` | Explicit hypotheses and thesis statements | Academic papers, research proposals |
| `assumptions_only` | Statements marked or implied as assumptions | Business plans, policy documents |
| `specific_sections` | Claims within specified sections only | Targeted review of known weak areas |

## Output Format

```yaml
inversion_report:
  document: "research_paper.md"
  inversion_target: "all_claims"
  timestamp: "2026-01-20T14:00:00Z"
  total_claims_found: 18
  total_invertible: 12
  results:
    - claim_location: "Section 4.2, paragraph 1"
      original_claim: "Our method improves performance by 15% over the baseline"
      inverted_claim: "Our method degrades performance by 15% compared to the baseline"
      claim_type: "empirical"
      evidence_for_original:
        direct: ["Table 3 shows 15.2% improvement on dataset A"]
        indirect: ["Similar methods in [ref 12] showed comparable gains"]
        none: false
      robustness_score: 72
      classification: "moderate"
      dependent_sections:
        - section_id: "Section 5 (Discussion)"
          impact: "weakened"
          description: "Discussion assumes positive results; no contingency for negative outcome"
        - section_id: "Section 6 (Conclusion)"
          impact: "collapses"
          description: "Conclusion directly claims superiority based on this result"
      conclusion_survives: false
      contingency_exists: false
      evidence_gaps:
        - "No results on datasets B or C — performance claim may not generalize"
        - "No statistical significance test reported"
      recommendation: "add_evidence"

    - claim_location: "Section 2.1, paragraph 3"
      original_claim: "We assume training data is representative of production distribution"
      inverted_claim: "Training data is NOT representative of production distribution"
      claim_type: "assumption"
      evidence_for_original:
        direct: []
        indirect: []
        none: true
      robustness_score: 15
      classification: "fragile"
      dependent_sections:
        - section_id: "Section 4 (Results)"
          impact: "collapses"
          description: "All experimental results are invalid if data is not representative"
        - section_id: "Section 5 (Discussion)"
          impact: "collapses"
          description: "Discussion of practical applicability is unfounded"
      conclusion_survives: false
      contingency_exists: false
      evidence_gaps:
        - "No distribution comparison between training and production data"
        - "No robustness analysis under distribution shift"
      recommendation: "add_evidence"

  summary:
    fragile_claims: 3
    weak_claims: 4
    moderate_claims: 3
    robust_claims: 2
    weakest_link:
      claim: "We assume training data is representative of production distribution"
      score: 15
    overall_argument_robustness: 42
```

## Severity Criteria

| Classification | Robustness Score | Meaning | Action |
|---------------|:---------------:|---------|--------|
| **Fragile** | 0–20 | No evidence; multiple sections collapse under inversion | Critical: add evidence or remove claim |
| **Weak** | 21–50 | Some support but key arguments fail under inversion | Major: strengthen evidence or add contingency |
| **Moderate** | 51–80 | Evidence exists but contingency planning is lacking | Minor: add contingency discussion or qualify scope |
| **Robust** | 81–100 | Well-supported; document addresses inverted scenario | Informational: no action required |

### Severity Context by Document Type

| Document Type | Fragile Claim Severity | Implication |
|--------------|:----------------------:|-------------|
| Academic Paper | Critical | Peer reviewers will attack unsupported claims |
| Business Plan | Critical | Investors will challenge untested assumptions |
| Policy Document | Major | Opposing stakeholders will exploit weak premises |
| Contract | Major | Conditional clauses without contingency create liability |
| Technical Spec | Moderate | Assumptions may be validated during implementation |

## Examples

### Example 1: Unsupported Claim in a Research Paper

**Input document** (excerpt):
```markdown
## 4. Results
Our approach achieves a 23% reduction in processing time compared to the
standard method. This improvement demonstrates the viability of parallel
decomposition for this problem class.

## 5. Conclusion
We have shown that parallel decomposition significantly improves performance,
making it the preferred approach for large-scale processing tasks.
```

**Inversion target**: "parallel decomposition significantly improves performance"

**Result**:
```yaml
inversion_result:
  original_claim: "parallel decomposition significantly improves performance"
  inverted_claim: "parallel decomposition does NOT significantly improve performance"
  claim_type: "empirical"
  evidence_for_original:
    direct: ["23% reduction in processing time (Section 4)"]
    indirect: []
    none: false
  robustness_score: 35
  classification: "weak"
  dependent_sections:
    - section_id: "Section 5 (Conclusion)"
      impact: "collapses"
      description: "Conclusion claims 'preferred approach' based solely on this result"
  conclusion_survives: false
  evidence_gaps:
    - "Only one metric reported (processing time) — no quality or accuracy comparison"
    - "No statistical significance test"
    - "'Significantly' is undefined — is 23% statistically or practically significant?"
  recommendation: "add_evidence"
```

### Example 2: Untested Assumption in a Business Plan

**Input document** (excerpt):
```markdown
## Market Analysis
We assume the enterprise SaaS market will grow at 12% annually over the
next 5 years, consistent with current analyst projections.

## Financial Projections
Based on market growth of 12%, we project revenue of $5M in Year 3.
```

**Inversion target**: "enterprise SaaS market will grow at 12% annually"

**Result**:
```yaml
inversion_result:
  original_claim: "enterprise SaaS market will grow at 12% annually"
  inverted_claim: "enterprise SaaS market will NOT grow at 12% annually (stagnation or decline)"
  claim_type: "assumption"
  evidence_for_original:
    direct: ["current analyst projections (unspecified source)"]
    indirect: []
    none: false
  robustness_score: 28
  classification: "weak"
  dependent_sections:
    - section_id: "Financial Projections"
      impact: "collapses"
      description: "Revenue projection of $5M directly depends on 12% growth assumption"
  conclusion_survives: false
  contingency_exists: false
  evidence_gaps:
    - "Analyst source not cited — reliability unknown"
    - "No sensitivity analysis for different growth rates"
    - "No contingency plan for market downturn scenario"
  recommendation: "add_contingency"
```

## Integration

### Invocation from mutadoc.sh

```bash
# Full inversion sweep (all claims)
mutadoc test document.md --strategy inversion

# Hypotheses only (for academic papers)
mutadoc test paper.md --strategy inversion --inversion-target hypotheses_only

# Assumptions only (for business plans)
mutadoc test plan.md --strategy inversion --inversion-target assumptions_only

# Specific section
mutadoc test document.md --strategy inversion --target "Section 4.2"

# With robustness threshold (only report fragile + weak claims)
mutadoc test document.md --strategy inversion --min-robustness 50
```

### Internal Integration

```bash
# In mutadoc.sh, the inversion strategy is invoked as:
run_strategy "inversion" "$DOCUMENT_PATH" "$INVERSION_TARGET" "$TARGET_SECTION"

# The function:
# 1. Reads the strategy template from strategies/inversion.md
# 2. If target is "all_claims":
#    a. Uses the systematic inversion prompt to extract and test all claims
# 3. If target is a specific section/claim:
#    a. Extracts the claim text
#    b. Generates the inversion (logical negation)
#    c. Uses the single-claim inversion prompt
# 4. Parses the YAML response
# 5. Sorts results by robustness score (lowest first)
# 6. Generates the overall argument robustness score
```

### Combination with Other Strategies

Inversion testing is most effective when combined with:

| Strategy | Combination Effect |
|----------|-------------------|
| **Deletion** | Critical dependencies identified by deletion are prime inversion targets — if the document depends heavily on a section, that section's claims must be robust |
| **Ambiguity** | Ambiguous claims are often invertible in multiple ways, revealing that the original text fails to commit to any specific meaning |
| **Contradiction** | Inverted claims may reveal hidden contradictions with other sections that were invisible in the original form |
| **Boundary** | Claims involving numerical parameters should be tested with both inversion (claim direction) and boundary (parameter extremes) |
