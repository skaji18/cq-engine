# Repair Template: Ambiguity

> Resolves ambiguities detected by the Ambiguity mutation strategy (S2).
> Pipeline stage: Detection → **Repair Draft Generation** → Regression Mutation

---

## Repair Approach

When an ambiguous modifier or phrase is detected, the repair process replaces vague language with precise, quantitative or qualitative definitions. Each repair presents 2-3 options at different specificity levels, allowing the document owner to choose the appropriate precision.

### Three Specificity Levels

| Level | Description | When to Use |
|-------|-------------|-------------|
| **Precise** | Exact numerical value or enumerated list | Obligations, deadlines, SLAs, financial terms |
| **Bounded** | Range with explicit minimum and maximum | Performance criteria, quality standards |
| **Qualified** | Qualitative definition with examples | Behavioral expectations, good faith clauses |

### Repair Logic

```
FOR each detected ambiguous phrase:
  1. Classify the phrase's role in the document:
     - Obligation → require Precise or Bounded repair
     - Description → Qualified repair may suffice
     - Condition → require Bounded repair (trigger thresholds)

  2. Analyze context to infer intended meaning:
     - Surrounding clauses, section purpose, document type
     - Domain conventions (legal, technical, academic)

  3. Generate 2-3 repair options at different specificity levels

  4. Score each option for auto-applicability
```

---

## Prompt Template

```markdown
You are a document precision specialist. An ambiguous phrase has been detected:

**Location**: {{section_location}}
**Ambiguous phrase**: "{{ambiguous_phrase}}"
**Full sentence**: "{{full_sentence}}"
**Phrase role**: {{role}} (obligation / description / condition)
**Document type**: {{document_type}}

**Extreme-value test results**:
- Minimum interpretation: "{{min_interpretation}}" → Impact: {{min_impact}}
- Maximum interpretation: "{{max_interpretation}}" → Impact: {{max_impact}}

Your task:
1. Analyze the context to infer the likely intended meaning
2. Generate repair options at 2-3 specificity levels:
   - **Precise**: Replace with exact value (number, date, enumerated list)
   - **Bounded**: Replace with explicit range (min-max)
   - **Qualified**: Replace with qualitative definition and examples
3. For each option, indicate whether it is auto-applicable
4. Identify any sections that use the same ambiguous phrase

Output format:
- **Inferred intent**: [what the author likely meant]
- **Option 1 (Precise)**: [repaired text] — Auto: [yes/no]
- **Option 2 (Bounded)**: [repaired text] — Auto: [yes/no]
- **Option 3 (Qualified)**: [repaired text] — Auto: [yes/no]
- **Same phrase elsewhere**: [list of other locations]
- **Recommended option**: [1/2/3] — [reasoning]
```

---

## Auto-Applicable Criteria

An ambiguity repair is **auto-applicable** when ALL of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Repair adds precision without changing meaning | Clarifies existing intent, does not create new obligations |
| 2 | The ambiguous phrase is in a description, not an obligation | Low-risk context |
| 3 | Only the Qualified level is being applied | Adding examples/definitions is safe |
| 4 | The same phrase is not used elsewhere in the document | No cascading repair needed |

---

## Needs-Human-Review Criteria

An ambiguity repair **requires human review** when ANY of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Ambiguous phrase is in an obligation or deadline | Precision changes legal meaning |
| 2 | Multiple valid Precise values exist | Choosing the "right" number is a policy decision |
| 3 | Same ambiguous phrase appears in 3+ locations | Repair must be consistent across all; may affect different sections differently |
| 4 | Repair requires choosing between Precise options | Each option has different trade-offs |
| 5 | Ambiguity appears intentional (hedge language in negotiations) | Removing ambiguity may not be desired |

---

## Diff Output Format

```diff
--- a/contract.md (Section 4.2, Line 67)
+++ b/contract.md (Section 4.2, Line 67, REPAIRED — Option 1: Precise)
@@ Response Time Obligations @@
- Provider shall respond to critical issues within a reasonable timeframe.
+ Provider shall respond to critical issues within 4 hours of receiving
+ notification via the designated support channel (Section 8.1).
```

```diff
--- a/contract.md (Section 4.2, Line 67)
+++ b/contract.md (Section 4.2, Line 67, REPAIRED — Option 2: Bounded)
@@ Response Time Obligations @@
- Provider shall respond to critical issues within a reasonable timeframe.
+ Provider shall respond to critical issues within 2 to 8 hours of
+ receiving notification, with the specific response time determined by
+ the severity level defined in Appendix B.
```

