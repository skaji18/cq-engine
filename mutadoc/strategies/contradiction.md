# Strategy: Contradiction (S1)

> **MutaDoc Mutation Strategy S1**
> **Purpose**: Detect hidden contradictions between document sections
> **Theoretical Basis**: [Assumption Mutation Pattern](../../patterns/05_assumption_mutation.md) — Strategy 1
> **Estimated Effort**: M

---

## Overview

The Contradiction strategy detects hidden logical conflicts between document sections by systematically altering one clause and observing whether other clauses become inconsistent. Documents often contain contradictions that are invisible when reading section-by-section but become catastrophic when the document is executed or enforced as a whole.

Contradictions arise because:
- Documents are authored by multiple people over time, each modifying their section without checking cross-references.
- Legal and technical documents restate terms in different sections, creating opportunities for divergence.
- Copy-paste-modify workflows propagate original constraints into new contexts where they conflict.

Unlike grammar checkers (which examine surface text) or plagiarism detectors (which compare against external sources), the Contradiction strategy examines **internal consistency** — whether the document agrees with itself.

---

## When to Use

| Scenario | Priority | Rationale |
|----------|:--------:|-----------|
| Contracts with 10+ sections | **High** | Cross-section contradictions are the #1 source of contract disputes |
| API specifications with multiple endpoints | **High** | Endpoint schemas, auth requirements, and error codes often diverge |
| Policy documents revised over 3+ iterations | **High** | Revision history accumulates contradictory rules |
| Technical specifications with dependencies between components | **Medium** | Component interfaces may contradict shared constraints |
| Single-author, short documents (<5 pages) | **Low** | Low contradiction probability, but not zero |
| Creative writing, marketing copy | **Skip** | Consistency is not the primary quality metric |

---

## Prompt Template

### Step 1: Clause Identification

```
You are a document structure analyst. Your task is to identify discrete testable
units (clauses) in the following document.

For each clause, extract:
1. Clause ID (sequential: C001, C002, ...)
2. Location (section heading + paragraph number)
3. Core assertion (one sentence summarizing what this clause states)
4. Key terms defined or referenced
5. Dependencies (other sections explicitly referenced, e.g., "as defined in Section 3.2")

Document:
---
{document_content}
---

Output as structured YAML:
clauses:
  - id: C001
    location: "Section 1, Paragraph 2"
    assertion: "..."
    key_terms: ["term1", "term2"]
    references: ["Section 3.2", "Appendix A"]
```

### Step 2: Contradiction Mutation Generation

```
You are a document mutation tester specializing in contradiction detection.

Given the following clause list, generate contradiction mutations. For each
clause that makes a specific assertion, create a mutated version that:
1. Directly contradicts the original assertion
2. Remains internally grammatically valid
3. Could plausibly exist in a poorly-edited document

Then identify which OTHER clauses in the document would conflict with the
mutated version. If many clauses conflict, the original assertion is
well-integrated (high structural importance). If no clauses conflict,
the assertion may be orphaned or redundant.

CRITICAL: Also check whether contradictions ALREADY EXIST between clauses
in the original document (no mutation needed). These are the highest-value
findings — real contradictions, not hypothetical ones.

Clauses:
---
{clause_list_yaml}
---

Full document for reference:
---
{document_content}
---

For each mutation, output:
mutations:
  - mutation_id: M001
    source_clause: C001
    original_text: "..."
    mutated_text: "..."
    conflicting_clauses: ["C005", "C012"]
    conflict_description: "..."
    severity: Critical|Major|Minor
    pre_existing: true|false  # true if contradiction exists in original
```

### Step 3: Cross-Impact Evaluation

