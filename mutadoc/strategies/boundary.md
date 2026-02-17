# Strategy: Boundary

## Overview

The Boundary strategy identifies numerical parameters in a document — dates, amounts, percentages, counts, durations — and mutates them to extreme values to observe whether the document's conclusions, obligations, or logic still hold. This is the direct analog of **boundary value testing** from software engineering, applied to documents.

The core insight: **documents often contain numerical parameters with implicit boundaries that no one has tested.** A contract says "30 days notice" but never specifies what happens at 0 days or 365 days. A budget projects 10% growth but never analyzes what happens at 0% or 50%. These untested boundaries are where hidden fragility lives.

Boundary testing classifies each parameter as:
- **Robust**: Conclusions hold across all reasonable boundary values
- **Sensitive**: Conclusions change at extreme but plausible values
- **Fragile**: Conclusions break at realistic boundary values — a serious vulnerability

## When to Use

| Scenario | Suitability | Notes |
|----------|:-----------:|-------|
| Contracts with numeric obligations (deadlines, amounts, thresholds) | High | Boundary testing exposes undefined edge cases in obligations |
| Financial projections and budget documents | High | Tests robustness of projections under parameter variation |
| SLAs with quantitative guarantees (uptime, response time) | High | Exposes gaps where SLA guarantees have no defined boundary behavior |
| Technical specs with performance thresholds | High | Tests whether specs handle extreme load, size, and timing parameters |
| Narrative documents with few numbers | Low | Insufficient parameters to test meaningfully |
| Documents where all parameters are legally defined ranges | Low | Boundaries already explicit; boundary testing adds little value |

## Prompt Template

### Single-Parameter Boundary Test

```markdown
You are a boundary analyst performing a Boundary Mutation Test on a document.

## Your Task

A numerical parameter in the document has been mutated to extreme boundary
values. Your job is to analyze how the document's logic, obligations, and
conclusions hold up at each boundary.

## Original Document

{full_document}

## Target Parameter

**Location**: {parameter_location}
**Parameter name**: {parameter_name}
**Original value**: {original_value}
**Parameter type**: {parameter_type}

## Boundary Values to Test

| Boundary | Value | Rationale |
|----------|-------|-----------|
| Zero | {zero_value} | What if this parameter is zero/none? |
| Minimum viable | {min_viable} | Smallest value that could plausibly occur |
| Maximum reasonable | {max_reasonable} | Largest value within normal business/technical range |
| Extreme | {extreme_value} | Far beyond normal range but theoretically possible |
| Negative | {negative_value} | Opposite direction (if applicable) |

## Analysis Instructions

For EACH boundary value:

1. **Substitution**: Replace the original value with the boundary value.
2. **Impact analysis**: Does the document's logic still hold?
   - Do obligations become impossible to fulfill?
   - Do calculations produce absurd results?
   - Are there missing constraints that should prevent this value?
   - Do other sections contradict the boundary value?
3. **Missing safeguard detection**: Does the document define:
   - A minimum acceptable value?
   - A maximum acceptable value?
   - A default/fallback value?
   - What happens when the value is outside expected range?
4. **Sensitivity assessment**: How much does the conclusion change as the
   parameter moves from original to each boundary?

## Output Format

```yaml
boundary_result:
  parameter_location: "{parameter_location}"
  parameter_name: "{parameter_name}"
  original_value: "{original_value}"
  parameter_type: "{parameter_type}"
  sensitivity_classification: "<robust | sensitive | fragile>"
  boundary_tests:
    - boundary: "zero"
      test_value: "{zero_value}"
      logic_holds: <true | false>
      impact: "Description of what breaks or holds"
      missing_safeguard: "What constraint is missing?"
    - boundary: "minimum_viable"
      test_value: "{min_viable}"
      logic_holds: <true | false>
      impact: "..."
      missing_safeguard: "..."
    - boundary: "maximum_reasonable"
      test_value: "{max_reasonable}"
      logic_holds: <true | false>
      impact: "..."
      missing_safeguard: "..."
    - boundary: "extreme"
      test_value: "{extreme_value}"
      logic_holds: <true | false>
      impact: "..."
      missing_safeguard: "..."
    - boundary: "negative"
      test_value: "{negative_value}"
      logic_holds: <true | false>
      impact: "..."
      missing_safeguard: "..."
  first_break_point: "The boundary at which the logic first fails"
  recommendation: "<add_bounds | add_default | add_contingency | accept_risk>"
