# Foundry development

## Standalone environment and checks

Run commands from this Foundry repository, including when it is nested under
Startup Lab. No parent checkout or learning directory is required. Use Python
3.11+ (default/recommended 3.13), GNU Make and uv. CI pins uv 0.12.4; local 0.11.29
is also exercised. The committed lock controls runtime and development packages.

```bash
make bootstrap                         # uv sync --locked --group dev
make check                             # Ruff, strict mypy, product + CI contracts
uv run playwright install chromium     # one-time browser binary install
make test-browser                      # actual desktop/mobile Chromium workflows
make verify-distribution               # isolated wheel install, migration/recovery/HTTP
```

`make bootstrap PYTHON_VERSION=3.11` selects the other supported CI Python.
`make test-product` runs unit/integration/CLI/package tests. The PostgreSQL CLI
case skips unless an explicit **disposable test** `FOUNDRY_DATABASE_URL` is set;
CI runs it in a separate PostgreSQL 18 service. Never aim tests at the operator
store. Use `make workflow-lint` and `make test-container` with Docker/Compose
available. Container acceptance creates unique disposable projects and removes
only their own resources. `make check` does not require Docker or include deferred
EvalOps/learner exercises.

A distribution check refuses an existing output directory. Choose a new one for
another run, e.g. `make verify-distribution DIST_VERIFY_ROOT=/tmp/foundry-dist-2`.
The target builds wheel/sdist, exports hash-locked runtime dependencies, installs
into an isolated venv and calls `scripts/verify_distribution.py`. This stdlib
harness imports from that venv, runs from an empty cwd, creates only synthetic
stores, exercises migrations/lifecycle resume, refuses backup overwrite, restores
and integrity-checks a copy, and starts/stops the packaged HTTP app twice. CI runs
this on both supported Python versions. Review its `smoke/summary.json` and logs.

Keep failed current-scope acceptance separate from green regression evidence;
do not skip or weaken tests to claim completion. Add tests around real changed
behavior, especially stale/conflicting writes, ownership and transaction rollback.

## CI and delivery

`.github/workflows/ci.yml` verifies pushes/PRs to main with Python 3.11/3.13, lint,
strict typing, locked dependencies, workflow checks, CLI and desktop/mobile browser
flows, standalone wheel recovery, PostgreSQL migration drift, and a non-root
image/Compose contract. Its final `ci` job requires every verification job to pass.
Retained artifacts contain synthetic test/coverage/distribution evidence, not
operator databases. Actions are pinned; permissions are read-only for validation.

Manual/scheduled `delivery.yml` calls the same image workflow. It defaults to
validation. Publishing additionally requires an explicit manual request, main,
a target environment and write permissions; a source push does not publish an
image or deploy an application. Historical learner attribution remains in the
parent Startup Lab learning records, if that optional checkout is available.
No learning slice is active or required to develop/run this product.

## Local data

Use a path ending in `.local.db` for SQLite experiments so Git ignores it. Keep
WAL/SHM sidecars out of Git as well. Never store credentials or sensitive
customer traces in the workspace. The completed container slice adds only a
local PostgreSQL container; it has no provider integration or cloud
requirement.

## Container lifecycle

The Compose topology keeps Foundry as an ephemeral CLI, with a healthy PostgreSQL
service and one-shot migration. It does not publish a database port. Runtime
configuration is local and must not be baked into the image or committed.

The configuration scaffold currently reads real process environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `FOUNDRY_DATABASE_URL` | Absolute SQLite URL under XDG data home | SQLAlchemy/Alembic database |
| `XDG_DATA_HOME` | `~/.local/share` | Parent of `startup-foundry/foundry.local.db`; must be absolute |
| `FOUNDRY_REQUESTS_DIR` | Repository `requests/`, otherwise XDG data directory `/requests` | Editable handoffs/inbox |
| `FOUNDRY_DEBUG` | `false` | Application diagnostic mode |
| `FOUNDRY_SQL_ECHO` | `false` | Explicit SQL statement/parameter echo |

