---
preset:
  name: policy
  description: "Government and corporate policy documents"
  strategies:
    contradiction: { weight: 0.9, enabled: true }
    ambiguity: { weight: 1.0, enabled: true }
    deletion: { weight: 0.6, enabled: true }
    inversion: { weight: 0.7, enabled: true }
    boundary: { weight: 0.8, enabled: true }
  default_persona: adversarial_reader
  severity_overrides:
    ambiguous_enforcement: Critical
    contradictory_provisions: Critical
    undefined_exemption_scope: Critical
    unenforceable_clause: Major
    missing_accountability: Major
    vague_timeline: Major
  domain_terminology:
    - shall
    - must
    - compliance
    - exemption
    - enforcement
    - provision
    - regulation
    - jurisdiction
    - mandate
    - waiver
    - penalty
    - effective date
    - sunset clause
    - stakeholder
    - due process
  output_format: full_report
---

# Preset: Policy

Mutation testing configuration for government and corporate policy documents. Designed to find ambiguities that prevent consistent enforcement, contradictions between provisions, and loopholes that undermine policy intent.

## Target Document Types

- **Government policy**: Legislation drafts, executive orders, agency guidelines
- **Corporate policy**: HR policies, data governance, security policies, code of conduct
- **Regulatory guidelines**: Industry-specific compliance requirements
- **Internal procedures**: SOPs, operational guidelines, process documents
- **Standards documents**: Organizational standards and frameworks

## Strategy Configuration

### Ambiguity (weight: 1.0)

Highest priority for policy documents. Ambiguous policy language is the root cause of inconsistent enforcement — two managers reading the same policy should reach the same conclusion.

**What it does**: Identifies terms and provisions that admit multiple valid interpretations.

**Policy-specific mutations**:
- Replace "appropriate" with specific actions to test if the policy actually prescribes behavior
- Replace "timely" with "within 24 hours" or "within 90 days" to reveal undefined deadlines
- Test "may" vs "shall" vs "must" usage — is the policy prescriptive or permissive?
- Replace "reasonable" with "any" or "no" to test if the qualifier is doing real work
- Test "including but not limited to" lists — are the unlisted items actually covered?

### Contradiction (weight: 0.9)

Very high priority. Policy contradictions create compliance nightmares — actors cannot simultaneously comply with contradictory provisions, creating legal exposure.

**What it does**: Identifies provisions that conflict with each other.

**Policy-specific mutations**:
- Cross-check exception clauses against general rules — does the exception swallow the rule?
- Cross-check different sections' definitions of the same term
- Test whether escalation procedures are consistent across all referenced scenarios
- Swap authority designations ("Department Head" ↔ "HR Director") to test if responsibilities are clearly separated

### Boundary (weight: 0.8)

High priority. Policy documents frequently reference thresholds, deadlines, and quantities without testing their extremes.

**What it does**: Pushes numeric values, deadlines, and thresholds to extremes.

**Policy-specific mutations**:
- "Within 30 days" → "Within 0 days" (is immediate compliance possible?)
- "Within 30 days" → "Within 365 days" (is there a maximum acceptable delay?)
- "Employees with 5+ years" → "Employees with 0 years" (does the policy cover new hires?)
- "$10,000 threshold" → "$0 threshold" (does the policy function at zero?)
- "3 or more violations" → "1 violation" (is the threshold justified?)

### Inversion (weight: 0.7)

Above moderate priority. Inverting policy provisions reveals whether the policy's enforcement mechanisms actually depend on the provisions being followed.

**What it does**: Reverses provisions to test enforcement robustness.

**Policy-specific mutations**:
- "Employees shall report incidents" → "Employees shall not report incidents" — does any enforcement mechanism detect non-reporting?
- "Management must approve" → "Management must not approve" — does any oversight catch blocked approvals?
- "Data shall be retained for 7 years" → "Data shall be deleted after 7 days" — does any audit process catch premature deletion?

### Deletion (weight: 0.6)

Moderate priority. Tests structural necessity of each provision and section.

**What it does**: Removes individual provisions and measures impact on policy coherence.

**Policy-specific mutations**:
- Delete the enforcement/penalty section — is compliance still incentivized?
- Delete individual exceptions — does the general rule become unworkable?
- Delete the definitions section — are terms still unambiguous from context?
- Delete the scope section — is it clear who the policy applies to?

## Default Persona Rationale

**Adversarial Reader** (`adversarial_reader`) is the default persona because:

1. Policy documents must withstand adversarial interpretation — people seeking to circumvent policy will read it with hostile intent
2. An adversarial reader finds loopholes that a cooperative reader would never notice
3. This persona naturally identifies provisions that are technically compliant but substantively void
4. Regulatory challenges come from adversarial parties — the policy must survive their reading

Alternative personas for specific use cases:
- `opposing_counsel`: For policies with legal enforcement implications
- `naive_implementer`: For testing whether frontline employees can follow the policy without interpretation

## Severity Overrides Explanation

| Override | Default → Override | Rationale |
|----------|-------------------|-----------|
| `ambiguous_enforcement` | Major → **Critical** | If enforcement is ambiguous, the policy is unenforceable. This is the single most common failure mode in policy documents — provisions without clear enforcement are suggestions, not rules. |
| `contradictory_provisions` | Major → **Critical** | Contradictory provisions create impossible compliance requirements. Actors must violate one provision to comply with another, exposing the organization to liability. |
| `undefined_exemption_scope` | Major → **Critical** | An exemption with unclear boundaries can be stretched to cover anything, effectively nullifying the provision it exempts from. |
| `unenforceable_clause` | Minor → **Major** | A clause that cannot be enforced (no penalty, no monitoring, no accountability) undermines the authority of the entire document. |
| `missing_accountability` | Minor → **Major** | Provisions without a designated responsible party are orphaned — nobody owns compliance, so nobody ensures it. |
| `vague_timeline` | Minor → **Major** | "In a timely manner" is the policy equivalent of no timeline. Without specific deadlines, compliance cannot be measured. |