```
```

### Systematic Boundary Sweep

```markdown
You are performing a systematic Boundary Mutation Test on a document.

## Your Task

Identify ALL numerical parameters in the document, then test each at boundary
values to assess the document's robustness under parameter variation.

## Document

{full_document}

## Parameter Scope: {parameter_scope}
(Options: all / specific_sections)

## Instructions

1. **Parameter extraction**: Identify every numerical parameter:
   - Dates and deadlines (days, months, years)
   - Monetary amounts (prices, budgets, limits, penalties)
   - Percentages (rates, thresholds, shares)
   - Counts (quantities, limits, minimum/maximum numbers)
   - Durations (hours, days, periods)
   - Measurements (sizes, distances, performance metrics)

2. **For each parameter**, generate 5 boundary values:
   - Zero (or equivalent null state)
   - Minimum viable (smallest plausible real-world value)
   - Maximum reasonable (largest value within normal range)
   - Extreme (far beyond normal, but theoretically possible)
   - Negative (opposite direction, if meaningful)

3. **Test each boundary** and classify the parameter sensitivity.

4. **Prioritize output**: Sort by sensitivity (fragile first).

## Output Format

```yaml
boundary_sweep:
  document: "{document_name}"
  parameter_scope: "{parameter_scope}"
  total_parameters_found: <N>
  results:
    - parameter_name: "..."
      parameter_location: "..."
      original_value: "..."
      parameter_type: "..."
      sensitivity_classification: "..."
      first_break_point: "..."
      has_explicit_bounds: <true | false>
  summary:
    fragile_parameters: <count>
    sensitive_parameters: <count>
    robust_parameters: <count>
    parameters_without_bounds: <count>
    highest_risk: "Parameter with lowest break point"
```
```

## Input Specification

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `document_path` | string | Yes | Path to the target document (Markdown or plain text) |
| `parameter_scope` | enum | No | `all` (default), specific section identifiers |
| `parameter_types` | list | No | Filter by type: `date`, `amount`, `percentage`, `count`, `duration`. Default: all types |
| `include_boundary_suggestions` | boolean | No | If true, recommend explicit bounds for each fragile parameter (default: true) |

### Parameter Type Definitions

| Type | Description | Zero Value | Example Boundaries |
|------|------------|------------|-------------------|
| `date` | Deadlines, dates, time periods | 0 days | 0, 1 day, 1 year, 10 years |
| `amount` | Monetary values, prices, penalties | $0 | $0, $1, $1M, $1B, negative |
| `percentage` | Rates, shares, thresholds | 0% | 0%, 1%, 100%, 500%, negative |
| `count` | Quantities, limits | 0 | 0, 1, 1000, 1M |
| `duration` | Time spans, periods | 0 hours | 0, 1 min, 24h, 1 year, 10 years |

## Output Format

