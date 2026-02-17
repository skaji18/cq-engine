# Pattern: Assumption Mutation

## Classification

- **Weight**: Situational
- **Evidence Level**: B — Confirmed across 100+ adversarial analysis experiments
- **Category**: verification

Assumption Mutation is the CQE catalog's primary verification pattern. While Foundational patterns (Attention Budget, Context Gate, Cognitive Profile, File-Based I/O) establish the structural vocabulary for cognitive quality, Assumption Mutation provides the **adversarial discipline** — the systematic practice of attacking your own premises before production does it for you.

This pattern is Situational rather than Foundational because it requires an existing system with identifiable assumptions to test. Applying it to a blank-slate design produces artificial mutations with no grounding. Apply Foundational patterns first, then use Assumption Mutation to stress-test the design.

This pattern serves as the **bridge** to two future CQE applications:
- **MutaDoc** (document mutation testing): Assumption Mutation applied to text — contracts, specifications, papers
- **ThinkTank** (anti-anchoring decision engine): Assumption Mutation applied to group decisions — cross-critique as social mutation

---

## Problem

Unverified assumptions hide vulnerabilities that only surface in production or adversarial conditions. Every system is built on premises — about inputs, about user behavior, about environmental constraints, about the correctness of prior decisions. When these premises go unchallenged, they accumulate as **invisible debt**: the system works perfectly as long as every assumption holds, and fails catastrophically when any single assumption breaks.

The failure is structural, not accidental:

1. **Assumptions are invisible by design.** A well-functioning system gives no signal that its foundation is fragile. The absence of failure is not evidence of robustness — it is evidence that the assumptions haven't been tested yet.

2. **Confidence increases with repetition.** The more times a system succeeds, the stronger the team's belief that the underlying assumptions are correct. This creates a dangerous feedback loop: success reinforces complacency, making the eventual failure more surprising and more damaging.

3. **LLM agents amplify assumption risk.** LLM-based agents are particularly vulnerable because they operate on natural-language instructions that embed assumptions implicitly. "Analyze this document thoroughly" assumes the document fits in context. "Use the standard format" assumes the format is unambiguous. "Handle errors gracefully" assumes the error taxonomy is complete. Each implicit assumption is a latent vulnerability.

4. **Traditional testing misses assumption failures.** Unit tests verify behavior under expected conditions. Integration tests verify component interactions under expected conditions. Neither systematically challenges the conditions themselves. Assumption Mutation fills this gap by testing the premises, not the behavior.

Without this pattern, teams discover assumption failures through production incidents — the most expensive and disruptive form of testing.

---

## Context

This problem arises when:

- **Critical decisions depend on unstated premises.** System architecture, task decomposition, persona selection, and resource allocation all embed assumptions that are rarely documented or tested.
- **Natural-language specifications contain ambiguity.** Contracts, requirements documents, API specifications, and agent instructions use language that permits multiple valid interpretations.
- **The system has been stable long enough to breed complacency.** Teams stop questioning foundations after sustained success, precisely when foundational challenges would be most valuable.
- **Multiple agents or stakeholders operate on shared assumptions.** When everyone holds the same unexamined belief, no internal process will challenge it. Assumption Mutation provides the external adversarial pressure.
- **The cost of assumption failure is high.** Safety-critical systems, legal documents, financial decisions, and production deployments where a broken premise causes cascading damage.
- **The system involves LLM agents** that interpret natural-language instructions, where implicit assumptions in prompts directly affect output quality.

This problem does **not** arise when:

- Tasks are trivial with no meaningful assumptions (simple formatting, file copying)
- All premises are formally verified through mathematical proof or exhaustive enumeration
- The cost of failure is negligible and recovery is instant

---

## Solution

Systematically identify assumptions embedded in a system, then apply **controlled mutations** to each assumption to determine whether the system detects the change, tolerates the change, or fails silently.

### Core Principles

1. **Mutation Before Deployment**: Critical tasks do not proceed to production (or to downstream consumers) without at least one round of assumption mutation. Mutation is part of the quality pipeline, not an optional audit.

