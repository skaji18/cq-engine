---
preset:
  name: contract
  description: "Legal contracts (M&A, SaaS, employment, NDA)"
  strategies:
    contradiction: { weight: 1.0, enabled: true }
    ambiguity: { weight: 1.0, enabled: true }
    deletion: { weight: 0.8, enabled: true }
    inversion: { weight: 0.5, enabled: true }
    boundary: { weight: 0.7, enabled: true }
  default_persona: opposing_counsel
  severity_overrides:
    ambiguity_in_obligation: Critical
    contradictory_clauses: Critical
    undefined_term: Major
    dead_clause: Minor
    redundant_clause: Minor
  domain_terminology:
    - indemnify
    - severability
    - force majeure
    - liquidated damages
    - material adverse change
    - representations and warranties
    - covenant
    - escrow
    - non-compete
    - non-solicitation
    - governing law
    - arbitration
    - breach
    - termination for cause
    - assignment
  output_format: full_report
---

# Preset: Contract

Mutation testing configuration for legal contracts. Designed to find hidden vulnerabilities, contradictions, and exploitable ambiguities that opposing counsel would target in a dispute.

## Target Document Types

- **M&A agreements**: Stock Purchase Agreements, Asset Purchase Agreements, Merger Agreements
- **SaaS contracts**: Master Service Agreements, Subscription Agreements, Order Forms
- **Employment contracts**: Offer Letters, Employment Agreements, Severance Agreements
- **NDAs**: Mutual and Unilateral Non-Disclosure Agreements
- **Licensing agreements**: Software Licenses, IP Licenses, Franchise Agreements

## Strategy Configuration

### Contradiction (weight: 1.0)

The highest-priority strategy for contracts. Legal contracts must be internally consistent — a single contradiction can void a clause or create unintended obligations.

**What it does**: Identifies pairs of clauses that make incompatible claims or create conflicting obligations.

**Contract-specific mutations**:
- Swap obligation parties ("Buyer shall" ↔ "Seller shall") to test if surrounding clauses still make sense
- Invert condition triggers ("upon closing" ↔ "prior to closing") to detect temporal contradictions
- Cross-reference defined terms against their usage to find definition drift

### Ambiguity (weight: 1.0)

Equally prioritized with contradiction. Ambiguous language in contracts is the primary source of disputes — what seems clear to the drafter may be interpreted differently by the counterparty.

**What it does**: Identifies terms and phrases that admit multiple valid legal interpretations.

**Contract-specific mutations**:
- Replace "reasonable" with extreme values to test if the clause still functions
- Replace "material" with "any" or "immaterial" to reveal whether the qualification is load-bearing
- Test "including but not limited to" lists for completeness — does the catch-all actually catch all?

### Deletion (weight: 0.8)

High priority. Tests whether each clause is structurally necessary. Dead clauses (present but functionally inert) waste attention and may create false confidence.

**What it does**: Removes individual clauses or sections and measures impact on the contract's overall structure.

**Contract-specific mutations**:
- Delete each non-definition clause and check if any other clause references it
- Delete indemnification carve-outs and test if the base indemnification clause still functions
- Remove conditions precedent one by one to identify which are truly gating

### Inversion (weight: 0.5)

Moderate priority. Tests the robustness of rights and obligations by reversing them.

**What it does**: Reverses the polarity of claims, obligations, or conditions.

**Contract-specific mutations**:
- "shall" → "shall not" to test if surrounding clauses detect the change
- "exclusive" → "non-exclusive" to test if licensing terms are self-reinforcing
- Swap indemnifying and indemnified parties to test clause symmetry

### Boundary (weight: 0.7)

Above moderate priority. Tests numeric and temporal boundaries that may be untested or arbitrary.

**What it does**: Pushes numeric values, dates, and thresholds to extremes.

**Contract-specific mutations**:
- "30 days notice" → "0 days" (is immediate termination possible?)
- "30 days notice" → "365 days" (does any clause cap notice periods?)
- "$1,000,000 liability cap" → "$0" (does the contract function with zero liability?)
- "2-year non-compete" → "20-year non-compete" (does any clause limit duration?)

## Default Persona Rationale

**Opposing Counsel** (`opposing_counsel`) is the default persona because:

1. The most dangerous vulnerabilities in a contract are those a skilled opposing lawyer would exploit
2. Opposing counsel thinks in terms of legal attack vectors — which clauses can be challenged, voided, or reinterpreted
3. This persona naturally prioritizes ambiguity (exploitable in litigation) and contradiction (voidable clauses)
4. The perspective is adversarial but legally grounded — it finds real vulnerabilities, not theoretical ones

