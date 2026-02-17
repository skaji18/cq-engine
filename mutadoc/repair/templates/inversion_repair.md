# Repair Template: Inversion

> Resolves weak arguments detected by the Inversion mutation strategy (S4).
> Pipeline stage: Detection → **Repair Draft Generation** → Regression Mutation

---

## Repair Approach

When the Inversion strategy reveals that a claim or assumption collapses under reversal (low robustness score), the repair strengthens the original claim through three mechanisms:

1. **Evidence reinforcement** — Add citations, data references, or supporting evidence that make the claim resistant to inversion
2. **Contingency clauses** — Add explicit handling for the inverted scenario ("If X does not hold, then Y")
3. **Scope qualification** — Narrow the claim's scope to the domain where evidence supports it

### Repair Selection Logic

```
IF robustness_score < 20 (fragile — claim collapses under inversion):
  IF evidence_exists_but_uncited:
    → Primary: Evidence reinforcement
    → Confidence: High

  ELSE IF claim_is_conditional:
    → Primary: Contingency clause
    → Secondary: Scope qualification
    → Confidence: Medium

  ELSE IF claim_is_too_broad:
    → Primary: Scope qualification
    → Confidence: Medium

  ELSE:
    → Flag as "unsupported claim" — needs human judgment
    → Confidence: Low

ELSE IF robustness_score 20-50 (weak — argument bends significantly):
  → Primary: Scope qualification or contingency
  → Confidence: Medium

ELSE:
  → Claim is robust; no repair needed
```

---

## Prompt Template

```markdown
You are a document argumentation specialist. A claim with low robustness
has been detected:

**Location**: {{section_location}}
**Original claim**: "{{original_claim}}"
**Inverted claim**: "{{inverted_claim}}"
**Robustness score**: {{robustness_score}} / 100
**Dependent sections that collapse under inversion**: {{collapsed_sections}}
**Evidence gaps exposed**: {{evidence_gaps}}

Your task:
1. Determine the best repair mechanism:
   - Evidence reinforcement: cite or reference supporting data
   - Contingency clause: handle the inverted scenario explicitly
   - Scope qualification: narrow the claim to its defensible domain
   - Combination of the above

2. Generate a repair draft that:
   - Strengthens the claim without overstating it
   - Addresses the specific evidence gaps exposed by inversion
   - Preserves the original intent while increasing robustness

3. If the claim cannot be strengthened (genuinely unsupported):
   - Recommend removing the claim or converting to a hypothesis
   - Draft alternative language

Output format:
- **Repair mechanism**: [evidence / contingency / scope / combination / remove]
- **Repair draft**: [repaired text]
- **Evidence added**: [what supporting material was referenced]
- **Robustness improvement**: [estimated new robustness score]
- **Confidence**: [High/Medium/Low] — [justification]
```

---

## Auto-Applicable Criteria

An inversion repair is **auto-applicable** when ALL of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Repair is additive (adds evidence reference or qualifier) | Does not change the claim's core meaning |
| 2 | Evidence source is already present in the document | Cross-reference to existing content, not new claims |
| 3 | Repair mechanism is scope qualification only | Narrowing scope is safer than broadening evidence |
| 4 | No dependent sections are affected by the qualification | Scope narrowing doesn't cascade |

---

## Needs-Human-Review Criteria

An inversion repair **requires human review** when ANY of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Repair adds new evidence not present in the document | New factual claims need verification |
| 2 | Repair recommends removing or weakening a claim | Reducing the document's assertions is a policy decision |
| 3 | Contingency clause introduces new obligations | New obligations require authorization |
| 4 | Robustness score < 20 and no evidence exists | Claim may be genuinely unsupported |
| 5 | Claim is the document's central thesis or conclusion | Repair affects the document's core argument |

---

## Diff Output Format

### Evidence Reinforcement

```diff
--- a/paper.md (Section 4.2, Line 156)
+++ b/paper.md (Section 4.2, Line 156, REPAIRED)
@@ Discussion @@
- Our approach consistently improves performance across all tested scenarios.
+ Our approach improves performance in 8 of 10 tested scenarios (Table 3),
+ with statistically significant gains (p < 0.05) in 6 scenarios. The two
+ scenarios without improvement (high-noise and adversarial inputs) are
+ discussed in Section 5.2 (Limitations).
```

### Contingency Clause

```diff
--- a/contract.md (Section 8.1, Line 201)
+++ b/contract.md (Section 8.1, Line 201, REPAIRED)
@@ Market Assumptions @@
- This pricing model assumes stable market conditions throughout the
-  contract period.
+ This pricing model is based on market conditions as of the Effective Date.
+ In the event of material market changes (defined as a 15% or greater
+ shift in the applicable commodity index), either party may request a
+ pricing review under the adjustment procedure in Section 12.4.
```

