# Pattern: Cognitive Profile

## Classification

- **Weight**: Foundational
- **Evidence Level**: B — Confirmed across multiple production multi-agent systems
- **Category**: knowledge

Cognitive Profile is a foundational pattern. LLM agents respond strongly to persona framing — a well-defined cognitive profile consistently outperforms a generic "helpful assistant" identity. Apply this pattern alongside Attention Budget and Context Gate when designing any multi-agent system.

---

## Problem

Generic agents ("you are a helpful assistant") underperform specialized ones because LLMs are persona-sensitive: the behavioral framing in the system prompt materially shapes output quality, style, and reasoning depth. Most multi-agent systems either ignore persona design entirely or apply it superficially (a name and a one-line description), leaving significant quality gains on the table.

The failure manifests in three ways:

1. **Homogeneous output quality.** Without differentiated profiles, agents producing code reviews, strategic analysis, and documentation all sound the same. A code reviewer should be skeptical and detail-oriented; a documentation writer should be clear and audience-aware. Generic agents default to a bland middle ground that serves none of these tasks well.

2. **Behavioral inconsistency.** A generic agent's behavior drifts as context changes. It may be thorough in its first task and careless in its fifth, because nothing anchors its behavioral norms. Without a profile, there is no reference point for "what good looks like" for this specific agent.

3. **Wasted specialization opportunity.** LLMs have demonstrated capacity to adopt and maintain complex personas — domain experts, adversarial thinkers, meticulous auditors. A system that fails to leverage this capacity through deliberate profile design is underutilizing its most flexible resource.

The root cause is treating agent identity as decoration rather than engineering. Profile design is not role-playing — it is a systematic technique for shaping LLM output quality through behavioral specification.

---

## Context

This problem arises when:

