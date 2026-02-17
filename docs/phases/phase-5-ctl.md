# Phase 5 (Cross-Cutting): CTL — Cognitive Task Language

> **Version**: 1.0.0
> **Status**: Conditional — activated only if revival conditions are met at Phase 3

---

## 1. CTL Revival Conditions

### 1.1 Background

CTL (Cognitive Task Language) was explored as a dedicated DSL for describing cognitive tasks with type-safe syntax and static analysis. It was **deferred** (not rejected) during the initial DSL/CTL exploration for a clear reason:

> *"New language learning cost is too high. cqlint delivers equivalent quality assurance."* — Sharpening Phase

The roadmap positions CTL with the principle: **"Tools first, language later"** — users experience cqlint, understand why it catches what it catches, and only then might want the expressiveness of a dedicated language.

### 1.2 Quantitative Revival Criteria

The revival decision is made at the **Phase 3 Checkpoint** (during CQ MCP Server development). All four conditions must be met:

| # | Criterion | Quantitative Threshold | Measurement Method |
|---|-----------|----------------------|-------------------|
| RC-1 | **CQE Patterns maturity** | Patterns v0.2+ published (≥ 12 patterns with ≥ 3 at Evidence Level A) | Count patterns in catalog; check Evidence Level field |
| RC-2 | **cqlint rule saturation** | ≥ 15 cqlint rules AND ≥ 3 user-reported "can't express this in YAML" complaints | Count rules in `cqlint/rules/`; count GitHub Issues tagged `expressiveness` |
| RC-3 | **Community demand signal** | ≥ 10 unique users requesting declarative task definition (GitHub Issues/Discussions) | Count unique authors on Issues/Discussions tagged `ctl` or `dsl` |
| RC-4 | **Reproducibility gap evidence** | ≥ 5 documented cases where task re-execution produced inconsistent quality due to lack of formal task definition | Review CQ MCP telemetry for quality variance on repeated tasks |

### 1.3 Revival Decision Checklist

```
Phase 3 CTL Revival Checkpoint
═══════════════════════════════

□ RC-1: CQE Patterns v0.2+ with ≥ 12 patterns, ≥ 3 at Evidence Level A
□ RC-2: cqlint has ≥ 15 rules AND ≥ 3 "expressiveness limit" reports
□ RC-3: ≥ 10 unique community members requesting CTL/DSL capability
□ RC-4: ≥ 5 documented reproducibility gap cases

DECISION:
  □ All 4 met     → REVIVE CTL (proceed to Phase 5 implementation)
  □ 3 of 4 met    → CONDITIONAL REVIVE (implement MVP Grammar only, defer runtime)
  □ 2 or fewer    → DEFER FURTHER (re-evaluate at Phase 4 completion)
  □ 0 met         → ARCHIVE (CTL concepts remain absorbed in cqlint; no standalone DSL)
```

### 1.4 Why These Specific Thresholds

| Criterion | Rationale |
|-----------|-----------|
| **12 patterns** | Original 8 + at least 4 discovered through real-world usage. Indicates the vocabulary is rich enough to warrant a formal language |
| **Evidence Level A** | At least 3 patterns quantitatively validated. CTL formalizes concepts — it should only formalize validated concepts |
| **15 cqlint rules** | Triple the initial 5. Indicates the verification space has outgrown ad-hoc rule definitions |
| **"Can't express" complaints** | Directly measures the pain point CTL solves. No complaints = no need |
| **10 unique users** | Minimum viable community interest. Below this, CTL is premature optimization |
| **5 reproducibility cases** | CTL's core promise is reproducible task execution. This threshold proves the problem exists |

---

## 2. MVP Grammar Definition Tasks

### 2.1 Minimum 5-Keyword Grammar

The CTL MVP grammar is built on exactly 5 keywords, each mapping to a CQE core concept:

| Keyword | CQE Concept | Syntax | Purpose |
|---------|-------------|--------|---------|
| `task` | — (container) | `task <name> { ... }` | Top-level task definition block |
| `wave` | Wave Scheduler | `wave <N> { ... }` | Phased execution with dependency control |
| `gate` | Context Gate | `gate: only(...)` | Information filtering between stages |
| `persona` | Cognitive Profile | `with persona(<name>)` | Cognitive profile assignment |
| `invariant` | — (quality constraint) | `invariant "<condition>"` | Compile-time quality assertions |

