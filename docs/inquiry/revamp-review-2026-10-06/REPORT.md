# Foundry revamp acceptance review

2026-10-06. **Do not accept the revamp as complete yet.** Much of the requested
structure exists and the host regression suite passes, but targeted negative
cases expose coordination, scoring and navigation defects. Browser acceptance
remains unavailable, and the official container gate still fails on GHCR access.

The implementation agent's own [October 5 report](../revamp-2026-10-05/REPORT.md)
already qualified completion with pending browser/container gates. This review
adds reproducible functional findings; it does not discard the useful work or
claim the entire implementation is broken. The executable repair order is in
[the next-agent handoff](../../plans/2026-10-06-revamp-review-fixes/README.md).

## Confirmed findings

Line references describe the inspected working tree, not clean HEAD. Reproduction
scripts and output are retained under `foundry/.local/revamp-review-2026-10-06/`.
All fault reproductions used disposable fixtures; no faulty fusion or cross-request
completion was applied to the real portfolio.

The repair handoff is also queued as manual work in the `v-foundry` workspace;
[coordination IDs](records.json) identify the work, review and saved handoff.
Queued does not mean an implementation agent has started or any fix is complete.

| ID | Priority | Verified behavior | Main location |
|---|---|---|---|
| F01 | P1 | Completing R006 can mark R007's explicitly linked blocked task DONE while R007 remains unanswered; only workspace/reason/status are validated | `src/startup_foundry/human_inputs.py:812–823` |
| F02 | P2 | A `no_change` review can append state, create work and close dependencies | `human_inputs.py:754–784` and subsequent change loop |
| F03 | P2 | Same fusion source set with a different request key creates a second pending proposal | `proposals.py:246–259` |
| F04 | P2 | Editing the composite venture objective does not change the downstream-activity digest; reversal succeeds without explicit treatment | `proposals.py:568–638` |
| F05 | P2 | From Original score view, appending a reviewed score submits expected sequence 0; once a reviewed baseline/assessment exists, refresh cannot clear the 409 conflict | `templates/venture_scores.html:2` |
| F06 | P2 | A new idea's primary `?tab=work` action renders the same content; no work tab/form handles it | `workspace_console.py:165–170`, `templates/idea.html` |
| F07 | P2 | `?tab=history&offset=bogus` yields HTTP 500 | `workspace_console.py:212` |
| F08 | P2 | Breakdown/history link drops `return_to`; module links also drop selected score view, so Back loses portfolio filters | `templates/score_summary.html:1`, `templates/workspace_header.html:4` |
| F09 | P3 | Unknown scorecard returns 200/unscored on idea/venture detail and venture score API, while list correctly returns 404 | `workspace_console.py:60–62`, `VentureScoringService.show` |
| F10 | P2 improvement | Promotion creates only a workspace/venture: no manual intake work/review/handoff. Even a scored source gets no copied baseline until separate global bootstrap | `portfolio.py:384–427` |

F10 is partly a missing ongoing lifecycle beyond the seeded-campaign acceptance;
it should be implemented as a narrowly justified improvement, not disguised as
an autonomous worker. The other findings reproduce concrete behavior contrary to
the intended coordination or navigation contracts.

Additional source-confirmed UX omissions: request history does not visibly label
historical reviews; their resulting WorkItem IDs are not navigable from the review;
proposal edits require raw JSON and cannot modify work treatments/next work title;
venture score fields omit risk direction/weight; unassessed venture cards are
labeled “Reviewed venture judgment”; Software work IDs and record history are
largely plain text/raw JSON. These belong in the follow-up tasks, with focused
acceptance rather than a frontend rewrite.

## Verification performed

| Check | Result |
|---|---|
| Host unit/integration/CLI/package suite | 85 passed, 1 PostgreSQL URL-dependent skip, one httpx deprecation warning |
| Ruff | Passed |
| Mypy | Passed, 31 source files |
| `make check` actionlint and repository test | Passed; repository test 1 passed |
| `make check` host suite | Again 85 passed, 1 skipped |
| `make check` official container suite | 3 failed, 2 passed; image build cannot obtain GHCR OAuth token, HTTP 403 |
| CI/delivery workflow contracts run separately | 12 passed |
| Existing reviewer-selected tests | Intake/fusion 8 passed; score/module/console 3 passed |
| Targeted fault reproductions | Confirmed findings above despite existing green tests |
| CUA inventory | `apps=[]`, `browsers=[]`; no desktop/mobile visual acceptance |

Logs: `regression.txt`, `lint.txt`, `types.txt`, `make-check.txt`,
`workflow-contracts.txt`, `input-fusion-repro.jsonl`, `navigation-repro.txt`.
Reproductions: `foundry-input-fusion-repro.py`, `foundry-score-ui-audit.py`,
`foundry-score-ui-audit-navigation.py`, with their frozen protocols. The initial
score script intentionally reaches an unhandled query error after printing score
results; the navigation script captures HTTP 500 with server exceptions disabled.
Its normalized comparison removes random request IDs; the earlier score script's
naive page comparison is not the evidence for the inert idea action.
Tests in this review do not establish mobile usability or actual PostgreSQL runtime
image acceptance. Fix the registry access/build dependency honestly; do not mark
these three failures skipped or weaken the tests.

## New Crous idea and venture

Before intake, the user's idea `a32e67a1-2289-46b4-b12a-d24d2032ef2c` and venture
`f0b5abfe-0274-42f7-9c9a-72dcbe68c116` had no assessment, review, evidence or work.
The source revision is `16159051-8c81-456b-a0ff-972479b2e187`. Unknown scores were
accurate; scoring can already be performed manually through the existing services.

The [Crous review](../crous-2026-10-06/REPORT.md) checks primary-source overlap,
records the user's Cuvier/Châtelet choice and identifies the next bounded test.
Affluences restaurant support and CrousRadar overlap are counterevidence to a broad
undifferentiated app. Local coverage, queue type and sustainable fresh data remain
the useful uncertainties. Three explicit criteria are assessed; no complete
priority total, revenue or demand signal is fabricated.

Live operation is recorded separately in [Crous record IDs](../crous-2026-10-06/records.json).
R010 captures/resolves the site-selection reply; R011 asks only about queue type
and an optional first ordinary visit. Existing R001–R009 replies and holds,
the sports proposal, and original idea text remain preserved. This is investigation
work, not a CROUS product build or an unattended-agent installation.

## Boundaries and local intake checks

No application source, runtime migration or tests were edited. No real fusion,
external contact, account, upload, paid action, deployment, commit or push occurred.
The root/submodule trees were already dirty; effective file/table hashes are in
the ignored review baseline manifest.

The authoritative untouched pre-intake backup is
`.local/revamp-review-2026-10-06/pre-live-crous-intake.local.db`. A first scratch
attempt filtered a global sync preview and was rejected by the service; it only
registered requests in that scratch database. The earlier file named
`before-crous-intake.local.db` was used for that scratch attempt and is **not** the
pristine restore point. A fresh online backup was taken before any live intake;
rehearsal then used `crous-rehearsal.local.db`, a separate copy. The corrected
operation uses a full preview and refuses unrelated changed answers.

Rehearsal passes integrity/FKs and a repeated intake adds no rows. Live Crous
verification passes integrity/FKs, preserves every pre-intake database row, and
returns 200 for six relevant detail/score/work/request routes. Both headers show
the 3/12 partial assessment and R011. All 124 baseline source/test/migration/script/
request files retain their hashes; the new Crous request file is an intentional
addition. `verification.json` retains the details. These data operations do not
repair the application defects listed above.