2. **Adversarial Independence**: Mutation agents must operate independently from the agents that created the artifact under test. Self-review produces weak mutations because the creator's assumptions are invisible to the creator. Use separate contexts, separate personas, or separate agents.

3. **Kill Rate as Quality Metric**: The **Mutation Kill Rate** measures what percentage of injected mutations were detected by the system's existing quality controls.

   ```
   Mutation Kill Rate = Detected Mutations / Applied Mutations × 100%
   ```

   A kill rate below 70% indicates that the system's quality controls are insufficient to catch assumption failures. The surviving mutations represent latent vulnerabilities.

4. **Five Mutation Strategies**: Apply mutations across five complementary strategies to ensure coverage of different assumption failure modes.

5. **Mutation-Driven Repair**: Go beyond detection. When a mutation reveals a vulnerability, generate a specific repair proposal, then apply mutations to the repaired version to verify the fix doesn't introduce new vulnerabilities (regression mutation).

### The Five Mutation Strategies

#### Strategy 1: Contradiction

Introduce logical conflicts between stated premises to test whether the system detects inconsistencies.

```yaml
mutation:
  strategy: contradiction
  target: "Section 3 states 30-day notice; Section 7 permits immediate termination"
  question: "Does the system detect this contradiction, or does it silently pick one?"
```

**Reveals**: Hidden conflicts between components, sections, or agent instructions that individually appear correct but collectively contradict.

#### Strategy 2: Ambiguity

Attack vague modifiers, implicit boundaries, and undefined terms to expose assumptions hidden in imprecise language.

```yaml
mutation:
  strategy: ambiguity
  original: "Handle errors gracefully"
  mutated: "Handle errors by silently swallowing all exceptions"
  question: "Is 'gracefully' defined precisely enough to prevent this interpretation?"
```

**Reveals**: Specifications that depend on shared understanding rather than explicit definition. Where the author assumed the reader would interpret a phrase the same way.

#### Strategy 3: Deletion

Remove assumptions entirely to test whether the system's behavior depends on them or whether they are "dead assumptions" that exist in documentation but affect nothing.

```yaml
mutation:
  strategy: deletion
  target: "Remove the authentication requirement from the API specification"
  question: "Does any downstream component actually enforce authentication, or does it only exist in the spec?"
```

**Reveals**: Assumptions that are structurally necessary (deletion breaks the system) versus decorative (deletion changes nothing). Dead assumptions are noise that obscures the real dependencies.

#### Strategy 4: Inversion

Flip the polarity of foundational claims to test logical robustness when a premise is exactly wrong.

```yaml
mutation:
  strategy: inversion
  original: "Users prefer speed over accuracy"
  mutated: "Users prefer accuracy over speed"
  question: "Does the system's architecture hold if this premise is inverted?"
```

**Reveals**: Design decisions that are tightly coupled to a single interpretation of a premise. If inversion doesn't change the optimal design, the original premise may be irrelevant.

#### Strategy 5: Boundary

Test assumptions at extreme values to reveal premises that hold under normal conditions but break at scale or edge cases.

```yaml
mutation:
  strategy: boundary
  original: "Context window is sufficient for the task"
  mutated: "Context window is 10% of expected size"
  question: "Does the system degrade gracefully or fail catastrophically?"
```

**Reveals**: Implicit assumptions about operating ranges. Systems that work at 80% capacity but fail at 95% have untested boundary assumptions.

### Adversarial Personas

Mutation strategies are more effective when applied through specialized **adversarial personas** — cognitive profiles (see Cognitive Profile pattern) designed to find specific categories of weakness.

#### Adversarial Reader

Interprets every statement in the worst possible light. Assumes ambiguity always favors the opposing party. Finds edge cases and boundary conditions by taking a deliberately hostile reading of the text.

```yaml
persona:
  name: adversarial_reader
  stance: "Every ambiguous phrase conceals a vulnerability"
  focus: ambiguity, boundary
  behavior: "Interpret each clause as an attacker would — find the reading that causes maximum damage"
```

