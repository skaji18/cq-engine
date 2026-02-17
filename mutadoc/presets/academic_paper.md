---
preset:
  name: academic_paper
  description: "Research papers (pre-submission review, peer review preparation)"
  strategies:
    contradiction: { weight: 0.7, enabled: true }
    ambiguity: { weight: 0.9, enabled: true }
    deletion: { weight: 0.5, enabled: true }
    inversion: { weight: 1.0, enabled: true }
    boundary: { weight: 0.8, enabled: true }
  default_persona: adversarial_reader
  severity_overrides:
    unsupported_claim: Critical
    methodology_gap: Critical
    circular_reasoning: Critical
    overgeneralization: Major
    missing_limitation: Major
    uncited_claim: Major
  domain_terminology:
    - hypothesis
    - methodology
    - p-value
    - control group
    - statistical significance
    - confidence interval
    - effect size
    - reproducibility
    - confounding variable
    - external validity
    - internal validity
    - literature review
    - null hypothesis
    - sample size
    - regression
  output_format: full_report
---

# Preset: Academic Paper

Mutation testing configuration for research papers and academic manuscripts. Designed to strengthen papers before submission by finding logical gaps, unsupported claims, and methodological weaknesses that peer reviewers would flag.

## Target Document Types

- **Research papers**: Empirical studies, theoretical papers, survey papers
- **Conference submissions**: Full papers, short papers, workshop papers
- **Thesis chapters**: Individual chapters or complete theses
- **Grant proposals**: Research methodology sections
- **Technical reports**: Research group internal reports

## Strategy Configuration

### Inversion (weight: 1.0)

Highest priority for academic papers. The strength of a paper is measured by how well its claims withstand reversal — if inverting a conclusion doesn't invalidate the methodology, the evidence is weak.

**What it does**: Reverses claims, hypotheses, and conclusions to test logical robustness.

**Academic-specific mutations**:
- Invert the main hypothesis — does the methodology still support the inverted claim?
- Reverse cause-and-effect relationships — is the causal direction actually established?
- Negate key results ("significant" → "not significant") — does the Discussion section still make sense?
- Invert comparison direction ("A outperforms B" → "B outperforms A") — does the data presentation unambiguously support the stated direction?

### Ambiguity (weight: 0.9)

Very high priority. Academic papers require precision — ambiguous claims cannot be reproduced, verified, or compared across studies.

**What it does**: Identifies vague, imprecise, or multiply-interpretable statements.

**Academic-specific mutations**:
- Replace "significant improvement" with specific percentages to test if quantitative data supports the qualifier
- Replace "several studies" with "2 studies" or "47 studies" to test if the scope is defined
- Test whether "our approach" is sufficiently described for reproduction
- Replace "reasonable assumptions" with specific assumptions to test if they are enumerated

### Boundary (weight: 0.8)

High priority. Tests whether reported results are robust to parameter variations and whether limitations are honestly acknowledged.

**What it does**: Pushes experimental parameters, thresholds, and assumptions to extremes.

**Academic-specific mutations**:
- p-value threshold: What if the threshold was 0.01 instead of 0.05? Do results still hold?
- Sample size: What if N was halved? Is the study still powered?
- Effect size: What if the measured effect was 50% smaller? Is it still practically significant?
- Test hyperparameter sensitivity by varying tuning parameters in reported ranges

### Contradiction (weight: 0.7)

Above moderate priority. Internal contradictions in a paper are reviewer red flags that trigger skepticism about the entire manuscript.

**What it does**: Identifies inconsistencies between sections, figures, and claims.

**Academic-specific mutations**:
- Cross-check Abstract claims against Results section — do they match exactly?
- Cross-check tables/figures against in-text descriptions — are numbers consistent?
- Cross-check Methodology against Results — does every described method produce a reported result?
- Check Literature Review claims against cited papers — do the citations actually support the stated claims?

### Deletion (weight: 0.5)

Moderate priority. Less critical for academic papers than for contracts, but useful for identifying redundant or disconnected sections.

**What it does**: Removes individual sections, paragraphs, or claims and measures impact.

**Academic-specific mutations**:
- Delete each paragraph in Related Work — does the remaining text still provide sufficient context?
- Delete a baseline comparison — does the paper's contribution claim still hold without it?
- Delete the limitations section — are limitations mentioned elsewhere, or only in the dedicated section?

## Default Persona Rationale

**Adversarial Reader** (`adversarial_reader`) is the default persona because:

1. Peer reviewers are adversarial by design — their job is to find flaws, not confirm quality
2. Reviewer 2 (the notoriously harsh reviewer) is the standard every paper must survive
3. An adversarial reader focuses on logical gaps and unsupported claims, which are the top reasons for rejection
4. This persona catches the "this is obvious to us but not to a skeptical outsider" blindspot

Alternative personas for specific use cases:
- `naive_implementer`: For testing reproducibility — can someone replicate this from the paper alone?
- `opposing_counsel`: For papers with policy implications where legal precision matters

## Severity Overrides Explanation