- A system runs **multiple agents with distinct responsibilities** (code review vs. documentation vs. testing), but all agents receive the same generic prompt framing.
- **Output quality varies unpredictably** across tasks of similar complexity, because agent behavior is unanchored.
- The system requires **adversarial or specialized reasoning** (security audits, devil's advocate analysis, compliance checks) that generic agents handle poorly.
- **Multi-perspective analysis** is needed — multiple agents analyze the same input from different angles, but without distinct profiles their perspectives converge rather than diverge.
- Agents interact with **domain-specific knowledge** (legal, financial, medical) where domain framing materially affects reasoning quality.

This problem does **not** arise when:

- The system has a single agent performing a single, well-defined task
- All tasks are homogeneous and require the same cognitive approach
- The system operates in a single-turn, one-shot mode where persona framing has minimal effect

---

## Solution

Define each agent's cognitive identity through a structured profile that specifies not just what the agent does, but how it thinks, what it prioritizes, and what failure modes it should avoid.

### Core Principles

1. **Profile as Behavioral Specification**: A profile is not a character description — it is a behavioral specification. Every element should be testable: "Was the agent's output consistent with its profile?"

2. **Cognitive Traits over Role Names**: A role name ("Senior Code Reviewer") is necessary but insufficient. The profile must specify cognitive traits: attention to detail, skepticism level, verbosity tolerance, domain expertise depth, and reasoning style.

3. **Anti-Pattern Awareness**: Each profile should include explicit failure modes to avoid. A code reviewer's profile should warn against rubber-stamping. An analyst's profile should warn against anchoring to the first data point.

4. **Profile-Task Alignment**: Different tasks demand different cognitive approaches. Match profiles to task types systematically rather than assigning tasks to whichever agent is available.

5. **Profile Stability**: Once assigned, a profile persists for the duration of a task or session. Profile switching mid-task degrades consistency. If a task requires multiple cognitive approaches, use multiple agents with distinct profiles rather than one agent switching profiles.

### Profile Specification Format

```yaml
cognitive_profile:
  identity:
    name: "Security Auditor"
    role: "Identify security vulnerabilities in code and configuration"
    expertise_domains: [application_security, authentication, input_validation]

  cognitive_traits:
    skepticism: high          # Question assumptions aggressively
    detail_orientation: high  # Examine edge cases and boundary conditions
    verbosity: medium         # Report findings concisely but completely
    creativity: medium        # Consider unconventional attack vectors
    risk_tolerance: low       # Flag potential issues even when uncertain

  behavioral_anchors:
    - "Assume all external input is malicious until proven otherwise"
    - "If a security control can be bypassed, it will be"
    - "The absence of a vulnerability is not proof of safety"

  failure_modes_to_avoid:
    - "Rubber-stamping: approving code without deep inspection"
    - "False confidence: stating 'no issues found' without exhaustive check"
    - "Scope creep: reviewing code quality when tasked with security review"

  output_format:
    structure: "findings_list_with_severity"
    required_fields: [vulnerability_type, severity, location, recommendation]
```

### Profile Complexity Levels

| Level | Description | When to Use | Example |
|-------|------------|-------------|---------|
| **Minimal** | Name + role + 3 behavioral anchors | Simple, homogeneous tasks | File formatter, log parser |
| **Standard** | Full trait specification + failure modes | Most production tasks | Code reviewer, documentation writer |
| **Deep** | Standard + domain expertise model + interaction rules | Specialized or adversarial tasks | Security auditor, legal analyst, devil's advocate |

### Profile Library Pattern

Maintain a library of tested profiles that can be instantiated on demand:

```
profiles/
├── engineering/
│   ├── code_reviewer.yaml
│   ├── architecture_analyst.yaml
│   └── test_designer.yaml
├── analysis/
│   ├── strategic_analyst.yaml
│   ├── risk_assessor.yaml
│   └── devils_advocate.yaml
├── domain/
│   ├── legal_reviewer.yaml
│   ├── financial_analyst.yaml
│   └── compliance_auditor.yaml
└── meta/
    ├── synthesizer.yaml          # Integrates outputs from other profiles
    └── quality_checker.yaml      # Validates other agents' outputs
```

Each profile in the library is version-controlled and improvement-tracked. When a profile consistently produces high-quality output, its configuration becomes a reference implementation. When a profile underperforms, the failure is traceable to specific trait settings.

---

## Anti-Pattern

What happens when Cognitive Profile is misapplied or partially applied:

- **[F001] Profile Bloat** — Overloading a single profile with contradictory traits. A profile that demands both "extreme skepticism" and "enthusiastic agreement" produces incoherent behavior. The agent oscillates between contradictory instructions, sometimes within the same output. The root cause is attempting to make one agent serve multiple cognitive roles simultaneously. Each profile should have a coherent, non-contradictory behavioral model.

- **[F002] Profile Drift** — The agent's behavior gradually diverges from its defined profile as context accumulates and the original profile specification is pushed out of the effective attention window. In long sessions, the agent "forgets" its persona and reverts to generic behavior. The symptom is that early outputs match the profile specification but later outputs do not. The fix is periodic profile reinforcement — re-injecting key behavioral anchors at regular intervals, especially after context compaction.

- **[F003] Shallow Profile** — Assigning a profile that consists of only a name and a one-line role description. "You are a Senior Code Reviewer. Review this code." This provides minimal behavioral specification — the LLM fills in the gaps with its default behavior, which may not match the system's requirements. A Shallow Profile is marginally better than no profile at all, but captures only a fraction of the available quality gain.

- **[F004] Profile Cargo Cult** — Copying profile specifications from one domain to another without understanding which traits matter. A profile designed for code review (high skepticism, high detail orientation) is applied verbatim to creative writing tasks, producing outputs that are technically correct but lifeless. Profile design must be task-aware — the same agent framework can host very different cognitive configurations.

- **[F005] Profile Rigidity** — Refusing to update profiles based on execution feedback. A profile that worked well six months ago may no longer be optimal as the LLM model improves, the domain evolves, or task requirements change. Profiles should be treated as living specifications that evolve through operational learning (see Pattern 06: Experience Distillation), not as permanent fixtures.

---

## Failure Catalog

Real examples drawn from production multi-agent system execution history.

| ID | Failure | Root Cause | Detection Point | Impact |
|----|---------|-----------|-----------------|--------|
| FC-01 | Agent assigned "analytical" role produced outputs indistinguishable from a generic assistant | Shallow Profile (F003): profile consisted of only a role name with no behavioral specification | Noticed during output comparison — profiled agent and unprofiled agent produced near-identical results | No quality improvement despite profile investment; team concluded "profiles don't work" |
| FC-02 | Adversarial reviewer agreed with the proposal it was supposed to critique | Profile Drift (F002): 80K tokens into the session, the adversarial anchors had been pushed out of effective attention | Detected when the reviewer's output was compared against its profile — zero adversarial findings in final output | Critical vulnerabilities in the proposal went undetected; discovered only in production |
| FC-03 | Agent configured as both "meticulous auditor" and "fast summarizer" produced inconsistent outputs — some thorough, some superficial | Profile Bloat (F001): contradictory traits (thoroughness vs. speed) caused oscillation | Quality variance analysis showed bimodal distribution — outputs were either very detailed or very shallow, never moderate | Downstream consumers could not rely on consistent output quality |
| FC-04 | Seven specialized agents produced outputs that were stylistically diverse but substantively identical | All profiles specified different names and domains but used the same underlying cognitive traits (all medium skepticism, medium detail, medium creativity) | Cross-agent output analysis revealed >85% content overlap despite distinct role names | Multi-agent system provided no diversity benefit over a single generic agent; resource waste was 7x |

---

## Interaction Catalog

How Cognitive Profile interacts with other CQE patterns.

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **01 Attention Budget** | is informed by | Different cognitive profiles have different budget requirements. An analytical profile performing deep code review needs more context than a formatting profile applying style rules. Budget allocation should be profile-aware — assign larger budgets to profiles with higher cognitive demands. |
| **02 Context Gate** | complements | Context Gate decides what information reaches an agent; Cognitive Profile determines how the agent processes that information. A security auditor profile with a well-configured Context Gate receives only security-relevant code, maximizing the value of both patterns. |
| **04 Wave Scheduler** | interacts with | Profile assignment influences wave composition. A wave should include complementary profiles (analyst + critic + synthesizer), not duplicate profiles. Wave Scheduler uses profile metadata to determine which agents can run in parallel without redundancy. |
| **05 Assumption Mutation** | enables | Adversarial personas are specialized cognitive profiles. Assumption Mutation requires agents with deliberately skeptical, contrarian, or destructive profiles. Without Cognitive Profile, mutation agents default to generic behavior that is insufficiently adversarial. |
| **06 Experience Distillation** | feeds into | Execution history reveals which profiles perform well for which tasks. "The security auditor profile with high skepticism caught 90% of vulnerabilities" is a distillable insight that improves profile selection and refinement. |
| **07 File-Based I/O** | complements | Profile specifications stored as files enable version control, sharing, and audit trails. File-based profiles are inspectable by humans and other agents, unlike profiles embedded in code. |
| **08 Template-Driven Role** | enables | Cognitive Profile defines the *who* (behavioral identity); Template-Driven Role defines the *how* (output structure and quality criteria). A complete agent specification combines both: the profile shapes reasoning, the template shapes output. Without a profile, templates constrain format but not cognitive quality. |

---

## Known Uses

### 1. Production Multi-Agent Development System — Hierarchical Persona Architecture

A production multi-agent system implemented Cognitive Profile through a hierarchical role architecture where each agent received a distinct behavioral specification:

- **Role-specific profiles**: Each agent type (coordinator, reviewer, implementer, auditor) had a dedicated profile file specifying cognitive traits, behavioral anchors, and failure modes to avoid
- **Adversarial profiles**: Dedicated agents with explicitly contrarian profiles performed critique and vulnerability analysis, consistently finding issues that agreeable agents missed
- **Profile persistence**: Profiles were reloaded after context compaction to prevent Profile Drift (F002)
- **Result**: Specialized agents outperformed generic agents on task-specific quality metrics. The gap was most pronounced for adversarial and analytical tasks, where generic agents frequently defaulted to agreeable, surface-level analysis

### 2. Multi-Perspective Decision Analysis System

A decision analysis system used Cognitive Profiles to instantiate independent perspectives:

- **Domain expert profiles**: CFO, CTO, legal counsel, customer advocate — each with domain-specific behavioral anchors
- **Independent execution**: Each profiled agent analyzed the same input in an isolated context, preventing perspective convergence
- **Profile-driven diversity**: Because each profile specified distinct priorities (cost vs. innovation vs. risk vs. user experience), the system produced genuinely diverse analyses rather than paraphrased versions of the same conclusion

### 3. Automated Code Review Pipeline

A code review system used three distinct profiles in sequence:

- **Correctness Reviewer** (high skepticism, high detail): Finds bugs, logic errors, edge cases
- **Security Reviewer** (adversarial mindset, low trust): Assumes malicious input, traces data flow
- **Maintainability Reviewer** (pragmatic, audience-aware): Evaluates readability, naming, documentation

Each profile found categories of issues the others missed, demonstrating that profile specialization provides non-overlapping coverage.

---

## Implementation Guidance

### Step 1: Identify Distinct Cognitive Roles

Audit your system's tasks and identify clusters that require different cognitive approaches:

```yaml
# Task-to-profile mapping analysis
task_clusters:
  - cluster: "Code analysis"
    cognitive_needs: [high_skepticism, detail_oriented, technical_depth]
    candidate_profile: "code_auditor"

  - cluster: "Documentation generation"
    cognitive_needs: [audience_awareness, clarity, structured_output]
    candidate_profile: "technical_writer"

  - cluster: "Strategic analysis"
    cognitive_needs: [multi_perspective, risk_awareness, creativity]
    candidate_profile: "strategic_analyst"
```

### Step 2: Create Minimal Viable Profiles

Start with the Standard level — do not attempt Deep profiles on the first iteration:

```yaml
# profiles/code_auditor.yaml
cognitive_profile:
  identity:
    name: "Code Auditor"
    role: "Identify defects, vulnerabilities, and quality issues in code"

  cognitive_traits:
    skepticism: high
    detail_orientation: high
    verbosity: medium

  behavioral_anchors:
    - "Every function has at least one edge case the author didn't consider"
    - "If a test is missing, the corresponding code is suspect"
    - "Review the error handling paths as carefully as the happy paths"

  failure_modes_to_avoid:
    - "Rubber-stamping: approving without thorough review"
    - "Nitpicking: focusing on style while missing logic errors"
    - "Scope creep: redesigning the architecture when asked to review a bug fix"
```

### Step 3: Implement Profile Injection

Inject the profile at the start of every task. For long-running tasks, reinject at intervals:

```yaml
# Profile injection configuration
profile_injection:
  timing:
    - task_start           # Always inject at task beginning
    - every_n_turns: 10    # Reinject behavioral anchors every 10 turns
    - after_compaction      # Reinject full profile after context compaction

  injection_format: |
    ## Your Cognitive Profile
    You are {name}. Your role: {role}.

    Behavioral anchors (follow these at all times):
    {behavioral_anchors}

    Failure modes to avoid:
    {failure_modes_to_avoid}
```

### Step 4: Measure Profile Effectiveness

Track whether profiled agents outperform unprofiled ones:

```yaml
# Profile effectiveness tracking
metrics:
  - name: "profile_adherence"
    description: "Does the output match the profile's behavioral specification?"
    measurement: "Human rating 1-5 on trait alignment"

  - name: "quality_delta"
    description: "Quality difference between profiled and generic agents"
    measurement: "Compare output quality scores for same task with/without profile"

  - name: "diversity_score"
    description: "How distinct are outputs from differently-profiled agents?"
    measurement: "Semantic similarity between outputs (lower = more diverse)"
```

### Step 5: Iterate Based on Evidence

After 20+ task executions per profile:

1. Identify traits that correlate with high output quality — strengthen them
2. Identify behavioral anchors that are consistently ignored — rephrase or replace
3. Identify failure modes that still occur despite warnings — add more specific examples
4. Retire profiles that show no quality improvement over generic agents

### Integration with CQ Benchmark

Cognitive Profile effectiveness maps to the **Decision Quality** axis of CQ Benchmark:

| Sub-Metric | Measurement |
|-----------|-------------|
| Profile Adherence Rate | `outputs_matching_profile / total_outputs` over rolling window |
| Specialization Benefit | `profiled_quality_score - generic_quality_score` per task type |
| Diversity Index | Cross-agent output similarity when using distinct profiles (lower is better) |

---

## Evidence

- **Level B**: Confirmed across 3 projects in a production multi-agent system. Agents with explicitly defined cognitive profiles showed:
  - Measurably higher output quality on specialized tasks (code review, adversarial analysis, documentation) compared to generic agents
  - Most significant improvement observed in adversarial tasks — generic agents frequently defaulted to agreeable analysis, while profiled agents with high-skepticism traits maintained critical perspective
  - Profile Drift (F002) observed in sessions exceeding 80K tokens — periodic profile reinforcement reduced drift incidents significantly
  - Multi-perspective analysis with distinct profiles produced genuinely diverse outputs (measured by cross-output similarity), while the same analysis with generic agents produced convergent outputs

- **Limitations of current evidence**:
  - No controlled A/B test (Level A) has been conducted with standardized quality metrics
  - "Quality improvement" assessments rely on human judgment, not automated scoring
  - Profile effectiveness may vary significantly with LLM model and task domain

- **Upgrade path to Level A**: Run controlled experiments across 50+ tasks:
  - Control group: generic agents with no cognitive profile
  - Treatment group 1: agents with Shallow Profiles (name + role only)
  - Treatment group 2: agents with Standard Profiles (full trait specification)
  - Measure: output quality (human-rated), task-specific accuracy, cross-output diversity
  - Required sample: 50+ tasks per group for statistical significance
  - This would quantify the marginal value of each profile complexity level