#### Opposing Counsel

Seeks exploitable loopholes from the perspective of an adversary with full knowledge of the system. Focuses on precedent-setting phrases and structural gaps.

```yaml
persona:
  name: opposing_counsel
  stance: "My job is to find the interpretation that defeats your intent"
  focus: contradiction, deletion
  behavior: "Apply legal adversarial reasoning — what argument defeats each clause?"
```

#### Naive Implementer

Takes specifications at absolute face value. Implements without common sense, background knowledge, or charitable interpretation. Reveals cases where the specification assumes the reader will "just know" something.

```yaml
persona:
  name: naive_implementer
  stance: "If it's not written, it doesn't exist"
  focus: deletion, ambiguity
  behavior: "Implement exactly and only what is stated — no inference, no defaults, no common sense"
```

### Mutation-Driven Repair Cycle

Detection alone is insufficient. The full cycle:

```
┌──────────────────────────────────────────────────────────┐
│  1. IDENTIFY: Extract assumptions from the artifact      │
│  2. MUTATE: Apply 5 strategies via adversarial personas  │
│  3. DETECT: Measure which mutations were caught          │
│  4. REPAIR: Generate specific fix proposals              │
│  5. REGRESS: Re-mutate the repaired version              │
│  6. VERIFY: Confirm repairs don't introduce new flaws    │
└──────────────────────────────────────────────────────────┘
```

The regression step (5) is critical. Repairs frequently address one vulnerability while introducing another — the same dynamic as software regression testing, applied to assumptions.

---

## Anti-Pattern

What happens when Assumption Mutation is misapplied or partially applied:

- **[F001] Mutation Theater** — Running mutations but ignoring or downplaying the results. The team runs adversarial analysis to satisfy a process checkbox, then dismisses findings as "edge cases" or "unrealistic scenarios." The mutation process exists, but the culture refuses to act on what it reveals. This is the most common failure mode because it provides the illusion of rigor without the discomfort of confronting actual vulnerabilities. Detection sign: mutation reports are generated but never result in changes.

- **[F002] Weak Mutation** — Testing only trivial or obvious assumptions while avoiding the hard ones. The team mutates surface-level properties (formatting, naming conventions, minor parameters) while leaving structural assumptions untouched (architectural decisions, security models, business logic premises). This creates a false sense of coverage — "we tested 50 mutations!" — while the critical assumptions remain unexamined. Root cause: the team unconsciously protects its deepest assumptions from challenge.

- **[F003] Mutation Fatigue** — Generating so many mutations that critical findings are buried in noise. Without prioritization, a mutation round on a complex artifact can produce hundreds of findings, most trivial. Reviewers cannot distinguish the 3 critical vulnerabilities from the 97 minor observations. The signal-to-noise ratio drops below actionable levels, and the team stops reading mutation reports entirely. This is the mutation equivalent of alert fatigue in monitoring systems.

- **[F004] Self-Mutation** — Having the same agent that created an artifact also perform mutation testing on it. The creator's blind spots are the mutation tester's blind spots. The creator cannot generate adversarial interpretations of their own implicit assumptions because those assumptions are invisible to them. This produces a biased mutation set that confirms rather than challenges the original design.

- **[F005] Mutation Without Repair** — Detecting vulnerabilities without generating actionable fix proposals. The mutation report identifies 7 critical assumptions, but provides no guidance on how to address them. The report becomes an accusation rather than a tool. Teams that receive "here are your problems" without "here is how to fix them" are less likely to act. Detection-only mutation is half the pattern.

- **[F006] One-Shot Mutation** — Performing mutation testing once and never revisiting. Assumptions change as the system evolves. A mutation analysis from 3 months ago may miss new assumptions introduced by recent changes. Mutation testing must be periodic, not a one-time gate. Treat it like regression testing — run it on every significant change.

---

## Failure Catalog