**Extended keywords** (MVP+, added if MVP validates):

| Keyword | Syntax | Purpose |
|---------|--------|---------|
| `budget` | `budget: <N> tokens` | Token budget declaration (Attention Budget pattern) |
| `mutate` | `mutate: <profile> @ <budget>` | Mutation testing step (Assumption Mutation pattern) |
| `challenge` | `challenge(<target>.assumptions)` | Explicit assumption challenge |
| `learn` | `learn from execution { ... }` | Learning signal configuration (Experience Distillation) |
| `import` | `import <path>` | Task definition reuse |

### 2.2 BNF Grammar Specification (MVP)

```bnf
<program>       ::= <task-def>+
<task-def>      ::= "task" <identifier> "{" <task-body> "}"
<task-body>     ::= <statement>*
<statement>     ::= <budget-decl>
                   | <quality-decl>
                   | <persona-decl>
                   | <wave-block>
                   | <invariant-decl>
                   | <learn-block>

<budget-decl>   ::= "budget:" <number> "tokens"
<quality-decl>  ::= "quality:" <level>
<level>         ::= "low" | "medium" | "high" | "critical"
<persona-decl>  ::= "with" "persona(" <identifier> ")"

<wave-block>    ::= "decompose" "into" "waves" "{" <wave-def>+ "}"
<wave-def>      ::= "wave" <number> "{" <subtask-def>+ "}"
<subtask-def>   ::= <identifier> ":" <identifier> "@" <number>
                     <subtask-opt>*
<subtask-opt>   ::= <depends-clause> | <gate-clause> | <mutate-clause>

<depends-clause>::= "depends_on" "[" <identifier-list> "]"
<gate-clause>   ::= "gate:" "only(" <identifier-list> ")"
<mutate-clause> ::= "mutate:" <identifier> "@" <number>
                     "challenge(" <dotted-id> ")"

<invariant-decl>::= "invariant" <string-literal>

<learn-block>   ::= "learn" "from" "execution" "{" <learn-body> "}"
<learn-body>    ::= "signals:" "[" <identifier-list> "]"
                     "scope:" <identifier>

<identifier-list>::= <identifier> ("," <identifier>)*
<dotted-id>     ::= <identifier> ("." <identifier>)*
<identifier>    ::= [a-zA-Z_][a-zA-Z0-9_]*
<number>        ::= [0-9]+ ("k")?
<string-literal>::= '"' [^"]* '"'
```

### 2.3 Implementation Tasks

| # | Task | Description | Estimated Size | Depends On |
|---|------|-------------|:-:|------------|
| T5.1 | **BNF/PEG formal grammar** | Write the complete formal grammar definition in PEG format (more practical for parser generation than BNF) | S | — |
| T5.2 | **Retrospective CTL authoring** | Rewrite 20 past crew/cq-engine executions as `.ctl` files to validate expressiveness | M | T5.1 |
| T5.3 | **Parser implementation** | Build a parser that converts `.ctl` files to AST (Abstract Syntax Tree). Bash + Python or tree-sitter | M | T5.1 |
| T5.4 | **Type checker** | Implement type checking: budget units (tokens), persona names, gate scopes | M | T5.3 |
| T5.5 | **`ctl check` command** | Static analysis: budget overflow, gate inconsistency, dependency cycles, undefined persona references | M | T5.3, T5.4 |
| T5.6 | **`ctl fmt` command** | Code formatter for `.ctl` files | S | T5.3 |
| T5.7 | **Runtime / interpreter** | Execute `.ctl` files by translating to Claude Code subprocess calls | L | T5.3, T5.5 |
| T5.8 | **Sample `.ctl` library** | 10+ ready-to-use `.ctl` files for common tasks (security review, code review, document analysis) | M | T5.2 |
| T5.9 | **Usability validation** | 3 developers write CTL tasks; measure learning curve and reuse rate | M | T5.7, T5.8 |
| T5.10 | **cqlint CTL adapter** | Extend cqlint to lint `.ctl` files natively | M | T5.3, cqlint stable |

### 2.4 Task Dependency Graph

