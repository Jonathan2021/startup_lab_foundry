# Revamp correction state

Closure 2026-10-06: the later lifecycle MVP implementation completed the A07
desktop/mobile checklist with real Chromium on disposable data. Full release
checks pass. The prior browser-blocked task is now done with an appended release
artifact and Foundry review; original reviews remain historical. See the
[lifecycle release report](../../inquiry/lifecycle-mvp-2026-10-06/REPORT.md) and
[completion records](../../inquiry/lifecycle-mvp-2026-10-06/records.json).
The earlier execution state below is preserved as history.

2026-10-06. User authorized repair execution. Baseline and verified online backup
are in ignored `.local/revamp-fixes-2026-10-06/`; frozen cases are in
`docs/inquiry/revamp-fixes-2026-10-06/PROTOCOL.md`. Functional repairs and official
checks pass; backed-up live migration is applied. Overall browser acceptance is
pending. See [repair report](../../inquiry/revamp-fixes-2026-10-06/REPORT.md) and
[canonical records](../../inquiry/revamp-fixes-2026-10-06/records.json).

| Task | State |
|---|---|
| A01 Exact request dependencies and review outcomes | Implemented; focused checks passed |
| A02 Fusion duplicates and reversal context | Implemented; 11 focused checks passed |
| A03 Fresh intake and promotion workflow | Implemented; 26 affected checks passed |
| A04 Score forms and labels | Implemented; focused editor checks pass |
| A05 Query validation and navigation | Implemented; malformed/unknown/context cases pass |
| A06 Review and proposal usability | Implemented; 26 affected checks passed |
| A07 Full acceptance | Host/container/workflow/migration checks pass; browser pending |

Crous desk review, user site-selection intake and partial scoring are separate
venture operations, not completion of these application fixes. See the review
report and Crous records for current state. Append concise evidence per executed
task; do not overwrite the review's counterexamples or earlier reports.

## A01

2026-10-06: reproduced F01/F02 before editing; retained original JSONL and red test
output. Added explicit `HumanRequestDependency` causes and satisfaction pointers,
validated registration, compatibility with legacy target links, outcome invariants,
shared-cause gating and correction invalidation. Files: `domain.py`,
`human_inputs.py`, request CLI/API, bounded bootstrap linkage, schema migration
`b10261006001`, dependency tests and schema/head assertions.
Cross-request and mixed changes roll back; no-change/partial/deferred cannot close
dependencies; shared/non-input causes remain blocked. Focused checks passed.
Read-only live audit found seven R005/R006 closures matching the documented inputs,
no R007 cross-closure or no-change target mutation; original records retained.
Evidence: `A01-red.txt`, `A01-green.txt`, `live-dependency-audit.json`.
Live schema subsequently applied after the A07 preservation rehearsal.
Next: A02 semantic fusion deduplication and reversal context.

## A02

2026-10-06: F03/F04 reproduced before editing. `proposals.py` now separates request
receipts from source-set identity, enforces pending uniqueness in storage
(`b10261006002`), reuses equivalent drafts and requires revision/supersession for
changed scope. Concurrent different keys produce one pending candidate.
Acceptance retains the complete initial result context; objective/current idea
revision, both assessment histories, workspace versions and request/dependency
changes trigger explicit reversal treatment and are displayed as differences.
Added controlled supersession and revised next-work/treatment contracts.
Tests: 11 passed (`A02-green-race.txt`), including four context mutations, racing
creation, immediate reversal, replay, authority and injected rollback. SQLite
constraint migration failed first; the final additive unique index preserves
populated participant foreign keys without rebuilding the table.
Real sports proposal remains untouched. Next: A03 manual initial intake.

## A03

