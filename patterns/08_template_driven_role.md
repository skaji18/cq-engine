# Pattern: Template-Driven Role

## Classification

- **Weight**: Situational
- **Evidence Level**: B
- **Category**: knowledge

**Rationale for Situational weight**: Template-Driven Role is most valuable when a system has multiple agents performing similar functions or when agent roles must be consistent across sessions. In simple systems with 1-2 unique agents, the overhead of maintaining templates may exceed the benefit. Apply this pattern when role consistency and reproducibility matter more than flexibility.

---

## Problem

When agent roles are defined implicitly — through ad-hoc system prompts, verbal instructions, or convention — the quality of agent behavior becomes unpredictable. The same "code reviewer" role, defined slightly differently across three projects, produces three different quality standards. An agent that performed well yesterday may behave differently today because its role description was paraphrased rather than reused verbatim.

This creates three failures:

1. **Quality variance**: Two agents assigned the same role produce outputs of significantly different quality because their role definitions differ in subtle but consequential ways
2. **Invisible drift**: Over time, role definitions evolve through casual edits. No one tracks what changed, and no one notices until output quality degrades
3. **Onboarding friction**: When a new agent joins the system (or an agent is replaced), reconstructing the "right" role definition requires tribal knowledge that may not exist

The root cause is the absence of a **canonical, versioned, structured** role definition. Without a template, role knowledge exists only in the minds of the developers who wrote the original prompts.

---

## Context

This problem arises when:

- **Role reuse**: The same role (e.g., "code reviewer," "documentation writer," "security auditor") is used across multiple projects or sessions
- **Team consistency**: Multiple agents perform the same role in parallel, and their outputs must be comparable in quality and format
- **Role handoff**: Agents are replaced or rotated, and the incoming agent must produce the same quality as the outgoing one
- **Quality standards**: The organization has specific expectations for how a role should behave (e.g., review thoroughness, output format, escalation criteria)
- **Auditability**: Stakeholders need to know exactly what instructions each agent received

This problem does **not** arise when:

- Each agent has a unique, one-off role that will never be reused
- The system has a single agent with no role variation
- Role definitions are trivial (less than 2-3 sentences)

---

## Solution

Define agent roles through explicit, structured template files. Each template captures the complete behavioral specification for a role — not just "who you are" but "how you work, what you produce, and what you must not do."

### Template Structure

Every role template must contain these sections:

```markdown
# Role: [Role Name]

## Identity
Who is this agent? Professional background, expertise domain, and perspective.

## Responsibilities
What must this agent do? Enumerated list of duties.

## Output Specification
What does this agent produce? Format, structure, required sections.

## Constraints
What must this agent NOT do? Explicit prohibitions and boundaries.

## Interaction Protocol
How does this agent communicate with other agents? Input sources, output destinations, escalation paths.

## Quality Criteria
How is this agent's output evaluated? Checklist of minimum quality standards.
```

### Example Template

```markdown
# Role: Security Auditor

## Identity
Senior security engineer with 10+ years of experience in application security.
Specializes in identifying OWASP Top 10 vulnerabilities, authentication flaws,
and data exposure risks. Approaches every review with a "red team" mindset.

## Responsibilities
1. Review code changes for security vulnerabilities
2. Identify authentication and authorization gaps
3. Flag data exposure risks (PII, credentials, tokens)
4. Verify input validation and output encoding
5. Check dependency versions against known CVE databases

## Output Specification
Produce a security review report in the following format:
- **Summary**: 1-2 sentence overview of findings
- **Critical**: Issues that must be fixed before merge (severity >= 7.0)
- **Warning**: Issues that should be addressed soon (severity 4.0-6.9)
- **Info**: Observations and best-practice suggestions (severity < 4.0)
- Each finding includes: location, description, severity, and remediation

## Constraints
- DO NOT modify code directly. Report findings only
- DO NOT review non-security aspects (style, performance, architecture)
- DO NOT approve changes. Only flag risks. Approval is the reviewer's decision
- NEVER disclose findings outside the review process

## Interaction Protocol
- Input: Code diff or file path from task assignment
- Output: Security review report written to reports/ directory
- Escalation: Flag any Critical finding to the project lead immediately

## Quality Criteria
- [ ] Every finding has a specific file and line reference
- [ ] Severity scores follow CVSS 3.1 guidelines
- [ ] Remediation suggestions are actionable (not just "fix this")
- [ ] No false positives from generic pattern matching
- [ ] Report is self-contained (reader needs no additional context)
```

### Template Versioning

Templates evolve. Track changes with version numbers and changelogs:

```markdown
## Version History
| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2025-01-15 | Initial template |
| 1.1 | 2025-02-20 | Added dependency CVE check to responsibilities |
| 1.2 | 2025-03-10 | Refined output format: added remediation to each finding |
```

### Template Composition

Complex roles can compose simpler templates:

```yaml
# roles/senior_reviewer.yaml
role: Senior Reviewer
composed_from:
  - roles/code_reviewer.yaml      # Base review skills
  - roles/security_auditor.yaml   # Security perspective
  - roles/mentor.yaml             # Teaching/feedback style
overrides:
  output_format: "Combined review with security section"
```

---

## Anti-Pattern

### [F001] Template Rigidity

**Description**: Templates are so prescriptive that agents cannot adapt to novel situations. A security auditor template that only covers OWASP Top 10 misses a novel vulnerability class because the template didn't mention it. The agent follows the template literally and ignores what it would otherwise recognize as a problem.

**Symptoms**:
- Agents miss obvious issues that fall outside template scope
- Output quality is high for template-covered scenarios but poor for edge cases
- Agents explicitly state "this is outside my role definition" when encountering novel situations

**Root cause**: Templates written as exhaustive checklists rather than guiding principles. The template replaces judgment instead of informing it.

**Fix**: Templates should define **principles and priorities**, not exhaustive task lists. Include a "Professional Judgment" section: "When encountering situations not covered by this template, apply your domain expertise. Flag the situation and your reasoning in the report."

### [F002] Template Sprawl

**Description**: Creating a new template for every minor role variation. The template library grows to dozens of nearly-identical files: `code_reviewer_python.yaml`, `code_reviewer_javascript.yaml`, `code_reviewer_python_security.yaml`. Maintenance becomes impossible; templates diverge silently.

**Symptoms**:
- 20+ templates with 80% content overlap
- Updating a shared concern (e.g., output format) requires editing multiple templates
- Developers create new templates by copying and modifying existing ones, introducing drift

**Root cause**: No composition mechanism. Every role variation requires a complete standalone template.

**Fix**: Implement template composition. Define base templates for core capabilities (review, analysis, writing) and compose them for specific roles. Use overrides for role-specific customization. Limit standalone templates to fundamentally different roles.

### [F003] Undocumented Deviation

**Description**: Agents silently deviate from their templates without recording why. A code reviewer template specifies "review all files in the diff," but the agent skips test files because "they're just tests." This deviation might be reasonable, but it's invisible — no one knows the template wasn't followed.

**Symptoms**:
- Output quality varies despite identical templates
- Stakeholders assume template compliance that doesn't exist
- Debugging reveals that agent behavior doesn't match the template

**Root cause**: No mechanism for agents to report template deviations. The template is a suggestion, not an auditable contract.

**Fix**: Require agents to declare deviations explicitly. Add a "Deviations" section to every output report where the agent lists any departures from the template and the reasoning. This makes deviations visible, reviewable, and learnable (see Experience Distillation).

---

## Failure Catalog

| ID | Failure | Root Cause | Detection Point |
|----|---------|-----------|-----------------|
| FC-01 | Three "code reviewer" agents across three projects produced inconsistent review depth; one flagged 12 issues, another flagged 2 on similar code | Each project defined the reviewer role with a different ad-hoc prompt. No shared template | Detected during cross-project quality comparison. Root cause: no canonical role definition |
| FC-02 | Agent replaced mid-project; replacement produced outputs in a completely different format, breaking the downstream pipeline | Role definition existed only in the original agent's system prompt, which was not preserved when the agent was replaced | Detected immediately when downstream agent failed to parse the new format |
| FC-03 | Security auditor template listed only OWASP Top 10; agent missed a business logic vulnerability because it fell outside the enumerated categories | Template Rigidity (F001). Template was an exhaustive checklist with no professional judgment clause | Detected in production when the vulnerability was exploited |
| FC-04 | Template library grew to 35 files; a critical update to the output format was applied to 28 of 35, leaving 7 templates producing the old format | Template Sprawl (F002). No composition mechanism; each template was a standalone copy | Detected when downstream consumers received mixed formats |

---

## Interaction Catalog