```
T5.1 (Grammar)
  │
  ├──▶ T5.2 (Retrospective authoring)
  │      │
  │      └──▶ T5.8 (Sample library) ──▶ T5.9 (Usability validation)
  │
  ├──▶ T5.3 (Parser)
  │      │
  │      ├──▶ T5.4 (Type checker) ──┐
  │      │                          ├──▶ T5.5 (ctl check)
  │      ├──────────────────────────┘
  │      │
  │      ├──▶ T5.6 (ctl fmt)
  │      │
  │      ├──▶ T5.7 (Runtime) ──▶ T5.9 (Usability validation)
  │      │
  │      └──▶ T5.10 (cqlint CTL adapter)
  │
  └──▶ (none without parser)
```

### 2.5 Size Estimates

| Component | Size | Rationale |
|-----------|:----:|-----------|
| Grammar + Parser | **M** | PEG grammar for 5 keywords is compact; parser can leverage existing tools (tree-sitter, PEG.js) |
| Type checker + Static analysis | **M** | Type system is simple (tokens, identifiers, scopes); static analysis is the core value proposition |
| Runtime | **L** | Translating CTL to Claude Code execution plans requires handling dependencies, parallelism, error recovery |
| Sample library + validation | **M** | 20 retrospective rewrites + 10 new samples + 3-person usability test |
| **Total Phase 5** | **L** | Sum of all components. Conditional on revival decision |

---

## 3. CTL ↔ cqlint Relationship

### 3.1 Current State (Phase 1–3): CTL Concepts Absorbed into cqlint

During Phase 1, CTL's design concepts are absorbed into cqlint rules:

| CTL Concept | cqlint Rule | How It's Expressed Without CTL |
|-------------|-------------|-------------------------------|
| `budget: N tokens` | CQ001 (budget-missing) | YAML field: `budget: 80000` in task definition |
| `gate: only(...)` | CQ002 (context-contamination) | YAML field: `context_scope: [file1, file2]` |
| `with persona(...)` | CQ003 (generic-persona) | YAML field: `persona: security-auditor` |
| `mutate: ... challenge(...)` | CQ004 (no-mutation-critical) | YAML field: `mutation: true` |
| `learn from execution` | CQ005 (learning-disabled) | YAML field: `learning: enabled` |
| `invariant "..."` | (no cqlint equivalent) | Manual documentation / code comments |
| Type-safe budget arithmetic | (no cqlint equivalent) | Manual calculation |
| Dependency cycle detection | (no cqlint equivalent) | Manual verification |

**Key insight**: cqlint covers 5 of 7 CTL concepts through YAML validation. The gap is in `invariant` (compile-time assertions) and type-safe static analysis (budget arithmetic, dependency resolution). These gaps become the primary justification for CTL revival.

### 3.2 Impact of CTL Revival on cqlint

| Aspect | Impact | Detail |
|--------|--------|--------|
| **cqlint rules** | Enhanced, not replaced | Existing YAML rules continue to work. New `.ctl` adapter added alongside `crew_yaml.sh` and `generic_yaml.sh` |
| **cqlint output** | Extended | `.ctl` files produce richer diagnostics (budget arithmetic, dependency analysis) than YAML files |
| **Rule count** | Grows | CTL enables new rules impossible with YAML (e.g., CQ006: budget-overflow, CQ007: gate-inconsistency, CQ008: dependency-cycle) |
| **User experience** | Two paths | Users choose: YAML (zero learning curve) or CTL (richer verification). Both paths through cqlint |

### 3.3 cqlint Rule Extension for CTL

| New Rule | Name | CTL-Only | Description |
|----------|------|:--------:|-------------|
| CQ006 | budget-overflow | Yes | Total subtask budgets exceed parent task budget |
| CQ007 | gate-inconsistency | Yes | Downstream task references data excluded by upstream gate |
| CQ008 | dependency-cycle | Yes | Circular dependency detected in wave definitions |
| CQ009 | unused-invariant | Yes | Invariant condition is trivially satisfied (dead assertion) |
| CQ010 | persona-mismatch | No* | Subtask persona doesn't match task complexity (*enhanced in CTL with type checking) |

### 3.4 Migration Path: YAML → CTL

CTL does not replace YAML. It provides an **opt-in upgrade path** for power users:

```
Stage 1: YAML Only (Phase 1–3)
┌─────────────────────────┐
│  task.yaml              │ ──▶ cqlint (5 rules) ──▶ execution
│  (crew/generic YAML)    │
└─────────────────────────┘

Stage 2: YAML + CTL Coexistence (Phase 5)
┌─────────────────────────┐
│  task.yaml              │ ──▶ cqlint (5 rules)    ──▶ execution
│  (zero learning curve)  │                              │
├─────────────────────────┤                              │
│  task.ctl               │ ──▶ cqlint (10+ rules)  ──▶ execution
│  (power users)          │     + type checking          │
│                         │     + static analysis        │
└─────────────────────────┘                              │
                                                         ▼
                                              same execution engine
```

**Key design decision**: Both YAML and CTL produce the same execution plan. The difference is in **pre-execution verification depth**, not in runtime behavior. A `.ctl` file can express everything a YAML file can, plus invariants and type-safe budget constraints.

### 3.5 YAML-to-CTL Conversion Tool

| Task | Description | Size |
|------|-------------|:----:|
| T5.11 | `ctl convert task.yaml` — auto-converts existing YAML task definitions to `.ctl` format | S |

This lowers the migration barrier: users can convert their existing tasks and immediately benefit from deeper static analysis.

### 3.6 Completion Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| CC-1 | cqlint runs on both `.yaml` and `.ctl` files with a single command | `cqlint check .` processes both file types |
| CC-2 | All 5 existing YAML rules (CQ001–CQ005) apply to `.ctl` files | Test suite passes for both formats |
| CC-3 | CTL-only rules (CQ006–CQ009) produce correct diagnostics | Test fixtures with known issues produce expected warnings/errors |
| CC-4 | `ctl convert` successfully converts 20 existing YAML tasks | Conversion produces valid `.ctl` files that pass `cqlint check` |
| CC-5 | No regression in YAML-only workflow | Users who never touch CTL see no behavior changes |

---

## 4. Phase 5 Overall Design

### 4.1 Revival Checkpoint Detail (Evaluated at Phase 3)

The checkpoint occurs **after M3.2** (Hooks auto-trigger) and **before M3.4** (Feedback loop v1):

```
Phase 3 Timeline:
  M3.1 (MCP installable) ──▶ M3.2 (Hooks auto-trigger)
                                │
                                ▼
                      ┌─────────────────────┐
                      │  CTL REVIVAL         │
                      │  CHECKPOINT          │
                      │                     │
                      │  Evaluate RC-1..RC-4 │
                      │  Make GO/NO-GO       │
                      └─────────┬───────────┘
                                │
                                ▼
                       M3.3 (Telemetry) ──▶ M3.4 (Feedback loop)
```

**Why this timing**: By M3.2, the ecosystem has real users (MCP installed, hooks active). Telemetry data (M3.3) is beginning to accumulate. This is the earliest point where RC-1 through RC-4 can be meaningfully measured.

### 4.2 Milestones (Conditional: Post-Revival Only)

| # | Milestone | Definition of Done | Depends On |
|---|-----------|-------------------|------------|
| M5.1 | Grammar specification complete | PEG grammar published, 20 retrospective `.ctl` files validate expressiveness | Revival GO decision |
| M5.2 | Parser and type checker functional | `ctl check task.ctl` produces correct diagnostics on test fixtures | M5.1 |
| M5.3 | cqlint CTL adapter integrated | `cqlint check .` processes `.ctl` files alongside `.yaml` | M5.2, cqlint v0.2+ |
| M5.4 | Runtime functional | `.ctl` files execute via Claude Code subprocess translation | M5.2 |
| M5.5 | Sample library and documentation | 10+ ready-to-use `.ctl` files + user guide | M5.4 |
| M5.6 | Usability validated | 3 developers achieve productive use within 30 minutes | M5.5 |
| M5.7 | YAML-to-CTL converter | `ctl convert` handles all existing YAML task patterns | M5.2 |

### 4.3 Dependencies on All Other Phases

