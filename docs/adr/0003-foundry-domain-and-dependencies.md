# ADR-0003: Relational Foundry domain and evidence loops

- Status: Accepted
- Date: 2026-08-08
- Supersedes: [ADR-0002](../../../docs/adr/0002-foundry-local-store-first.md)
- Schema: [foundry-domain.dbml](../foundry-domain.dbml)

## Context

The Foundry needs enough durable structure to manage Agent EvalOps as a real
venture without becoming a speculative all-purpose startup platform. Its value
is not a clever prompt: it is the attributable history connecting what was
believed, what was tried, what was observed, what was decided, and what happened
next.

The first bootstrap proposed a replaceable JSON store. Before that learner work
started, we reviewed `startup_ideas_portfolio_v2.xlsx` as a second real usage
case. The workbook contained 238 ideas, 25 generated or newly added ideas, 148
market actors, a versionable weighted score guide, market references, confidence
labels, recommendations, validation tests, and a Top 25 view. Its SHA-256 at
review was
`ebc5028a27aaed5c574da0355a1a7f1dc361c35493106b77d013b645ba7339e4`.

That exercise revealed requirements a venture-only JSON aggregate would make
awkward:

- preserve idea provenance, derivation, narrowing, and pivots;
- rescore the same idea revision with different scorecards without erasing old
  assessments;
- treat rank as a point-in-time portfolio result rather than an intrinsic idea
  property;
- retain the sources and confidence behind a score or recommendation;
- turn promising ideas into ventures without losing their provenance;
- distinguish work that discovers a problem, tests an assumption, and executes
  a decision;
- let evidence create or refine assumptions instead of forcing a one-way
  assumption-to-task pipeline;
- discover Foundry product capabilities from repeated friction across real
  ventures; and
- propose and trace agent actions while keeping consequential effects under
  human approval.

Changing to a relational store before learner persistence work begins is much
cheaper than migrating an established file format later. It also creates a real
transactional foundation without requiring a server during local development.

## Decision

### 1. Use a relational domain from Slice 001

Use SQLAlchemy 2 annotated declarative models as the canonical relational
mapping. Use SQLite for the local adapter and Alembic for migrations. Preserve a
database/session boundary so PostgreSQL can replace SQLite when concurrency and
deployment justify it.

The model uses portable UUID strings, UTC timestamps, named constraints, enum
checks, uniqueness constraints, and SQLAlchemy optimistic version counters on
mutable aggregates. A transaction, not per-record file replacement, is the unit
of atomic persistence.

### 2. Use a workspace as the common learning context

A `Workspace` belongs to a `Portfolio` and has one of three kinds:

- `IDEA`: an opportunity before commitment to a venture;
- `VENTURE`: an actively managed business/product effort; or
- `FOUNDRY_CAPABILITY`: a candidate improvement to the Foundry itself.

Assumptions, work, evidence, decisions, artifacts, runs, and audit events attach
to a workspace. `Idea`, `Venture`, and `CapabilityCandidate` remain distinct
entities with distinct invariants; the workspace only gives their shared loops
a strong relational context. This avoids nullable polymorphic “subject type +
subject id” links with no foreign-key integrity.

### 3. Preserve idea portfolio provenance and scoring history

Use these groups:

- `Idea`, immutable `IdeaRevision`, `IdeaRelation`, `ReferenceSource`, and
  `IdeaSource` preserve origin, generation, combination, pivots, and sources.
- `MarketActor` and `IdeaMarketActor` retain competitors, alternatives,
  partners, and benchmarks against the exact idea revision considered.
- versioned `Scorecard` and `ScoringCriterion` define an assessment method.
- `IdeaAssessment`, `CriterionScore`, and `CriterionScoreEvidence` retain the
  result, confidence, rationale, and supporting evidence.
- `RankingSnapshot` and `RankingEntry` capture a comparable portfolio view.

An idea's title, scope, customer, and validation test change by creating a new
revision. A new scorecard or new evidence creates a new assessment. A Top 25 is
generated as a ranking snapshot. None overwrites the earlier interpretation.

