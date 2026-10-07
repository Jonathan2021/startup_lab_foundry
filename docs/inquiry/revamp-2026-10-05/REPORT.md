# Venture workspace revamp execution

2026-10-05. The user authorized execution of the
[October 4 handoff](../../plans/2026-10-04-venture-workspace-revamp/README.md).
The local implementation and permanent-store intake are applied. Overall
acceptance remains pending: no enabled browser is exposed, and the official
container build cannot authorize its pinned uv image through GHCR (HTTP 403).
HTTP checks do not certify desktop/mobile layout or interaction.

Open the [local console](http://127.0.0.1:8765),
[R006 and its saved review](http://127.0.0.1:8765/requests/R006), or the
[pending volleyball fusion proposal](http://127.0.0.1:8765/proposals/91fe8686-6638-5dba-bb0a-34fe222a0be5).
The console process was started against the permanent configured store. It is a
local operating UI, with manual agent pickup; queued work is not a running worker.

## Resulting behavior

Portfolio navigation now exposes Overview, Ideas, Ventures, Inbox and Proposals.
Idea/venture headers identify the subject, score meaning, current focus and one
contextual next action. Venture tabs load scoped work, evidence, decisions,
history, scores and settings. History is paginated and links the original records;
filtered list links and a workspace switcher keep navigation contextual.

Human requests have durable owners and explicit targets. File preview/sync and
contextual UI answers use the same receipt service. Corrections preserve immutable
ancestry; stale previews, changed questions, repeat submissions and file/UI
divergence have explicit handling. The review handoff carries exact request,
response, work and score IDs. Manual claim/release/completion retains ownership
and only changes specified target dependencies. Saving or copying never launches
an agent. Review completion is distinct from venture validation.

Venture assessments are independent append-only records using existing
scorecards/calculation and a shared score summary. Nine source baselines are
explicitly copied and frozen in the live store. Later idea assessments cannot
silently change them. Native assessments, factor sorting, coverage, partial/zero
values, unknown totals and stale context are exercised on fixtures. No live native
score was invented merely because an answer arrived.

Fusion proposals preserve revision comparisons, source-state snapshots, scope,
alternatives and rationale. Exact acceptance applies atomic local effects;
rejection has no source effects. Application/reversal, replay prevention and
separately recorded delegated authority pass disposable tests. Application creates
a new idea/venture, retains both sources and shared canonical answers, and starts
the composite unscored. A reversal retains that history and requires explicit
treatment if downstream work exists.

Software and Outreach are optional built-ins, selected through versioned settings.
Hiding either keeps its records. Coopain has both enabled, with existing repository
and checkpoint provenance. Missing runtime/security evidence is not a pass.
Business metrics remain manual and distinguish unknown, zero, reported actuals,
estimates, periods and currency. There is no dynamic plugin platform, new
dispatcher or venture-product algorithm.

Primary files are the new `human_inputs.py`, `venture_scoring.py`,
`score_presentation.py`, `proposals.py`, `workspace_modules.py`,
`workspace_console.py`, `workspace_history.py`, `snapshots.py`,
`revamp_bootstrap.py` and `revamp_commands.py` under `src/startup_foundry/`;
the existing domain/scoring/views/web/CLI/step adapters, Jinja templates and static
assets integrate them. See [ADR-0011](../../adr/0011-venture-workspaces-inputs-and-fusion.md)
and [development instructions](../../../DEVELOPMENT.md) for the actual boundaries,
CLI/API and operating procedure.

## Answer intake and venture work

All R001–R009 are registered. R001–R004 have typed wrappers pointing to the original
receipt IDs and source digests; their historical campaign was not rerun. Five
latest replies were explicitly synchronized and reviewed. A repeat bootstrap
imports zero answers, appends zero scores and completes zero additional reviews.
The two Markdown input files remain byte-for-byte unchanged.

| Request | Saved outcome | Result and remaining gate |
|---|---|---|
| R005 | Resolved | Broad route preferences and target 4–5 h riding, breaks separate; [three-option comparison brief](ROUTE.md) prepared. Actual routes/ETAs require a routing basis; no planning trial performed. |
| R006 | Resolved | One canonical volleyball/WhatsApp observation shared by both sports ideas/ventures; [trial sheet](VOLLEYBALL.md) prepared. Planned outing is not observed attendance; role, formats and consent remain unknown. |
| R007 | Resolved | [Private tester walkthrough and ownership checklist](COOPAIN.md) prepared. No real tests, buyer validation or rights agreement; runtime and compatibility labeling precede a private demo. Shared monetization body remains unreviewed. |
| R008 | Deferred | Physical-task ventures/ideas held pending competent feedback, absent from Needs you and ready venture investigation. |
| R009 | Deferred | Receipt/transition ventures/ideas held pending a receiving practitioner, absent from Needs you and ready venture investigation. Existing drafts remain unsent. |

Exact receipt/review/work/target IDs and source-baseline IDs are in
[records.json](records.json), without private GPX or answer payloads. Three brief
artifacts are `fb577953-dbe2-5413-b4e3-c1cb648d91ec` (route),
`3ed84550-ff4e-51a7-b761-ceb3aae69835` (volleyball), and
`fb76e961-6211-573d-a706-b0256f84000e` (Coopain).
Their preparation tasks are completed. The route comparison and Coopain runtime
investigations are saved as ready next work, not performed trials. Sports next
action is proposal review. Older multi-cause Coopain work remains blocked rather
than being closed because only one missing input was answered.

The real proposal is `91fe8686-6638-5dba-bb0a-34fe222a0be5`, version 1,
revision artifact `3d7a168a-139a-4046-9d95-25ac82a1b8f2`, state `proposed`,
with no resolution artifact. P023 / `v-sports-ranking` workspace
`6e2795a7-2457-44e1-b3e1-0bc66ed4f734` and P103 / `v-sports-session` workspace
`417476af-0674-4aba-9022-843957dc3ca2` remain separate and readable.
The proposed result is `v-volley-sessions`; neither it nor a derived idea was
created in the real portfolio. An exact-revision human decision remains necessary.

## Storage and migration evidence

Before substantive work, [PROTOCOL.md](PROTOCOL.md) froze the hypothesis and bounded
criteria. Root HEAD was `e6a83e470d052439e5c8d4a943428f5bbd132f7f`, Foundry HEAD
`3b082507062838df4009d4b636c4f320436f3b41`; both trees already had unrelated edits.
Effective hashes, row IDs/counts and dirty status were retained in ignored
`foundry/.local/revamp-2026-10-05/baseline.json`.

The effective permanent database is
`/home/jonathan/.local/share/startup-foundry/foundry.local.db`.
Its initial head `9af261004001` was upgraded through three additive schema-only
migrations: `b10261005001` (requests/targets), `b10261005002` (venture assessments),
and `b10261005003` (proposals/participants). Campaign intake is a separate explicit
operation, not an Alembic side effect.

Verified online backups, including committed WAL content, are
`foundry/.local/revamp-2026-10-05/pre-revamp.db` and
`foundry/.local/revamp-2026-10-05/pre-live-upgrade.db` (mode 0600).
Three disposable SQLite rehearsals preceded live application. Rehearsal and live
checks pass integrity, foreign keys, Alembic schema parity, repeat-zero bootstrap
and original-row comparisons. Original source records, ideas/revisions,
scorecards/criteria, assessments/factors/evidence, rankings, ventures, artifacts,
evidence, decisions and old workspace reviews retain IDs and values. Existing
outreach content/checkpoints are among the preserved Artifact rows. Only explicit
input dependencies and completed preparation tasks changed existing work status.

Live counts are 250 ideas/revisions, 243 idea assessments and 10 ventures,
unchanged from baseline; 9 human requests, 9 venture baselines, 1 pending proposal,
606 artifacts, 516 work items and 294 reviews. Input SHA-256 values remain:

```text
INBOX.md                 383231335395f22202b8fc59786f09a0625b6118d826b821cb1b045da8468971
2026-10-04-followups.md  8705a386ac0e8588cfd8d70e397c509ef56391ce6a85f1e8f1d94a4ef0411d7b
```

For rollback, stop the console, preserve the upgraded store with a new online
backup, and run the old release against a separate copy of the pre-upgrade backup
using `FOUNDRY_DATABASE_URL`. Retain the upgraded store; do not destructively
downgrade populated tables or overwrite the live file as a test. Full operating
instructions are in DEVELOPMENT.md. No rollback was needed.

## Actual verification

Logs and local databases below are in the ignored
`foundry/.local/revamp-2026-10-05/` directory.

| Check | Actual result | Evidence |
|---|---|---|
| Unit/integration/CLI workspace/package boundary suite | 85 passed, 1 skipped, 1 FastAPI/httpx deprecation warning; generic PostgreSQL CLI test requires an explicit URL | `regression.txt`, `make-check.txt` |
| Final focused input, score, proposal, module and HTTP flow tests | 11 passed | `final-focus.txt` |
| Ruff, mypy and actionlint | Passed; 31 source files type checked | `lint.txt`, `types.txt`, `make-check.txt`; verification script also linted |
| Repository test / delivery workflow contracts | 1 passed / 12 passed | `make-check.txt`, `workflow-contracts.txt` |
| JavaScript syntax | `node --check .../console.js` passed | Rehearsal command |
| SQLite rehearsal and permanent-store verification | Passed schema/integrity/FKs, original rows, quiet holds, pending proposal and 12 routes | `rehearsal-final.json`, `live-verification.json`; `scripts/verify_workspace_revamp.py` |
| Persistent live server | Five representative routes returned 200 on port 8765 | `live-server.json`, `console.log` |
| Local disposable PostgreSQL 18 | New-service fixture transactions and Alembic parity passed; container removed afterward | `postgres-local.txt`, `tests/fixtures/revamp_postgresql.py` |
| Official container checks in `make check` | 2 passed, 3 failed at image build: GHCR OAuth HTTP 403 for `ghcr.io/astral-sh/uv:0.11.29` | `make-check.txt`, `postgres-revamp.txt` |
| Real desktop/mobile browser acceptance | Pending; CUA inventory contains no apps or browsers | No screenshots or visual pass claimed |

The PostgreSQL exercise exposed a `DISTINCT` comparison on a JSON-bearing request
row; the proposal service now selects distinct IDs through a subquery instead.
The corrected fixture passed. An earlier cached-image attempt contained old source;
official acceptance now requests an image rebuild, which exposes the registry
authorization failure. The host-venv PostgreSQL fixture is useful transaction
evidence and does not certify the official runtime image. No required tests were
weakened to obtain a green summary.

## Pending acceptance and next work

The next acceptance task is the exact desktop/mobile checklist in
[V06](../../plans/2026-10-04-venture-workspace-revamp/04-MODULES-AND-DELIVERY.md#checks-and-browser-acceptance)
using disposable records: P103 initial viewport, answer/sync/review transitions,
holds, score persistence/sorting, proposal edit/reject/apply/reverse, module
settings, keyboard/focus/overflow and recoverable form errors. No enabled browser
is available in this session. The official container suite also needs rerunning
after GHCR access is restored. These gates remain explicit in
[STATE.md](../../plans/2026-10-04-venture-workspace-revamp/STATE.md).

Separately, the user can decide the pending sports proposal's exact revision.
Route, volleyball and Coopain briefs specify their own bounded trial gates;
preparation is complete, observations/adoption/fairness/planning speed/security/
revenue are not validated. No agent worker is running those investigations.
There was no spend, cloud provisioning, external contact/publication, account
creation, model download/training, Hindsight installation or learner credit.
Unrelated edits and earlier reports remain preserved. No commit or push was made.
