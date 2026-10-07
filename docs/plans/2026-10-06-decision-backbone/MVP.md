# Lifecycle decision MVP

2026-10-06. The user authorized implementation, refactoring and synthetic trials.
This supersedes the earlier stop-after-planning instruction and makes paid
execution/training a later concern. Implemented status is recorded in STATE.md.

## Target

A local, single-operator venture workbench usable with an existing agent, from
initial discovery through an operating venture's repeated decisions. A user can
capture a change, see its relationship to current work, hand sufficient context
to an agent, review an attributed result, and resume after a restart. Portfolio
coordination remains separate from each venture's authoritative history.

The MVP includes the existing portfolio, scores, input reviews and fusion; the
intake repairs; a small versioned decision map; change/coverage visibility;
agent context and result contracts; CLI and readable local UI; explicit outcome
and work consequences; portable snapshots and documented recovery. A synthetic
demo must cover discovery, operating software and supplier operations. An
operating venture must not be reset to concept/triage by a later investigation.

No paid executor, training, unattended external action, hosted multi-user service,
general workflow canvas or plugin framework is required. Shipping means a tested
local distribution/container and documented run/upgrade/backup path. Publication,
external deployment and credentials are outside this authorization.

## Acceptance before implementation

- Existing tests are the regression baseline; add red behavior tests for the
  new contracts before implementation. All failures remain visible.
- Stop/hold can finish without a new task; promotion avoids duplicate intake.
- Current and historical maps retain exact scope, relationships and rationale.
- Changed dependencies affect only explicitly dependent work. Existing claim and
  execution paths enforce unresolved review; unrelated work remains usable.
- Context includes counterevidence and exposes unclassified arrivals, omissions
  and required fetches. No invisible relevance or completeness claim.
- Stale results are retained but cannot alter current state; accepted effects are
  atomic, repeat-safe, scoped and audited. No automatic score increase.
- CLI and UI complete create/resume/submit/review/restart loops without SQL or
  mandatory raw JSON editing in the human flow.
- Meaningful unit/integration/CLI checks, real browser desktop/mobile interaction,
  lint/types, migration/restore rehearsal and the existing container gates pass.
- Synthetic lifecycle replays test known changes, contradiction, pivot, restart,
  duplicate and stale results. Token savings remain unclaimed without telemetry.

## Provenance and working order

Root HEAD: e6a83e470d052439e5c8d4a943428f5bbd132f7f.
Foundry HEAD: 3b082507062838df4009d4b636c4f320436f3b41.
Both trees were dirty before work. Baseline hashes and diffs are retained in the
ignored `.local/lifecycle-mvp-2026-10-06/` folder. Preserve unrelated work.

Work order follows CHUNK_1.md: repairs, typed map/storage, context, results and
eligibility, agent commands, UI, lifecycle trials and release checks. Refine
contracts where repository evidence requires it and record material deviations.
No production database trial fixtures; rehearse migrations on a backup first.