The host CLI needs no `.env` for local SQLite. For Compose development, copy `.env.example`
to `.env.dev`, replace the password placeholder with a generated URL-safe local
value, and run from this repository. Compose passes that product-local file to every
service, so later `docker compose run` commands do not need to repeat
`--env-file`. Both populated files are ignored and must not be committed.

`python-dotenv` affects only the CLI adapter, which merges sources in this
order: CLI options, real process environment, `.env`, safe local default. The
shared settings parser and Alembic do not search for dotenv files implicitly;
Compose supplies their process environment. SQL echo remains separate from
DEBUG because emitted bound parameters can disclose venture data. Expected
errors carry a correlation ID in stderr logs without logging command payloads.

## Container commands

Run these from this repository after copying `.env.example` to the
ignored `.env.dev` and replacing its password placeholder:

```bash
make foundry-up
make foundry FOUNDRY_ARGS='venture show --id venture-1'
make foundry-down
```

`foundry-up` waits for a healthy database and runs the migration. `foundry`
starts one ephemeral CLI container. `foundry-down` removes containers and the
network but preserves PostgreSQL data. To deliberately delete that data, run
`make foundry-reset CONFIRM=yes`; the confirmation prevents an accidental
volume reset.

## Database lifecycle

Every normal application command applies checked-in Alembic migrations before opening its
application session. Startup never calls `Base.metadata.create_all()`. Each
application operation uses one `UnitOfWork`: repositories and use cases flush as
needed, while the unit of work alone commits or rolls back and closes the
session. This makes experiment work, experiment metadata, and assumption links
atomic.

## Disposable migration drill

Run destructive downgrade practice only against a newly created disposable
directory, never against a venture database:

```bash
FOUNDRY_L004_TMP="$(mktemp -d)"
export FOUNDRY_DATABASE_URL="sqlite:///$FOUNDRY_L004_TMP/foundry.local.db"

uv run alembic upgrade head
uv run alembic current
uv run alembic downgrade base
uv run alembic upgrade head
uv run alembic check
```

Verification should assert revision/table state and that no
default database appeared elsewhere; a successful command transcript alone is
not a transaction or migration test.

## Layout

- `src/startup_foundry/` — local lifecycle product package.
- `tests/unit/` — focused application, configuration, migration, and transaction
  behavior.
- `tests/integration/` — relational schema and repository integration.
- `tests/acceptance/` — CLI-workspace and container-stack end-to-end behavior.
- `tests/contract/` — package-boundary and accepted CI workflow structure.
- `.github/workflows/ci.yml` — read-only verification workflow with a
  learner-authored foundation and agent-authored production hardening.
- `.github/workflows/delivery.yml` — reviewed manual/scheduled delivery caller.
- `.github/workflows/reusable-image-delivery.yml` — reviewed reusable image
  validation/publication workflow.
- `.github/actions/release-metadata/action.yml` — reviewed local composite
  metadata action.
- `docs/` — the preserved product brief, usage guides, ADRs and release documentation.


## Permanent local workspace and console

Run `make foundry-ui` from the root, or `foundry ui --port 8765` from an installed
environment. It serves `http://127.0.0.1:8765` until Ctrl-C. `make foundry-local
FOUNDRY_ARGS='venture list'` uses the host database; the existing `make foundry`
uses Compose's PostgreSQL and is a different store. `foundry storage info` shows
the effective database (password redacted) and inbox path. Explicit CLI/environment/
dotenv configuration still takes precedence over the stable default.

The adopted desktop store is `~/.local/share/startup-foundry/foundry.local.db`.
`foundry storage backup --output /absolute/new-backup.local.db` performs a consistent
SQLite backup without changing schema or overwriting a destination. Backups stay
on this machine; an off-machine backup policy is not configured. To inspect a
backup without changing the working database, use `foundry --store
/absolute/new-backup.local.db venture list` (normal reads may apply newer
migrations, so inspect a copy if preserving the backup byte-for-byte matters).
For restoration, stop the UI, preserve the current database using the backup
command, and use a copy of the selected backup through `FOUNDRY_DATABASE_URL`;
verify `storage info`, counts and venture history before switching the default.
Do not merge stores or overwrite a live SQLite file by hand.