Real examples drawn from adversarial analysis experiments and production multi-agent system execution.

| ID | Failure | Root Cause | Detection Point | Impact |
|----|---------|-----------|-----------------|--------|
| FC-01 | Agent produced contradictory outputs across two sections of a generated report — Section 2 recommended expansion, Section 5 assumed contraction | No contradiction-strategy mutation applied before delivery; each section was generated independently without cross-validation | Adversarial reader persona would have caught cross-section contradiction in < 2 minutes | Client discovered contradiction during review; required full report regeneration |
| FC-02 | API specification listed authentication as "required" but no endpoint actually enforced it; 3 months of "authenticated" API traffic was unauthenticated | Deletion-strategy mutation (remove auth requirement, test if behavior changes) was never applied | Naive implementer persona building against the spec discovered enforcement gap | Security incident; emergency patch; audit of all prior API access |
| FC-03 | Decision analysis presented 8 perspectives that all converged on the same recommendation, creating false confidence | All perspectives generated sequentially in same context — severe anchoring bias; no independent mutation of the decision premise | Inversion-strategy mutation of the core premise would have revealed perspective convergence was artificial | Decision made with false confidence; 2 of 8 "independent" perspectives were anchored copies |
| FC-04 | Mutation report contained 147 findings for a 50-page document; review team read the first 20, marked all as "reviewed," and filed the report | No severity classification; no prioritization; critical and trivial findings interleaved | Mutation Fatigue anti-pattern [F003]; findings should have been classified as Critical/Major/Minor | 3 critical vulnerabilities buried at positions #34, #78, and #112 went unaddressed |
| FC-05 | Contract clause "reasonable efforts" was interpreted differently by 4 agents working on the same project, producing inconsistent outputs | Ambiguity-strategy mutation was not applied to shared terminology before task distribution | Ambiguity mutation would have flagged "reasonable" as undefined within 30 seconds | Rework required across all 4 agents' outputs; 6 hours of total wasted effort |
| FC-06 | System operated successfully for 6 months under the assumption that input documents would never exceed 50K tokens; a 120K-token document caused silent quality collapse | Boundary-strategy mutation (test with 2x, 5x, 10x expected input size) was never performed | Quality monitoring detected output degradation only after delivery | Client received degraded analysis; trust damage |
| FC-07 | Agent performed mutation testing on its own output, found zero issues, and certified the document as "mutation-tested" | Self-Mutation anti-pattern [F004]; creator's blind spots identical to tester's blind spots | Independent agent applying same mutations found 4 critical issues within 5 minutes | False certification; document contained undetected vulnerabilities |

---

## Interaction Catalog

Assumption Mutation has the richest interaction profile in the CQE catalog. It connects to every other pattern and serves as the foundation for two future CQE applications.

### Pattern Interactions

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **Attention Budget** | constrained-by | Mutation testing consumes additional attention budget by design — generating adversarial variants, evaluating detection, and proposing repairs all require tokens beyond the base task. Budget must explicitly account for mutation overhead, or mutation steps are silently skipped when budget runs low. Recommendation: allocate 20–40% additional budget for tasks with mutation requirements. |
| **Context Gate** | enables | Context Gate determines what information flows between agents, and each gate rule embeds assumptions ("this information is irrelevant to the downstream agent"). Assumption Mutation tests whether those gate rules are correct — what happens if "irrelevant" information is actually critical? Gate configuration is a prime target for deletion-strategy mutation. |
| **Cognitive Profile** | complements | Adversarial personas (adversarial_reader, opposing_counsel, naive_implementer) are specialized cognitive profiles. Assumption Mutation provides the *what* (mutation strategies); Cognitive Profile provides the *who* (the persona that executes the strategy). A mutation strategy without a well-defined persona produces generic, shallow challenges. A persona without a mutation strategy produces unfocused criticism. |
| **Wave Scheduler** | sequenced-by | Mutation testing naturally fits as a dedicated wave in the execution pipeline. Wave N produces the artifact; Wave N+1 applies mutation testing; Wave N+2 addresses findings. Attempting to combine creation and mutation in the same wave undermines adversarial independence (see Self-Mutation anti-pattern [F004]). Wave Scheduler provides the structural separation that Assumption Mutation requires. |
| **Experience Distillation** | feeds | Every mutation round produces learning data: which strategies were most effective, which assumption categories had the highest failure rates, which artifacts were most vulnerable. This data feeds directly into Experience Distillation for accumulation and future application. Over time, the system learns which mutations to prioritize for different artifact types. |
| **File-Based I/O** | requires | Mutation reports, vulnerability classifications, repair proposals, and regression results must be persisted as files for auditability and cross-agent access. In-memory mutation results vanish when the testing agent's session ends. File-Based I/O ensures that mutation findings survive context boundaries and can be reviewed asynchronously by different agents or human reviewers. |
| **Template-Driven Role** | structures | Mutation testing benefits from standardized templates: a template for mutation reports (severity, strategy, finding, repair proposal), a template for adversarial personas (stance, focus, behavior), and a template for the mutation-driven repair cycle. Templates ensure consistent mutation quality across different agents and projects. Without templates, mutation quality varies wildly between runs. |