```yaml
boundary_report:
  document: "contract.md"
  parameter_scope: "all"
  timestamp: "2026-01-25T09:00:00Z"
  total_parameters_found: 8
  results:
    - parameter_name: "notice_period"
      parameter_location: "Section 5.1"
      original_value: "30 days"
      parameter_type: "duration"
      sensitivity_classification: "fragile"
      boundary_tests:
        - boundary: "zero"
          test_value: "0 days"
          logic_holds: false
          impact: "Immediate termination with no time to cure breach — contradicts Section 8.2 which requires 'reasonable time to remedy'"
          missing_safeguard: "No minimum notice period defined"
        - boundary: "minimum_viable"
          test_value: "1 day"
          logic_holds: false
          impact: "Section 12.3 requires asset transfer 'during the notice period' — 1 day is insufficient for the described transfer process"
          missing_safeguard: "No link between notice period and asset transfer timeline"
        - boundary: "maximum_reasonable"
          test_value: "365 days"
          logic_holds: true
          impact: "Technically valid but commercially unreasonable — contract has no upper bound"
          missing_safeguard: "No maximum notice period defined"
        - boundary: "extreme"
          test_value: "3650 days (10 years)"
          logic_holds: true
          impact: "Contract allows indefinite lock-in with no escape mechanism"
          missing_safeguard: "No reasonableness constraint on notice period"
        - boundary: "negative"
          test_value: "-30 days (retroactive)"
          logic_holds: false
          impact: "Retroactive termination is nonsensical — contract does not address retroactivity"
          missing_safeguard: "No forward-looking constraint"
      first_break_point: "zero"
      has_explicit_bounds: false
      recommendation: "add_bounds"
      suggested_bounds:
        minimum: "14 days"
        maximum: "180 days"
        rationale: "Minimum ensures cure period (Section 8.2); maximum prevents lock-in"

    - parameter_name: "annual_growth_rate"
      parameter_location: "Section 3.2"
      original_value: "12%"
      parameter_type: "percentage"
      sensitivity_classification: "sensitive"
      boundary_tests:
        - boundary: "zero"
          test_value: "0%"
          logic_holds: false
          impact: "Revenue projections in Section 5 collapse — Year 3 drops from $5M to $2.1M"
          missing_safeguard: "No scenario analysis for zero growth"
        - boundary: "minimum_viable"
          test_value: "3%"
          logic_holds: true
          impact: "Projections reduced but business case still viable — break-even shifts from Year 2 to Year 4"
          missing_safeguard: "None — model is flexible"
        - boundary: "maximum_reasonable"
          test_value: "25%"
          logic_holds: true
          impact: "Projections improve significantly — but infrastructure section doesn't address scale"
          missing_safeguard: "No scaling plan for high-growth scenario"
        - boundary: "extreme"
          test_value: "100%"
          logic_holds: false
          impact: "Revenue figures become astronomical — clearly untested"
          missing_safeguard: "No ceiling on growth assumptions"
        - boundary: "negative"
          test_value: "-5%"
          logic_holds: false
          impact: "Business case is unviable — no contingency for market contraction"
          missing_safeguard: "No downturn scenario"
      first_break_point: "zero"
      has_explicit_bounds: false
      recommendation: "add_contingency"

  summary:
    fragile_parameters: 2
    sensitive_parameters: 3
    robust_parameters: 3
    parameters_without_bounds: 5
    highest_risk:
      parameter: "notice_period"
      reason: "Breaks at zero with legal impossibility; no upper bound enables lock-in"
```

## Severity Criteria

| Classification | Definition | Action |
|---------------|-----------|--------|
| **Fragile** | Logic breaks at realistic boundary values (zero or minimum viable) | Critical: add explicit bounds and safeguard clauses |
| **Sensitive** | Logic breaks at extreme but plausible values; holds at reasonable values | Major: add contingency analysis or scenario planning |
| **Robust** | Logic holds across all reasonable boundaries; breaks only at absurd extremes | Minor: document the assumed range for clarity |

### Severity Context by Parameter Type

| Parameter Type | Fragile = Critical When... | Example |
|---------------|--------------------------|---------|
| Duration/deadline | Zero or minimum makes obligation impossible | 0-day notice period vs. required cure period |
| Monetary amount | Zero makes contract non-viable or creates loophole | $0 penalty clause = no enforcement mechanism |
| Percentage | Zero or 100% creates degenerate case | 0% interest rate in financial model → division by zero in NPV |
| Count | Zero or one creates edge case | "Committee of at least N members" — what if N=0? |

## Examples

### Example 1: Fragile Parameter in a Contract