The one-time `scripts/adopt_local_workspace.py` reconciled existing trial stores
and six specific startup CSV exports; it refuses an existing target. The generic
`portfolio import --csv-directory ... --campaign-directory ...` command expects
the reviewed campaign's `ideas.json`/`sources.json` plus those named exports.
Identical imports are idempotent; changed imports with existing idea IDs stop for
explicit revision review. It is not an arbitrary spreadsheet inference service.
Source rows are retained as untrusted source material. Generated/dashboard tabs
are views of existing ideas, not extra intake. The original campaign report is
historical; it is not silently rewritten after product code changes.

## Steps, derivations and later agents

`idea create` accepts repeated `--parent-id` and a `--derivation-reason`. The UI's
Derive or combine form records the same lineage. `idea promote --id ...` opens an
investigation workspace without asserting commercial viability. Source reuse is
available through `PortfolioService.record_source`; this round's bookkeeping is
`scripts/record_console_investigations.py`. No automatic idea generator is installed.

`step catalog`, `step list`, `step show --id ...` and `step start` expose durable
execution. Readiness checks presence of inputs; research_brief prepares a comparison
protocol. `agent_research` without an adapter creates a blocked `agent-*.md` request.
Replies in those files or `requests/INBOX.md` are reviewed in the next agent session;
there is no background watcher or automatic response ingestion. A process killed
mid-step may leave `running`; use `step recover --id ... --reason ...`, then a new
request key to retry. Successful/failed/blocked outcomes cannot be overwritten by
recovery. Idempotency does not rerun an old key with new context.

A future local runner implements `AgentRunner.name`, `.version`, and `.run(context)`.
Inject it in `StepService`; provider/tool execution stays outside the domain.
Before enabling it in the console, add the provider's timeout/resource policy,
reviewed examples and task-specific held-out comparisons. Recorded runs are not
automatically approved training data. Keep synthetic examples labeled, compare
fine-tuning to a prompt-only baseline, and separate quality from commercial value.
The current request explicitly defers downloading models and training them.

## Portfolio and existing-project operation (October 4)

The shared SQL query powers `idea list`, `venture list`, HTML and JSON lists.
Use `--disposition`, `--investigation-stage`, `--product-maturity`, `--blocker`,
`--score-view original|reviewed|SCORECARD_ID`, `--criterion`, `--min-score`,
`--sort score|priority|stage|recent|name|id`, `--direction asc|desc`, `--limit` and
`--offset`; venture lists also accept `--stage`. Unknown scores sort last and
filters/pagination persist in links. Empty filters mean all, including dropped/held.

```bash
foundry score import-original --sources-directory docs/sources
foundry scorecard list
foundry score show --idea-id P046
foundry score sensitivity --idea-id P046 --scorecard-id portfolio-original-v1
foundry score assess --input assessment.json
foundry scorecard import --input scorecard-v2.json
foundry score rank --scorecard-id portfolio-reviewed-v1 --label reviewed-20261004
foundry review import-legacy
foundry review show --workspace-id WORKSPACE_ID
foundry review append --input review.json
foundry existing-project intake --input checkpoint.json
foundry existing-project show --venture-id v-coopain
```

Original workbook import is atomic and immutable: Decimal formula with penalty
`raw-1`, half-away rounding, 12 factors, original recommendation/confidence and
monthly-revenue provenance. It reuses the source digest across relocated files.
Reviewed assessments explicitly supply or carry factors; null/omitted scores mean
unknown and prevent a total. Year-1/year-3 revenue fields remain null. Scorecard
JSON requires `id`, `name`, `version`, `rationale` and unique criteria with `key`,
`name`, `direction`, `weight`, scale 1–10. Changing an existing method is rejected;
use a new ID/version. Rankings record exact latest comparable assessment IDs.