### 4. Model learning as a loop, not a pipeline

`Evidence` is a sourced observation. It is not automatically “proof” and is not
owned by one assumption. `AssumptionAssessment` interprets a set of evidence for
an assumption at a point in time as supported, weakened, refuted, or
inconclusive. `Decision` records a commitment and its rationale, linked to the
relevant evidence and assessments.

The intended loops are:

```text
question → investigation → evidence → new/refined assumption
assumption → experiment → evidence → assessment ─┬→ another experiment
                                                  ├→ new/refined assumption
                                                  └→ decision
decision → execution work → artifact/outcome → evidence or friction
```

New assumptions may therefore originate in idea analysis, a founder statement,
an investigation, an experiment's surprise, an execution outcome, or friction.
`Assumption.origin_evidence_id` and `AssumptionRelation` make derivation and
refinement explicit. Assessments append over time; the assumption's status is
only a current coordination summary.

### 5. Replace ambiguous ProductTask with typed WorkItem

There are not two unrelated task entities. There is one `WorkItem` lifecycle
with three explicit intents:

- `INVESTIGATION` answers an open question and may generate candidate
  assumptions or baseline evidence;
- `EXPERIMENT` tests one or more named assumptions through an `Experiment` with
  success and failure criteria; and
- `EXECUTION` carries out an accepted decision and has acceptance criteria.

This keeps assignment, status, ownership, blocking, budgets, and hierarchy
consistent while preventing a delivery task from masquerading as validation.

An `Artifact` is a version-addressable output of work or an agent run: for
example a report, interview synthesis, dataset, prototype, model, configuration,
prompt, evaluation, or release. The database stores identity, location, digest,
version, and lineage; large bytes stay in Git, object storage, an artifact store,
or another replaceable system. An artifact can be linked to evidence, but the
artifact itself is not evidence until someone records the relevant observation.

### 6. Let repeated venture friction drive Foundry features

Every awkward workaround can be recorded as a `FrictionOccurrence` with a
stable recurrence key, context, severity, and cost. Similar occurrences across
workspaces link to a `CapabilityCandidate`. The capability gets its own Foundry
workspace and uses the same assumptions, experiments, evidence, decisions, and
work items as a venture.

The smallest candidate capability is piloted in a real venture. `CapabilityUse`
records the outcome and supporting evidence. Generalization is justified by
repeated successful uses, not by abstract elegance.

```text
venture friction(s) → capability candidate → minimal pilot in venture A
                   → evidence/decision → use in venture B → generalize or reject
```

This process never silently promotes a complaint into product scope. A human or
an explicitly authorized application use case creates the candidate and accepts
the decision.

### 7. Separate intent, approval, attempt, and outcome for agent actions

The Foundry can act on a venture only through application services and
replaceable adapters:

```text
WorkItem → AgentRun → proposed Artifact and/or ExternalAction
ExternalAction → ApprovalRequest when consequential → ActionAttempt → outcome
```

`AgentDefinition` and immutable `AgentVersion` identify prompt, toolset, policy,
code, provider, and runtime configuration. `AgentRun` attributes a run to that
version and a venture workspace. It may store an Agent EvalOps trace identifier,
but evaluation data remains in the separate Agent EvalOps product.

`ExternalAction` freezes the exact payload, digest, risk, cost estimate,
idempotency key, and expiry. Sending communication, spending money, destructive
operations, provisioning, and other consequential effects require an explicit
approval record before an adapter may attempt them. `ActionAttempt` stores the
provider receipt or failure. `AuditEvent` supplies technical actor/correlation
history; business evidence and decisions remain semantically distinct.

### 8. Use semantic history instead of universal SQLAlchemy-Continuum history

Do not enable SQLAlchemy-Continuum globally now. Generic row versions would
answer “which columns changed?” but not “which evidence changed our belief?” or
“which scorecard produced this rank?” They would also version high-volume link
and audit tables whose records should simply be append-only.

Use:

