# Revamp execution state

Acceptance review update, 2026-10-06: targeted counterexamples found request,
fusion, scoring and navigation defects despite green host tests. The implementation
is **not accepted as complete**. The October 5 task history below is preserved;
current correction work is tracked in the
[October 6 handoff](../2026-10-06-revamp-review-fixes/README.md) and
[review report](../../inquiry/revamp-review-2026-10-06/REPORT.md).

Updated 2026-10-05 after the user's execution request. Implementation and
permanent-store intake are applied. Overall acceptance remains pending: no browser
is exposed, and the official image build receives GHCR HTTP 403. The real sports
fusion is intentionally pending, independently of the passing fixture tests.
See [report](../../inquiry/revamp-2026-10-05/REPORT.md),
[record manifest](../../inquiry/revamp-2026-10-05/records.json) and
[ADR-0011](../../adr/0011-venture-workspaces-inputs-and-fusion.md).

| Task | State | Next step |
|---|---|---|
| V00 | Complete | Preserve both verified online backups |
| V01a | Complete | Use explicit sync or contextual UI answers |
| V01b | Complete | Manually claim any future answer revision |
| V02 | Complete | Append native assessments only with justified factors |
| V03 | Implemented; HTTP flows pass | Perform desktop/mobile browser acceptance |
| V04a | Complete; real proposal pending | Human decision on its exact revision |
| V04b | Complete on disposable fixtures | No real application without acceptance |
| V05 | Complete | Run bounded venture trials only when their gates are met |
| V06 | Independent checks complete; acceptance pending | Browser walkthrough and official container rerun |

## V00 — 2026-10-05

Read root/Foundry and central inquiry-memory rules; no learning slice or memory
service work. Frozen criteria: `docs/inquiry/revamp-2026-10-05/PROTOCOL.md`.
Recorded dirty status, HEADs, input/source hashes and original IDs in ignored
`.local/revamp-2026-10-05/baseline.json`. `pre-revamp.db` and fresh
`pre-live-upgrade.db` are verified SQLite online backups, mode 0600.
New input/score/proposal/module cases initially failed on missing services.
Input file hashes remain unchanged; unrelated changes preserved. Next: V01a.

## V01a — 2026-10-05

Files: `src/startup_foundry/{domain,human_inputs,snapshots,revamp_commands}.py`,
`alembic/versions/b10261005001_human_requests.py`, `tests/unit/test_human_inputs.py`.
Durable R001–R009 and targets; immutable responses, correction ancestry, safe
preview/sync, UI/file conflict preservation, optimistic ownership and stale checks.
Focused tests pass; exact saved receipt IDs are in the manifest. Next: V01b.

## V01b — 2026-10-05

Files: `human_inputs.py`, `revamp_bootstrap.py`, `steps.py`, `console_commands.py`.
Explicit live `foundry workspace bootstrap --review-latest`: imported five replies,
completed five exact-answer reviews; historical R001–R004 receipts remain intact.
R005–R007 resolved; R008/R009 deferred with no ready held-venture investigation.
Repeat imports/scores/reviews: zero. R006 receipt `272f190e-a1b7-5dc1-aa2d-a36eccf16d20`,
review `ba52b072-c9a6-4a11-a916-5cb9c821b5cd`. Full effects/IDs: manifest.
Manual export/claim/release/complete pass tests; no worker started. Next: V02/V03.

## V02 — 2026-10-05

Files: `venture_scoring.py`, `score_presentation.py`, `scoring.py`, `views.py`,
`domain.py`, migration `b10261005002_venture_scores.py`, score/view tests.
Nine frozen source baselines in the live store; no fabricated native live scores.
Independent revisions, source immutability, zero/unknown/partial scores, stale
context, idempotence and selected-factor sorting pass fixture checks.
Both lists default to reviewed; continued sources have an explicit filter.
Exact baseline/source assessment IDs: manifest. Next: V03.

## V03 — 2026-10-05

Files: `web.py`, `workspace_console.py`, `workspace_history.py`, templates,
`static/console.{css,js}`, `tests/unit/test_revamp_console.py`.
Contextual header/action, scoped tabs/history, filtered back link, answer form,
handoff export, review states and portfolio queues implemented. HTTP lifecycle
and persistence tests pass; twelve live-store routes return 200. JS syntax passes.
CUA inventory: `apps=[]`, `browsers=[]`; no screenshots or visual/layout claim.
Gate: desktop/mobile interactions, keyboard/focus, overflow and error recovery.
Next: browser acceptance when an enabled browser is available.

## V04a — 2026-10-05

Files: `proposals.py`, `domain.py`, migration `b10261005003_portfolio_fusion.py`,
proposal templates/routes/CLI and `tests/unit/test_portfolio_proposals.py`.
Pending proposal `91fe8686-6638-5dba-bb0a-34fe222a0be5`, version 1;
revision artifact `3d7a168a-139a-4046-9d95-25ac82a1b8f2`. Read scope, alternatives,
source snapshots and proposed effects at the local proposal URL in the report.
Edit/reject/exact-resolution fixture checks pass; no real source was continued.
Next: user's exact-revision accept/edit/reject decision, separately from V04b.

## V04b — 2026-10-05

Files: `proposals.py`, proposal tests, `tests/fixtures/revamp_postgresql.py`.
Disposable fixtures pass atomic application, fault rollback, stale source/revision
rejection, exact delegated authority, replay safety, lineage and reversal with
downstream-treatment gates. Both original sports URLs remain accessible.
SQLite and local PostgreSQL transactions pass. New composite is unscored.
The real proposal has no resolution artifact and creates no real D004/venture.
Next: V05; real application awaits a human decision.

## V05 — 2026-10-05

Files: `workspace_modules.py`, module/settings/metrics/software templates and tests;
`docs/inquiry/revamp-2026-10-05/{ROUTE,VOLLEYBALL,COOPAIN}.md`.
Software/Outreach are static built-ins; settings preserve hidden data. Manual
metrics distinguish unknown/zero, actual/estimate and currency. Checkpoints do not
claim runtime/security success. Coopain enables both modules.
Three frozen brief artifacts retained; exact IDs in manifest. Preparation tasks
are done, route/Coopain next investigations queued, sports awaits proposal review.
No routing algorithm, real trial, tester invitation or sports product built.
Next: V06 and separately gated venture work.

## V06 — 2026-10-05

Files: migration/schema tests, DBML, `DEVELOPMENT.md`, Help, verification script,
record manifest/report and this state. Rehearsal and live integrity/FKs/schema
parity and original-row comparison pass; repeat bootstrap creates nothing new.
Regression: 85 passed, 1 PostgreSQL-URL skip; final focused set: 11 passed.
Lint/types/actionlint pass; workflow contracts 12 passed. Local disposable
PostgreSQL fixture and Alembic parity pass; official `make check` container stage
has 3 failures/2 passes because GHCR OAuth returns 403 for the pinned uv image.
Browser acceptance remains pending. No checks weakened, commit or push performed.
Next: complete V03/V06 browser checklist and rerun official container checks after
registry access works; then decide whether the revamp passes overall acceptance.
