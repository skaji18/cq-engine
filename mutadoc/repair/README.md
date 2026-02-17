# MutaDoc: Mutation-Driven Repair

> Extends MutaDoc from "detection only" to "detect + repair," mirroring ESLint's
> auto-fix revolution. Core insight: detect + repair achieves 10x adoption over
> detect only.

---

## Pipeline Architecture

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

### Stage 1: Detection

Mutation strategies (S1–S5) and adversarial personas generate a Vulnerability
Report containing findings classified as Critical, Major, or Minor.

### Stage 2: Repair Draft Generation

For each Critical/Major finding, the corresponding repair template generates
a concrete fix suggestion. Each template produces:

- **Repair draft** — repaired text in GitHub PR diff format
- **Impact analysis** — predicted cascading effects on other sections
- **Confidence score** — High / Medium / Low
- **Classification** — Auto-applicable or Needs-human-review

### Stage 3: Regression Mutation

All 5 mutation strategies are re-applied to the repaired document to verify
that fixes do not introduce new vulnerabilities. This is the "test the test"
stage — ensuring repairs are safe before delivery.

---

## Repair Templates

Each mutation strategy has a corresponding repair template:

| Strategy | Template | Repair Approach | Primary Mechanism |
|----------|----------|-----------------|-------------------|
| **S1: Contradiction** | [`templates/contradiction_repair.md`](templates/contradiction_repair.md) | Identify dominant clause, amend subordinate clause | Priority analysis + cross-reference alignment |
| **S2: Ambiguity** | [`templates/ambiguity_repair.md`](templates/ambiguity_repair.md) | Replace vague language with precise definitions | 2–3 options at Precise / Bounded / Qualified levels |
| **S3: Deletion** | [`templates/deletion_repair.md`](templates/deletion_repair.md) | Remove dead clauses or integrate via cross-references | Structural impact analysis + dependency graph |
| **S4: Inversion** | [`templates/inversion_repair.md`](templates/inversion_repair.md) | Strengthen weak claims against reversal | Evidence reinforcement / contingency / scope qualification |
| **S5: Boundary** | [`templates/boundary_repair.md`](templates/boundary_repair.md) | Add explicit boundary constraints to parameters | Min / max / default values + edge case handling |

### Template Structure

Every repair template follows the same structure:

```
# Repair Template: [Strategy Name]
## Repair Approach           — decision logic for selecting repair mechanism
## Prompt Template           — LLM prompt for generating repair drafts
## Auto-Applicable Criteria  — conditions for automatic application
## Needs-Human-Review Criteria — conditions requiring human judgment
## Diff Output Format        — GitHub PR diff style examples
## Repair Confidence Scoring — High/Medium/Low with scoring algorithm
## Regression Check Template — post-repair regression test instructions
## Examples                  — concrete before/after repair demonstrations
```

---

## Auto-Repair vs Suggestion Classification

The classification system determines whether a repair can be applied
automatically or requires human review.

### Auto-Applicable Criteria (apply without review)

A repair is auto-applicable when **ALL** of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Fix is purely additive (adds precision without changing meaning) | No existing content altered |
| 2 | Fix does not modify an obligation, right, or deadline | No legal/contractual impact |
| 3 | Only one valid repair exists (no alternatives to choose from) | No policy decision needed |
| 4 | Fix does not remove text | Deletion always requires authorization |
| 5 | Fix adds explicit boundary to an implicit parameter | Adding precision is safe |

### Needs-Human-Review Criteria (present as suggestion)

A repair requires human review when **ANY** of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Fix modifies an obligation or right | Changes legal/contractual meaning |
| 2 | Fix involves choosing between 2+ valid alternatives | Policy decision required |
| 3 | Fix removes text | Content deletion needs authorization |
| 4 | Fix resolves a contradiction by choosing one interpretation | Interpretation is a judgment call |
| 5 | Fix affects financial terms, deadlines, or penalties | Commercial decision |
| 6 | Fix modifies the document's central thesis or conclusion | Structural integrity risk |

### Strategy-Specific Classification Summary