```
PHASE 1 (Foundation)
┌──────────────────────────────────────────────────────────────────┐
│ CQE Patterns v0.1 (8 patterns)                                  │
│   └──▶ CTL formalizes pattern concepts as language syntax        │
│                                                                  │
│ cqlint v0.1 (5 rules, YAML adapters)                            │
│   └──▶ CTL adds new adapter (ctl_adapter.sh) + rules CQ006-CQ009│
│                                                                  │
│ CQ Benchmark v0.1 (spec)                                        │
│   └──▶ CTL tasks can declare benchmark measurement points       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
PHASE 2 (Killer App)
┌──────────────────────────────────────────────────────────────────┐
│ MutaDoc v0.1                                                     │
│   └──▶ MutaDoc strategies can be described as .ctl templates     │
│        (reproducible mutation testing pipelines)                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
PHASE 3 (Distribution)
┌──────────────────────────────────────────────────────────────────┐
│ CQ MCP Server v0.1                                               │
│   └──▶ CTL Revival Checkpoint (after M3.2)                       │
│   └──▶ If revived: crew_cq__ctl_check MCP tool added             │
│                                                                  │
│ Telemetry baseline                                               │
│   └──▶ Provides data for RC-4 (reproducibility gap evidence)     │
│                                                                  │
│ Community (GitHub Discussions)                                    │
│   └──▶ Provides data for RC-3 (community demand signal)          │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
PHASE 4 (Expansion)
┌──────────────────────────────────────────────────────────────────┐
│ ThinkTank v0.1                                                   │
│   └──▶ ThinkTank 3-Wave pipeline can be described as .ctl file   │
│        (reproducible multi-perspective analysis)                  │
│                                                                  │
│ Feedback loop                                                    │
│   └──▶ CTL usage telemetry feeds back into pattern evolution     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
PHASE 5 (Cross-Cutting, Conditional)
┌──────────────────────────────────────────────────────────────────┐
│ CTL Grammar + Parser + Type Checker + Runtime                    │
│ cqlint CTL adapter + new rules                                   │
│ Sample library + YAML-to-CTL converter                           │
│ Usability validation                                             │
└──────────────────────────────────────────────────────────────────┘
```

### 4.4 Full Dependency Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ PHASE 1  │────▶│ PHASE 2  │────▶│ PHASE 3  │────▶│ PHASE 4  │
│Foundation│     │MutaDoc   │     │MCP Server│     │ThinkTank │
└──────────┘     └──────────┘     └─────┬────┘     └──────────┘
     │                                   │                │
     │         ┌─────────────────────────┘                │
     │         │ Revival Checkpoint                       │
     │         ▼                                          │
     │    ┌─────────┐                                     │
     │    │ GO / NO │                                     │
     │    └────┬────┘                                     │
     │         │ GO                                       │
     │         ▼                                          │
     │    ┌──────────────────────────────────────────┐    │
     │    │            PHASE 5 (Conditional)         │    │
     │    │                                          │    │
     │    │  M5.1: Grammar ──▶ M5.2: Parser+Types    │    │
     │    │                       │                  │    │
     │    │          ┌────────────┼────────────┐     │    │
     │    │          ▼            ▼            ▼     │    │
     │    │       M5.3:       M5.4:        M5.7:    │    │
     │    │       cqlint      Runtime      Convert  │    │
     │    │       adapter        │                  │    │
     │    │          │           ▼                  │    │
     │    │          │        M5.5: Samples         │    │
     │    │          │           │                  │    │
     │    │          │           ▼                  │    │
     │    │          └────▶ M5.6: Validation        │    │
     │    └──────────────────────────────────────────┘    │
     │                          │                         │
     │                          ▼                         │
     │              ┌───────────────────────┐             │
     │              │ Feedback to Phase 1+  │◀────────────┘
     │              │ (pattern evolution)   │
     └─────────────▶│                       │
                    └───────────────────────┘
