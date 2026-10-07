# Venture modules and implementation delivery

## Common workspace and optional modules

The user is describing two product levels: Foundry coordinates a portfolio, and a
venture has its own operating context. Support that now through workspace-scoped
navigation/data, without a deployment, plugin system or database per venture.
Software businesses can also have suppliers; venture type must not become one
exclusive enum that dictates everything.

Keep state, objective, score, next work, evidence, decisions, history and a small
business summary common to every venture. Store venture preferences as versioned
`venture-workspace-config/v1` Artifacts, with expected latest revision and actor;
do not infer permissions from arbitrary `IdeaRevision.venture_type` strings.

| Component | Deliver now | Later trigger |
|---|---|---|
| Common business summary | Show maturity and reported revenue/cost status; unknown remains unknown | Accounting/payment integration only when an operating venture needs it |
| Software module | Linked repositories/checkpoints, latest known runtime/test result with date, links to recorded bugs/security work, next technical action | Automated issue/code/security integrations after an actual chosen repo workflow |
| Outreach module | Contextual list/create/edit/export using existing draft service, and recorded responses | Sending provider only under existing exact-payload approval rules |
| Research and trial work | Existing Work/Evidence/Decisions, with venture-specific descriptions and templates | A new domain tool only after a real repeated task cannot use these components |
| Suppliers and operations | Document the future boundary; no empty Suppliers tab or supplier schema now | A real venture with named supplier/quote/lead-time work |
| Sports or route product tools | Link the investigation briefs; no product algorithms/screens in Foundry now | Separate justified implementation task for that venture |

Common business summary may use an optional validated `venture-metrics/v1` Artifact
with append-only snapshots: measure, value nullable, currency/unit, period,
`reported_actual`/`estimate` label, source and recorded-by/time. Support a small
manual form for reported revenue and costs, with explicit unknown, as part of V05.
Do not derive actual revenue from `IdeaAssessment.revenue_year_1/year_3` or original
mature-monthly ranges. Show estimates in a separately labeled forecast section,
never as money earned. Do not convert currencies or build accounting.

For Software, reuse `projects.py` checkpoints and linked WorkItems. Represent
optional bug/security categorization as a small validated companion Artifact
referencing the WorkItem, with reported severity/source/date; generic WorkItem
status remains the lifecycle. A missing assessment means **Security status not
assessed**, not “secure”. A claimed issue is distinct from a confirmed incident.
Retain sanitized summaries and links, not credentials or sensitive exploit traces.
Merely viewing a repository reference must not read or execute its code.

The initial allowlisted built-in registry needs only `software` and `outreach`.
A specification can describe key, label, required context, renderer/data service
and available actions. Users enable/disable these through **Workspace settings**;
defaults can be suggested from existing checkpoints. Hiding a module preserves
its data and links. Direct module routes still enforce venture scoping and explain
a disabled module; core work remains accessible. No dynamic imports, downloaded
plugins, arbitrary shell buttons, external marketplace or new framework.

Demonstrate the same shell with Coopain (Software/Outreach enabled), a concept
sports venture (core plus trial work), and a route investigation (core evidence
and route brief). Supplier capabilities remain a documented extension, not a
fake functional tab. The actual Coopain codebase and Agent EvalOps remain outside
Foundry runtime imports; `learning/` is never a runtime dependency.

## Backend changes and reuse

Recommended schema addition is seven tables, split into focused migrations:
three venture-scoring tables, two human-request tables and two proposal tables.
Their contracts live in the linked specifications and proposed ADR. Reuse
Artifacts for immutable payload revisions, WorkItems for execution, Reviews for
state, and AuditEvents for transitions. Reuse the current SQLAlchemy UnitOfWork;
avoid one route directly calling multiple independently committing services.

Refactor session-aware internal operations where a fusion/review requires one
transaction. Keep public interfaces typed and storage/provider boundaries intact.
All request/response/proposal/config payloads have schema versions and bounded
Pydantic validation. Add indexes/unique/check constraints for specified identities
and revisions. SQL list filtering/counting/pagination must remain correct; do not
load all records into templates or create a per-row query waterfall.

Database migrations are additive and schema-only, starting from the actual current
Alembic head. Campaign bootstrap/intake is a separate explicit idempotent command.
No rewriting original assessments, copying every Evidence row, or generic event
sourcing rewrite. Store JSON only for typed immutable snapshots, not to avoid
essential target/participant foreign keys and queryable workflow state.

## Task boundaries for a smaller agent