Example partial assessment (no inferred neutral factors):

```json
{"idea_id":"P046","scorecard_id":"portfolio-reviewed-v1","scores":{"mvp_speed":8},"rationale":"Existing code inspected; runtime, payer and adoption still unknown","author":"operator","confidence":"low"}
```

Review JSON needs `workspace_id`, `expected_revision` (zero for first),
`investigation_stage`, `product_maturity`, `disposition`, `reason`, `next_action`,
`author`, optional same-workspace `next_work_item_id`, `source_artifact_id` and
`decision_id`. Stale/cross-workspace writes fail. WorkspaceReview is append-only;
Venture.stage and Idea.status retain their existing meanings. The schema-only
migration is `9af261004001`; legacy campaign state is an explicit idempotent backfill.

Existing-project manifests use `existing-project/v1`; the actual Coopain manifest
under `docs/inquiry/handoff-2026-10-04/` is a complete reference. Repository refs
are data: HTTP never recursively reads or executes them. Same manifest is reused;
a changed manifest appends a checkpoint and review with expected review revision.
The UI has `/existing-project`, contextual checkpoint links and history.

## Manual outreach

```bash
foundry outreach list --venture-id v-receipt
foundry outreach create --venture-id v-receipt --request-key unique-key --input draft.json
foundry outreach show --id DRAFT_ID
foundry outreach revise --id DRAFT_ID --expected-version 1 --actor operator --input draft.json
foundry outreach export --id DRAFT_ID --format text --output new-draft.txt
foundry outreach export --id DRAFT_ID --format eml --output new-draft.eml
foundry outreach record-outcome --id DRAFT_ID --input outcome.json
```

Draft JSON fields: `purpose`, `subject`, `body_text`, `language` (en/fr), `tone`
(formal/informal), optional `sender_identity` (unverified), `to`, `cc`, `bcc`,
`attachment_artifact_ids`, `source_evidence_ids`, `related_request_id`.
Mode remains `manual`; no provider exists. Snapshot/AuditEvent history complements
optimistic version locking. Missing recipients are visible. Header injection and
cross-workspace references fail. Text export lists selected attachment IDs without
reading files. `.eml` exports only selected registered files with matching SHA-256,
regular-file/2 MB bounds, no symlinks and approved-root checks; mail-client import
has not been tested. Export files are created without overwrite.

`FOUNDRY_ATTACHMENT_ROOTS` is an OS-path-separator list of local approved directories;
default `~/.local/share/startup-foundry/outreach-attachments` (under XDG data home
when configured). It is independent of HTTP inputs. Registration plus explicit
selection is required; arbitrary paths/HTTP URLs are not fetched.

Outcome JSON: `kind` sent_manually/reply, `draft_revision`, `actor`, timezone-aware
`stated_at`, `summary`. It creates attributed Evidence linked to the exact snapshot,
never a provider ActionAttempt or delivery receipt. Approval-required PROPOSED
actions remain drafts; manual outcome labels do not grant future send permission.

HTTP mutations still need the per-process local token and same Origin. `/help`
explains actual flows. The dated follow-up file leaves original inbox responses
untouched; the explicit October 4 scripts retain receipt digests and findings.
Real user trials and venture runtime checks remain separate from Foundry's
synthetic tests. Actual Foundry browser checks are described above.

## Venture workspace revamp (ADR-0011)

The permanent store remains authoritative. Schema-only migrations add two human
input tables, three independent venture score tables and two fusion tables through
`b10261005003`. No migration imports answers or accepts a proposal. Back up a
file-backed SQLite database with `foundry storage backup --output PATH` before
upgrading; this uses SQLite's online backup, including committed WAL content.
Rehearse on a copy. Check `PRAGMA integrity_check`, `foreign_key_check` and Alembic
`command.check(alembic_config(url))`. Retain the pre-upgrade and post-upgrade stores.
For rollback stop the app and use a pre-upgrade backup at a separate configured
path; do not downgrade a populated database or automatically replace the live file.

