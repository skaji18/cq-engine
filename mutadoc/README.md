# MutaDoc — Document Mutation Testing

> **Version**: 0.1
> **Status**: Phase 2 implementation
> **Principle**: Zero Infrastructure (Bash + Markdown + Claude Code)

---

## Overview

MutaDoc applies **mutation testing** — a technique proven in software engineering — to documents. It intentionally introduces controlled mutations (contradictions, ambiguities, deletions, inversions, boundary violations) into a target document, then analyzes which mutations are "killed" (detected by existing safeguards) and which survive (indicating hidden vulnerabilities).

**What makes MutaDoc different from document review tools:**

- **Grammarly** checks grammar. **MutaDoc breaks your document** to find structural vulnerabilities.
- **ChatGPT review** reads your document. **MutaDoc mutates it** — altering clauses, reversing assumptions, deleting sections — and measures what breaks.
- **Turnitin** detects plagiarism. **MutaDoc detects fragility** — the difference between a document that looks correct and one that actually is.

The core metric is the **Mutation Kill Score**: the percentage of applied mutations that are detected by the document's internal structure (cross-references, evidence, logical consistency). A document with a 90% kill score is structurally robust; a document with a 40% kill score has significant hidden vulnerabilities.

```
Mutation Kill Score = (killed mutations / total mutations) × 100%
```

MutaDoc also provides **Mutation-Driven Repair** — for each detected vulnerability, it generates a concrete fix suggestion in GitHub PR diff format, with confidence scoring and regression testing. Detect + repair achieves 10x adoption over detect-only tools.

---

## Key Concepts

### Mutation Strategies

5 strategies for systematically breaking documents:

| # | Strategy | What It Does | Exposes |
|---|----------|-------------|---------|
| S1 | [Contradiction](strategies/contradiction.md) | Alters a clause and detects cross-clause conflicts | Hidden contradictions between sections |
| S2 | [Ambiguity](strategies/ambiguity.md) | Replaces vague modifiers with extreme values | Meaningless language ("reasonable", "appropriate") |
| S3 | [Deletion](strategies/deletion.md) | Removes a section and measures structural impact | Dead clauses (zero-impact text) and critical dependencies |
| S4 | [Inversion](strategies/inversion.md) | Reverses assumptions and claims | Unsupported assertions and evidence gaps |
| S5 | [Boundary](strategies/boundary.md) | Mutates numerical parameters to extremes | Fragile parameters with undefined boundaries |

### Adversarial Personas

3 personas that adopt specific adversarial reading postures. Personas are orthogonal to strategies — any persona can be combined with any strategy.

| Persona | Role | Best For |
|---------|------|----------|
| [Adversarial Reader](personas/adversarial_reader.md) | Bad-faith actor seeking exploitable loopholes | Contracts, policies, terms of service |
| [Opposing Counsel](personas/opposing_counsel.md) | Opposing lawyer seeking legal attack vectors | Contracts, SLAs, compliance documents |
| [Naive Implementer](personas/naive_implementer.md) | Developer who implements text literally with zero context | API specs, requirements, technical standards |

### Document Type Presets

Pre-configured profiles that optimize strategy weights, persona selection, and severity thresholds for specific document types:

| Preset | Target Documents | Primary Strategies | Default Persona |
|--------|-----------------|-------------------|-----------------|
| [contract](presets/contract.md) | Legal contracts (M&A, SaaS, employment) | Contradiction, Ambiguity, Deletion | Opposing Counsel |
| [api_spec](presets/api_spec.md) | API/technical specifications (OpenAPI, gRPC) | Contradiction, Boundary, Deletion | Naive Implementer |
| [academic_paper](presets/academic_paper.md) | Research papers (pre-submission review) | Inversion, Ambiguity, Boundary | Adversarial Reader |
| [policy](presets/policy.md) | Government/corporate policy documents | Ambiguity, Contradiction, Boundary | Adversarial Reader |

---

## Quick Start

```bash
# Quick mode — ambiguity scan, results in ~30 seconds
mutadoc quick README.md

# Full analysis with preset
mutadoc test contract.md --preset contract

# Specific strategies only
mutadoc test spec.md --strategies contradiction,boundary

# With specific persona
mutadoc test contract.md --persona opposing_counsel

# Full analysis with repair suggestions
mutadoc test spec.md --preset api_spec --repair

# Full pipeline: detect + repair + regression check
mutadoc test contract.md --preset contract --repair --regression

# Just the Mutation Kill Score
mutadoc score document.md
```

---

## CLI Reference

### Subcommands

