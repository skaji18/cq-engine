# Repair Template: Contradiction

> Resolves contradictions detected by the Contradiction mutation strategy (S1).
> Pipeline stage: Detection → **Repair Draft Generation** → Regression Mutation

---

## Repair Approach

When a contradiction is detected between two or more document sections, the repair process follows three steps:

1. **Identify the dominant clause** — Determine which clause represents the document's primary intent by analyzing context, document structure (earlier definitions tend to dominate), and explicit priority language ("notwithstanding," "subject to," "in the event of conflict")
2. **Generate amendment for subordinate clause** — Rewrite the subordinate clause to align with the dominant clause, preserving its original purpose while eliminating the contradiction
3. **Verify cross-reference consistency** — Ensure the amendment doesn't create new contradictions with other sections that reference either the dominant or subordinate clause

### Decision Logic

```
IF contradiction involves an explicit priority clause ("notwithstanding Section X"):
  → Dominant = the clause with priority language
  → Subordinate = the referenced clause
  → Confidence: High

ELSE IF contradiction involves a definition and its usage:
  → Dominant = the definition clause
  → Subordinate = the usage that contradicts the definition
  → Confidence: High

ELSE IF contradiction involves two obligations:
  → Dominant = CANNOT auto-determine (needs human review)
  → Confidence: Low
  → Present both options with trade-off analysis

ELSE:
  → Use structural proximity and document hierarchy
  → Earlier/higher-level clause is tentatively dominant
  → Confidence: Medium
```

---

## Prompt Template

```markdown
You are a document repair specialist. A contradiction has been detected:

**Clause A** ({{clause_a_location}}):
> {{clause_a_text}}

**Clause B** ({{clause_b_location}}):
> {{clause_b_text}}

**Contradiction description**: {{contradiction_description}}

**Detected dominant clause**: {{dominant_clause}} (Basis: {{dominance_basis}})

Your task:
1. Confirm or challenge the dominant clause identification. If you disagree, explain why.
2. Generate a repair draft for the subordinate clause that:
   - Resolves the contradiction
   - Preserves the original intent of the subordinate clause as much as possible
   - Uses language consistent with the document's style and terminology
   - Adds an explicit cross-reference to the dominant clause where appropriate
3. Identify any other sections that may be affected by this repair.
4. Rate your confidence: High / Medium / Low with justification.

Output format:
- **Dominant clause**: [confirmed/challenged] — [reasoning]
- **Repair draft**: [repaired text for subordinate clause]
- **Affected sections**: [list of sections to check]
- **Confidence**: [High/Medium/Low] — [justification]
```

---

## Auto-Applicable Criteria

A contradiction repair is **auto-applicable** (can be applied without human review) when ALL of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Dominant clause is determined by explicit priority language | No ambiguity about which clause takes precedence |
| 2 | Repair is purely additive (adds cross-reference or qualifier) | Does not change obligations or rights |
| 3 | Only one subordinate clause needs amendment | Single-point fix with limited blast radius |
| 4 | Repair confidence is High | Automated determination is reliable |

---

## Needs-Human-Review Criteria

A contradiction repair **requires human review** when ANY of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Both clauses have equal structural authority | Cannot auto-determine which should dominate |
| 2 | Repair modifies an obligation, right, or deadline | Changes legal or contractual meaning |
| 3 | Contradiction involves 3+ clauses | Cascading repair risk too high for auto-fix |
| 4 | Dominant clause is determined by context inference (not explicit language) | Inference may be wrong |
| 5 | Repair requires choosing between two valid interpretations | Policy decision, not technical fix |

---

## Diff Output Format

Repairs are displayed in GitHub PR diff style for easy human review:

```diff
--- a/document.md (Section 12.3, Line 145)
+++ b/document.md (Section 12.3, Line 145, REPAIRED)
@@ Termination Provisions @@
- Section 12.3: "Following the notice period, either party may terminate
-  this agreement immediately upon written notification."
+ Section 12.3: "Following the 30-day notice period defined in Section 5.1,
+  either party may terminate this agreement upon written notification
+  delivered in accordance with Section 15 (Notices)."
```

**Metadata block** (appended to each diff):

