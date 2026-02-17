# Strategy: Deletion

## Overview

The Deletion strategy removes a clause, section, or paragraph entirely from the document and measures the structural impact of its absence. The core insight: **if removing a section has zero impact on the rest of the document, that section is a "dead clause" — text that exists but contributes nothing.**

Dead clauses are not harmless. They:
- Create maintenance burden (updating text that serves no purpose)
- Give false confidence (readers assume every section matters)
- Obscure the document's actual structure by adding noise
- May become stale without anyone noticing (since nothing depends on them)

Conversely, sections with very high structural impact are **critical dependencies** — if they contain errors, the damage cascades broadly.

Deletion testing reveals both extremes: dead weight to remove and critical sections to protect.

## When to Use

| Scenario | Suitability | Notes |
|----------|:-----------:|-------|
| Legal contracts with boilerplate clauses | High | Contracts accumulate clauses over decades; many are dead weight |
| API specifications with deprecated endpoints | High | Deprecated sections often remain in specs long after relevance ends |
| Policy documents with historical provisions | High | Policies grow by accretion; deletion testing identifies obsolete provisions |
| Short, tightly written documents (<2 pages) | Low | Too few sections to have dead clauses; every section likely matters |
| Creative writing or narrative text | Low | Structural dependencies are semantic, not logical — deletion testing is less meaningful |

## Prompt Template

The following prompt template is sent to the LLM for each deletion target. Variables in `{braces}` are replaced at runtime.

```markdown
You are a structural analyst performing a Deletion Mutation Test on a document.

## Your Task

A specific section has been DELETED from the document. Your job is to analyze the
impact of this deletion on the remaining document.

## Original Document (complete)

{full_document}

## Deleted Section

**Section identifier**: {section_id}
**Deleted text**:
{deleted_text}

## Deletion Mode: {deletion_mode}

## Analysis Instructions

1. **Cross-reference scan**: List every other section that references, depends on,
   or is affected by the deleted section. Include:
   - Direct references (e.g., "as defined in Section X")
   - Implicit dependencies (e.g., a term defined in the deleted section used elsewhere)
   - Logical dependencies (e.g., a conclusion that relies on the deleted section's premises)

2. **Impact assessment**: For each affected section, describe:
   - What breaks or becomes incomplete
   - How severe the breakage is (cosmetic / functional / structural)
   - Whether the affected section can still be understood without the deleted section

3. **Structural impact score**: Rate the overall impact on a scale of 0-100:
   - 0: Zero impact — no section references or depends on the deleted text (dead clause)
   - 1-20: Low impact — minor references that could be trivially reworded
   - 21-50: Moderate impact — several sections weakened but document remains coherent
   - 51-80: High impact — multiple sections become incomplete or confusing
   - 81-100: Critical dependency — document structure fundamentally broken

4. **Dead clause assessment**: If the impact score is 0, explicitly state:
   - "DEAD CLAUSE DETECTED"
   - Recommendation: remove, archive, or justify retention

## Output Format

Respond in the following YAML structure:

```yaml
deletion_result:
  section_id: "{section_id}"
  deleted_text_preview: "first 80 characters..."
  impact_score: <0-100>
  classification: "<dead_clause | low_impact | moderate_impact | high_impact | critical_dependency>"
  affected_sections:
    - section_id: "..."
      dependency_type: "<direct_reference | implicit_dependency | logical_dependency>"
      breakage_severity: "<cosmetic | functional | structural>"
      description: "..."
  dead_clause: <true | false>
  recommendation: "<remove | archive | justify_retention | protect_as_critical>"
  reasoning: "Brief explanation of the score"
```
```

### Iterative Deletion Mode

For comprehensive analysis, the strategy supports iterating over all sections:

```markdown
You are performing a systematic Deletion Mutation Test.

For each section in the document below, evaluate: "If this section were deleted,
what would break?"

## Document

{full_document}

## Instructions

For EACH top-level section (identified by heading), produce:
1. Section identifier and first-line preview
2. Impact score (0-100)
3. Classification (dead_clause / low_impact / moderate_impact / high_impact / critical_dependency)
4. Number of dependent sections
5. Dead clause flag (true/false)

## Output Format

Respond as a YAML list:

```yaml
deletion_sweep:
  document: "{document_name}"
  total_sections: <N>
  results:
    - section_id: "..."
      preview: "first 60 chars..."
      impact_score: <0-100>
      classification: "..."
      dependent_count: <N>
      dead_clause: <true | false>
  summary:
    dead_clauses: <count>
    critical_dependencies: <count>
    average_impact: <0-100>
```
```

## Input Specification

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `document_path` | string | Yes | Path to the target document (Markdown or plain text) |
| `deletion_mode` | enum | No | `section-level` (default), `clause-level`, `paragraph-level` |
| `target_section` | string | No | Specific section to delete. If omitted, iterates over all sections |
| `include_dead_clause_report` | boolean | No | If true, generates a dedicated dead clause summary (default: true) |

### Deletion Mode Definitions

| Mode | Unit of Deletion | When to Use |
|------|-----------------|-------------|
| `section-level` | Top-level sections (H2 headings) | Default for most documents; coarse-grained structural analysis |
| `clause-level` | Individual clauses (numbered items, sub-headings) | Legal contracts, detailed specifications with numbered provisions |
| `paragraph-level` | Individual paragraphs | Dense documents without clear heading structure |

## Output Format

