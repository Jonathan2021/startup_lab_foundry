# Foundry architecture

Current investment scope (2026-10-02): [internal use under evaluation](docs/CURRENT_DIRECTION.md),
per [ADR-0008](../docs/adr/0008-evidence-first-venture-realignment.md). The schema
and possible adapters below describe domain boundaries, not a mandate to implement
them. Agent EvalOps is a deferred case study; its prepared run/link commands remain
incomplete. Current operations support the full portfolio and retained venture workspaces.

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
CLI / local HTTP console / agent adapters
              │
              ▼
       application use cases ───────► approval and action policies
              │                                  │
              ▼                                  ▼
 SQLAlchemy relational domain          replaceable external adapters
              │
              ▼
 repository/session boundary ───────► SQLite local / PostgreSQL deployment
```

SQLAlchemy 2 provides the typed mapping and database constraints. SQLite is the
local Slice 001 database; Alembic owns migrations. Slice 002 introduced
PostgreSQL only as a container deployment adapter while preserving the same
domain/application boundary. Completed Slice 003 verifies those completed
boundaries in CI and does not change the runtime architecture. Reviewed Slice
004 adds package-delivery automation around the existing image; it does not add a
runtime service or product-domain dependency. Pydantic belongs at external
contract boundaries and DSPy belongs behind agent adapters.
Provider SDKs and Agent EvalOps runtime code do not enter the domain module.

See [ADR-0003](docs/adr/0003-foundry-domain-and-dependencies.md) for the domain
decision, accepted
[ADR-0004](docs/adr/0004-containerized-cli-and-postgresql.md) for the current
container lifecycle,
[accepted ADR-0005](docs/adr/0005-ci-evidence-and-trust-boundary.md) for the CI
evidence boundary,
[accepted ADR-0006](docs/adr/0006-guarded-image-delivery.md) for the reviewed
image-delivery boundary, and [the DBML schema](docs/foundry-domain.dbml) for a
copy/paste visualization.

## Lifecycle coordination

Accepted [ADR-0014](docs/adr/0014-decision-map-and-agent-context.md) adds one
`DecisionMap` head per workspace. Immutable `Artifact` revisions store typed
maps, pinned context, executor results and acceptance receipts. Existing
assumptions/evidence/decisions/work remain canonical; map nodes reference them.

`decision_contracts.py` owns external schemas; `decision_maps.py` owns revision,
reference and execution-impact rules; `agent_handoffs.py` owns context selection
and atomic result acceptance. `decision_commands.py` and `decision_console.py`
are CLI/HTTP adapters over the same services. `snapshots.py` centralizes
immutable receipts and transactional conflict handling. Today is a bounded
read projection across venture state. It creates no second task store.

Capturing an event records evidence without guessing its implications. Preparing
context closes explicit relationships, includes contradictory assessments,
discloses unselected evidence and rejects an insufficient byte budget. Results
separate findings from proposed work/venture effects. Acceptance rechecks scope,
map, review, work, evidence, human input and proposed-reference versions in one
transaction. Retries return the same receipt. A rollback-only preview uses the
same acceptance path. Changed dependencies require review before execution;
existing claim/start paths enforce that rule. Already running external agents
remain beyond the application's process control.

This is a single-operator local boundary. Source text is untrusted data, actions
are explicit, and no result authorizes remote send/spend/deploy operations.
There is no provider dependency in the lifecycle services.

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
| Bounded step execution | StepRun, WorkItem | Retain the input snapshot, runner/version, idempotency key and terminal outcome |
| Agent execution (largely deferred) | AgentDefinition, AgentVersion, AgentRun | Attribute runs to prompt/tool/policy/code/provider configuration |
| Controlled effects | ExternalAction, ApprovalRequest, ActionAttempt, AuditEvent | Freeze intent, require human control, and retain outcome/actor history |

The schema is intentionally comprehensive enough to avoid redefining identities
and history later. It is not a mandate to expose generic CRUD for all 44 tables.
Each capability must support a current venture task or demonstrated recurring friction.

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
and inspect an Agent EvalOps-shaped venture workspace. Slice 002 changed its
local packaging/deployment environment, not this application scope. Slice 003
adds verification evidence only. Slice 004 may publish a container package
after exact human approval but does not deploy or operate the application.
The later product-first request adds CSV intake, idea derivation/promotion,
list/read operations and a loopback console. Automated scoring, agent orchestration,
capability promotion, approvals and external adapters remain deferred. No current product code sends messages,
provisions infrastructure, or spends money.


## Current local operation

[ADR-0009](docs/adr/0009-local-console-and-executable-steps.md) adds a stable XDG
SQLite location and safe online backup. Original trial databases remain unchanged.
`PortfolioService` uses existing Idea/Revision/Relation/Source records; source
summaries retain their claim, limits, check date and digest. Identical checked
claims can be linked to several ideas; changed claims remain separate records.
This is provenance reuse, not an automatic crawler or freshness guarantee.

The FastAPI/Jinja console and CLI share application services. The console binds
loopback, checks Host/Origin and a local mutation token, escapes evidence text and
ships its own static assets. It is single-user local tooling; remote deployment
requires an explicit authentication/access design.

`StepService` snapshots bounded context and creates a WorkItem plus StepRun before
execution. A request key prevents duplicate submission for the same subject/kind.
Readiness and research briefs are deterministic. `AgentRunner` is an optional
Python protocol; absent adapters produce blocked editable handoffs. No subprocess,
provider default, model training or external action is hidden in that boundary.
A synchronous adapter must provide its own time/resource limits; long-running
work requires a durable worker before deployment. Interrupted runs stay visible
until explicit recovery; recovery never replaces an existing terminal outcome.

October 4 operation adds `scoring.py` (immutable methods and judgments), `reviews.py`
(append-only coordination), `views.py` (shared SQL filtering/sorting/pagination),
`projects.py` (reference-only checkpoints) and `outreach.py` (manual drafts/outcomes).
Provider/model/action interfaces remain independent; none imports learning code.
[ADR-0010](docs/adr/0010-portfolio-reviews-and-draft-history.md) records the one new
review table and existing Artifact/AuditEvent history reuse.
October 9 `discovery_records.py` exposes the existing source, market-actor,
revision and relation tables plus cohort comparison
([ADR-0019](docs/adr/0019-discovery-records-sources-competition-revisions.md)). Schema migrations never
import campaign data. Intake/backfills are explicit idempotent operator operations.
[ADR-0020](docs/adr/0020-truthful-venture-state-requests-and-drift.md) adds the
read-only `venture_state.py` projection, `request_files.py` (explicit request-file
registration) and `venture_identity.py` (aliases and `--id` selectors).