Explicit campaign registration and reviewed intake are:

```bash
.venv/bin/foundry workspace bootstrap --review-latest
```

This is specific to the preserved R001–R009 campaign. It links the original four
receipt IDs through typed response/review artifacts, imports the five newer answers,
records narrow review outcomes, snapshots source score baselines, enables Coopain's
Software/Outreach modules, saves the preparation briefs, and seeds a **pending**
sports proposal. `--review-latest` requires the documented October 4 follow-up file
digest; changed answers must be interpreted manually. Repeating the command creates
no duplicate responses, reviews, baselines, briefs or proposal. It does not start a
worker, conduct a trial, accept a fusion or send anything.

General ongoing workflow (JSON inputs are bounded to 100 KB):

```bash
.venv/bin/foundry input list --status awaiting_review
.venv/bin/foundry input show --id R006
.venv/bin/foundry input preview > /tmp/foundry-input-preview.json
.venv/bin/foundry input sync --preview /tmp/foundry-input-preview.json
.venv/bin/foundry input handoff --id R006 > /tmp/foundry-R006-handoff.json
.venv/bin/foundry input claim --id R006 --input claim.json
.venv/bin/foundry input complete --id R006 --input review.json
```

`claim.json` has `expected_version` and `actor`. Completion has exact `work_id`,
`response_id`, `actor`, `interpretation`, `outcome` (`sufficient`, `partial`,
`deferred`, `no_change`), `rationale`, remaining unknowns, score explanation and
optional typed per-target changes. Only this answered human dependency closes;
other runtime/access/rights/validation causes remain open. Interrupted reviewers
use `input release --id R006 --input release.json`, including expected version,
claimed work ID, actor and reason. Nothing silently times out. A review of an older
reply remains historical while a newer reply stays pending.

`input register --input request.json` creates or explicitly revises a request.
`input submit --id R006 --input response.json` requires expected version, exact
text, author and submission key. File/UI conflicts require `input sync ...
--reconciliation keep_ui` or `use_file`; the candidate and earlier response remain
retained. UI answers never rewrite Markdown. Read-only source detection registers
only named sections, rejects traversal/symlinks/nonregular/oversized/non-UTF-8 sources
and does not ingest arbitrary `agent-*.md` output. Question-only edits do not create
fake answers. Saving/syncing queues a ready review WorkItem without calling a model.

Independent scoring: `venture-score bootstrap`, `venture-score show --id V
[--scorecard-id CARD]`, and `venture-score assess --input assessment.json`.
Native inputs require venture ID, card (default reviewed), expected latest sequence,
request key, scores, author and rationale. Unknown factors produce a partial total;
numeric zero is valid. Evidence must belong to that venture. Copied source baselines
retain original assessment IDs/assessors and never refresh after source rescoring.
Headers prefer native reviewed scores, then copied reviewed baselines, then original
fallback. Lists default to reviewed, rank only their selected card and factor, and
sort missing values last. `--score-view original` preserves the workbook view.
`--continued exclude` filters sources of applied proposals; All retains them.

Proposals: `proposal list`, `show --id ID`, `create --input fusion.json`, `revise
--id ID --input revision.json`, `resolve --id ID --input decision.json`.
Resolution needs exact `revision_id`, expected proposal version, action
(`accept`, `reject`, `reverse`), rationale, actor, explicit `actor_kind` (`user` or
`agent`), and request key. Agent decisions require an existing exact human delegation
receipt, registered through `ProposalService.delegate`; arbitrary actor text or
answer Markdown provides no authority. No such delegation exists for the real sports
proposal. An edited/stale effects preview cannot be applied. Reversal retains lineage
and later evidence; downstream activity requires its current digest and an explicit
state/work treatment. Later source state/work cannot be overwritten by replay.