## Domain Terminology

| Term | Policy Meaning | Enforcement Implication |
|------|---------------|------------------------|
| **Shall** | Mandatory requirement (RFC 2119: MUST equivalent) | Non-compliance is a violation |
| **Must** | Absolute requirement — no exceptions | Strongest obligation level |
| **Compliance** | Adherence to all applicable provisions | Requires measurable criteria |
| **Exemption** | Authorized exception to a provision | Must define scope, duration, and authority |
| **Enforcement** | Mechanism for ensuring compliance | Must define who enforces, how, and consequences |
| **Provision** | Individual requirement within the policy | Must be independently testable |
| **Mandate** | Required action or behavior | Must specify who, what, when |
| **Waiver** | Temporary suspension of a requirement | Must define duration, scope, and approval authority |
| **Penalty** | Consequence for non-compliance | Must be proportionate and specific |
| **Sunset clause** | Automatic expiration of a provision | Must define expiration date and renewal process |
| **Due process** | Fair procedure before adverse action | Must define steps, timeline, and appeal mechanism |

## Usage Examples

```bash
# Test a corporate data governance policy
mutadoc test data_governance_policy.md --preset policy

# Test a government regulation draft
mutadoc test regulation_draft.md --preset policy --strategies ambiguity,contradiction

# Test enforceability with opposing counsel persona
mutadoc test employee_handbook.md --preset policy --persona opposing_counsel

# Quick compliance check (Critical only)
mutadoc test security_policy.md --preset policy --min-severity critical

# Test with naive implementer to check frontline clarity
mutadoc test workplace_safety.md --preset policy --persona naive_implementer
```

## Sample Output

```markdown
# MutaDoc Report: remote_work_policy.md
**Preset**: policy | **Persona**: adversarial_reader | **Score**: 54/100

## Critical Findings (4)

### [C-001] Ambiguous Enforcement (Ambiguity)
- **Location**: Section 4.2, Performance Monitoring
- **Finding**: "Managers shall ensure remote employees maintain appropriate productivity
  levels." Three undefined terms: "ensure" (how?), "appropriate" (what threshold?),
  "productivity levels" (measured how?). An adversarial reader could comply with any
  productivity level and argue it is "appropriate."
- **Exploitation**: An employee producing minimal output argues their level is "appropriate
  for remote work conditions." The manager has no documented standard to counter this claim.
- **Recommendation**: Replace with measurable criteria: "Remote employees shall complete
  assigned deliverables by deadline. Managers shall conduct bi-weekly progress reviews using
  the standard evaluation rubric (Appendix C)."

### [C-002] Contradictory Provisions (Contradiction)
- **Location**: Section 3.1 vs Section 5.3
- **Finding**: Section 3.1 states "Remote work is available to all employees who have
  completed the probationary period." Section 5.3 states "Remote work eligibility requires
  manager approval based on role suitability assessment." These provisions contradict:
  Section 3.1 creates an entitlement (all post-probation employees), while Section 5.3
  creates a discretionary gate (manager approval).
- **Exploitation**: An employee denied remote work under Section 5.3 cites Section 3.1 as
  creating an automatic right. HR cannot enforce both simultaneously.
- **Recommendation**: Reconcile: "Remote work eligibility begins after the probationary
  period, subject to role suitability assessment by the employee's manager per the criteria
  in Appendix B."

### [C-003] Undefined Exemption Scope (Boundary)
- **Location**: Section 6.1, Exceptions
- **Finding**: "Exceptions to this policy may be granted by senior leadership in
  extraordinary circumstances." Three boundary issues: "senior leadership" is undefined
  (VP? Director? C-suite?), "extraordinary circumstances" is undefined, and there is no
  limit on the scope of exceptions.
- **Exploitation**: A Director grants a permanent exception for their entire department,
  arguing the restructuring is an "extraordinary circumstance." The policy has no mechanism
  to challenge this.
- **Recommendation**: Define: "Exceptions require written approval from a VP or above, are
  limited to 90 days, must specify scope (individual/team), and are reviewed quarterly by HR."

### [C-004] Ambiguous Enforcement (Ambiguity)
- **Location**: Section 7, Compliance
- **Finding**: "Non-compliance with this policy may result in disciplinary action." The word
  "may" makes enforcement entirely discretionary. Combined with the ambiguous provisions
  above, this means the policy has no teeth — even clear violations only "may" have
  consequences.
- **Exploitation**: An adversarial reader notes that "may" imposes no obligation on
  management to act, making the entire enforcement section advisory rather than mandatory.
- **Recommendation**: Replace "may" with "shall": "Non-compliance with this policy shall
  result in disciplinary action in accordance with the Progressive Discipline Policy
  (Section 12.3 of the Employee Handbook)."

## Major Findings (3)

### [M-001] Missing Accountability (Deletion)
- **Location**: Section 4, Responsibilities
- **Finding**: Deletion mutation removed Section 4 (Responsibilities). No other section
  assigns responsibility for policy compliance monitoring, exception tracking, or periodic
  review. The policy exists but nobody owns it.
- **Impact**: Without an owner, the policy will drift into irrelevance within 6-12 months.

...

## Summary
| Severity | Count |
|----------|-------|
| Critical | 4 |
| Major | 3 |
| Minor | 5 |
| **Total Mutations Applied** | **26** |
| **Mutations Survived (undetected)** | **12** |
| **Mutation Kill Rate** | **54%** |
```