```
Repair ID:       CR-001
Strategy:        Contradiction
Dominant clause: Section 5.1 (explicit definition of notice period)
Confidence:      High
Classification:  Auto-applicable
Affected:        Section 15 (Notices) — verify delivery method consistency
```

---

## Repair Confidence Scoring

| Level | Definition | Criteria |
|-------|-----------|----------|
| **High** | Repair is almost certainly correct | Dominant clause identified by explicit language; single subordinate clause; repair is additive |
| **Medium** | Repair is likely correct but should be verified | Dominant clause identified by structural position; 1-2 subordinate clauses; repair modifies non-critical text |
| **Low** | Repair is a suggestion only | Dominant clause unclear; multiple subordinate clauses; repair modifies obligations or rights |

**Scoring algorithm**:

```
score = 0

IF explicit_priority_language: score += 40
ELSE IF definition_vs_usage: score += 30
ELSE IF structural_hierarchy: score += 15

IF single_subordinate_clause: score += 20
ELSE IF two_subordinate_clauses: score += 10

IF repair_is_additive: score += 20
ELSE IF repair_modifies_non_obligation: score += 10

IF score >= 70: confidence = "High"
ELSE IF score >= 40: confidence = "Medium"
ELSE: confidence = "Low"
```

---

## Regression Check Template

After applying a contradiction repair, run the following regression checks:

```markdown
You are a regression tester for document repairs. A contradiction was repaired:

**Original subordinate clause** ({{location}}):
> {{original_text}}

**Repaired clause**:
> {{repaired_text}}

**Dominant clause** ({{dominant_location}}):
> {{dominant_text}}

Regression checks:
1. Does the repaired clause introduce any NEW contradiction with other sections?
   - Check all sections that reference {{location}} or {{dominant_location}}
   - Check all sections referenced BY the repaired clause
2. Does the repair change any obligation, right, or deadline not covered by the original contradiction?
3. Does the repair introduce any ambiguity that did not exist before?
4. Is the repaired language consistent with the document's terminology and style?

Output:
- **New contradictions found**: [yes/no] — [details if yes]
- **Unintended obligation changes**: [yes/no] — [details if yes]
- **New ambiguity introduced**: [yes/no] — [details if yes]
- **Style consistency**: [pass/fail] — [details if fail]
- **Regression verdict**: PASS / FAIL
```

---

## Examples

### Example 1: Explicit Priority — Auto-Applicable (High Confidence)

**Detection finding**:
- Section 5.1 defines notice period as "30 calendar days"
- Section 12.3 states "either party may terminate immediately"
- Contradiction: "30 days" vs "immediately"

**Dominant clause**: Section 5.1 (contains the explicit definition)

**Repair draft**:

```diff
--- a/contract.md (Section 12.3)
+++ b/contract.md (Section 12.3, REPAIRED)
- Either party may terminate this agreement immediately upon written notice.
+ Either party may terminate this agreement upon 30 calendar days' written
+ notice as defined in Section 5.1.
```

**Confidence**: High (definition dominates usage; repair is additive)
**Classification**: Auto-applicable
**Regression**: PASS — no other sections reference Section 12.3's termination timing

### Example 2: Competing Obligations — Needs Human Review (Low Confidence)

**Detection finding**:
- Section 7.2: "Contractor shall deliver source code upon request"
- Section 9.1: "All intellectual property remains with Contractor until final payment"
- Contradiction: delivery obligation vs. IP retention

**Dominant clause**: Cannot determine — both are substantive obligations

**Repair options presented**:

Option A — Contractor IP dominates:
```diff
- Section 7.2: "Contractor shall deliver source code upon request."
+ Section 7.2: "Contractor shall deliver source code upon request,
+  subject to the intellectual property provisions of Section 9.1.
+  Full transfer of source code ownership occurs upon final payment."
```

Option B — Delivery obligation dominates:
```diff
- Section 9.1: "All intellectual property remains with Contractor
-  until final payment."
+ Section 9.1: "All intellectual property remains with Contractor
+  until final payment, provided that Contractor shall grant Client
+  a limited license to use delivered source code for the purposes
+  specified in Section 3 (Scope of Work) during the interim period."
```

**Confidence**: Low (competing obligations; policy decision required)
**Classification**: Needs-human-review
**Note**: Both options are legally viable. The choice depends on the commercial intent of the agreement.
