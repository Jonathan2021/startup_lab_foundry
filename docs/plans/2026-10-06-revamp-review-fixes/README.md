# Foundry revamp corrections for the implementation agent

Subsequent completion: A07 is now verified by the
[lifecycle MVP release](../../inquiry/lifecycle-mvp-2026-10-06/REPORT.md), including
the desktop/mobile browser checklist. Earlier execution notes below are historical.

2026-10-06 execution update: A01–A06 repairs are implemented and applied. Host,
official image/PostgreSQL and workflow checks pass. Browser acceptance remains
pending because no browser is exposed and creating `iab` fails. See
[STATE.md](STATE.md) and the [repair report](../../inquiry/revamp-fixes-2026-10-06/REPORT.md).
The instructions below retain the repair contract and review's counterexamples.

2026-10-06 handoff. Repair the reviewed implementation incrementally. Read root/Foundry
AGENTS.md and [review findings](../../inquiry/revamp-review-2026-10-06/REPORT.md).
Preserve unrelated edits, current database records and the original October 4
design. Do not rerun the old campaign or treat existing passing tests as proof of
these missing behaviors. The original review made no application fixes; execution
evidence is recorded separately above.

## Execution order

| Task | Priority | Scope | Depends on |
|---|---|---|---|
| A01 | P1 | Exact request dependency ownership and outcome invariants | Fresh backup/baseline |
| A02 | P2 | Fusion deduplication and complete reversal context | A01 for request-aware fixtures |
| A03 | P2 | Fresh idea and promotion produce actionable manual intake | A01 |
| A04 | P2 | Score editor/view separation and honest empty labels | Independent |
| A05 | P2 | Validated navigation and preserved list context | Independent |
| A06 | P2/P3 | Human-readable reviews, proposal edits and linked work | A01/A02/A05 |
| A07 | Gate | Full regression, official image path and browser walkthrough | All fixes |

Execute one task at a time. Add the failing behavioral cases first and turn them
green without weakening existing checks. A local code fix does not authorize
accepting the live sports fusion, external outreach or a CROUS product build.

## A01 Protect human request semantics

Reproduce F01/F02 with the retained fixture script; inspect `human_inputs.py`
completion and `HumanRequestTarget` linkage. An input work item can close only if
it is an explicit dependency of this request/target and has no unresolved shared
causes. Being in the same workspace with `blocked_reason=human_input` is insufficient.
Do not solve this by trusting an unvalidated caller-supplied list of work IDs.

Specify outcome invariants in the service: `no_change` rejects target mutations;
`partial` cannot resolve unsatisfied dependencies; `deferred` retains the hold and
cannot queue investigation; `sufficient` closes only the exact satisfied input
and preserves other causes. Keep atomic review/effects persistence and optimistic
concurrency. A stale historical response must remain historical with no current
state effects.

Acceptance: R006 review attempting to close R007-linked work rejects atomically;
legitimate R006-only work closes; shared work stays blocked if another input is
open; all-invalid/mixed changes leave no partial result; `no_change` with changes
fails and without changes records a review only; repeat/race/stale cases retain
history. Audit existing live completion payloads for this specific risk after
backup; do not assume fixture defects prove live corruption. If correction is
needed append reasoned records rather than editing immutable history.

## A02 Make portfolio changes consistent

Normalize source participant sets by portfolio/kind/identity so repeated equivalent
pending fusion suggestions reuse or identify the existing proposal, even when
request keys differ. Separate request idempotency from semantic deduplication.
Different scope should explicitly revise/supersede, not create indistinguishable
pending proposals. Enforce the race case in storage/transaction logic.

Extend reversal's downstream-state snapshot beyond work/evidence counts to include
the composite idea's current revision, venture objective/source and relevant
workspace versions, assessments and request changes. If those change, display
what changed and require explicit treatment. Do not refresh a stored acceptance
snapshot silently to bypass the gate. Preserve all target activity on reversal.

Acceptance: duplicate source set/new key and concurrent creation produce one pending
proposal; intentional supersession remains possible; result objective/idea revision/
score/request changes each trigger treatment; unchanged immediate reversal still
works; repeat acceptance/reversal and injected rollback remain safe. Real proposal
`91fe8686-6638-5dba-bb0a-34fe222a0be5` stays proposed unless the user decides it.

## A03 Close the fresh intake gap

`PortfolioService.promote_idea` currently only creates records. Give UI-created
ideas a real **Request initial review** action and new venture promotion an
idempotent, scoped manual intake task with owner, purpose and status. Label it
**Queued for manual agent review**, never running. Give a copyable handoff with
exact idea revision/venture/work IDs, known input and completion requirements.
Do not install an unattended worker or infer a score during a GET.

When promoting an already-scored idea, copy its pinned source baselines through a
targeted session-aware operation in the promotion transaction, or provide an
explicit targeted import action with a clear initial state. Prefer atomic copy
so users do not need global bootstrap. An unscored idea stays unknown. Repeated
promotion must not duplicate venture, work or baselines. Distinguish intentionally
creating a second venture from an accidental double click.

Manual intake completion appends attributed research, partial/complete assessment,
review and concrete next action or narrowly scoped human input. It must record
why some scores remain unknown and what needs checking next. Existing `WorkItem`,
runner seams and services are sufficient; no new scheduling framework.

Acceptance fixture: create through UI/API, promote, see identity/unknown and queued
task, export handoff, complete manual review, see partial score/reason/next owner
after restart. Repeat for a scored source and two distinct ventures with independent
scores. The idea primary button must reach a functioning form/work section instead
of an ignored `?tab=work`. Use the Crous records below as an observed case, not as
hardcoded runtime behavior. Do not duplicate their already completed intake.