**Input document** (excerpt):
```markdown
## Section 5: Termination
5.1 Either party may terminate this agreement with 30 days written notice.

## Section 8: Remediation
8.2 Upon receiving notice of breach, the breaching party shall have a
reasonable period to cure the breach before termination takes effect.
```

**Parameter**: "30 days" in Section 5.1

**Boundary test at zero (0 days)**:
```yaml
boundary_result:
  parameter_name: "notice_period"
  original_value: "30 days"
  sensitivity_classification: "fragile"
  boundary_tests:
    - boundary: "zero"
      test_value: "0 days"
      logic_holds: false
      impact: "Section 8.2 promises a 'reasonable period to cure' but 0-day notice provides no cure period. Legal contradiction."
      missing_safeguard: "No minimum notice period; no explicit link between notice period and cure period"
  first_break_point: "zero"
  recommendation: "add_bounds"
  suggested_bounds:
    minimum: "14 days"
    rationale: "Must exceed cure period implied by Section 8.2"
```

### Example 2: Sensitive Parameter in a Budget

**Input document** (excerpt):
```markdown
## Revenue Projections
Based on 15% year-over-year growth (consistent with industry average),
we project:
- Year 1: $1.2M
- Year 2: $1.38M
- Year 3: $1.59M

## Hiring Plan
We plan to hire 3 engineers in Year 2, funded by Year 1 revenue.
```

**Parameter**: "15%" growth rate

**Boundary test at zero (0%)**:
```yaml
boundary_result:
  parameter_name: "yoy_growth_rate"
  original_value: "15%"
  sensitivity_classification: "sensitive"
  boundary_tests:
    - boundary: "zero"
      test_value: "0%"
      logic_holds: false
      impact: "Year 2 revenue stays at $1.2M. Hiring plan assumes $1.38M — $180K gap. 3 engineer hires become unfunded."
      missing_safeguard: "No contingency hiring plan; no minimum revenue threshold for hiring trigger"
  first_break_point: "zero"
  recommendation: "add_contingency"
```

## Integration

### Invocation from mutadoc.sh

```bash
# Full boundary sweep (all parameters)
mutadoc test document.md --strategy boundary

# Specific parameter types only
mutadoc test contract.md --strategy boundary --param-types duration,amount

# Specific section
mutadoc test document.md --strategy boundary --target "Section 5"

# With bound suggestions
mutadoc test contract.md --strategy boundary --suggest-bounds
```

### Internal Integration

```bash
# In mutadoc.sh, the boundary strategy is invoked as:
run_strategy "boundary" "$DOCUMENT_PATH" "$PARAMETER_SCOPE" "$PARAMETER_TYPES"

# The function:
# 1. Reads the strategy template from strategies/boundary.md
# 2. If scope is "all":
#    a. Uses the systematic boundary sweep prompt to extract all parameters
#    b. For each parameter, generates 5 boundary values based on type
# 3. If scope is a specific section/parameter:
#    a. Extracts the parameter value
#    b. Generates boundary values for that parameter type
#    c. Uses the single-parameter boundary test prompt
# 4. Parses the YAML response
# 5. Classifies each parameter (fragile / sensitive / robust)
# 6. Sorts results by sensitivity (fragile first)
# 7. Generates suggested bounds for fragile parameters (if enabled)
```

### Combination with Other Strategies

Boundary testing is most effective when combined with:

| Strategy | Combination Effect |
|----------|-------------------|
| **Inversion** | Inversion tests claim direction ("X improves Y" → "X degrades Y"); Boundary tests parameter magnitude ("30 days" → "0 days"). Together they cover both qualitative and quantitative robustness. |
| **Ambiguity** | Parameters modified by vague language ("approximately 30 days", "reasonable amount") are prime boundary targets — the ambiguity hides undefined boundaries |
| **Contradiction** | Boundary testing may reveal contradictions that only appear at extreme values — Section A says "at least 30 days" but Section B's timeline assumes 7 days |
| **Deletion** | Parameters in dead clauses (identified by deletion testing) need not be boundary-tested — the parameter has no structural impact regardless of value |