```yaml
deletion_report:
  document: "contract.md"
  deletion_mode: "clause-level"
  timestamp: "2026-01-15T10:30:00Z"
  total_units_tested: 25
  results:
    - section_id: "5.1"
      preview: "Termination for Cause. Either party may terminate..."
      impact_score: 85
      classification: "critical_dependency"
      affected_sections:
        - section_id: "12.3"
          dependency_type: "direct_reference"
          breakage_severity: "structural"
          description: "Section 12.3 references 'notice period defined in Section 5.1'"
        - section_id: "8.2"
          dependency_type: "logical_dependency"
          breakage_severity: "functional"
          description: "Section 8.2 payment terms assume termination triggers from 5.1"
      dead_clause: false
      recommendation: "protect_as_critical"

    - section_id: "14.2"
      preview: "Governing Law. This agreement shall be governed by..."
      impact_score: 0
      classification: "dead_clause"
      affected_sections: []
      dead_clause: true
      recommendation: "remove"
      reasoning: "No other section references governing law. Clause is self-contained boilerplate with no structural connections."

  summary:
    dead_clauses: 3
    dead_clause_ids: ["14.2", "14.5", "16.1"]
    critical_dependencies: 2
    critical_dependency_ids: ["5.1", "3.2"]
    average_impact: 28.4
    dependency_graph:
      "5.1": ["12.3", "8.2", "9.1"]
      "3.2": ["5.1", "7.4", "11.2", "12.3"]
      "14.2": []
```

## Severity Criteria

| Classification | Impact Score | Meaning | Action |
|---------------|:-----------:|---------|--------|
| **Dead clause** | 0 | No section depends on this text | Recommend removal or justify retention |
| **Low impact** | 1–20 | Minor, easily repairable references | Review for necessity; consider consolidation |
| **Moderate impact** | 21–50 | Several sections weakened | Ensure accuracy; add cross-reference checks |
| **High impact** | 51–80 | Multiple sections become incomplete | High-priority review; consider redundancy for resilience |
| **Critical dependency** | 81–100 | Document structure fundamentally breaks | Protect with maximum review rigor; flag as single point of failure |

### Severity Context by Document Type

| Document Type | Dead Clause Severity | Critical Dependency Severity |
|--------------|:--------------------:|:---------------------------:|
| Contract | Minor (boilerplate is common) | Critical (cascading legal obligations) |
| API Spec | Major (deprecated endpoints confuse implementers) | Critical (authentication/authorization sections) |
| Academic Paper | Minor (background sections may be contextual) | Major (methodology/results linkage) |
| Policy | Major (obsolete provisions create compliance risk) | Critical (enforcement mechanisms) |

## Examples

### Example 1: Dead Clause Detection in a Contract

**Input document** (excerpt):
```markdown
## Section 5: Termination
5.1 Either party may terminate this agreement with 30 days written notice.
5.2 Termination for cause requires documented breach notification.

## Section 14: Miscellaneous
14.1 Headings are for convenience only and do not affect interpretation.
14.2 This agreement may be executed in counterparts.
```

**Deletion target**: Section 14.2

**Result**:
```yaml
deletion_result:
  section_id: "14.2"
  impact_score: 0
  classification: "dead_clause"
  affected_sections: []
  dead_clause: true
  recommendation: "remove"
  reasoning: "No other section references counterpart execution. The clause is self-contained boilerplate with no structural effect on the agreement."
```

### Example 2: Critical Dependency in an API Spec

**Input document** (excerpt):
```markdown
## Authentication
All endpoints require Bearer token authentication. Tokens are obtained via
the /auth/token endpoint with client credentials.

## GET /users
Returns a list of users. Requires authentication.

## PUT /users/{id}
Updates a user. Requires authentication and admin role.
```

**Deletion target**: Authentication section

**Result**:
```yaml
deletion_result:
  section_id: "Authentication"
  impact_score: 92
  classification: "critical_dependency"
  affected_sections:
    - section_id: "GET /users"
      dependency_type: "direct_reference"
      breakage_severity: "structural"
      description: "'Requires authentication' has no definition without this section"
    - section_id: "PUT /users/{id}"
      dependency_type: "direct_reference"
      breakage_severity: "structural"
      description: "'Requires authentication and admin role' undefined — both authentication and role model are gone"
  dead_clause: false
  recommendation: "protect_as_critical"
  reasoning: "All endpoints depend on the authentication section. Removing it makes the entire API spec unimplementable."
```

## Integration

### Invocation from mutadoc.sh

```bash
# Single section deletion test
mutadoc test document.md --strategy deletion --target "Section 5.1"

# Full deletion sweep (all sections)
mutadoc test document.md --strategy deletion

# Clause-level deletion (for contracts)
mutadoc test contract.md --strategy deletion --deletion-mode clause-level

# Dead clause report only
mutadoc test document.md --strategy deletion --dead-clauses-only
```

### Internal Integration

```bash
# In mutadoc.sh, the deletion strategy is invoked as:
run_strategy "deletion" "$DOCUMENT_PATH" "$DELETION_MODE" "$TARGET_SECTION"

# The function:
# 1. Reads the strategy template from strategies/deletion.md
# 2. Parses the document to identify deletion units (sections/clauses/paragraphs)
# 3. For each unit (or the specified target):
#    a. Constructs the prompt by substituting variables into the template
#    b. Sends the prompt to the LLM via Claude Code Task tool
#    c. Parses the YAML response
# 4. Aggregates results into the deletion report
# 5. Generates the dependency graph from affected_sections data
```

### Combination with Other Strategies

Deletion testing is most effective when combined with:

| Strategy | Combination Effect |
|----------|-------------------|
| **Contradiction** | Run contradiction first to find conflicting clauses, then deletion to determine which clause is structurally dominant |
| **Ambiguity** | Dead clauses often contain the most ambiguous language (since nothing depends on their precision) |
| **Inversion** | Critical dependencies identified by deletion are prime targets for inversion testing — if the document is fragile at that point, test whether the claim there is robust |