| Related Pattern | Relationship | Notes |
|----------------|-------------|-------|
| **01 Attention Budget** | informed by | Template length contributes to an agent's attention budget consumption. Verbose templates consume budget that could be used for task content. Keep templates concise — under 500 tokens for the core specification |
| **02 Context Gate** | complements | Templates define what each agent should receive and produce; Context Gates enforce these boundaries at runtime. Templates are the specification; gates are the enforcement |
| **03 Cognitive Profile** | requires | A template structures the delivery of a cognitive profile. The Profile defines *who* the agent is (identity, expertise, perspective); the Template adds *how* the agent works (responsibilities, output format, constraints). Profile without Template = identity without process. Template without Profile = process without identity |
| **04 Wave Scheduler** | complements | Wave definitions reference templates to specify what each wave member does. "Wave 1: each agent uses `independent_analyst.yaml` template. Wave 2: each agent uses `cross_reviewer.yaml` template" |
| **05 Assumption Mutation** | complements | Mutation personas (adversarial reader, devil's advocate) are specialized templates. The template system provides the structure; mutation provides the adversarial perspective |
| **06 Experience Distillation** | feeds into | Template deviations and effectiveness observations are distillable signals. "Template X works well for API reviews but poorly for UI reviews" can feed back into template improvement |
| **07 File-Based I/O** | uses | Templates are files. The file system provides storage, versioning (via git), and discoverability. Template organization follows File-Based I/O conventions |

---

## Known Uses

### Production Multi-Agent System — Instructions Files

A production orchestration system defines agent roles through `instructions/*.md` files:

- Each role (manager, worker, reviewer) has a dedicated instructions file
- Files contain: identity, responsibilities, forbidden actions, communication protocol, and quality criteria
- New agents read their instructions file at startup and adhere to its specification
- **Result**: Consistent agent behavior across sessions. When an agent was replaced, the new agent produced identical-quality output by reading the same instructions file

### Software Engineering Templates

The pattern mirrors established practices:
- **Pull request templates**: GitHub/GitLab PR templates ensure consistent information in every PR
- **Code review checklists**: Structured guides that ensure reviewers cover all relevant areas
- **Incident response runbooks**: Step-by-step templates for handling incidents consistently

### Prompt Engineering Libraries

Several AI development frameworks implement variants:
- **LangChain prompt templates**: Parameterized prompts with consistent structure
- **Claude CLAUDE.md files**: Project-level instructions that shape agent behavior
- **OpenAI system prompts**: Role definitions injected at conversation start

The key differentiator of Template-Driven Role is the **structured format** with explicit sections for constraints, output specification, and quality criteria — not just an identity paragraph.

---

## Implementation Guidance

### Minimal Implementation (Recommended Starting Point)

```yaml
# config/templates.yaml
templates:
  storage_path: "roles/"
  required_sections:
    - identity
    - responsibilities
    - output_specification
    - constraints
  optional_sections:
    - interaction_protocol
    - quality_criteria
    - version_history
  composition:
    enabled: true
    base_templates_path: "roles/base/"
    override_mechanism: "section-level"  # Override entire sections, not individual lines
```

### Directory Structure

```
roles/
├── base/                       # Composable base templates
│   ├── reviewer.md             # Base review capabilities
│   ├── analyst.md              # Base analysis capabilities
│   └── writer.md               # Base writing capabilities
├── security_auditor.md         # Composed: reviewer + security expertise
├── code_reviewer.md            # Composed: reviewer + code expertise
├── documentation_writer.md     # Composed: writer + documentation expertise
└── README.md                   # Template catalog and usage guide
```

### Step-by-Step Adoption

1. **Audit existing roles** — List every agent role in the current system. For each, document the current role definition (even if it's just an ad-hoc prompt)
2. **Create templates for high-frequency roles** — Start with roles used in 3+ projects. Convert ad-hoc prompts to structured templates with all required sections
3. **Add the "Deviations" requirement** — Every agent output must include a "Deviations" section listing any departures from the template. This makes template compliance visible
4. **Implement composition** — Identify overlapping content across templates. Extract shared sections into base templates. Rewrite role-specific templates as compositions
5. **Version and review** — Add version headers to all templates. Review templates quarterly: are they still accurate? Have deviations revealed needed updates?
6. **Connect to Experience Distillation** — Route template deviation reports to the learning pipeline. "Template X is consistently deviated from in scenario Y" may indicate the template needs updating

### Template Quality Checklist

Before deploying a template, verify:

| # | Criterion | Check |
|---|-----------|-------|
| TQ-1 | Identity section defines expertise and perspective, not just a name | More than "You are a code reviewer" |
| TQ-2 | Responsibilities are enumerated (numbered list) | Not a paragraph; each duty is a discrete item |
| TQ-3 | Output specification defines format, not just content | Includes section headings, structure requirements |
| TQ-4 | Constraints include at least 2 explicit prohibitions | "DO NOT" statements that prevent common misuse |
| TQ-5 | Template is under 500 tokens | Concise enough to fit within attention budget |
| TQ-6 | Professional judgment clause present | Agent can handle situations outside template scope |

---

## Evidence

- **Level B**: Confirmed across 3 projects in a production multi-agent system:
  - Projects using structured role templates showed measurably more consistent output quality (variance in review thoroughness reduced by ~50%) compared to projects using ad-hoc role definitions
  - Agent replacement time reduced from ~30 minutes (reconstructing role from memory) to ~2 minutes (reading template file)
  - Template deviations, when tracked, provided valuable feedback for template improvement (40% of deviations led to template updates)

- **Limitations of current evidence**:
  - No controlled experiment comparing templated vs. non-templated roles on identical tasks
  - "Consistency" measured qualitatively (human judgment), not quantitatively
  - Evidence limited to text-based agent roles; may not generalize to code-generation or data-analysis roles

- **Upgrade path to Level A**: Conduct a controlled experiment:
  - Treatment group: agents with structured templates (all required sections)
  - Control group: agents with single-paragraph role descriptions (same content, unstructured)
  - Measure: output consistency (inter-rater reliability), quality scores, and deviation rate
  - Required sample: 30+ tasks per group across 3+ role types