| Override | Default → Override | Rationale |
|----------|-------------------|-----------|
| `unsupported_claim` | Major → **Critical** | A claim without supporting evidence is the #1 reason papers are rejected. It signals sloppy or dishonest scholarship. |
| `methodology_gap` | Major → **Critical** | Incomplete methodology prevents reproduction. Reviewers will reject on this alone, and it damages the field by introducing unreproducible results. |
| `circular_reasoning` | Major → **Critical** | Using the conclusion as a premise invalidates the entire argument chain. This is a fatal logical flaw. |
| `overgeneralization` | Minor → **Major** | Claiming results generalize beyond what the evidence supports is a common reviewer complaint. It undermines trust in the specific results too. |
| `missing_limitation` | Minor → **Major** | Reviewers expect honest limitation acknowledgment. Missing limitations suggest the authors don't understand their own work's boundaries. |
| `uncited_claim` | Minor → **Major** | Factual claims without citations are either plagiarism or unsupported assertions. Both are serious in academic writing. |

## Domain Terminology

| Term | Academic Meaning | Mutation Relevance |
|------|-----------------|-------------------|
| **Hypothesis** | Testable prediction derived from theory | Inversion target — inverting the hypothesis tests the strength of evidence |
| **p-value** | Probability of observing results under the null hypothesis | Boundary target — test sensitivity to threshold choice |
| **Control group** | Baseline comparison condition | Deletion target — what happens if the control is removed from analysis? |
| **Effect size** | Magnitude of the observed phenomenon | Boundary target — is the effect practically significant or just statistically significant? |
| **Confidence interval** | Range of plausible values for a parameter | Boundary target — do CIs overlap between conditions? |
| **Reproducibility** | Ability to replicate results from the paper | Ambiguity target — is the method described precisely enough? |
| **Confounding variable** | Uncontrolled variable that may explain results | Inversion target — could the confound explain the result instead? |
| **External validity** | Generalizability of results beyond the study | Boundary target — how far do the results generalize? |

## Usage Examples

```bash
# Pre-submission review of a research paper
mutadoc test paper_draft.md --preset academic_paper

# Focus on logical robustness (inversion testing)
mutadoc test methodology_section.md --preset academic_paper --strategies inversion

# Reproducibility check with naive implementer
mutadoc test paper.md --preset academic_paper --persona naive_implementer

# Quick pre-submission check (Critical only)
mutadoc test camera_ready.md --preset academic_paper --min-severity critical

# Test a specific section
mutadoc test results_section.md --preset academic_paper --strategies inversion,boundary
```

## Sample Output

```markdown
# MutaDoc Report: neural_pruning_paper.md
**Preset**: academic_paper | **Persona**: adversarial_reader | **Score**: 58/100

## Critical Findings (3)

### [C-001] Unsupported Generalization (Inversion)
- **Location**: Abstract, line 3
- **Finding**: The abstract claims "Our method generalizes to any transformer architecture"
  but experiments are conducted only on BERT-base and GPT-2-small. Inverting this claim to
  "Our method may not generalize beyond BERT-base and GPT-2-small" is equally supported by
  the presented evidence.
- **Reviewer Impact**: Reviewer 2 will immediately flag this as overclaiming. The Abstract
  promise exceeds what the Results section delivers.
- **Recommendation**: Replace with "Our method shows consistent results on BERT-base and
  GPT-2-small, suggesting potential applicability to other transformer architectures."

### [C-002] Methodology Gap (Ambiguity)
- **Location**: Section 3.2, Pruning Procedure
- **Finding**: "We prune neurons with activation below a threshold." The threshold value is
  not specified. The selection criterion ("activation") is not defined (mean activation?
  max activation? activation on what data?). A naive implementer cannot reproduce this step.
- **Reviewer Impact**: Any reviewer who attempts mental reproduction will fail at this step
  and question the validity of the entire experimental setup.
- **Recommendation**: Specify: "We compute mean activation magnitude across the validation
  set (N=1000 samples) and prune neurons below the 20th percentile (threshold=0.043)."

### [C-003] Circular Reasoning (Inversion)
- **Location**: Section 5.1, Discussion
- **Finding**: "The success of our pruning method confirms that redundant neurons exist in
  transformer models." This uses the method's results to validate the method's assumption.
  Inverting: "If redundant neurons did not exist, our method would fail" — but the paper
  provides no independent evidence of redundancy.
- **Reviewer Impact**: A careful reviewer will identify this as begging the question.
- **Recommendation**: Provide independent evidence of neuron redundancy (e.g., ablation
  studies, prior work on lottery ticket hypothesis) before claiming confirmation.

## Major Findings (4)

### [M-001] Missing Limitation (Deletion)
- **Location**: Section 6, Limitations (absent)
- **Finding**: The paper has no Limitations section. Deletion mutation reveals that known
  limitations (small model scale, English-only data, single hardware configuration) are
  not acknowledged anywhere in the manuscript.
- **Impact**: Reviewers expect intellectual honesty about scope. Missing limitations
  suggests either unawareness or deliberate omission.

...

## Summary
| Severity | Count |
|----------|-------|
| Critical | 3 |
| Major | 4 |
| Minor | 7 |
| **Total Mutations Applied** | **28** |
| **Mutations Survived (undetected)** | **12** |
| **Mutation Kill Rate** | **57%** |
```