- explicit revisions for ideas, scorecards, agent definitions, and artifacts;
- append-only assessments, evidence, decisions, rankings, attempts, and audit
  events;
- `supersedes` or relation links where semantic lineage matters; and
- optimistic `version_id` counters for concurrent updates to mutable workflow
  state.

Reconsider Continuum selectively if a real venture demonstrates a compliance or
support need for field-level before/after history that cannot be represented as
a meaningful domain event. If adopted, it should augment rather than replace
semantic history, and its Alembic/PostgreSQL behavior must be tested first.

### 9. Keep dependency direction explicit

- SQLAlchemy is used for relational mapping and constraints.
- Alembic owns schema migrations; model `create_all()` is for tests and initial
  inspection, not production upgrades.
- Pydantic may define external command/API/agent input and output contracts; it
  does not own persistence history.
- DSPy may be used behind an agent adapter. Domain state does not import DSPy or
  provider SDKs.
- Provider, artifact storage, action, and repository/session interfaces remain
  replaceable at application boundaries.

The comprehensive schema is a map, not authorization to implement every
capability in Slice 001. The initial vertical slice still only needs local
venture memory and the narrow behavior required to register and manage Agent
EvalOps.

## Worked example

Suppose the portfolio's “Evaluation Dataset Builder” idea becomes the Agent
EvalOps venture.

1. An `IdeaRevision` narrows the customer to AI teams with human-review queues.
   An `IdeaAssessment` records the score, confidence, criterion rationale, and
   sources. A `RankingSnapshot` places it in that day's Top 25.
2. Creating the venture preserves `source_idea_revision_id`. The team records
   the assumption: “reviewed failures recur because corrections are not retained
   as regression cases.”
3. An `EXPERIMENT` work item inspects two teams' correction histories. The
   resulting `Evidence` is linked to an `AssumptionAssessment`: supported, but
   only medium confidence due to sample size.
4. A surprising observation—that teams cannot reconstruct the prompt/model
   configuration—creates a new reproducibility assumption using
   `origin_evidence_id`; it does not silently mutate the first assumption.
5. A `Decision` narrows the MVP to trace-to-case conversion. An `EXECUTION` work
   item produces a versioned trace-contract `Artifact`.
6. During the work, approval state for proposed customer emails is repeatedly
   tracked in notes. Each occurrence is friction. Similar friction in another
   venture creates the “approval-controlled external actions” capability
   candidate.
7. The Foundry pilots exact-payload approval in Agent EvalOps. The proposed
   email is an `ExternalAction`; it cannot be sent until its `ApprovalRequest` is
   approved. The result becomes evidence for or against the Foundry capability.

## Consequences

### Positive

- The current spreadsheet portfolio and future venture operation fit one
  traceable model without treating either as a throwaway import format.
- New assumptions and the distinction between discovery, testing, and delivery
  are explicit.
- Rankings, evidence interpretation, decisions, and agent configurations are
  reproducible rather than overwritten.
- Foundry product scope can emerge from measurable cross-venture friction.
- SQLite gives immediate local use; PostgreSQL remains a deployment choice
  rather than a domain migration.

### Costs and limitations

- Forty-three normalized tables are more schema than Slice 001 will expose. The
  application must implement narrow use cases rather than generic CRUD for all
  tables.
- Some invariants span tables—for example workspace kind matching its specialized
  entity—and must be enforced in application services and tested.
- SQLite does not model production concurrency or all PostgreSQL behavior; later
  slices must exercise migrations and transaction behavior against PostgreSQL.
- Append-only policy is not fully expressible through portable constraints. The
  application layer and focused database permissions/triggers may strengthen it
  when needed.

## Revisit when

- two or more real ventures need a missing relationship or materially different
  workflow;
- multi-user concurrency or deployment requires PostgreSQL;
- a compliance case requires generic field-level history in addition to semantic
  history;
- workspace ownership or tenancy needs access-control boundaries;
- action policies require multiple approvals or role separation; or
- the normalized schema produces measured friction that a narrower read model or
  event stream would solve.
