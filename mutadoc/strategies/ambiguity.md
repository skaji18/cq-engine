# Strategy: Ambiguity (S2)

> **MutaDoc Mutation Strategy S2**
> **Purpose**: Expose vague modifiers by replacing them with extreme values
> **Theoretical Basis**: [Assumption Mutation Pattern](../../patterns/05_assumption_mutation.md) — Strategy 2
> **Estimated Effort**: M

---

## Overview

The Ambiguity strategy detects hidden vagueness in documents by replacing imprecise modifiers with extreme values. If replacing "reasonable" with "unlimited" or "zero" changes the document's meaning dramatically, then the original word was **load-bearing ambiguity** — it carried important meaning but defined none of it.

Documents rely on vague language because:
- Authors assume shared understanding ("reasonable" means the same thing to everyone — it doesn't).
- Vague terms defer hard decisions ("appropriate security measures" avoids specifying which measures).
- Legal drafting traditions use intentionally flexible terms that create plausible deniability but also create enforcement gaps.

The Ambiguity strategy is the document equivalent of **fuzz testing**: inject extreme values at points of imprecision and observe whether the system (document) behaves differently. If extreme-value substitution produces absurd results, the original term needed precision. If extreme-value substitution changes nothing, the original term was decorative.

---

## When to Use

| Scenario | Priority | Rationale |
|----------|:--------:|-----------|
| Contracts defining obligations, rights, or deadlines | **High** | Vague obligations are unenforceable obligations |
| SLAs and performance agreements | **High** | "Best effort" vs "99.9% uptime" is the difference between a promise and a guarantee |
| Technical specifications distributed to multiple implementers | **High** | Each implementer interprets ambiguity differently (34% divergence rate observed) |
| Policy documents with compliance requirements | **Medium** | Regulators interpret "adequate" differently than authors intend |
| Internal team guidelines | **Low** | Ambiguity may be acceptable when audience is small and aligned |
| Creative writing, narratives | **Skip** | Ambiguity is often intentional and desirable |

---

## Vague Modifier Catalog

The following catalog maps common vague modifiers to their extreme-value replacements. During analysis, both the minimum and maximum extremes are tested.

### Quantity and Degree

| Vague Modifier | Min Extreme | Max Extreme | Category |
|---------------|-------------|-------------|----------|
| reasonable | zero / none | unlimited / infinite | quantity |
| appropriate | the minimum legally required | the maximum technically possible | degree |
| adequate | barely sufficient to avoid failure | exceeding all known requirements | degree |
| sufficient | exactly 1 | unbounded | quantity |
| significant | 0.01% | 99.99% | quantity |
| material | trivially small | existentially critical | degree |
| substantial | negligible | total | quantity |

### Time and Frequency

| Vague Modifier | Min Extreme | Max Extreme | Category |
|---------------|-------------|-------------|----------|
| timely | within 1 second | within 10 years | time |
| promptly | immediately (0 delay) | as soon as practically convenient (indefinite) | time |
| periodically | once per decade | every millisecond | frequency |
| regularly | once ever | continuously without pause | frequency |
| as soon as possible | instantly | when all other priorities are complete | time |

### Effort and Quality

| Vague Modifier | Min Extreme | Max Extreme | Category |
|---------------|-------------|-------------|----------|
| best efforts | minimal token effort that can be documented | unlimited resources and time | effort |
| commercially reasonable | the cheapest option available | whatever the most well-funded competitor would do | effort |
| good faith | letter of the law only | spirit of the law with generous interpretation | effort |
| industry standard | the lowest practice in any company in the industry | the highest practice in the leading company | quality |
| state of the art | the most recent published research | bleeding-edge unreleased technology | quality |

### Scope and Extent

| Vague Modifier | Min Extreme | Max Extreme | Category |
|---------------|-------------|-------------|----------|
| including but not limited to | only the listed items (treated as exhaustive) | absolutely everything conceivable | scope |
| generally | in 51% of cases | in 100% of cases | scope |
| primarily | in the majority of cases | exclusively | scope |
| as needed | never (no need arises) | constantly (need is perpetual) | frequency |
| to the extent possible | not at all (it wasn't possible) | fully and completely (everything was possible) | scope |

---

## Prompt Template

### Step 1: Vague Modifier Identification

```
You are a precision analyst specializing in document language quality.
Scan the following document and identify every vague modifier — words or
phrases that carry important meaning but lack precise definition.

For each vague modifier found:
1. Modifier ID (sequential: V001, V002, ...)
2. Location (section + paragraph + sentence)
3. The vague word/phrase
4. The full sentence containing it
5. What the modifier is qualifying (an obligation, right, deadline, scope, etc.)
6. Why it is vague (what information is missing for precise interpretation?)

Sensitivity level: {sensitivity_level}
- strict: Flag all subjective terms, including commonly accepted ones
- normal: Flag terms where reasonable people could disagree on meaning
- lenient: Flag only terms where the meaning is critically undefined

Document:
---
{document_content}
---

Output as structured YAML:
vague_modifiers:
  - id: V001
    location: "Section 3, Paragraph 1, Sentence 2"
    modifier: "reasonable"
    full_sentence: "Provider shall use reasonable efforts to maintain uptime."
    qualifying: "obligation (effort level)"
    vagueness_reason: "'Reasonable' is undefined — no metric, no comparison baseline, no consequence for falling short."
```

### Step 2: Extreme-Value Mutation

```
You are a document mutation tester. For each vague modifier identified below,
generate two extreme-value mutations: one minimum extreme and one maximum extreme.

For each mutation:
1. Replace the vague modifier with the extreme value in the original sentence
2. Assess the impact score (0-100): how much does the document's meaning change?
   - 0: No meaningful change (modifier was decorative)
   - 50: Moderate change (meaning shifts but document remains functional)
   - 100: Radical change (document becomes absurd or unenforceable)
3. Determine if the extreme version is actually what one party might argue the
   vague term means in a dispute

Use the vague modifier catalog for standard replacements. For domain-specific
terms not in the catalog, generate contextually appropriate extremes.

Vague modifiers:
---
{vague_modifiers_yaml}
---

Full document:
---
{document_content}
---

Output:
mutations:
  - modifier_id: V001
    original: "reasonable efforts"
    min_mutation:
      replacement: "zero effort"
      mutated_sentence: "Provider shall use zero effort to maintain uptime."
      impact_score: 95
      plausible_in_dispute: false
    max_mutation:
      replacement: "unlimited effort at any cost"
      mutated_sentence: "Provider shall use unlimited effort at any cost to maintain uptime."
      impact_score: 90
      plausible_in_dispute: true
    combined_impact: 92
    recommendation: define_precisely|accept_ambiguity|remove
    recommendation_detail: "Define 'reasonable efforts' with specific metrics: e.g., 'maintain 99.5% monthly uptime as measured by {monitoring_tool}.'"
```

### Step 3: Ambiguity Impact Report

```
You are a document quality auditor. Given the extreme-value mutation results,
produce a prioritized ambiguity report.

Rank findings by:
1. Severity (Critical > Major > Minor)
2. Combined impact score (higher = more dangerous ambiguity)
3. Dispute plausibility (could a party actually argue for the extreme interpretation?)

For each finding, provide:
- A specific rewrite recommendation that eliminates the ambiguity
- The minimum information needed to make the term precise
- Whether the ambiguity appears intentional (strategic vagueness) or accidental

Mutations:
---
{mutations_yaml}
---

Output:
ambiguity_report:
  metadata:
    document: "{document_path}"
    strategy: ambiguity
    sensitivity: {sensitivity_level}
    timestamp: "{timestamp}"
    modifiers_found: {count}
    findings: {count}
  findings:
    - modifier_id: V001
      severity: Critical|Major|Minor
      original_phrase: "..."
      location: "..."
      impact_score: 0-100
      intentional_ambiguity: true|false
      rewrite: "..."
      minimum_precision_needed: "..."
```

---

## Input Specification

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `document_path` | string | Yes | Path to the target document |
| `sensitivity_level` | enum | No | `strict` / `normal` (default) / `lenient` — controls how aggressively vague terms are flagged |
| `custom_catalog` | string | No | Path to domain-specific vague modifier catalog (extends built-in catalog) |
| `focus_sections` | list | No | Limit analysis to specific sections. Default: all |
| `max_modifiers` | integer | No | Maximum number of modifiers to analyze. Default: 50 |

### Input Example

```yaml
strategy: ambiguity
input:
  document_path: "contracts/sla_enterprise_v2.md"
  sensitivity_level: strict
  focus_sections: ["Service Levels", "Obligations", "Remedies"]
  max_modifiers: 30
```

---

## Output Format

```yaml
ambiguity_report:
  metadata:
    document: "contracts/sla_enterprise_v2.md"
    strategy: ambiguity
    sensitivity: strict
    timestamp: "2026-02-17T11:00:00Z"
    modifiers_found: 12
    findings_by_severity:
      critical: 3
      major: 5
      minor: 4

  findings:
    - modifier_id: V001
      severity: Critical
      original_phrase: "reasonable efforts"
      location: "Section 4.1, Paragraph 1"
      full_sentence: "Provider shall use reasonable efforts to maintain 99.9% uptime."
      qualifying: "obligation (effort level for uptime)"
      impact_score: 92
      min_extreme: "zero effort → Provider has no uptime obligation"
      max_extreme: "unlimited effort → Provider must spend any amount to prevent downtime"
      intentional_ambiguity: false
      rewrite: "Provider shall maintain 99.9% monthly uptime as measured by {monitoring_endpoint}, calculated excluding scheduled maintenance windows communicated 48 hours in advance."
      minimum_precision_needed: "Specific uptime percentage + measurement method + exclusion criteria"

    - modifier_id: V002
      severity: Critical
      original_phrase: "timely manner"
      location: "Section 6.2, Paragraph 3"
      full_sentence: "Provider shall respond to Critical incidents in a timely manner."
      qualifying: "deadline (incident response)"
      impact_score: 88
      min_extreme: "within 10 years → no effective SLA"
      max_extreme: "within 1 second → physically impossible for human response"
      intentional_ambiguity: false
      rewrite: "Provider shall acknowledge Critical incidents within 15 minutes and provide initial diagnosis within 2 hours of acknowledgment."
      minimum_precision_needed: "Specific time limit for acknowledgment + specific time limit for response"

    - modifier_id: V003
      severity: Major
      original_phrase: "appropriate security measures"
      location: "Section 8.1, Paragraph 1"
      full_sentence: "Provider shall implement appropriate security measures to protect Customer data."
      qualifying: "scope (security requirements)"
      impact_score: 78
      min_extreme: "minimum legally required → may be below customer's actual needs"
      max_extreme: "maximum technically possible → unreasonably expensive"
      intentional_ambiguity: true
      rewrite: "Provider shall implement security measures consistent with SOC 2 Type II certification, including encryption at rest (AES-256) and in transit (TLS 1.3)."
      minimum_precision_needed: "Named security standard or specific technical requirements"

  summary:
    total_ambiguity_score: 72.3  # Average impact score across all findings
    highest_risk: "V001: 'reasonable efforts' for uptime obligation — no enforceable standard"
    strategic_vagueness_count: 1  # Intentionally vague terms
    recommendation: "12 vague modifiers found; 3 Critical findings require immediate precision before execution."
```

---

## Severity Criteria

| Severity | Definition | Qualifying Context | Action Required |
|----------|-----------|-------------------|-----------------|
| **Critical** | Ambiguity in obligations, rights, or deadlines — the terms that determine what parties must do, may do, or when they must do it. Extreme-value substitution produces either "no obligation" or "impossible obligation." | Effort clauses ("reasonable efforts"), time clauses ("timely"), payment terms ("fair market value"), termination conditions | Must define precisely before execution |
| **Major** | Ambiguity in scope, definitions, or conditions — the terms that determine what is covered or excluded. Extreme-value substitution changes the scope dramatically but the document remains nominally functional. | Scope clauses ("including but not limited to"), definitions ("material breach"), conditions ("as needed") | Should define; risk of divergent interpretation |
| **Minor** | Ambiguity in descriptions, context, or non-binding language. Extreme-value substitution changes tone but not substance. | Background sections, preambles, "whereas" clauses, aspirational language | Optional; low enforcement risk |

---

## Examples

### Example 1: SLA with "Reasonable Efforts"

**Input document excerpt:**

> **Section 4 — Service Levels**
> Provider shall use reasonable efforts to maintain 99.9% uptime for all production services.

**Ambiguity detection:**

```yaml
- modifier_id: V001
  severity: Critical
  original_phrase: "reasonable efforts"
  impact_score: 92
  analysis: |
    "Reasonable efforts" is the most common and most dangerous vague modifier
    in service agreements. It creates a nominal obligation with no enforcement
    mechanism.

    Min extreme: "zero effort" → Provider has no actual uptime obligation.
    The 99.9% target is aspirational, not contractual.

    Max extreme: "unlimited effort at any cost" → Provider must spend any
    amount to prevent even 0.01% downtime, which is economically irrational.

    In a dispute, Provider argues "reasonable" means "within normal operating
    budget" while Customer argues it means "whatever is necessary to hit 99.9%."
    Neither interpretation is wrong because "reasonable" is undefined.
  rewrite: "Provider shall maintain 99.9% monthly uptime as measured by
    [monitoring_endpoint], calculated excluding scheduled maintenance windows
    communicated 48 hours in advance. Failure to meet this target entitles
    Customer to service credits as defined in Section 7."
```

### Example 2: Technical Spec with Multiple Ambiguities

**Input document excerpt:**

> **Section 3 — Security**
> The system shall implement appropriate security measures. All sensitive data must be handled in a secure manner. Access controls should be periodically reviewed.

**Ambiguity detection:**

```yaml
findings:
  - modifier_id: V001
    severity: Critical
    original_phrase: "appropriate security measures"
    impact_score: 78
    rewrite: "...implement security measures consistent with SOC 2 Type II, including..."

  - modifier_id: V002
    severity: Major
    original_phrase: "secure manner"
    impact_score: 65
    rewrite: "...encrypted at rest using AES-256 and in transit using TLS 1.3..."

  - modifier_id: V003
    severity: Major
    original_phrase: "periodically reviewed"
    impact_score: 60
    rewrite: "...reviewed quarterly, with audit logs retained for 12 months..."
```

### Example 3: Precise Document (False Positive Check)

**Input:** Document using only quantitative, defined terms.

> Provider shall maintain 99.95% monthly uptime. Response time for P1 incidents: 15 minutes. Encryption: AES-256 at rest, TLS 1.3 in transit. Review cycle: quarterly.

```yaml
ambiguity_report:
  modifiers_found: 0
  findings_by_severity:
    critical: 0
    major: 0
    minor: 0
  summary:
    notes: "No vague modifiers detected. All terms are quantitatively defined."
```

---

## Integration

### Calling from mutadoc.sh

```bash
#!/usr/bin/env bash
# Run S2 Ambiguity strategy on a target document

STRATEGY="ambiguity"
DOCUMENT="$1"
SENSITIVITY="${2:-normal}"
OUTPUT_DIR="${3:-./reports}"

# Step 1: Identify vague modifiers
echo "=== S2 Ambiguity: Modifier Identification ==="
claude --prompt "$(cat strategies/ambiguity.md | sed -n '/Step 1/,/Step 2/p')" \
  --var "sensitivity_level=$SENSITIVITY" \
  --input "$DOCUMENT" \
  --output "$OUTPUT_DIR/vague_modifiers.yaml"

# Step 2: Generate extreme-value mutations
echo "=== S2 Ambiguity: Extreme-Value Mutation ==="
claude --prompt "$(cat strategies/ambiguity.md | sed -n '/Step 2/,/Step 3/p')" \
  --input "$DOCUMENT" \
  --context "$OUTPUT_DIR/vague_modifiers.yaml" \
  --output "$OUTPUT_DIR/mutations.yaml"

# Step 3: Produce ambiguity report
echo "=== S2 Ambiguity: Impact Report ==="
claude --prompt "$(cat strategies/ambiguity.md | sed -n '/Step 3/,/---/p')" \
  --input "$DOCUMENT" \
  --context "$OUTPUT_DIR/mutations.yaml" \
  --output "$OUTPUT_DIR/ambiguity_report.yaml"

echo "Report: $OUTPUT_DIR/ambiguity_report.yaml"
```

### Pipeline Position

```
Document → [S1 Contradiction] → [S2 Ambiguity] → [S3 Deletion] → ...
                                      │
                                      ▼
                              ambiguity_report.yaml
                                      │
                                      ▼
                              Repair Proposal Generator
```

S2 Ambiguity runs **after** S1 Contradiction. Sections that passed contradiction testing (internally consistent) may still contain ambiguous language. S2 focuses on the precision of individual terms rather than cross-section consistency. Together, S1 + S2 catch both structural defects (contradictions) and linguistic defects (ambiguity).
