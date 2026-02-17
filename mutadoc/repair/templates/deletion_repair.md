# Repair Template: Deletion

> Resolves dead clauses and structural isolation detected by the Deletion mutation strategy (S3).
> Pipeline stage: Detection → **Repair Draft Generation** → Regression Mutation

---

## Repair Approach

When the Deletion strategy identifies a clause with zero or near-zero structural impact (a "dead clause"), two repair paths exist:

1. **Remove** — Delete the dead clause with documented justification, if it truly adds no value
2. **Integrate** — Add cross-references and structural connections to make the clause relevant within the document's dependency graph

### Decision Logic

```
IF structural_impact_score == 0:
  IF clause_is_boilerplate AND document_has_equivalent_elsewhere:
    → Recommend: Remove (duplicate boilerplate)
    → Confidence: High

  ELSE IF clause_was_likely_important_but_orphaned:
    → Recommend: Integrate (add cross-references)
    → Confidence: Medium

  ELSE:
    → Present both options to human
    → Confidence: Low

ELSE IF structural_impact_score < 20:
  → Recommend: Integrate (strengthen connections)
  → Confidence: Medium

ELSE:
  → Not a dead clause; no deletion repair needed
```

---

## Prompt Template

```markdown
You are a document structure specialist. A clause with low structural impact
has been detected:

**Location**: {{section_location}}
**Clause text**: "{{clause_text}}"
**Structural impact score**: {{impact_score}} / 100
**Sections that reference this clause**: {{referencing_sections}}  (may be empty)
**Sections this clause references**: {{referenced_sections}}  (may be empty)

**Dependency context**:
{{dependency_graph_excerpt}}

Your task:
1. Determine whether this clause should be REMOVED or INTEGRATED:
   - REMOVE if: duplicate boilerplate, superseded by other sections,
     or genuinely unnecessary
   - INTEGRATE if: clause has value but is structurally disconnected

2. If REMOVE:
   - Provide justification for removal
   - Identify any implicit dependencies that may break
   - Suggest where the clause's intent (if any) is already covered

3. If INTEGRATE:
   - Identify 1-3 sections that should cross-reference this clause
   - Draft the cross-reference language
   - Explain how integration strengthens the document

4. Rate confidence: High / Medium / Low

Output format:
- **Recommendation**: Remove / Integrate
- **Repair draft**: [removal justification OR cross-reference additions]
- **Confidence**: [High/Medium/Low] — [justification]
```

---

## Auto-Applicable Criteria

A deletion repair is **auto-applicable** when ALL of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Recommendation is INTEGRATE (add cross-references only) | Additive change; no content removed |
| 2 | Impact score is between 1-19 (low but non-zero) | Clause has some value; integration is safe |
| 3 | Cross-reference targets clearly exist | No ambiguity about where to connect |

**Note**: REMOVE recommendations are **never auto-applicable**. Removing text always requires human review.

---

## Needs-Human-Review Criteria

A deletion repair **requires human review** when ANY of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Recommendation is REMOVE | Content deletion requires human authorization |
| 2 | Impact score is exactly 0 and clause appears substantive | May have implicit dependencies not captured by structural analysis |
| 3 | Clause involves legal, financial, or safety provisions | Even dead legal clauses may serve a defensive purpose |
| 4 | Clause was recently added (based on version history) | May be intentionally new and not yet connected |

---

## Diff Output Format

### Remove Recommendation

```diff
--- a/contract.md (Section 14.7, Lines 312-318)
+++ b/contract.md (Section 14.7, REMOVED)
@@ Miscellaneous Provisions @@
- 14.7 Publicity. Neither party shall issue any press release or public
-  statement regarding this Agreement without the prior written consent
-  of the other party.
+
+ [REMOVED — Section 14.7: Duplicate of Section 3.4 (Confidentiality),
+  which already covers public disclosure restrictions with broader scope.
+  Impact score: 0. No sections reference 14.7.]
```

### Integrate Recommendation

```diff
--- a/spec.md (Section 6.3, Line 89)
+++ b/spec.md (Section 6.3, Line 89, INTEGRATED)
@@ Rate Limiting @@
  6.3 Rate Limiting. The API enforces rate limits of 100 requests per
- minute per API key.
+ minute per API key. Rate limit responses follow the error handling
+ protocol defined in Section 4.1 (Error Responses). Clients exceeding
+ rate limits should implement the retry strategy specified in
+ Section 7.2 (Client Best Practices).
```