```diff
--- a/contract.md (Section 4.2, Line 67)
+++ b/contract.md (Section 4.2, Line 67, REPAIRED — Option 3: Qualified)
@@ Response Time Obligations @@
- Provider shall respond to critical issues within a reasonable timeframe.
+ Provider shall respond to critical issues within a timeframe consistent
+ with industry standards for the applicable severity level (e.g., Severity 1:
+ same business day; Severity 2: next business day; Severity 3: within
+ 5 business days).
```

**Metadata block**:

```
Repair ID:       AR-003
Strategy:        Ambiguity
Ambiguous phrase: "reasonable timeframe"
Phrase role:      Obligation
Options:         3 (Precise / Bounded / Qualified)
Recommended:     Option 1 (Precise) — obligation context demands specificity
Classification:  Needs-human-review (obligation context; multiple valid values)
Same phrase at:  Section 6.4 (Line 112), Section 9.1 (Line 198)
```

---

## Repair Confidence Scoring

| Level | Definition | Criteria |
|-------|-----------|----------|
| **High** | One clearly correct repair exists | Phrase in description; domain convention defines the value; single occurrence |
| **Medium** | Reasonable repair can be inferred from context | Phrase in condition; context suggests a range; 1-2 other occurrences |
| **Low** | Multiple valid repairs; choice depends on policy | Phrase in obligation; no contextual clues; 3+ occurrences |

**Scoring algorithm**:

```
score = 0

IF phrase_role == "description": score += 30
ELSE IF phrase_role == "condition": score += 15
ELSE IF phrase_role == "obligation": score += 0

IF domain_convention_exists: score += 25
ELSE IF context_suggests_value: score += 15

IF single_occurrence: score += 20
ELSE IF two_occurrences: score += 10

IF only_qualified_option_needed: score += 15

IF score >= 65: confidence = "High"
ELSE IF score >= 35: confidence = "Medium"
ELSE: confidence = "Low"
```

---

## Regression Check Template

```markdown
You are a regression tester for document repairs. An ambiguity was repaired:

**Original phrase** ({{location}}): "{{original_phrase}}"
**Repaired text**: "{{repaired_text}}"
**Specificity level**: {{level}} (Precise / Bounded / Qualified)

Regression checks:
1. Does the repaired text introduce any contradiction with other sections?
   - Especially check sections with numerical values or deadlines that
     may conflict with the new precise language
2. Does the repair create a new ambiguity? (e.g., "4 hours" — business
   hours or calendar hours?)
3. If the same phrase exists elsewhere, is the repair consistent?
   - Locations: {{other_locations}}
   - Would the same repair make sense at each location?
4. Does the Precise/Bounded value conflict with any industry standard
   or regulatory requirement?
5. Is the repaired language consistent with the document's terminology?

Output:
- **New contradictions**: [yes/no] — [details]
- **New ambiguities**: [yes/no] — [details]
- **Cross-location consistency**: [pass/fail] — [details]
- **Regulatory conflict**: [yes/no] — [details]
- **Style consistency**: [pass/fail] — [details]
- **Regression verdict**: PASS / FAIL
```

---

## Examples

### Example 1: SLA with Domain Convention — Auto-Applicable (High Confidence)

**Detection finding**:
- Section 4.2: "Provider shall ensure reasonable uptime"
- Extreme test: "0% uptime" still satisfies the literal text → ambiguity is load-bearing

**Repair options**:

Option 1 (Precise — Recommended):
```diff
- Provider shall ensure reasonable uptime for the hosted services.
+ Provider shall ensure 99.9% monthly uptime for the hosted services,
+ measured as defined in Appendix C (SLA Metrics).
```

Option 2 (Bounded):
```diff
- Provider shall ensure reasonable uptime for the hosted services.
+ Provider shall ensure between 99.5% and 99.99% monthly uptime for
+ the hosted services, with the specific tier determined by the
+ service plan selected by Client.
```

**Confidence**: Medium (obligation context, but domain convention [99.9%] provides guidance)
**Classification**: Needs-human-review (obligation with financial implications)

### Example 2: Description Context — Auto-Applicable (High Confidence)

**Detection finding**:
- README Section 2: "MutaDoc performs comprehensive document analysis"
- "comprehensive" is vague — what exactly is covered?

**Repair** (Qualified — auto-applicable):
```diff
- MutaDoc performs comprehensive document analysis.
+ MutaDoc performs document analysis across five dimensions: contradiction
+ detection, ambiguity identification, structural dependency mapping,
+ claim robustness testing, and boundary condition validation.
```

**Confidence**: High (description context; single occurrence; adds precision without changing meaning)
**Classification**: Auto-applicable
