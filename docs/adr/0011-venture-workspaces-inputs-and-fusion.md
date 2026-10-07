# ADR 0011 Venture workspaces inputs and fusion

Date: 2026-10-04. **Status: implemented 2026-10-05**, after the user requested
execution of the handoff. Three additive migrations and explicit campaign intake
are applied to the permanent local store. Browser acceptance and the official
container build remain pending; see the
[execution report](../inquiry/revamp-2026-10-05/REPORT.md).
This architecture decision does not accept the real sports fusion, which remains
a pending exact-revision proposal.

## Context

Actual operator feedback exposes missing venture IDs/scores on details, unclear
places to answer questions, no reliable pickup of dated follow-up replies, and
overlapping sports ventures without a reviewable consolidation decision.
Repository inspection confirms list scores belong to source ideas, answer-state
detection covers only R001–R004, and record-heavy venture pages have no contextual
answer form. The product already has useful immutable records, reviews,
work items, scoring rules, checkpoints, drafts and a replaceable runner seam.

The user also needs portfolio management distinct from each venture's working
environment. Real ventures differ in operational needs, but there is not yet a
case for a generic plugin platform or separate deployments per workspace.

## Decision

Retain the local modular monolith, FastAPI/Jinja, SQLAlchemy, Alembic and existing
SQLite/PostgreSQL boundary. Provide portfolio-level attention/comparison/proposal
views and a scoped venture shell with persistent identity/score and contextual
next action. Preserve original definitions and independent products.

Add independent append-only venture assessments using the existing scorecards
and calculation. Snapshot source idea scores explicitly as baselines; never let
venture evolution overwrite original ideas or let later idea scores silently
move venture baselines. Keep unknown totals, provenance and version comparability.

Add durable HumanRequest and target records, with immutable response/review
Artifacts. Treat Markdown files as supported input sources and the database as
the saved operational state. Synchronization is explicit and repeat-safe; file
and UI conflicts preserve both candidates. Queue and claim review through existing
WorkItems. No answer automatically runs an agent or closes validation work.

Add versioned portfolio fusion proposals and typed participants. Acceptance binds
an exact proposal revision and rationale to atomic local effects. Create a new
composite idea/venture; preserve source histories, lineage, shared evidence and
reasoned reversals. Default to human acceptance; future delegated decisions need
explicit authority. For P023/P103 recommend a volleyball-first combined
investigation, but retain its pending decision state until accepted.

Use seven targeted new tables: VentureAssessment, VentureCriterionScore,
VentureCriterionScoreEvidence, HumanRequest, HumanRequestTarget,
PortfolioProposal, ProposalParticipant. Reuse typed Artifact snapshots and existing
Review/WorkItem/AuditEvent/Decision models elsewhere. Keep domain transactions
atomic and enforce identity/reference/concurrency constraints. Schema changes and
idempotent campaign bootstrap are separate operations.

Make Software and Outreach built-in optional modules with a static allowlist,
versioned workspace configuration and existing service adapters. Keep common
state, work, evidence, history and explicitly sourced business metrics available.
Defer supplier tooling, dynamic plugins, autonomous dispatch and venture-specific
product algorithms until real work justifies them.

## Alternatives considered

A cosmetic template-only fix would expose IDs and source scores but would leave
venture evolution, answer pickup and safe fusion unresolved. Continuing with
hardcoded dated scripts would repeat the R005–R009 detection gap. Conversely, a
frontend rewrite, generic workflow engine, event-sourced rebuild or plugin
marketplace would expand cost without evidence of need. Reusing IdeaAssessment
for ventures would conflate distinct subjects and constrain existing projects.

## Consequences

The schema and service surface grow modestly and require migration/transaction
tests. Existing imports and historical identifiers survive. A native venture
assessment and an inherited idea baseline require clear labels throughout UI,
CLI and API. File editing remains convenient, but users need visible sync and
conflict status. Optional modules cannot change core identity or action authority.

The application can queue work truthfully without an unattended worker. Humans
still explicitly initiate agent sessions and approve exact consequential actions.
Holding or consolidating a venture remains separate from validation outcomes.
Learning stays paused, Hindsight optional, and external spending/sending/publishing
rules unchanged.

## Revisit conditions

Revisit the module boundary when two ventures need the same genuinely new tool;
consider extraction only then. Revisit dispatch when manual pickup repeatedly
loses work and a bounded runner has reviewed inputs/results, cost limits and
recovery semantics. Revisit scoring abstraction if maintaining idea and venture
assessment persistence duplicates substantial behavior beyond their tables.
Revisit proposal generality when another real split/pivot/fusion requires different
effects. Consider deployment/storage changes only after measured operational need.

Detailed contracts, task order and acceptance:
[venture workspace revamp handoff](../plans/2026-10-04-venture-workspace-revamp/README.md).

## October 6 repair

The [acceptance review](../inquiry/revamp-review-2026-10-06/REPORT.md) found that
workspace membership alone was insufficient dependency ownership. Add one narrow
`HumanRequestDependency` table: explicit target/work cause, exact response that
satisfied it, other unresolved causes and optimistic version. Keep earlier target
work links as compatible explicit dependencies. No-change cannot mutate targets;
partial/deferred cannot close dependencies; sufficient closes work only after all
registered causes are satisfied. Corrections invalidate satisfaction. Do not infer
these links from a completion payload or silently backfill historical completion.

Pending fusion identity uses a portfolio/kind/source-set hash and a unique index,
separate from request-key receipts. Changed scope needs a revision or explicit
supersession. Stored acceptance includes complete result definition/workspace,
score and request context; later changes require exact downstream treatment on
reversal. Keep source/composite history and human decision boundaries.

Promotion queues a deterministic manual intake task and copies only that venture's
pinned source assessments in its transaction. An explicit separate venture ID
expresses a deliberate second investigation. Initial review completion atomically
retains research/evidence, unknown reasons, an assessment, state and scoped next
work/input. It uses existing records and manual runner boundaries, with no worker.
Typed detail queries and one URL contract preserve score/portfolio context;
structured proposal fields and scoped readable work/state links expose the stored
effects. The [repair report](../inquiry/revamp-fixes-2026-10-06/REPORT.md) records
checks, migration preservation and remaining browser acceptance.