2026-10-06: retained two red UI/promotion cases. Added `manual_intake.py`, scoped
UI/API/CLI request/export/claim/release/complete, an actual idea Work section and
initial-review form. Promotion atomically queues one deterministic manual task
and copies this venture's pinned source baselines, including custom cards.
Default repeat promotion reuses the venture; distinct explicit IDs create separate
ventures. Completion atomically retains attributed research, evidence, unknown
reasons, independent assessment, review and bounded agent/human next work.
Human next work registers an exact request dependency; stale/foreign completion
rejects and duplicate completion is repeat-safe. No GET dispatch or worker added.
26 affected tests pass (`A03-green-complete.txt`); mypy passes 32 source files.
An existing global-bootstrap count assertion changed because promotion now does
the copy; provenance/frozen-baseline assertions remain. Existing Crous intake is
not repeated. Next: A04 score editor and provenance labels.

## A04

2026-10-06: retained failing Original-view sequence and custom-rubric cases.
`workspace_console.py` now supplies a distinct editor card/actual latest sequence;
Original displays source judgments while editing Reviewed. Idea and venture forms
use the selected editable rubric's keys, risk direction and weights; stale tabs
retain conflicts. Optional idea expected-sequence checking also protects UI edits.
Unknown venture list cards say Not yet scored; zero/partial/baseline/native remain
distinct. GET rubrics recognize empty built-ins without writing schema/data.
Files: score services/context, `views.py`, scoring templates and editor tests.
Editor checks passed (`A04-green.txt`); expanded affected checks recorded separately.
Source baselines stay frozen. Next: A05 typed navigation and preserved context.

## A05

2026-10-06: retained 500/missing-context/unknown-card counterexamples and new red
HTTP cases. Added `workspace_navigation.py` with bounded typed tabs/card/offset/
limit and safe return paths. Malformed, negative and excessive paging returns
400; unknown cards return 404 across detail/list/API and the same service in CLI.
One URL helper carries score selection and portfolio return through tabs,
breakdown, modules, context work, history paging/events, source and switch links.
Switching resets scoped tabs/paging. Promotion redirects preserve context.
Custom-card list factors are validated against that rubric; built-in unknown
criteria still fail existing validation. Empty known cards remain valid/read-only.
Checks: navigation/editor/view cases pass; JS syntax passes. Browser keyboard and
mobile walkthrough remains an A07 gate. Next: A06 readable reviews/work/proposals.

## A06

2026-10-06: new red historical-review and structured-editor cases retained.
Current-answer review is separate from explicitly labeled older-reply reviews.
Effects resolve original state/work and current next work with persisted statuses
and owners. Added scoped readable work/review pages and links from Work/Software;
history state/score records have readable summaries and optional provenance.
Proposal edits use labeled scope rows, alternatives, next-work title and source
work treatment controls. Revisions show complete before/after differences;
stale revision authority still rejects. Raw JSON is optional inspection only.
Files: `workspace_records.py`, request/proposal/context adapters, templates and JS.
26 affected HTTP/service/serialization checks pass (`A06-green-complete.txt`),
including exact fixture application and no-JSON control payloads. JS syntax passes.
Real portfolio not mutated. Next: A07 full acceptance and backed-up migration.

## A07

2026-10-06: `make check` exits 0: actionlint/Ruff/mypy pass (34 source files),
repository 1 passed, product 120 passed/1 existing PostgreSQL-URL skip,
official container/security/PostgreSQL 5 passed, workflow contracts 12 passed.
Same uv 0.11.29 uses hash-verified official PyPI wheels (ADR-0012); original pins
and security assertions retained. Earlier denied GHCR and failed fixture logs kept.
Rehearsal/live head `b10261006002` matches metadata, integrity/FKs pass, all 52
original tables' old rows/columns preserved apart from identified coordination
work status/cause/version. Input hashes, Crous 3/12 and pending sports stay intact.
Console restarted on 8765; twelve stored-data HTTP routes and six server routes
pass. No GET intake/dispatch. Browser inventory empty; creation fails `iab unavailable`.
Coordination task `2e3c7521-3da1-55d8-be65-3b4adfa0febe` is blocked on external
browser access, with appended review `f614a4b3-1155-4c08-b1fe-98f885d6f023` and
verification artifact `9543ef95-efd1-5bef-953d-27a0978066b9`. No commit/push.
Next: exact desktop/mobile disposable-fixture checklist in the repair report;
overall acceptance remains pending until it passes.