### Scope Qualification

```diff
--- a/spec.md (Section 3.1, Line 45)
+++ b/spec.md (Section 3.1, Line 45, REPAIRED)
@@ Performance Guarantees @@
- The system handles any volume of concurrent requests without degradation.
+ The system handles up to 10,000 concurrent requests without degradation,
+ as validated in the load testing results documented in Appendix D.
+ Behavior above this threshold is not guaranteed and depends on the
+ infrastructure configuration specified in Section 2.3.
```

**Metadata block**:

```
Repair ID:       IR-007
Strategy:        Inversion
Original claim:  "consistently improves performance across all tested scenarios"
Robustness:      25 / 100 → estimated 75 / 100 after repair
Mechanism:       Evidence reinforcement + Scope qualification
Confidence:      Medium
Classification:  Needs-human-review (adds specific data claims)
```

---

## Repair Confidence Scoring

| Level | Definition | Criteria |
|-------|-----------|----------|
| **High** | Evidence already in document; just needs cross-reference | Repair is purely additive cross-reference; scope narrowing with clear bounds |
| **Medium** | Context suggests the right qualification/contingency | Evidence can be inferred; scope bounds are reasonable |
| **Low** | Claim may be genuinely unsupported | No evidence in document; claim is central thesis; contingency would fundamentally alter the argument |

**Scoring algorithm**:

```
score = 0

IF evidence_in_document: score += 35
ELSE IF evidence_inferable: score += 15

IF scope_bounds_clear: score += 20
IF repair_is_additive: score += 20
IF claim_is_not_central: score += 15

IF no_dependent_sections_affected: score += 10

IF score >= 65: confidence = "High"
ELSE IF score >= 35: confidence = "Medium"
ELSE: confidence = "Low"
```

---

## Regression Check Template

```markdown
You are a regression tester for document repairs. A weak claim was strengthened:

**Original claim** ({{location}}): "{{original_claim}}"
**Repaired text**: "{{repaired_text}}"
**Repair mechanism**: {{mechanism}}

Regression checks:
1. Does the repair overstate the evidence? Are citations/data accurate?
2. If scope was narrowed, does the narrower scope still support the
   document's conclusions?
   - Check: {{dependent_sections}}
3. If a contingency clause was added, does it conflict with other sections?
4. Does the repair introduce new ambiguity? (e.g., "material market
   changes" — is "material" defined?)
5. Is the qualified claim still strong enough to serve its purpose in
   the document's argument?

Output:
- **Evidence accuracy**: [pass/fail] — [details]
- **Scope sufficiency**: [pass/fail] — [details]
- **Contingency conflicts**: [yes/no] — [details]
- **New ambiguity**: [yes/no] — [details]
- **Argument integrity**: [pass/fail] — [details]
- **Regression verdict**: PASS / FAIL
```

---

## Examples

### Example 1: Uncited Evidence — Auto-Applicable (High Confidence)

**Detection finding**:
- Claim: "Our method outperforms all baselines"
- Inverted: "Our method underperforms all baselines"
- Robustness score: 30 — no evidence cited in the claim sentence
- Table 3 (already in document) shows the method outperforms 8/10 baselines

**Repair** (Evidence reinforcement):
```diff
- Our method outperforms all baselines in the evaluation.
+ Our method outperforms 8 of 10 baselines (Table 3), with a mean
+ improvement of 12.3% on the primary metric. Exceptions are noted
+ in Section 5.2 (Limitations).
```

**Confidence**: High (evidence is in the document; repair is cross-reference + scope)
**Classification**: Needs-human-review (adds specific numerical claims from table)

### Example 2: Unsupported Assumption — Low Confidence

**Detection finding**:
- Claim: "Users will adopt the new workflow within 2 weeks"
- Inverted: "Users will NOT adopt the new workflow within 2 weeks"
- Robustness score: 10 — no evidence for adoption timeline
- No supporting data in the document

**Repair options**:

Option A — Convert to hypothesis:
```diff
- Users will adopt the new workflow within 2 weeks of deployment.
+ Based on comparable workflow changes in similar organizations, we
+ estimate a 2-4 week adoption period. This assumption should be
+ validated through a pilot program (see Section 7: Validation Plan).
```

Option B — Add contingency:
```diff
- Users will adopt the new workflow within 2 weeks of deployment.
+ Users are expected to adopt the new workflow within 2 weeks of
+ deployment, supported by the training program in Section 6.3.
+ If adoption metrics (defined in Appendix E) are not met within
+ 4 weeks, the fallback procedure in Section 9.1 will be activated.
```

**Confidence**: Low (no evidence; claim is a planning assumption)
**Classification**: Needs-human-review (unsupported claim; policy decision)