| Command | Description |
|---------|-------------|
| `mutadoc test <file>` | Run full mutation analysis on a document |
| `mutadoc quick <file>` | Quick mode — ambiguity scan only, ~30 seconds |
| `mutadoc score <file>` | Calculate and display Mutation Kill Score only |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--preset <name>` | Document type preset (contract, api_spec, academic_paper, policy) | Auto-detect |
| `--strategies <list>` | Comma-separated strategies (contradiction, ambiguity, deletion, inversion, boundary, all) | all |
| `--persona <name>` | Adversarial persona (adversarial_reader, opposing_counsel, naive_implementer) | Preset default |
| `--repair` | Generate repair suggestions for Critical/Major findings | off |
| `--regression` | Run regression mutation on repaired document | off (requires --repair) |
| `--output <file>` | Write report to file instead of stdout | stdout |

### Output Report Structure

```markdown
# MutaDoc Report: contract.md

> Preset: contract | Persona: opposing_counsel
> Mutation Kill Score: 72% (18 killed / 25 applied)
> Generated: 2026-01-15

## Summary
- Critical: 3
- Major: 7
- Minor: 8
- Dead Clauses: 2

## Critical Findings

### [C1] Contradiction: Termination clauses conflict
- **Location**: Section 5.1 vs Section 12.3
- **Strategy**: Contradiction
- **Mutation**: Changed "30 days" to "immediately" in Section 5.1
- **Impact**: Section 12.3 becomes impossible to fulfill
- **Repair Suggestion**: [View Diff]
- **Repair Confidence**: High (auto-applicable)
- **Regression Check**: PASS (no new issues introduced)

...
```

---

## Mutation-Driven Repair

MutaDoc extends beyond detection to provide concrete fix suggestions for every Critical and Major finding. The repair pipeline:

```
Detection (Strategies + Personas)
        │
        ▼
Vulnerability Report
        │
        ▼
Repair Draft Generation (per finding)
        │
        ▼
Regression Mutation (verify repairs are safe)
        │
        ▼
Final Report (auto-applicable + needs-review)
```

Each repair suggestion includes:
- **Diff view** — GitHub PR format showing exact text changes
- **Confidence score** — High / Medium / Low
- **Classification** — Auto-applicable (safe to apply) or Needs-human-review
- **Regression result** — Whether the repair introduces new issues

Target: **30%+ of repair suggestions are directly usable** without modification.

See [repair/README.md](repair/README.md) for the full repair pipeline documentation.

---

## Architecture

```
mutadoc/
├── README.md                          # This file
├── mutadoc.sh                         # Entry point (Bash, zero infrastructure)
├── strategies/
│   ├── contradiction.md               # S1: Cross-clause contradiction detection
│   ├── ambiguity.md                   # S2: Vague modifier exposure
│   ├── deletion.md                    # S3: Structural impact / dead clause detection
│   ├── inversion.md                   # S4: Assumption reversal / robustness testing
│   └── boundary.md                    # S5: Numerical parameter boundary testing
├── personas/
│   ├── adversarial_reader.md          # Bad-faith reader seeking loopholes
│   ├── opposing_counsel.md            # Adversarial lawyer seeking legal attacks
│   └── naive_implementer.md           # Literal interpreter with zero context
├── presets/
│   ├── contract.md                    # Legal contracts
│   ├── api_spec.md                    # API / technical specifications
│   ├── academic_paper.md              # Research papers
│   └── policy.md                      # Policy documents
├── repair/
│   ├── README.md                      # Repair pipeline documentation
│   └── templates/
│       ├── contradiction_repair.md    # Repair: resolve contradictions
│       ├── ambiguity_repair.md        # Repair: replace vague language
│       ├── deletion_repair.md         # Repair: remove/integrate dead clauses
│       ├── inversion_repair.md        # Repair: strengthen weak claims
│       └── boundary_repair.md         # Repair: add explicit bounds
├── test_fixtures/
│   ├── contracts/                     # Test contracts with known issues
│   │   └── sample_contract.md
│   ├── papers/                        # Test papers with known issues
│   │   └── sample_paper.md
│   └── specs/                         # Test specs with known issues
│       └── sample_api_spec.md
└── output/
    └── (generated reports)
```

---

## Relationship to CQE Patterns

MutaDoc is the first **killer application** of Cognitive Quality Engineering (CQE). It is grounded in [Pattern 05: Assumption Mutation](../patterns/05_assumption_mutation.md), which establishes the theoretical foundation for intentionally challenging premises to discover hidden vulnerabilities.

| CQE Pattern | How MutaDoc Uses It |
|-------------|-------------------|
| **05 Assumption Mutation** | Core theoretical foundation — all 5 strategies are specialized forms of assumption mutation applied to documents |
| **01 Attention Budget** | Guides token budget allocation for parallel strategy execution |
| **02 Context Gate** | Isolates each strategy's analysis context to prevent cross-contamination |
| **03 Cognitive Profile** | Shapes adversarial persona definitions for domain-specific reading postures |
| **04 Wave Scheduler** | Structures multi-strategy execution into waves (detect → repair → regress) |
| **07 File-Based I/O** | All inter-stage communication uses structured files (YAML reports, Markdown templates) |
| **08 Template-Driven Role** | Strategy and persona templates ensure consistent, reproducible analysis |

MutaDoc demonstrates that CQE patterns are not abstract theory — they are directly applicable engineering tools that produce real-world applications.