```

### 4.5 Risks and Mitigations

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|:----------:|------------|
| R5.1 | **Revival conditions never met** | Phase 5 never activates; design effort partially wasted | Medium | Design document doubles as architectural reference for cqlint improvements. No implementation effort is spent until revival GO |
| R5.2 | **Learning curve too steep** | Users don't adopt CTL despite revival | Medium | YAML path always remains. CTL is opt-in. `ctl convert` auto-generates from existing YAML. Target 30-minute productive use |
| R5.3 | **Parser maintenance burden** | New language = ongoing maintenance cost | High | Use established parser generator (tree-sitter/PEG.js). Minimize grammar size (5 keywords MVP). Grammar is intentionally small and stable |
| R5.4 | **CTL diverges from cqlint** | Two verification systems that disagree | Low | Single cqlint binary handles both formats. CTL adapter shares rule logic with YAML adapter. Unified test suite |
| R5.5 | **"Just use YAML" resistance** | Community prefers YAML simplicity over CTL expressiveness | High | Frame CTL as power-user tool, not replacement. Demonstrate value with concrete examples where YAML fails (budget overflow, gate inconsistency) |
| R5.6 | **Runtime complexity** | CTL-to-execution translation is harder than expected | Medium | Ship `ctl check` (static analysis) before runtime. Users get value from verification alone. Runtime can be phased |
| R5.7 | **Scope creep** | CTL grammar grows beyond 5 keywords, becomes complex | Medium | Grammar extension requires explicit proposal + community approval. Extended keywords (budget, mutate, etc.) added only with evidence of need |

### 4.6 The "No Revival" Scenario

If CTL is **not revived**, the following happens:

| Aspect | Outcome |
|--------|---------|
| **cqlint** | Continues as the sole verification tool. YAML-based rules grow to 15+ |
| **Static analysis gap** | Budget arithmetic and dependency cycle detection remain manual or are approximated by cqlint heuristics |
| **Reproducibility** | Task definitions remain in YAML; reproducibility depends on disciplined YAML authoring |
| **This document** | Serves as architectural reference. CTL's design concepts continue to influence cqlint rule design |
| **Community** | If demand resurfaces later, this document provides a ready-to-implement specification |

**No revival is a valid outcome.** The "Tools first, language later" principle means the language may never be needed if the tools are good enough.

---

## 5. Hypotheses to Validate (Post-Revival)

| # | Hypothesis | Method | Success Threshold |
|---|-----------|--------|-------------------|
| H5.1 | CTL static analysis detects issues cqlint YAML rules cannot | Run `ctl check` and `cqlint check` on same 20 tasks; compare unique findings | CTL finds 3+ issues per task that YAML rules miss |
| H5.2 | CTL task definitions improve reproducibility | Execute same `.ctl` file 10 times; measure quality variance vs YAML-defined tasks | Quality variance < 50% of YAML baseline |
| H5.3 | Developers achieve productive CTL use within 30 minutes | 3 developers write a CTL file for a real task; measure time-to-first-valid-file | All 3 produce valid `.ctl` in ≤ 30 min |
| H5.4 | CTL files are reused more than YAML definitions | Track `.ctl` imports vs YAML copy-paste in CQ MCP telemetry | Import-to-copy ratio ≥ 2:1 |
| H5.5 | Budget overflow detection prevents token waste | Compare token usage on tasks with/without `ctl check` pre-validation | 20%+ token reduction on overflow-prone tasks |

---

## 6. Sample CTL File (Reference)

From the original DSL/CTL exploration (explore_abstractions.md, Form 4):

```ctl
task authenticate_system {
  budget: 80k tokens
  quality: high

  with persona(security_auditor)

  decompose into waves {
    wave 1 {
      analyze_requirements: researcher @ 20k
      review_existing_auth: researcher @ 15k
    }
    wave 2 {
      design_auth_flow: coder @ 30k
        depends_on [analyze_requirements, review_existing_auth]
        gate: only(file_paths, key_decisions)
    }
    wave 3 {
      implement: coder @ 40k
        depends_on [design_auth_flow]
      mutate: reviewer @ 10k
        challenge(design_auth_flow.assumptions)
    }
  }

  invariant "No hardcoded credentials"
  invariant "All endpoints require authentication"

  learn from execution {
    signals: [course_correction, rejection]
    scope: project
  }
}
```

**Static analysis output** (`ctl check` would produce):

```
$ ctl check auth_task.ctl
WARNING: wave 2 coder @ 30k is 37.5% of budget 80k.
         wave 1 (35k) + wave 2 (30k) = 65k, wave 3 (50k) exceeds budget.
ERROR:   mutate depends on design_auth_flow.assumptions but
         design_auth_flow output is filtered by gate: only(file_paths, key_decisions).
         Verify that assumptions are included in gate scope.
```

This demonstrates the two key capabilities YAML-based cqlint cannot provide:
1. **Budget arithmetic across waves** (WARNING)
2. **Gate-dependency cross-reference** (ERROR)

---

<!-- PHASE 5 DETAIL COMPLETE -->