| Strategy | Typical Auto-Applicable Scenario | Typical Needs-Review Scenario |
|----------|----------------------------------|-------------------------------|
| Contradiction | Dominant clause determined by explicit priority language; additive cross-reference | Competing obligations with equal authority; policy choice |
| Ambiguity | Qualified-level repair in description context; single occurrence | Obligation context; multiple valid precise values |
| Deletion | Integrate (add cross-references) with clear targets | Remove recommendation; legal/financial/safety clauses |
| Inversion | Scope qualification using in-document evidence | New evidence claims; removing/weakening assertions |
| Boundary | Logical constraints (0–100%, non-negative counts) | Negotiated terms; financial amounts; policy allocations |

---

## Target Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| **Use-as-is rate** | **30%+** | Percentage of repair suggestions directly usable without modification |
| Critical finding repair coverage | 100% | All Critical findings receive a repair draft |
| Major finding repair coverage | 80%+ | Most Major findings receive a repair draft |
| Classification accuracy | 80%+ | Auto-applicable vs needs-review correctly classified |
| Regression detection | >0 | Regression engine catches at least 1 issue introduced by repairs |

---

## Confidence Scoring

Each repair template includes a confidence scoring algorithm. The general
framework:

| Level | Definition | Typical Score Range |
|-------|-----------|---------------------|
| **High** | Repair is almost certainly correct; objectively determinable | 65+ |
| **Medium** | Repair is reasonable but should be verified | 35–64 |
| **Low** | Repair is a suggestion only; requires human judgment | 0–34 |

Scoring factors common across strategies:

| Factor | Points | Condition |
|--------|--------|-----------|
| Evidence / logical constraint | +30 to +40 | Repair is objectively determined |
| Context inference | +15 | Repair is reasonably inferred |
| Additive repair | +15 to +20 | Does not modify existing text |
| Non-obligation context | +15 to +20 | Technical/descriptive, not contractual |
| No cascading effects | +10 to +15 | Isolated, single-point fix |
| Consistency with other parameters | +10 to +15 | No conflicts detected |

Each template's scoring algorithm is tuned to its strategy's specific
risk profile. See individual templates for exact algorithms.

---

## Diff Output Format

All repair suggestions use GitHub PR diff format for human review:

```diff
--- a/document.md (Section X.Y, Line NNN)
+++ b/document.md (Section X.Y, Line NNN, REPAIRED)
@@ Section Title @@
- Original text that contains the vulnerability.
+ Repaired text that resolves the vulnerability with added
+ precision, cross-references, or boundary constraints.
```

Each diff includes a metadata block:

```
Repair ID:       [XX]-[NNN]
Strategy:        [Contradiction/Ambiguity/Deletion/Inversion/Boundary]
Confidence:      [High/Medium/Low]
Classification:  [Auto-applicable / Needs-human-review]
[Strategy-specific metadata fields]
```

---

## Regression Check

After applying any repair, the regression check template verifies:

1. **No new contradictions** — repair does not conflict with other sections
2. **No unintended changes** — obligations, rights, and deadlines preserved
3. **No new ambiguity** — repaired text is not vaguer than original
4. **Style consistency** — language matches document's existing terminology
5. **Cross-reference accuracy** — all references point to correct sections
6. **Strategy-specific checks** — each template adds its own regression criteria

**Regression verdict**: PASS (safe to apply) or FAIL (repair needs revision).

---

## Usage Flow

```
1. Run MutaDoc detection (strategies + personas)
         │
         ▼
2. Receive Vulnerability Report
         │
         ▼
3. For each Critical/Major finding:
   a. Select corresponding repair template
   b. Fill template variables from finding data
   c. Generate repair draft + confidence score
   d. Classify: auto-applicable or needs-review
         │
         ▼
4. Apply auto-applicable repairs to draft document
         │
         ▼
5. Run regression mutation on repaired document
         │
         ▼
6. Present to human:
   - Auto-applied repairs (for confirmation)
   - Needs-review suggestions (for decision)
   - Regression report (any new issues)
```

---

## Examples

### Example 1: Contradiction Repair (Auto-Applicable)

**Detection finding** (from S1 Contradiction strategy):
```
Finding ID: C1
Severity: Critical
Location: Section 5.1 vs Section 12.3
Issue: Section 5.1 allows "immediate termination for cause" but Section 12.3
       requires "transfer of assets during the notice period defined in Section 5"
```

**Repair draft** (from `templates/contradiction_repair.md`):