| Task | Primary files to read/change | Required result before moving on |
|---|---|---|
| V00 | Root/Foundry instructions, this baseline, migration/storage docs, relevant existing tests | Effective file/DB identities, backup integrity, frozen test cases and clear distinction between current failures and new red tests |
| V01a | `domain.py`, migrations, `human_inputs.py` new, request CLI/API, `reviews.py` inbox compatibility | Persisted request/response model; file preview/sync and UI submission share service; repeated/corrected/conflicting responses behave correctly |
| V01b | Same service, `steps.py` context seam, `console_commands.py`, explicit new intake script, CURRENT_DIRECTION.md | Claim/review/export loop; old receipts preserved; R005–R009 outcomes applied; precise next work, held tracks quiet |
| V02 | `scoring.py`, `domain.py`, `views.py`, migrations, score DTO/components/CLI | Independent assessments and copied baselines; correct list/detail selection; partial/stale/cross-workspace checks |
| V03 | `web.py`, `templates/`, `static/console.css`, `static/console.js`, help | Header IDs/scores; scoped shell; contextual answers; functional portfolio attention queues; form errors retain user input |
| V04a | `proposals.py` new, domain/migration, proposal views/CLI, source-detail cards | Pending sports proposal with complete comparison and rationale; edit/reject preserve history and source records |
| V04b | Proposal service, session-aware portfolio/review operations, transactions tests | Atomic application/reversal on fixtures; source history retained; live proposal stays pending without acceptance |
| V05 | `workspace_modules.py` new, `projects.py`/`outreach.py` reuse, config/metric forms, related templates, inquiry brief artifacts | Two selectable built-ins, business summary, Software example and R005–R007 next-test briefs; no sports/route product build |
| V06 | Focused new tests, existing suites, DBML/DEVELOPMENT/help, STATE.md | Migration rehearsal, full required checks and truthful desktop/mobile browser results |

Use the root `.venv` as documented. New tests should be named for behavior, e.g.
`test_human_inputs.py`, `test_venture_scoring.py`, `test_portfolio_proposals.py`,
`test_workspace_modules.py` and a focused end-to-end console flow. Existing
`test_handoff_console.py`, `test_workspace_reviews.py`, `test_portfolio_views.py`,
`test_portfolio_scoring.py`, migration and transaction tests provide patterns.

Avoid giant rewrites of `web.py` or `domain.py` to satisfy style preferences.
Small helpers/shared partials are useful where the new behavior needs them.
Document the final actual routes and CLI, not commands merely proposed here.

## Data migration and rollback procedure

Before implementation, record git status in root and submodule, effective source
digests, resolved DB location, Alembic head and relevant row IDs/counts. Back up
with the existing SQLite backup service and verify integrity. Do not use a raw
file copy of an active WAL database as the only backup. Rehearse upgrades and
bootstrap on a copy; production intake happens only after the rehearsal passes.

Require `PRAGMA integrity_check` and `foreign_key_check` on the upgraded SQLite
copy, SQLAlchemy/Alembic schema parity, restart persistence and repeat-zero intake.
Verify old idea scores, immutable source revisions, historical requests, existing
outreach drafts and source-workspace URLs retain their identities and values.
New tables must not require an installed memory service, provider or worker.

Rehearse supported PostgreSQL behavior through the repository's disposable test
path if available. Record an unavailable environment as a gap, not proof of
compatibility. Keep default operation local. If reverting an application release,
stop its process and use the preserved pre-upgrade backup in an isolated path;
retain the post-upgrade database. Do not destructively downgrade a populated store
or replace the live file automatically during testing.

## Checks and browser acceptance

Start each task with relevant failing tests. Run focused checks as it changes;
perform broader verification once integrated, or earlier for a justified regression:

```text
.venv/bin/pytest -q foundry/tests/unit foundry/tests/integration foundry/tests/acceptance/test_cli_workspace.py foundry/tests/contract/test_package_boundary.py
.venv/bin/ruff check foundry/src foundry/tests tests
.venv/bin/mypy --config-file foundry/pyproject.toml foundry/src
make check
```

`make check` includes repository-required workflow/container checks. Use existing
local fixtures/infrastructure and document exact failures or unavailable checks;
do not add cloud provisioning or weaken tests. Deferred EvalOps/learning contracts
remain distinct; this revamp does not earn learner credit or repair unrelated
intentionally red contracts. Do not claim the previous 87 passing tests as this
change's result.

Browser acceptance must use the running app with disposable data at desktop and
mobile sizes. HTTP/HTML assertions complement these tasks but cannot certify
layout, focus, clipping or successful real form interaction:

1. From portfolio, open P103 and its venture; find both IDs, score meaning and
   next action without searching a record list. Capture initial viewport images.
2. Answer R006 from a venture; verify confirmation, exact saved text and pending
   review. Edit a fixture file, sync, review via a manual agent/service, and see
   the next task update without falsely claiming a worker ran automatically.
3. Demonstrate deferred R008/R009 are visible as holds but absent from “Needs you”
   and ready venture-investigation queues.
4. Append a venture score, refresh/restart, inspect history and verify list sorting.
   Demonstrate unknown, zero, partial and source-baseline cases.
5. Read the sports comparison, edit a proposal with reason, reject a disposable
   proposal, and accept a different fixture. Visit old source URLs, new lineage,
   shared answer and reversal history. The user's real proposal remains pending.
6. Open Coopain with Software enabled; see repo/checkpoint and honest test/security
   status. Toggle modules without losing records. A sports concept has no empty
   supplier/code dashboards.
7. Exercise keyboard navigation, mobile tab overflow, visible focus, error recovery,
   long IDs/titles, escaped HTML, empty states and back-to-filtered-list navigation.

If no browser is exposed (as in this planning session), finish independent work
and explicitly retain visual acceptance as pending. Do not mark the whole revamp
complete on HTTP checks alone. Record issues and screenshots locally without
exposing private GPX, participant information or secrets.

## Completion contract

The final implementation report must identify changed behavior and actual checks,
link the pending sports proposal, state whether latest answers were imported and
reviewed, list remaining human/external gates, and distinguish saved/queued work
from running/completed work. Preserve all source reports. Avoid claims of improved
fairness, faster planning, adoption, security or revenue without relevant evidence.