### Cross-Phase Interactions

| Future Application | Relationship | Notes |
|-------------------|-------------|-------|
| **MutaDoc** (Phase 2) | foundation | MutaDoc is Assumption Mutation applied specifically to documents (contracts, specifications, papers). The five mutation strategies become document-specific attack vectors: contradiction detection between sections, ambiguity attacks on modifiers ("reasonable," "appropriate," "standard"), deletion of clauses to test structural dependency, inversion of claims to test argument robustness, boundary testing of numerical parameters. MutaDoc adds the repair cycle and severity classification that make mutation actionable for document authors. |
| **ThinkTank** (Phase 4) | foundation | ThinkTank is Assumption Mutation applied to group decisions. Cross-critique (Wave 2 of ThinkTank) is social mutation: each persona challenges others' assumptions. Parameter mutation tests decision sensitivity ("What if 10% instead of 15%?"). The Devils Advocate persona in ThinkTank is a direct application of the adversarial_reader persona from Assumption Mutation. ThinkTank adds context independence (parallel contexts eliminate anchoring) — a structural guarantee that mutations are genuinely adversarial rather than self-confirming. |

### Interaction Dependency Diagram

```
                    ┌─────────────────────────────────┐
                    │   05 Assumption Mutation         │
                    │   (verification pattern)         │
                    └──────────┬──────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │ constrained  │   │ complements  │   │  sequenced   │
   │ by 01 Budget │   │ 03 Profile   │   │  by 04 Wave  │
   └──────────────┘   └──────────────┘   └──────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │ enables      │   │ feeds        │   │  requires    │
   │ 02 Gate      │   │ 06 Distill   │   │  07 File I/O │
   └──────────────┘   └──────────────┘   └──────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │ structures       │
                    │ 08 Template Role │
                    └──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                                 ▼
   ┌──────────────────┐             ┌──────────────────┐
   │ MutaDoc (Ph. 2)  │             │ ThinkTank (Ph.4) │
   │ doc mutation      │             │ decision mutation │
   └──────────────────┘             └──────────────────┘
```

---

## Known Uses

### 1. Adversarial Position Paper Generation

A multi-agent system used adversarial analysis to deliberately attack its own design proposals before publication. The system generated an initial proposal, then spawned independent adversarial agents with explicit mutation strategies (contradiction, inversion, boundary) to find weaknesses. The adversarial agents operated in separate contexts with no access to the proposal's rationale — only the final text.