```
You are a document integrity auditor. Given the contradiction mutations below,
evaluate the cascading impact of each detected conflict.

For each conflict pair:
1. Identify which interpretation would prevail if both clauses were enforced
2. Estimate the practical consequence of the contradiction
3. Recommend a specific resolution (which clause to amend, and how)
4. Assess whether the contradiction is detectable by a typical human reviewer
   reading linearly (or if it requires cross-section analysis)

Mutations with conflicts:
---
{mutations_yaml}
---

Full document:
---
{document_content}
---

Output:
impact_assessment:
  - mutation_id: M001
    prevailing_interpretation: "..."
    practical_consequence: "..."
    resolution: "..."
    human_detectable: true|false
    confidence: 0.0-1.0
```

---

## Input Specification

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `document_path` | string | Yes | Path to the target document (Markdown, plain text, or structured text) |
| `clause_mode` | enum | No | `auto` (default): LLM identifies clauses. `manual`: User provides clause list via `clauses_path` |
| `clauses_path` | string | No | Path to a pre-defined clause list (YAML format). Required if `clause_mode: manual` |
| `focus_sections` | list | No | Limit analysis to specific sections (e.g., `["Section 3", "Section 7"]`). Default: all sections |
| `max_mutations` | integer | No | Maximum number of mutations to generate. Default: `clause_count * 2` |

### Input Example

```yaml
strategy: contradiction
input:
  document_path: "contracts/service_agreement_v3.md"
  clause_mode: auto
  focus_sections: ["Terms of Service", "Termination", "Liability"]
  max_mutations: 30
```

---

## Output Format

```yaml
contradiction_report:
  metadata:
    document: "contracts/service_agreement_v3.md"
    strategy: contradiction
    timestamp: "2026-02-17T10:30:00Z"
    clauses_identified: 24
    mutations_generated: 18
    contradictions_found: 3
    pre_existing_contradictions: 1

  pre_existing_contradictions:
    - id: PE-001
      clause_a:
        id: C005
        location: "Section 5, Paragraph 1"
        text: "Either party may terminate with 30 days written notice."
      clause_b:
        id: C012
        location: "Section 12, Paragraph 3"
        text: "Provider may terminate immediately upon breach."
      conflict: "Section 5 requires 30-day notice for all terminations, but Section 12 permits immediate termination without notice period."
      severity: Critical
      practical_consequence: "A provider claiming breach could terminate immediately, contradicting the other party's expectation of 30-day cure period."
      resolution: "Add exception clause to Section 5: 'except as provided in Section 12 for material breach.'"
      human_detectable: false

  mutation_findings:
    - id: MF-001
      mutation_id: M003
      source_clause: C008
      original_text: "All data shall be encrypted at rest."
      mutated_text: "No data shall be encrypted at rest."
      conflicting_clauses:
        - clause_id: C015
          text: "Provider certifies compliance with SOC 2 Type II."
          conflict: "SOC 2 requires encryption at rest; removing encryption invalidates compliance."
      severity: Major
      structural_importance: high
      notes: "Encryption requirement is load-bearing — it supports compliance claims elsewhere."

  summary:
    critical: 1
    major: 1
    minor: 1
    false_positives: 0
    highest_risk: "PE-001: Conflicting termination clauses could be exploited by either party."
```

---

## Severity Criteria

| Severity | Definition | Examples | Action Required |
|----------|-----------|----------|-----------------|
| **Critical** | Legal or logical impossibility — both clauses cannot be simultaneously true. Enforcement of one necessarily violates the other. | Conflicting termination periods; contradictory liability caps; mutually exclusive obligations | Must resolve before document is finalized |
| **Major** | Significant inconsistency that creates ambiguity about intent. Both clauses could technically coexist but create confusion or risk. | Different definitions of the same term in different sections; inconsistent scope descriptions; conflicting but non-binding recommendations | Should resolve; document functional but risky |
| **Minor** | Stylistic or tonal tension between sections. No logical impossibility, but creates an impression of careless drafting. | Formal language in one section, informal in another; different measurement units; inconsistent formatting of the same concept | Optional; cosmetic improvement |

---

## Examples

### Example 1: Contract with Conflicting Termination Clauses

**Input document excerpt:**

