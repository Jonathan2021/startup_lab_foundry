# Revamp review repair execution

Later update 2026-10-06: the [lifecycle MVP release](../lifecycle-mvp-2026-10-06/REPORT.md)
closes the browser gate described below, with real desktop/mobile Chromium
checks and audited completion of A01–A07. The report below retains the state
and evidence of the earlier repair run.

2026-10-06. The user authorized execution of the
[repair handoff](../../plans/2026-10-06-revamp-review-fixes/README.md).
A01–A06 functional repairs are implemented and applied to the backed-up permanent
store. `make check` passes, including the official image/PostgreSQL path.
Overall browser acceptance remains pending: inventory is `apps=[]`, `browsers=[]`,
and attempting to create the in-app browser returns **Browser is not available: iab**.
HTTP/HTML and Node serialization checks do not certify visual interaction.

The [local console](http://127.0.0.1:8765) is running with the repaired code.
The [real sports proposal](http://127.0.0.1:8765/proposals/91fe8686-6638-5dba-bb0a-34fe222a0be5)
remains proposed; no real fusion was accepted, rejected or revised.
[Crous](http://127.0.0.1:8765/ventures/f0b5abfe-0274-42f7-9c9a-72dcbe68c116)
retains its 3/12 partial assessment and unknown total. R011 remains the existing
queue-type/optional-first-visit request; site selection and desk review were not
repeated. R008/R009 remain deferred and quiet.

## Fixed behaviors

| Task / findings | Result |
|---|---|
| A01 / F01–F02 | Explicit target/work dependency registration replaces workspace-only closure authority. Satisfaction identifies the exact response. Shared input or other unresolved causes keep work blocked. No-change rejects target changes; partial/deferred cannot close dependencies; deferred cannot queue investigation. Mixed invalid changes roll back all effects. Older responses cannot mutate current state. |
| A02 / F03–F04 | Request-key receipts are distinct from normalized portfolio/kind/source-set identity. Equivalent pending drafts reuse one proposal, including concurrent creation. Changed scope needs a revision or explicit supersession. Acceptance retains full result definition/workspace, assessment and request context; later changes require exact digest and treatment before reversal. |
| A03 / F06/F10 | Fresh ideas have a functioning Request initial review action and Work section. Promotion atomically queues a deterministic manual task and copies that venture's pinned source baselines. Repeated default promotion reuses the venture; distinct explicit IDs express separate investigations. Handoffs retain exact subject/revision/work IDs, known input and completion requirements. Claimed completion atomically records attributed research, evidence, unknown reasons, assessment, state and scoped next work/input. No worker is installed. |
| A04 / F05 | Display and edit cards are separate. Original display edits the Reviewed card's actual sequence. Custom cards use their own supported factors and sequence. Forms show directions/weights and stale tabs still conflict. Unscored list cards say Not yet scored; partial, zero, native and inherited cases remain distinct. |
| A05 / F07–F09 | Bounded typed detail queries return 400 for malformed/negative/excessive paging and 404 for unknown cards across detail/list/API and the shared CLI service. One URL contract preserves selected scores and safe portfolio return paths through tabs, modules, history/events, work, source and switch links. Switching resets scoped paging/tab state. |
| A06 / source-confirmed interface gaps | Current-answer review is separated from older-reply history. Effect artifacts link original state/work and the current next work, showing persisted status/owner. Work and Software links open scoped readable records. Proposal edits use labeled scope rows, alternatives, next-work title and work treatment controls; new revisions expose before/after effects with JSON inspection optional. |

Primary runtime additions are `manual_intake.py`, `workspace_navigation.py` and
`workspace_records.py`; existing human input, proposals, portfolio, scoring,
views, CLI, console, templates and JS integrate the repairs. The two new migrations
are `b10261006001` (dependency causes) and `b10261006002` (pending-source unique index).
See [ADR-0011 corrections](../../adr/0011-venture-workspaces-inputs-and-fusion.md#october-6-repair),
[operating instructions](../../../DEVELOPMENT.md#october-6-corrections),
[STATE.md](../../plans/2026-10-06-revamp-review-fixes/STATE.md) and
[canonical records](records.json).

## Live dependency audit

Before repair, a fresh online backup was verified and the retained F01/F02 fixture
script reproduced both defects. Read-only inspection of all live completion
payloads found seven closures: three R005 route dependencies and four R006 sport/
group dependencies. Their workspace/title/source context matches the documented
inputs. No live R007 cross-request closure or no-change target mutation was found.
These older records lacked explicit target/work links, which was the implementation
gap; their matching context does not justify silently inventing historical cause
records or treating a fixture failure as live corruption.

No immutable review or answer was rewritten. The old compound task titles also
mention later comparisons; their input closure does not establish a performed
route or sports trial. The October 5 preparation artifacts and saved next tasks
remain the actual boundary. The repaired answer page now distinguishes resulting
preparation work (done) from the current next investigation (queued).
Audit evidence is `live-dependency-audit.json` in the ignored evidence directory.

## Actual checks and failure evidence

Frozen criteria are in [PROTOCOL.md](PROTOCOL.md). Baseline HEADs remain root
`e6a83e470d052439e5c8d4a943428f5bbd132f7f` and Foundry
`3b082507062838df4009d4b636c4f320436f3b41`; both trees were already dirty.
Effective hashes/status/table counts are in ignored
`foundry/.local/revamp-fixes-2026-10-06/baseline.json`.
Original reproduction outputs, red tests and intermediate failures are retained;
the review's source reports/counterexamples are unchanged.

| Check | Actual result |
|---|---|
| A01 dependency/input/schema cases | 17 passed; cross-request and mixed effects reject atomically, shared causes and non-sufficient outcomes covered |
| A02 proposal cases | 11 passed; semantic races, supersession, four result-context changes, exact authority, replay, immediate reversal and fault rollback |
| A03 affected cases | 26 passed; UI promotion, partial manual completion/restart, human next input, atomic rollback, copied baselines and independent ventures |
| A04 score/editor affected cases | 17 passed; original/custom editor, stale sequence, partial/unknown/frozen-source behavior |
| A05 navigation/view/editor cases | 24 passed; malformed bounds, invalid cards/criteria, safe returns and carried context |
| A06 interface/proposal/navigation cases | 26 passed; historical reviews, scoped records, structured controls, exact edited fixture application and Node serialization |
| Final focused integration adjustments | 25 passed; queued intake also appears in portfolio attention, completion uses its own final review context, dependency invalidation avoids an intermediate request flush |
| Full `make check` | Exit 0: actionlint, Ruff and mypy pass; repository test 1 passed; product regression 120 passed/1 skipped; official container tests 5 passed; workflow contracts 12 passed |
| Host PostgreSQL-URL-dependent test | One existing skip without an explicit PostgreSQL URL; the official disposable PostgreSQL acceptance path passes separately |
| Types / JS | 34 source files type checked; `node --check console.js` passes |
| SQLite rehearsal/live | Integrity, foreign keys and Alembic schema parity pass; all 52 original tables' existing columns/rows preserved before coordination bookkeeping |
| Live HTTP | Twelve representative stored-data routes return 200; malformed offset 400, unknown card 404; GET appends no records |
| Live server after restart | Six representative routes return 200 on port 8765 |
| Desktop/mobile browser | Pending; no enabled surface and explicit browser-creation failure |

Logs are in `foundry/.local/revamp-fixes-2026-10-06/`: `A01-*` through `A06-*`,
`A07-focused-final.txt`, `make-check.txt`, `migration-rehearsal.json`,
`live-before-coordination.json`, `live-verification.json`, `live-server.json`,
`registry-retry.txt` and `container-first.txt`.
One FastAPI/httpx deprecation warning remains; dependencies were not upgraded for it.

The first generated uniqueness migration used SQLite constraint ALTER and failed
on fresh fixtures. The final migration uses an additive unique index, retaining
populated participant foreign keys; the real-data rehearsal passes preservation.
The first official image run passed four checks but exposed a hardcoded request
version in its PostgreSQL fixture. Dependency invalidation had introduced an
intermediate autoflush; it now groups the request update, and the fixture uses the
returned version as real callers should. The full official rerun passes all five
checks, including new cross-request/outcome, semantic duplicate and reversal-scope
cases on PostgreSQL. Required checks were not skipped or weakened.

GHCR still denies the uv manifest. The build now uses Astral's official PyPI
distribution of the same uv 0.11.29 release with enforced published SHA-256 hashes
for Linux wheels. Frozen runtime dependencies, non-root runtime, absence of dev
tools and secret exclusion are retained and tested. Package format differs from
the GHCR binary; byte identity is not claimed. Linux amd64 is tested; arm64 hashes
are retained without claiming that platform tested. See
[ADR-0012](../../adr/0012-hash-pinned-official-uv-build-source.md) and
[Astral's PyPI installation guidance](https://docs.astral.sh/uv/getting-started/installation/#pypi).

## Permanent store and recovery

The configured store is
`/home/jonathan/.local/share/startup-foundry/foundry.local.db`, now at
`b10261006002`. Verified online backups (mode 0600) are
`foundry/.local/revamp-fixes-2026-10-06/pre-fixes.db` and
`pre-live-fixes.db`. `final-rehearsal.db` was upgraded and checked first.
No campaign/bootstrap was rerun against the live portfolio.

The original repair coordination work `2e3c7521-3da1-55d8-be65-3b4adfa0febe`
is retained and explicitly blocked on browser access after independent fixes and
checks. Its owner/status/cause/version change is audited, with an appended
Foundry review and verification artifact. All other original rows and input-file
hashes remain unchanged. Exact bookkeeping IDs are in records.json; the read-only
verification permits only this identified work change, retaining all original
review/decision/score/answer history.

For recovery, stop the local console, preserve the upgraded store with another
online backup, and run the earlier release against a separate copy of the chosen
pre-upgrade backup using `FOUNDRY_DATABASE_URL`. Retain the upgraded database;
do not destructively downgrade populated tables or replace the live file as a test.
No rollback was needed. Disposable acceptance containers/volumes were removed;
unrelated Odysseus services were preserved.

## Remaining acceptance and venture gates

The remaining A07 browser checklist must use disposable data at desktop and mobile
sizes: fresh idea → intake → promotion → manual completion; P103 IDs/score/next
action; answer correction, sync, claim/review and older-reply labels; zero/partial/
source/custom score forms and stale tabs; structured proposal scope/work edits,
exact acceptance/rejection/reversal; Software work links and hidden module data;
filtered Back paths, pagination, keyboard/focus, mobile overflow and form-error
recovery. No screenshots, layout pass or successful real browser form interaction
are claimed. Overall revamp acceptance stays pending until this checklist passes.

Real sports acceptance remains an exact human decision, independently of passing
fixture tests. Crous app coverage and firsthand observations remain access/human
gates; no absence, field measurement, prediction accuracy or adoption is invented.
Route/volleyball/Coopain preparations remain preparations. No external contact,
publication, account creation, spend, cloud resources, model training/download,
Hindsight integration, worker or learning slice was added. No commit or push.