## A04 Repair score forms and provenance labels

Separate selected display card from the editable reviewed card. Fetch the edit
card's actual latest sequence and pass it to the form; never hardcode sequence 0
just because Original view is selected. Keep expected-version conflicts for real
concurrent edits. The same rule must hold for custom scorecards.

Show risk direction and weights beside venture factors, matching idea scoring.
Unknown current scores must say **Not yet scored** rather than **Reviewed venture
judgment**. Keep zero, partial, inherited baseline and native reviewed labels distinct.

Acceptance: Original view with existing reviewed sequence successfully appends;
two stale edit tabs still yield one conflict; custom view has consistent selected
card and supported factors; unchanged source baselines stay frozen; current partial
assessment remains unknown total; unscored cards are honestly labeled. Fix only
the actual form/data-selection problem, not by disabling concurrency checks.

## A05 Validate route inputs and preserve context

Use a bounded typed query contract for detail history offsets and scorecards.
Reject malformed/negative/out-of-range pagination with clear 400/422 responses;
unknown scorecards should fail consistently across detail, list, API and CLI.
Preserve legitimate original/custom-card views and explicit unknown-score records.

One URL helper should carry selected score view and safe `return_to` through tabs,
score/history links, module links, contextual work actions and history pagination.
Keep external/malicious return targets rejected. A venture switch resets scoped
filters while preserving a meaningful portfolio return path.

Acceptance: the captured invalid offset returns no 500; valid paging works;
unknown card yields consistent not-found/validation behavior; open a filtered
portfolio, visit scores/software/history and return with the same search, sort,
page and filter chips; selected scorecard remains visible. Verify keyboard use
and a mobile viewport when a browser is available.

## A06 Finish the decision and work interfaces

Label historical answer reviews as applying to older replies; show the current
answer's review separately. Resolve `human-review-effects/v1` to real work/state
links and show the persisted work status/owner. Work IDs in the Software module
and venture Work tab should open scoped readable detail, not require manual search.

Replace raw JSON proposal-edit fields with labeled rows/text controls for retained,
combined, deferred and excluded scope, alternatives and affected work treatments.
Allow `next_work_title` and `work_treatments` to be revised as part of a new exact
proposal revision; make the complete before/after effects reviewable. Keep an
optional JSON inspection disclosure for technical provenance.

Acceptance: user can alter the proposed sports scope and how open work is handled,
preview differences, and reject or accept a disposable exact revision with rationale
without editing JSON. Prior revision authority cannot approve the edited payload.
Old reviews/records remain readable, and review-to-next-work navigation takes one
action. Do not build a generic form designer or change externally consequential
approval rules.

## A07 Complete acceptance honestly

Use the existing root `.venv`. Run affected tests per task, then `make check` and
the documented desktop/mobile tasks. Current baseline: 85 host tests pass, one
PostgreSQL URL test skips; Ruff/mypy/actionlint pass; workflow contracts 12 pass;
official container tests have three build failures caused by GHCR OAuth 403.

Resolve registry/build access with the existing pinned dependency or a documented,
equivalent reproducible official build source. Do not change pinning, image security
assertions or required checks merely to make the summary green. Do not publish
or provision cloud resources. When browser access is still unavailable, record
the exact blocked checklist and finish independent work; overall acceptance stays
pending. HTTP/HTML tests are necessary but not visual acceptance.

Use fixture data for fusion/form/invalid-input tests; preserve the live portfolio.
Retain updated migration integrity/FKs, restart persistence, repeat-safe intake,
original-row preservation and package boundary checks. Do not prepare a learner
slice or repair unrelated intentionally red EvalOps contracts.

## Crous work already handled and what comes next

Read [Crous review](../../inquiry/crous-2026-10-06/REPORT.md),
[source ledger](../../inquiry/crous-2026-10-06/SOURCES.md) and
[record IDs](../../inquiry/crous-2026-10-06/records.json). The source description
remains intact. The paired idea/venture now receive explicit partial assessments
for problem 7, competition risk 8 and network risk 8; the remaining nine factors
and total are unknown. Do not create an arbitrary total to fill the UI.

User selected RU Cuvier and RU Châtelet. R010 is the site-selection receipt;
R011 contains only the remaining queue-type/optional-first-visit question in
`foundry/requests/2026-10-06-crous.md`. Public coverage searches did not establish
absence in either incumbent app. Actual app lookup is still an access-gated task;
local firsthand observations are a separate human task. No consumer product,
rating/forecast model, crowd-data collection or paid feature is authorized here.

Continue the real venture in parallel with independent repairs only when its
specific input/tool gates are met. Review any new R011 answer through the corrected
request service, preserve attribution and update exact next work. Do not ask again
which restaurants to use or rerun broad competitor research without a refresh reason.

## Completion record and copyable prompt

Maintain [STATE.md](STATE.md) with each task's files, commands, passing/failing
checks, remaining gaps and the next task. Keep failed experiment evidence. Do not
claim all work is finished while functional reproductions or browser/container
gates remain unresolved.

> Read `/home/jonathan/startup_lab/foundry/docs/plans/2026-10-06-revamp-review-fixes/README.md`
> and STATE.md, then execute the first pending correction. Reproduce the finding
> before fixing it, use root `.venv` and disposable fixtures, and preserve the
> dirty tree and live records. Complete scoped fixes and meaningful tests; update
> STATE.md. Do not accept the real sports fusion, fabricate Crous scores or field
> observations, start a worker, spend/send/publish/provision, commit/push or change
> learning ownership. Continue Crous only through its recorded inputs and bounded
> investigation, and report actual acceptance gaps.