**Metadata block**:

```
Repair ID:       DR-005
Strategy:        Deletion
Impact score:    0 / 100 (dead clause)
Recommendation:  Remove
Justification:   Duplicate of Section 3.4
Classification:  Needs-human-review (content removal)
```

---

## Repair Confidence Scoring

| Level | Definition | Criteria |
|-------|-----------|----------|
| **High** | Clear dead clause with obvious resolution | Impact 0; duplicate boilerplate identified; OR integration targets are unambiguous |
| **Medium** | Likely dead but judgment needed | Impact 1-19; clause has some contextual relevance; integration targets require inference |
| **Low** | Unclear whether clause is dead or merely disconnected | Impact 0 but clause appears substantive; may have implicit dependencies |

**Scoring algorithm**:

```
score = 0

IF impact_score == 0 AND duplicate_identified: score += 40
ELSE IF impact_score == 0 AND clause_is_boilerplate: score += 30
ELSE IF impact_score < 20: score += 15

IF integration_targets_clear: score += 25
IF clause_is_non_substantive: score += 20
IF no_legal_financial_safety: score += 15

IF score >= 65: confidence = "High"
ELSE IF score >= 35: confidence = "Medium"
ELSE: confidence = "Low"
```

---

## Regression Check Template

```markdown
You are a regression tester for document repairs. A dead clause was repaired:

**Repair type**: {{repair_type}} (Remove / Integrate)

{{#if remove}}
**Removed clause** ({{location}}): "{{removed_text}}"
**Justification**: {{justification}}

Regression checks:
1. Does any other section implicitly depend on the removed clause?
   (e.g., "as described above" that might refer to it)
2. Does removal change the document's section numbering in a way that
   breaks cross-references?
3. Does the clause serve a legal or defensive purpose not captured by
   structural analysis? (e.g., a severability clause)
4. Is the duplicate/replacement identified in the justification truly
   equivalent in scope?
{{/if}}

{{#if integrate}}
**Integrated clause** ({{location}}): "{{original_text}}"
**Added cross-references**: {{cross_references}}

Regression checks:
1. Do the added cross-references accurately describe the relationship?
2. Do the target sections actually cover what the cross-reference claims?
3. Does the integration create any circular references?
4. Does the added language introduce any ambiguity?
{{/if}}

Output:
- **Implicit dependencies broken**: [yes/no] — [details]
- **Numbering/reference issues**: [yes/no] — [details]
- **Scope equivalence** (remove only): [pass/fail] — [details]
- **Cross-reference accuracy** (integrate only): [pass/fail] — [details]
- **Regression verdict**: PASS / FAIL
```

---

## Examples

### Example 1: Duplicate Boilerplate — Remove (High Confidence)

**Detection finding**:
- Section 14.7 (Publicity): "Neither party shall issue any press release..."
- Impact score: 0 — no sections reference 14.7
- Section 3.4 (Confidentiality) already covers: "Neither party shall disclose any information regarding this Agreement to any third party..."

**Repair** (Remove — needs human review):
```diff
- 14.7 Publicity. Neither party shall issue any press release or public
-  statement regarding this Agreement without the prior written consent
-  of the other party.
+ [Section removed — covered by Section 3.4 (Confidentiality)]
```

**Confidence**: High (duplicate identified; zero impact)
**Classification**: Needs-human-review (removal always requires human authorization)

### Example 2: Orphaned Clause — Integrate (Medium Confidence)

**Detection finding**:
- Section 6.3 (Rate Limiting): defines rate limits
- Impact score: 3 — only 1 weak reference from Section 2 (Overview)
- Sections 4.1 (Error Responses) and 7.2 (Client Best Practices) exist but don't reference rate limiting

**Repair** (Integrate — auto-applicable):
```diff
  6.3 Rate Limiting. The API enforces rate limits of 100 requests per
- minute per API key.
+ minute per API key. Requests exceeding this limit receive a 429 status
+ code as specified in Section 4.1 (Error Responses). For recommended
+ retry behavior, see Section 7.2 (Client Best Practices).
```

**Confidence**: Medium (integration targets are clear but inferred)
**Classification**: Auto-applicable (additive cross-references only)