Alternative personas for specific use cases:
- `adversarial_reader`: For a more general "hostile reader" perspective
- `naive_implementer`: For testing whether contract terms can be operationalized without legal training

## Severity Overrides Explanation

| Override | Default → Override | Rationale |
|----------|-------------------|-----------|
| `ambiguity_in_obligation` | Major → **Critical** | Ambiguous obligations are the #1 source of contract disputes. "Commercially reasonable efforts" without definition is a lawsuit waiting to happen. |
| `contradictory_clauses` | Major → **Critical** | Contradictory clauses can void sections of the contract or create unintended obligations for either party. |
| `undefined_term` | Minor → **Major** | Undefined terms in contracts (capitalized but not in definitions section) create interpretation risk. |
| `dead_clause` | Major → **Minor** | A clause that doesn't connect to anything is wasteful but not dangerous — it doesn't create obligations or risks. |
| `redundant_clause` | Major → **Minor** | Redundant clauses are harmless if consistent. They only become problems if they contradict each other. |

## Domain Terminology

The following terms have specific legal meanings that differ from common usage. MutaDoc's mutation strategies are calibrated to respect these distinctions:

| Term | Legal Meaning | Common Misconception |
|------|-------------|---------------------|
| **Indemnify** | Obligation to compensate for loss or damage | Often confused with "insure" or "protect" |
| **Severability** | If one clause is invalid, others remain in effect | Often assumed to mean "separable" |
| **Force majeure** | Extraordinary events beyond parties' control | Not a blanket excuse for non-performance |
| **Liquidated damages** | Pre-agreed damages amount for breach | Not a penalty — must be a reasonable estimate |
| **Material adverse change** | Significant negative event affecting value | "Material" is often undefined and contested |
| **Representations and warranties** | Statements of fact that form basis of the deal | "Representations" and "warranties" have different legal implications |
| **Covenant** | Promise to do or refrain from doing something | Not the same as a "condition" |
| **Governing law** | Which jurisdiction's law applies | Does not determine venue for disputes |

## Usage Examples

```bash
# Test an M&A agreement
mutadoc test acquisition_agreement.md --preset contract

# Test with full report output
mutadoc test saas_msa.md --preset contract --format full_report

# Test only contradiction and ambiguity strategies
mutadoc test nda.md --preset contract --strategies contradiction,ambiguity

# Test with custom severity threshold (only Critical and Major)
mutadoc test employment_agreement.md --preset contract --min-severity major

# Override the default persona
mutadoc test license_agreement.md --preset contract --persona naive_implementer
```

## Sample Output

```markdown
# MutaDoc Report: acquisition_agreement.md
**Preset**: contract | **Persona**: opposing_counsel | **Score**: 72/100

## Critical Findings (2)

### [C-001] Contradictory Indemnification Scope (Contradiction)
- **Location**: Section 8.2 vs Section 8.4
- **Finding**: Section 8.2 states "Seller shall indemnify Buyer for all losses arising from
  breach of representations" but Section 8.4 states "Total indemnification liability shall not
  exceed the Purchase Price." Section 8.2's "all losses" is uncapped but Section 8.4 imposes
  a cap. Which controls?
- **Exploitation**: Opposing counsel would argue the uncapped provision in 8.2 supersedes the
  cap in 8.4 under the specific-over-general doctrine.
- **Recommendation**: Harmonize by adding "subject to Section 8.4" to Section 8.2.

### [C-002] Ambiguous Closing Condition (Ambiguity)
- **Location**: Section 6.1(c)
- **Finding**: "Material Adverse Change" is used as a closing condition but is defined as
  "any event that would reasonably be expected to have a material adverse effect" — circular
  definition using "material" to define "material."
- **Exploitation**: Either party could argue virtually any negative event does or does not
  constitute an MAC, making this condition practically unenforceable.
- **Recommendation**: Replace with specific quantitative thresholds (e.g., revenue decline
  exceeding 15% over trailing twelve months).

## Major Findings (3)

### [M-001] Dead Clause Detection (Deletion)
- **Location**: Section 12.7 (Non-Solicitation)
- **Finding**: Deletion mutation removed Section 12.7 entirely. No other clause references it,
  no penalty clause applies to its breach, and the non-compete in Section 12.6 already covers
  the same employees. This clause is structurally disconnected.
- **Impact**: The clause exists but has no enforcement mechanism. It provides false confidence.

...

## Summary
| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 3 |
| Minor | 5 |
| **Total Mutations Applied** | **24** |
| **Mutations Survived (undetected)** | **7** |
| **Mutation Kill Rate** | **71%** |
```
