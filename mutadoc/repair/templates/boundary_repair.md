# Repair Template: Boundary

> Resolves missing or fragile boundary conditions detected by the Boundary mutation strategy (S5).
> Pipeline stage: Detection → **Repair Draft Generation** → Regression Mutation

---

## Repair Approach

When the Boundary strategy reveals that a parameter lacks explicit constraints or that the document's logic breaks at realistic boundary values, the repair adds explicit boundary definitions:

1. **Explicit constraints** — Add minimum, maximum, and/or default values to parameters that lack them
2. **Parameter precision** — Replace vague numerical references with precise, bounded definitions
3. **Edge case handling** — Add explicit language for what happens at boundary values (zero, maximum, overflow)

### Repair Logic

```
FOR each fragile parameter:
  1. Identify parameter type:
     - Duration (days, hours, months)
     - Quantity (count, percentage, amount)
     - Threshold (limit, cap, floor)

  2. Determine which boundaries are missing:
     - Minimum (floor / zero case)
     - Maximum (ceiling / overflow case)
     - Default (what applies when unspecified)

  3. Infer appropriate boundaries from:
     - Document context (related parameters, stated objectives)
     - Domain conventions (industry standards, regulatory limits)
     - Logical constraints (e.g., percentage cannot exceed 100%)

  4. Generate repair with explicit boundary constraints
```

---

## Prompt Template

```markdown
You are a document precision specialist focused on numerical parameters.
A fragile parameter has been detected:

**Location**: {{section_location}}
**Parameter**: {{parameter_name}}
**Current value**: {{current_value}}
**Parameter type**: {{param_type}} (duration / quantity / threshold)

**Boundary test results**:
| Boundary Value | Impact | Document Logic Status |
|----------------|--------|----------------------|
| Zero ({{zero_value}}) | {{zero_impact}} | {{zero_status}} |
| Minimum viable ({{min_value}}) | {{min_impact}} | {{min_status}} |
| Maximum reasonable ({{max_value}}) | {{max_impact}} | {{max_status}} |
| Extreme ({{extreme_value}}) | {{extreme_impact}} | {{extreme_status}} |

**Missing boundaries**: {{missing_boundaries}}
**Sensitivity**: {{sensitivity}} (robust / sensitive / fragile)

Your task:
1. For each missing boundary, propose an explicit constraint:
   - Minimum value with justification
   - Maximum value with justification
   - Default value (if applicable) with justification
2. Add edge case handling language where the document logic breaks
3. Ensure proposed boundaries are consistent with other parameters
   in the document

Output format:
- **Proposed boundaries**:
  - Minimum: {{value}} — {{justification}}
  - Maximum: {{value}} — {{justification}}
  - Default: {{value}} — {{justification}}
- **Edge case handling**: [language for boundary behavior]
- **Consistency check**: [conflicts with other parameters? yes/no]
- **Confidence**: [High/Medium/Low] — [justification]
```

---

## Auto-Applicable Criteria

A boundary repair is **auto-applicable** when ALL of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Repair adds explicit boundary to an implicit parameter | Adding precision is additive; does not change existing meaning |
| 2 | Boundary values are derived from logical constraints | e.g., percentage capped at 100%, count minimum 0 — objectively correct |
| 3 | No financial, legal, or deadline implications | Boundary values in technical specifications are lower risk |
| 4 | Boundaries are consistent with all other parameters in the document | No conflicts detected |

---

## Needs-Human-Review Criteria

A boundary repair **requires human review** when ANY of the following are true:

| # | Criterion | Rationale |
|---|-----------|-----------|
| 1 | Boundary values affect obligations, payments, or deadlines | Policy/commercial decision |
| 2 | Multiple valid boundary values exist | Choice depends on business context |
| 3 | Document logic breaks at a realistic boundary value | May indicate a design flaw, not just missing text |
| 4 | Proposed boundary conflicts with another parameter | Resolution requires understanding priority between parameters |
| 5 | Parameter is a negotiated term (price, timeline, penalty) | Boundary changes are contractual modifications |

---

## Diff Output Format

### Adding Missing Boundaries

```diff
--- a/contract.md (Section 6.1, Line 98)
+++ b/contract.md (Section 6.1, Line 98, REPAIRED)
@@ Payment Terms @@
- Client shall pay invoices within 30 days of receipt.
+ Client shall pay invoices within 30 calendar days of receipt, but in
+ no event later than 45 calendar days from the invoice date. Invoices
+ not disputed within 10 business days of receipt are deemed accepted.
+ Late payments are subject to the interest provisions in Section 6.4.
```

### Adding Edge Case Handling

```diff
--- a/spec.md (Section 5.2, Line 134)
+++ b/spec.md (Section 5.2, Line 134, REPAIRED)
@@ Retry Configuration @@
- The client may configure the number of retry attempts.
+ The client may configure the number of retry attempts, with a minimum
+ of 0 (no retries) and a maximum of 10. The default is 3 attempts.
+ If set to 0, the client receives the first response without retry.
+ If the maximum is exceeded in configuration, the system clamps to 10
+ and logs a warning.
```

