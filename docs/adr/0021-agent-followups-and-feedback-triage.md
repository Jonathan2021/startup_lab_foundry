# ADR 0021 Agent followups and feedback triage

Date: 2026-10-11. Status: accepted for local implementation under the user's
explicit request to digest portfolio feedback, implement, test and deliver to main.
Package: F10. Contract and repository bridge: 2026-10-11.1. No database migration.

## Evidence and scope

The six independent venture repositories and portfolio coordinator repeatedly
reported lost map focus, old accepted findings reappearing as arrivals, insufficient
context budgets and missing optimistic-concurrency pins. A new connected-party
game inquiry used the permanent store before this repair. Its research and raw
operator receipts stay local. Local triage retains all 120 feedback evidence IDs,
source ventures and explicit dispositions; these include previously reviewed
history, not 120 new defects. Main-package feedback families:

- Map focus: evidence `13bf681d-37e9-473c-9001-79436c5888b8`,
  `39de8a11-0287-4082-bac5-af2262461c5a`.
- Accepted arrivals: `511c528c-815e-4201-af63-30af61fa1791`.
- Own map changes and work text: `15acd945-a43d-4336-b11e-b41984382c62`,
  `916421e0-98d8-439e-89e1-37173128a06b`.
- Budget recurrence: `98a45aec-1d04-4081-8ec8-9c2ec7094d04`,
  `01e8e0de-59f6-48ba-a8f1-0c43af1ebaf4`.
- Pins, aliases and list shape: `799315e9-a11b-4225-8f55-49a1c8f3f2f0`,
  `ebb6a55d-006d-4ef4-85aa-235a2a79fe2c`,
  `29f88bec-05f5-440b-9116-86f52051fd79`,
  `fca3aa86-acd3-4512-9842-22584f7e406f`.
- Source guidance, score provenance and retained ranking access:
  `bb620401-c05b-406e-a6b6-08ecfaa6e6ca`,
  `dc07ffcf-51bb-4083-849d-8ebcf5c2bbb3`,
  `366f1a46-061d-4ed8-9f69-158ce5f1a428`.

## Decisions

1. Work-scoped results preserve the deliberate full-map focus, including when
   scheduling next work. An explicit result map can change focus. Venture-scoped
   decisions retain their direction-changing behavior. Current work remains
   independently scheduled and claimable. Preview shows the focus before/after.
2. Context preparation excludes an unchanged digest already classified by an
   accepted map revision from unclassified arrivals. The complete evidence
   manifest remains pinned: changes still stale a result. Selected dependency
   records remain in context; new or changed unselected evidence requires review.
   Saved old contexts and their arrival lists remain immutable.
3. A claimant's deliberate map revision does not manufacture a review blocker
   or bump its own in-progress work. Reusing its context is permitted only if
   **every** intervening map revision has the same actor and unchanged selected
   task map and scope. Changed goals, prerequisites, work text, referenced records,
   evidence, inputs or review revisions still require fresh context. This is a
   bounded exception for irrelevant edits, not a stale-result bypass. Other work
   retains the normal review guard. Work treatments can revise question and
   acceptance criteria; stale errors name the work and versions.
4. The bridge retries context preparation once, only on the exact reported size
   error and at most 100000 bytes. Claim is not repeated; arbitrary errors and
   unknown mutation outcomes are not retried. Failed normal preparation releases
   its exact claim; failed recovery preserves existing ownership. Successful retry
   reports the requested and used budget. Doctor checks Git-ignore status of the
   durable feedback outbox.
5. Result views expose `resolution_pins` from their saved context, never newer
   live versions. Venture reads expose `version_id`. Resume returns `needs_review`
   as an array of work IDs and reasons; internal map history keeps its existing
   dictionary. Alias reads serve the original URL without a redirect. No alias
   mutation API or automatic external action is added.
6. Preserve the venture-level HOLD/narrowed next action; show the scheduled
   package action separately. If an older review has no work pointer, one unique
   in-progress claim identifies the package; ambiguous claims are never guessed.
   This missing-pointer case was observed while running F10 itself. Scores explicitly distinguish imported, reviewed,
   stale and absent judgments. Unknown totals remain unknown. Publish source
   locator/observation rules in the input schema and guide.
7. `score rank` already returns `ranked_entries` lists in the current code; the
   counts-only report does not reproduce against that contract. Add read-only
   `score ranking-show --id` to recover a retained snapshot's exact pinned
   assessment, revision, total and grade after newer assessments arrive. The
   existing market-actor query filter and ID reuse are the resolution for name
   collisions; do not silently merge conflicting websites. Error guidance now
   names the lookup command. Existing MVP-week schema bounds are tested; zero
   remains invalid and fractional positive estimates remain permitted.

## Deferred feedback and limits

Request-number allocation needs a separate bounded package that defines central
versus venture-local request ownership and protects inline replies during
multi-file writes. Batch recording needs latency profiling plus atomic/idempotent
failure semantics before choosing a CLI batch or persistent process. Automated
placeholder matching, automatic maturity inference, typed delivery blocks and
cross-actor claim reassignment are deferred. Existing maps, review commands,
bounded selectors and explicit treatment/recovery remain usable workarounds.
Do not weaken prerequisite review to avoid a cosmetic blocker or infer real
demand/maturity from an engineering release. Prior onboarding, output, lineage
and request-drift fixes stay in their historical ADRs.

Changes are checked through unit/CLI regressions, desktop/mobile lifecycle browser
acceptance, installed-wheel recovery, and CI for the exact delivered commit.
The local checkpoint records commands and outcomes. No hardware trial, new
service, paid inference, deployment or learner implementation is part of F10.