Workspace settings: `workspace show --id V`, `configure --id V --input config.json`,
`metrics --id V --input metrics.json`, `issue --id V --input issue.json`. Config uses
expected revision, actor and allowlisted `software`/`outreach` keys; hiding modules
preserves data. Manual metrics require source, period, currency, actor and expected
revision; revenue/costs may be null. `reported_actual` and `estimate` are separate.
Security/bug categories are attributed artifacts referencing local WorkItems; missing
security assessment never means secure. Repository links do not execute code.

### October 6 corrections

Migrations `b10261006001` and `b10261006002` add explicit request dependency causes
and a pending-fusion source-set unique index. They neither rerun campaign intake
nor change existing score/decision payloads. The unique index is additive on SQLite,
so populated participant foreign keys do not require a table rebuild. Back up and
rehearse before upgrading, using the operating procedure above.

Register a dependency before completing the input review:

```bash
.venv/bin/foundry input link-dependency --id R011 --input dependency.json
```

The input has current request `expected_version`, target `workspace_id`, exact
blocked human-input `work_id`, `actor`, `reason` and optional `other_causes`.
Registration validates the target and work scope; a completion list alone cannot
assert ownership. Existing `HumanRequestTarget.work_item_id` links remain compatible.
Only `sufficient` can satisfy explicit input causes. Shared work remains blocked
while another input or other cause is unresolved; `partial` cannot close it and
`no_change` rejects all target mutations. Deferred reviews keep holds and cannot
queue investigation. Use returned versions instead of assuming one numeric step
per service operation. Corrections/revised questions invalidate satisfaction.
HTTP registration is `POST /api/inputs/{id}/dependencies`.

Manual initial review uses an explicit idea action or automatic scoped task on
promotion. Default repeated promotion reuses the same venture; an explicit distinct
`venture_id` means a deliberately separate venture. Each gets independent pinned
source baselines at creation; unscored sources remain unknown. GET never queues
or scores. Requests and promotion tasks say **Queued for manual agent review**.

```bash
.venv/bin/foundry intake request --subject idea --id IDEA --input request.json
.venv/bin/foundry intake handoff --subject venture --id VENTURE
.venv/bin/foundry intake claim --subject venture --id VENTURE --input claim.json
.venv/bin/foundry intake complete --subject venture --id VENTURE --input result.json
.venv/bin/foundry intake release --subject venture --id VENTURE --input release.json
```

Request contains `expected_revision_id` and `actor`. Claim uses the returned work
version. Completion requires exact work/version and claimant, a request key,
attributed `research_summary`, `research_source`, `research_limits`, justified
`scores`, `score_rationale`, `unknown_reason`, current `expected_sequence` and
`expected_review_revision`, and concrete `next_action`, `next_work_title`,
`next_owner` (`agent` or `you`). Human next work also needs `question_id` and
`question`; the transaction registers its explicit dependency. Failed/stale
completion rolls back research, scores, review and work together. Repeated exact
completion returns the saved result. Release includes exact work ID, current
version, claimant and reason. Handoff includes current versions and known input;
copying it starts nothing. Both `/api/ideas/{id}/intake` and
`/api/ventures/{id}/intake` accept requests, with `/claim`, `/release`, `/complete`
children; readable JSON is at `/ideas/{id}/intake-handoff` and
`/ventures/{id}/intake-handoff`.

Original score display edits the Reviewed rubric's actual latest sequence. Custom
views edit their own rubric/factors. Forms display directions/weights and retain
stale conflicts. Detail queries permit only registered cards or known empty
built-ins, supported tabs, offset 0–1,000,000 and limit 1–200. Invalid queries return
400, unknown cards 404. Safe portfolio return URLs survive tabs, modules, history
and work links; external/control-character/backslash targets are rejected.