The repair template identifies Section 5.1 as the dominant clause (it defines the termination mechanism) and amends Section 12.3 to align:

```diff
--- a/contract.md (Section 12.3, Line 287)
+++ b/contract.md (Section 12.3, Line 287, REPAIRED)
@@ Asset Transfer @@
- 12.3 Transfer of assets shall occur during the notice period
- defined in Section 5.
+ 12.3 Transfer of assets shall occur during the notice period
+ defined in Section 5.1 (30 days for termination without cause).
+ In the event of immediate termination for cause under Section 5.1,
+ asset transfer shall be completed within 14 business days following
+ the termination effective date.
```

```
Repair ID:       CR-001
Strategy:        Contradiction
Confidence:      High (72/100)
Classification:  Needs-human-review (modifies an obligation)
Dominant clause: Section 5.1 (defines termination mechanism)
Reasoning:       Adding explicit timeline for cause-based termination resolves
                 the impossible obligation. 14 days is inferred from industry
                 standard but should be reviewed.
```

**Regression check**: PASS — re-running all 5 strategies on the repaired document detects no new contradictions, ambiguities, or broken dependencies.

---

### Example 2: Boundary Repair (Auto-Applicable)

**Detection finding** (from S5 Boundary strategy):
```
Finding ID: B3
Severity: Critical
Location: Section 7.2
Parameter: "notice_period" = 30 days
Issue: At boundary value 0 days, obligation in Section 8.2 (cure period)
       becomes impossible. No minimum bound defined.
```

**Repair draft** (from `templates/boundary_repair.md`):

```diff
--- a/contract.md (Section 7.2, Line 156)
+++ b/contract.md (Section 7.2, Line 156, REPAIRED)
@@ Notice Requirements @@
- 7.2 Either party may terminate this agreement with 30 days
- written notice.
+ 7.2 Either party may terminate this agreement with 30 days
+ written notice. The notice period shall be no less than 14 days
+ and no more than 180 days.
```

```
Repair ID:       BR-003
Strategy:        Boundary
Confidence:      High (78/100)
Classification:  Auto-applicable (adds explicit boundary to implicit parameter)
Min bound:       14 days (derived from Section 8.2 cure period requirement)
Max bound:       180 days (industry standard reasonableness constraint)
```

**Regression check**: PASS — boundary re-test confirms the parameter is now classified as "robust" (logic holds at all 5 boundary values).

---

### Example 3: Ambiguity Repair (Needs Human Review)

**Detection finding** (from S2 Ambiguity strategy):
```
Finding ID: A2
Severity: Critical
Location: Section 4.1
Issue: "reasonable efforts" in an obligation clause — no definition provided.
       Extreme-value mutation reveals the phrase is effectively meaningless.
```

**Repair draft** (from `templates/ambiguity_repair.md`):

Three options at increasing specificity:

**Option A — Precise**:
```diff
- 4.1 Provider shall use reasonable efforts to maintain 99.5% uptime.
+ 4.1 Provider shall maintain 99.5% uptime, measured monthly, excluding
+ scheduled maintenance windows announced at least 48 hours in advance.
```

**Option B — Bounded**:
```diff
- 4.1 Provider shall use reasonable efforts to maintain 99.5% uptime.
+ 4.1 Provider shall use commercially reasonable efforts, defined as
+ efforts consistent with industry-standard practices for comparable
+ SaaS providers, to maintain 99.5% uptime.
```

**Option C — Qualified**:
```diff
- 4.1 Provider shall use reasonable efforts to maintain 99.5% uptime.
+ 4.1 Provider shall use reasonable efforts to maintain 99.5% uptime.
+ For the purposes of this agreement, "reasonable efforts" means efforts
+ that do not require expenditure exceeding 10% of annual contract value.
```

```
Repair ID:       AR-002
Strategy:        Ambiguity
Confidence:      Medium (48/100)
Classification:  Needs-human-review (multiple valid alternatives; obligation context)
Options:         3 (Precise / Bounded / Qualified)
Reasoning:       All three options eliminate the ambiguity. Selection depends on
                 the desired balance between precision and flexibility — a
                 policy decision requiring human judgment.
```

**Regression check**: All three options PASS — no new contradictions or ambiguities introduced by any option.
