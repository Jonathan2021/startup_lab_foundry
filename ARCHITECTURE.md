# Foundry architecture

## Product boundary

The Foundry owns durable venture execution memory: idea portfolios, ventures,
assumptions, experiments, evidence, decisions, work, artifacts, Foundry product
friction, agent runs, approvals, and external-action receipts.

It does not own Agent EvalOps evaluations or releases. A Foundry agent run may
retain an EvalOps trace ID, but the trace and evaluation records remain under
`agentevalops/`. It does not own curriculum, slice, learner, or certification
state; those remain under `learning/`.

## Architectural style

The product is a modular monolith with dependencies pointing toward application
behavior and the relational model:

```text
CLI / future API / agent adapters
              │
              ▼
       application use cases ───────► approval and action policies
              │                                  │
              ▼                                  ▼
 SQLAlchemy relational domain          replaceable external adapters
              │
              ▼
 repository/session boundary ───────► SQLite local / PostgreSQL later
```

SQLAlchemy 2 provides the typed mapping and database constraints. SQLite is the
local Slice 001 database; Alembic owns migrations; PostgreSQL enters when a
named concurrency or deployment need justifies it. Pydantic belongs at external
contract boundaries and DSPy belongs behind agent adapters. Provider SDKs and
Agent EvalOps runtime code do not enter the domain module.

See [ADR-0003](docs/adr/0003-foundry-domain-and-dependencies.md) for the decision
and [the DBML schema](docs/foundry-domain.dbml) for a copy/paste visualization.

## Domain map

`Workspace` is a shared context for three different subjects: `Idea`, `Venture`,
and `CapabilityCandidate`. It lets them use one evidence and execution loop
without pretending they are the same entity.

| Area | Principal records | Purpose |
|---|---|---|
| Portfolio discovery | Idea, IdeaRevision, IdeaRelation, ReferenceSource, MarketActor | Preserve where opportunities came from and how they were narrowed |
| Evaluation | Scorecard, ScoringCriterion, IdeaAssessment, CriterionScore, RankingSnapshot | Make scores, confidence, rationale, and Top-N comparisons reproducible |
| Venture learning | Assumption, Experiment, Evidence, AssumptionAssessment | Separate a belief, its test, observations, and interpretation |
| Commitment and work | Decision, WorkItem, Artifact | Explain why work exists and retain its version-addressable output |
| Foundry discovery | FrictionOccurrence, CapabilityCandidate, CapabilityUse | Generalize only after repeated friction and real venture pilots |
| Agent execution | AgentDefinition, AgentVersion, AgentRun | Attribute runs to prompt/tool/policy/code/provider configuration |
| Controlled effects | ExternalAction, ApprovalRequest, ActionAttempt, AuditEvent | Freeze intent, require human control, and retain outcome/actor history |

The schema is intentionally comprehensive enough to avoid redefining identities
and history later. It is not a mandate to expose generic CRUD for all 43 tables.
Each vertical slice implements only the smallest current venture capability.

## Core flows

### Portfolio to venture

```text
source → idea → idea revision → assessment ─┐
                         scorecard/criteria ├→ ranking snapshot
                         evidence/confidence┘

accepted idea revision → venture workspace
```

An idea can be derived, combined, narrowed, rescored, or rejected without losing
the prior interpretation. Rank only exists inside a snapshot.

### Learning and delivery

```text
question → INVESTIGATION work → evidence → new/refined assumption

assumption → EXPERIMENT work → evidence → assessment ─┬→ test again
                                                       ├→ new assumption
                                                       └→ decision

decision → EXECUTION work → artifact/outcome → evidence or friction
```

Evidence is a neutral observation. `AssumptionAssessment` supplies its meaning
for one belief at one time. Decisions link to both evidence and assessments.
This is why a ProductTask is represented as a typed `WorkItem`: discovery,
validation, and delivery share workflow mechanics but not intent.

### Foundry capability discovery

```text
friction in venture A ─┐
friction in venture B ─┴→ capability candidate → smallest pilot
                                      │                 │
                                      └── decision ← evidence/use outcome
```

A recurrence key helps group similar friction, but a human or authorized use
case decides whether it represents one capability. Successful use in multiple
real ventures is the signal to generalize.

### Acting on a venture

```text
WorkItem → AgentRun → Artifact
                   └→ ExternalAction → ApprovalRequest → ActionAttempt → Evidence
```

Internal analysis can produce a draft or artifact. Consequential actions freeze
the exact payload, risk, estimated cost, idempotency key, and expiry before
approval. Sending communication, spending, destructive operations, and
provisioning remain denied until explicitly approved. Adapters execute only an
approved action and retain the provider receipt or error.

## History and concurrency

- Ideas, scorecards, agent definitions/configurations, rankings, assessments,
  evidence, decisions, attempts, and audit events have explicit semantic
  versions or append-only records.
- Artifacts carry a location, digest, semantic version, and lineage relation;
  large payloads live outside the relational database.
- Mutable coordination aggregates use `version_id` for optimistic concurrency.
  That counter prevents stale writes but is not audit history.
- SQLAlchemy-Continuum is intentionally deferred. It may later supplement—not
  replace—semantic records if real compliance/support work requires generic row
  before/after history.

## Initial implementation boundary

Slice 001 exposes only enough local persistence and command behavior to create
and inspect an Agent EvalOps-shaped venture workspace. Portfolio importing,
automated scoring, agent orchestration, capability promotion, approvals, and
external adapters remain unimplemented until a named product or learning slice
needs them. No current code sends messages, provisions infrastructure, or spends
money.