### Precision Improvement

```diff
--- a/policy.md (Section 3.4, Line 72)
+++ b/policy.md (Section 3.4, Line 72, REPAIRED)
@@ Budget Allocation @@
- A significant portion of the annual budget shall be allocated to
-  research and development.
+ Between 15% and 25% of the annual operating budget shall be allocated
+ to research and development, with the specific percentage determined
+ annually by the Board based on the strategic plan (Section 2.1).
+ The minimum allocation of 15% may not be reduced without Board
+ supermajority approval (Section 11.3).
```

**Metadata block**:

```
Repair ID:       BR-012
Strategy:        Boundary
Parameter:       retry_attempts
Current value:   unspecified
Sensitivity:     fragile (logic breaks at 0 and at very high values)
Added boundaries: min=0, max=10, default=3
Confidence:      High
Classification:  Auto-applicable (logical constraints; technical spec)
```

---

## Repair Confidence Scoring

| Level | Definition | Criteria |
|-------|-----------|----------|
| **High** | Boundaries are logically determined | e.g., 0-100 for percentage; 0-N for count; domain standard values exist |
| **Medium** | Boundaries are reasonable inferences from context | Related parameters suggest range; document objectives imply limits |
| **Low** | Boundaries are policy choices | Financial amounts, negotiated timelines, strategic allocations |

**Scoring algorithm**:

```
score = 0

IF logical_constraint_determines_boundary: score += 40
ELSE IF domain_standard_exists: score += 30
ELSE IF context_inference_possible: score += 15

IF parameter_is_technical: score += 20
ELSE IF parameter_is_operational: score += 10

IF no_financial_legal_deadline: score += 15
IF consistent_with_other_params: score += 15

IF score >= 65: confidence = "High"
ELSE IF score >= 35: confidence = "Medium"
ELSE: confidence = "Low"
```

---

## Regression Check Template

```markdown
You are a regression tester for document repairs. Boundary constraints
were added to a parameter:

**Parameter** ({{location}}): {{parameter_name}}
**Original text**: "{{original_text}}"
**Repaired text**: "{{repaired_text}}"
**Added boundaries**: min={{min}}, max={{max}}, default={{default}}

Regression checks:
1. Are the boundary values internally consistent?
   (min < default < max; no logical impossibilities)
2. Do the boundaries conflict with any other parameter in the document?
   - Check all sections containing numerical values related to {{parameter_name}}
3. Does the edge case handling language create new ambiguity?
4. If a default value was added, does it conflict with any existing
   default or assumption elsewhere?
5. Do the boundaries make any existing use case impossible?
   (e.g., a max of 10 retries when another section expects 20)

Output:
- **Internal consistency**: [pass/fail] — [details]
- **Cross-parameter conflicts**: [yes/no] — [details]
- **New ambiguity**: [yes/no] — [details]
- **Default conflicts**: [yes/no] — [details]
- **Use case impact**: [pass/fail] — [details]
- **Regression verdict**: PASS / FAIL
```

---

## Examples

### Example 1: Logical Constraints — Auto-Applicable (High Confidence)

**Detection finding**:
- Section 5.2: "The client may configure the number of retry attempts"
- Boundary test: 0 retries → client gets raw error (undefined behavior); -1 retries → nonsensical; 1000000 retries → infinite loop
- Sensitivity: fragile

**Repair**:
```diff
- The client may configure the number of retry attempts.
+ The client may configure the number of retry attempts, with a minimum
+ of 0 (disabled) and a maximum of 10. Default: 3. Values outside this
+ range are clamped to the nearest boundary.
```

**Confidence**: High (logical constraints: retries must be non-negative, upper bound prevents resource exhaustion)
**Classification**: Auto-applicable (technical spec; logical constraints)

### Example 2: Negotiated Parameter — Needs Human Review (Low Confidence)

**Detection finding**:
- Section 6.1: "Client shall pay invoices within 30 days"
- Boundary test: 0 days → payment due immediately (impractical); 365 days → effectively interest-free loan; no maximum explicitly stated
- Sensitivity: sensitive

**Repair options**:

Option A — Add maximum only:
```diff
- Client shall pay invoices within 30 days of receipt.
+ Client shall pay invoices within 30 calendar days of receipt, but in
+ no event later than 60 calendar days from the invoice date.
```

Option B — Add maximum + late payment handling:
```diff
- Client shall pay invoices within 30 days of receipt.
+ Client shall pay invoices within 30 calendar days of receipt. Invoices
+ outstanding beyond 45 days accrue interest at 1.5% per month. Invoices
+ outstanding beyond 90 days constitute a material breach under
+ Section 10.2.
```

**Confidence**: Low (payment terms are negotiated; boundary values are commercial decisions)
**Classification**: Needs-human-review (financial obligations)