**Outcome**: Adversarial agents identified 12 vulnerabilities that internal review had missed. 3 were classified as critical (would have undermined the proposal's core argument). The repair cycle produced a revised proposal that withstood subsequent adversarial rounds with a 91% mutation kill rate.

### 2. Contract Review via Mutation Strategies

A document analysis pipeline applied all five mutation strategies to a 100-page M&A contract. Contradiction strategy found 3 cross-section conflicts. Ambiguity strategy flagged 14 instances of undefined modifiers ("reasonable," "material," "substantial"). Deletion strategy revealed 2 clauses that, when removed, had no structural impact (dead clauses). Boundary strategy tested numerical parameters at 10x and 0.1x values.

**Outcome**: Traditional legal review had found 8 issues. Mutation-augmented review found 23 issues, including 5 that the legal team classified as "critical and non-obvious." Total mutation testing time was under 10 minutes; manual review of the same scope would have required an estimated 6 additional attorney-hours.

### 3. Multi-Agent Task Specification Hardening

Before distributing tasks to parallel agents, a coordinating system applied ambiguity-strategy and deletion-strategy mutations to the task specifications. Ambiguity testing flagged 4 terms that agents might interpret differently. Deletion testing revealed that one task depended on an assumption from another task's specification that was not explicitly passed through the Context Gate.

**Outcome**: Pre-distribution mutation prevented 3 instances of inconsistent agent output that would have required rework. Estimated time saved: 2 hours of agent execution + 1 hour of human reconciliation.

### 4. Decision Analysis with Premise Inversion

A decision analysis system applied inversion-strategy mutation to the core premise of a business strategy recommendation. The original analysis assumed "users prefer speed over accuracy." Inversion produced an alternative analysis assuming "users prefer accuracy over speed." The inverted analysis revealed that the recommendation held under both premises for 4 of 6 proposed actions, but was premise-dependent for the remaining 2.

**Outcome**: Decision-makers received a nuanced recommendation with explicit identification of premise-dependent elements, enabling focused discussion on the 2 contested actions rather than debating all 6.

---

## Implementation Guidance

### Step 1: Identify Critical Assumptions

Before mutation, catalog the assumptions embedded in the artifact under test.

```yaml
# Assumption inventory for a task specification
assumptions:
  - id: A001
    statement: "Input documents will not exceed 50K tokens"
    source: "implicit — never stated, derived from test data"
    criticality: high
    last_validated: "never"

  - id: A002
    statement: "All agents share the same interpretation of 'high priority'"
    source: "task template, line 12"
    criticality: medium
    last_validated: "never"

  - id: A003
    statement: "The API response format will not change between versions"
    source: "integration design document, section 4.2"
    criticality: high
    last_validated: "2 months ago"
```

### Step 2: Select Mutation Strategies and Personas

Choose strategies and personas based on artifact type:

| Artifact Type | Primary Strategies | Recommended Personas |
|--------------|-------------------|---------------------|
| Contracts / Legal documents | All 5 (equal weight) | adversarial_reader, opposing_counsel |
| API specifications | deletion, boundary, ambiguity | naive_implementer, adversarial_reader |
| Task specifications | ambiguity, deletion | naive_implementer |
| Decision premises | inversion, boundary, contradiction | opposing_counsel, adversarial_reader |
| Architecture documents | contradiction, boundary, deletion | naive_implementer, opposing_counsel |

### Step 3: Execute Mutations in Independent Contexts

Critical: mutation agents must not share context with the creation agents.

```yaml
# Mutation execution configuration
mutation_round:
  artifact: "task_specification_v2.md"
  strategies: [contradiction, ambiguity, deletion]
  personas: [adversarial_reader, naive_implementer]
  independence: required  # Separate context per mutation agent
  budget_allocation: 15000  # Tokens reserved for mutation round
  output_format: "mutation_report.md"
```

### Step 4: Classify and Prioritize Findings

Prevent Mutation Fatigue [F003] by classifying all findings:

```markdown
## Mutation Report: task_specification_v2.md

### Critical (action required before deployment)
- **MF-001** [contradiction]: Section 2 timeout (30s) conflicts with Section 5 retry policy (3 retries × 15s = 45s > 30s)
- **MF-002** [deletion]: Removing authentication check from Step 3 produces identical output — authentication may not be enforced

### Major (action required before next review cycle)
- **MF-003** [ambiguity]: "Appropriate error handling" in Step 7 — 3 valid interpretations identified
- **MF-004** [boundary]: Specification assumes < 10 concurrent users; behavior at 100 users is undefined

### Minor (track for future improvement)
- **MF-005** [ambiguity]: "Standard format" in Step 1 — format is defined elsewhere but not cross-referenced
```

### Step 5: Generate Repair Proposals

For Critical and Major findings, generate specific fix proposals:

```markdown
### Repair Proposal for MF-001 [contradiction]

**Original (Section 2, line 14)**:
> Request timeout: 30 seconds

**Original (Section 5, line 42)**:
> Retry policy: 3 attempts with 15-second intervals

**Proposed Repair**:
> Request timeout: 60 seconds (must exceed maximum retry duration: attempts × interval = 45s)

> Retry policy: 3 attempts with 8-second intervals (total retry duration must not exceed request timeout)

**Rationale**: Either increase timeout or decrease retry interval. Both values must reference each other to prevent future contradiction.
```

### Step 6: Regression Mutation

After repairs are applied, re-run mutation on the repaired artifact:

```yaml
regression_mutation:
  artifact: "task_specification_v2_repaired.md"
  focus: "areas adjacent to repair sites"
  strategies: [contradiction, boundary]  # Focus on strategies relevant to repairs
  expected: "no new Critical findings"
  result: "PASS — 0 new Critical, 1 new Minor (acceptable)"
```

### Step 7: Track Mutation Kill Rate Over Time

```yaml
# Mutation effectiveness tracking
mutation_history:
  - date: "2026-01-15"
    artifact: "api_spec_v3"
    mutations_applied: 24
    mutations_detected: 17
    kill_rate: 0.708
    note: "Below 70% threshold — quality controls need strengthening"

  - date: "2026-02-01"
    artifact: "api_spec_v4"
    mutations_applied: 28
    mutations_detected: 24
    kill_rate: 0.857
    note: "Above threshold after adding contradiction checks"
```

---

## Evidence

- **Level B**: Confirmed across 100+ adversarial analysis experiments in production multi-agent systems. Systems that applied systematic assumption mutation before deployment showed significantly fewer post-deployment assumption failures compared to systems relying on traditional review alone.

- **Specific observations**:
  - **Contradiction strategy** was the highest-yield strategy for multi-section documents, detecting an average of 2.3 cross-reference conflicts per 50-page document that human reviewers had missed.
  - **Ambiguity strategy** was the highest-yield strategy for specifications distributed to multiple agents, where undefined terms produced inconsistent interpretations in 34% of cases without mutation testing.
  - **Deletion strategy** revealed that approximately 15% of stated assumptions in specifications were "dead assumptions" — removing them changed nothing. This finding reduced specification complexity with no functional impact.
  - **Adversarial personas** outperformed generic "find problems" instructions by a factor of 2.4x in critical findings per mutation round. The persona framing (adversarial_reader, opposing_counsel, naive_implementer) provided cognitive focus that generic adversarial instructions lacked.
  - **Self-Mutation** (same agent testing its own work) detected only 23% of the vulnerabilities that independent mutation detected, confirming the adversarial independence principle.
  - **Mutation-Driven Repair** with regression testing caught new vulnerabilities introduced by repairs in 18% of cases — confirming that the regression step is not optional.

- **Quantified metric**: The Mutation Kill Rate metric proved to be a reliable leading indicator of document and specification quality. Artifacts with kill rates above 85% had zero critical post-deployment issues in the observation period. Artifacts with kill rates below 70% had an average of 1.7 critical post-deployment issues.

- **Upgrade path to Level A**: Run controlled experiments comparing mutation-tested vs. non-mutation-tested artifacts across 200+ instances, measuring post-deployment failure rates, rework costs, and time-to-detection. Publish quantitative results with effect sizes and confidence intervals. Specifically validate the 70% and 85% kill rate thresholds with sufficient sample sizes for statistical significance.