Proposal request idempotence is separate from semantic source-set uniqueness.
Equivalent pending suggestions reuse the existing proposal; changed scope must
revise or explicitly supersede it. `proposal supersede --id ID --input replacement.json`
takes `expected_version` and a full typed `replacement`. Proposal revisions can
change `next_work_title` and `work_treatments`. The UI has labeled rows and before/
after effects, with JSON inspection optional. Reversal binds the current activity
digest and treatment for changed result definitions, scores, workspace or request
context; it never refreshes a stored acceptance snapshot to bypass the gate.

Work/state links are scoped readable routes:
`/ideas/{id}/work/{work_id}`, `/ventures/{id}/work/{work_id}`, and corresponding
`/reviews/{review_id}`. Foreign workspace references return 404. Answer pages
separate the current review from older replies, resolve effect artifacts and show
the actual status/owner of original resulting work and current next work.

The official image uses the same uv 0.11.29 release from hash-pinned official PyPI
wheels in the build stage, retaining frozen runtime dependencies and non-root
image security checks. See [ADR-0012](docs/adr/0012-hash-pinned-official-uv-build-source.md).
The registry failure and subsequent passing image path are recorded in the
[repair report](docs/inquiry/revamp-fixes-2026-10-06/REPORT.md). `make test-container`
exercises the container/PostgreSQL path. Desktop/mobile interaction is a separate
browser acceptance gate and cannot be certified by HTTP or Node serialization.

HTTP: `/requests?status=needs_you|awaiting_review|deferred|history`, `/requests/R006`
and `/requests/R006/handoff`; `/api/inputs` (list), `/api/inputs/preview` (GET),
`/api/inputs/sync` (POST with exact preview and optional reconciliation),
`/api/inputs/{id}/responses|claim|release|complete` (POST). `/api/venture-scores`
appends a judgment; `/api/ventures/{id}/scores` reads it. `/proposals` and
`/proposals/{id}` show revisions/effects; `/api/proposals` creates and
`/api/proposals/{id}/revise|resolve` mutates. `/api/ventures/{id}/config|metrics|issues`
uses the same services. Mutations require the local token and same-origin boundary,
bounded bodies and return 409 on stale state. GET does not create receipts or work.

Venture tabs use `/ventures/{id}?tab=overview|work|evidence|decisions|history|scores|
settings|software|outreach`; all retain identity and score meaning. Filtered list
queries travel via `return_to`; switching venture resets scoped filters. History is
paginated references to original events with workspace-checked `/events/{event_id}`
links. Existing `/steps`, `/requests`, `/outreach` and CLI contracts remain available.
Software and Outreach are static builtins; suppliers and venture-product algorithms
are future boundaries, independent of Foundry runtime and `learning/`.

## Lifecycle MVP

See the [operator and agent guide](docs/LIFECYCLE_MVP.md) and
[release report](docs/inquiry/lifecycle-mvp-2026-10-06/REPORT.md).
`make test-product` now includes the subprocess lifecycle replay. Run
`make test-browser` separately for actual Chromium interaction at desktop/mobile
sizes; CI installs Chromium and runs this check on Python 3.13. Locally use
`.venv/bin/playwright install chromium` or `FOUNDRY_BROWSER_EXECUTABLE`.
Screenshots can be retained with `FOUNDRY_BROWSER_ARTIFACTS=/absolute/directory`.
The dev-only Playwright dependency is absent from the runtime container.

`python -m startup_foundry.demo --store /absolute/new-demo.db` creates labelled
synthetic discovery, software and supplier scenarios. It refuses an existing
file. Always keep this store separate from the configured permanent portfolio.

Decision maps, contexts and results use validated artifact schemas and one
coordination-head table. Use the service/CLI/HTTP contracts rather than raw SQL;
concurrent acceptance and stale effects are tested on SQLite and PostgreSQL.
Before any upgrade, use `foundry storage backup` with a fresh filename.
`storage info` and `storage backup` do not trigger migrations; normal data commands
and UI startup do. A result preview uses the same transaction as acceptance and
always rolls back; new entity IDs in previews are provisional.