> **Section 5 — Termination**
> Either party may terminate this Agreement by providing thirty (30) days written notice to the other party.
>
> **Section 12 — Breach**
> In the event of material breach, the non-breaching party may terminate this Agreement immediately upon written notice.

**Contradiction detection:**

```yaml
- id: PE-001
  severity: Critical
  clause_a: "Section 5: 30 days written notice for termination"
  clause_b: "Section 12: immediate termination upon breach"
  conflict: "Section 5 establishes a universal 30-day notice requirement. Section 12 creates an exception for breach that Section 5 does not acknowledge. If the breaching party relies on Section 5's 30-day cure period while the other party invokes Section 12's immediate termination, a dispute arises."
  resolution: "Amend Section 5 to read: 'Either party may terminate this Agreement by providing thirty (30) days written notice, except as otherwise provided in Section 12.'"
```

### Example 2: API Specification with Schema Contradiction

**Input document excerpt:**

> **GET /users/{id}**
> Response: `{ "user_id": string, "name": string, "email": string }`
>
> **PUT /users/{id}**
> Response: `{ "id": integer, "name": string, "email_address": string }`

**Contradiction detection:**

```yaml
- id: PE-002
  severity: Major
  clause_a: "GET /users/{id} returns user_id (string) and email (string)"
  clause_b: "PUT /users/{id} returns id (integer) and email_address (string)"
  conflict: "Same resource uses different field names (user_id vs id, email vs email_address) and different types (string vs integer for identifier). Clients parsing GET and PUT responses with the same model will fail."
  resolution: "Standardize field names and types across all /users endpoints. Define a shared User schema referenced by both endpoints."
```

### Example 3: No Contradictions Found (False Positive Check)

**Input:** Well-structured document with consistent cross-references.

```yaml
contradiction_report:
  contradictions_found: 0
  pre_existing_contradictions: []
  mutation_findings: []
  summary:
    critical: 0
    major: 0
    minor: 0
    notes: "No contradictions detected. 15 clauses tested with 30 mutations."
```

---

## Integration

### Calling from mutadoc.sh

```bash
#!/usr/bin/env bash
# Run S1 Contradiction strategy on a target document

STRATEGY="contradiction"
DOCUMENT="$1"
OUTPUT_DIR="${2:-./reports}"

# Step 1: Identify clauses
echo "=== S1 Contradiction: Clause Identification ==="
claude --prompt "$(cat strategies/contradiction.md | sed -n '/Step 1/,/Step 2/p')" \
  --input "$DOCUMENT" \
  --output "$OUTPUT_DIR/clauses.yaml"

# Step 2: Generate contradiction mutations
echo "=== S1 Contradiction: Mutation Generation ==="
claude --prompt "$(cat strategies/contradiction.md | sed -n '/Step 2/,/Step 3/p')" \
  --input "$DOCUMENT" \
  --context "$OUTPUT_DIR/clauses.yaml" \
  --output "$OUTPUT_DIR/mutations.yaml"

# Step 3: Evaluate cross-impact
echo "=== S1 Contradiction: Impact Evaluation ==="
claude --prompt "$(cat strategies/contradiction.md | sed -n '/Step 3/,/---/p')" \
  --input "$DOCUMENT" \
  --context "$OUTPUT_DIR/mutations.yaml" \
  --output "$OUTPUT_DIR/contradiction_report.yaml"

echo "Report: $OUTPUT_DIR/contradiction_report.yaml"
```

### Pipeline Position

```
Document → [S1 Contradiction] → [S2 Ambiguity] → [S3 Deletion] → ...
                 │
                 ▼
         contradiction_report.yaml
                 │
                 ▼
         Repair Proposal Generator
```

S1 Contradiction is typically run **first** in the pipeline because contradictions are the most severe class of document defect. Contradiction findings inform subsequent strategies (e.g., S2 Ambiguity may focus on sections where contradictions were NOT found, since those sections passed the stronger test).
