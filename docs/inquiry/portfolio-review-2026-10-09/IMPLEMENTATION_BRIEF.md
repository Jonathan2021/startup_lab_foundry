# Implementation brief for venture agents (2026-10-09 portfolio pass)

You implement bounded packages in ONE venture repository, through that repository's
Foundry bridge. Read this file fully, then the repo's `AGENTS.md`, `README`,
`cleanup/README.md` (notes from today's maintenance merge), `docs/mvp/REVIEW_NEXT.md`
and the portfolio review for your venture at
`/home/jonathan/startup_lab/foundry/docs/inquiry/portfolio-review-2026-10-09/<slug>/REVIEW.md`
(sections 3, 5 and 6 and the closing JSON block are your specification).

## Ground rules

- One writer per venture: you are the only agent in this repository. Do not touch
  other repositories or Foundry's own source (`/home/jonathan/startup_lab/foundry/src`).
- The checkout is already fast-forwarded to `origin/main`. Verify with `git status`
  and `git log -1`. Preserve every untracked operator file you did not create (do not
  delete, move or commit `remarks/`, prompt notes or test leftovers unless a package
  says so). The `feedback/` outbox files created by Foundry feedback ARE meant to be
  committed with your work.
- Git: commit in small, conventional commits; end every commit message with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. **Pushing to `origin
  main` is explicitly authorised by the user for this repository.** Never force-push,
  never rewrite history, never create a new remote or repository. If a push is
  rejected because the remote moved, fetch, rebase your commits, rerun checks, push.
- After each push, wait for GitHub Actions on that exact SHA (`gh run list --repo
  Jonathan2021/<repo> --commit <sha>` then `gh run watch <id> --exit-status`, up to
  ~20 minutes). A package is complete only when its exact SHA has a successful run.
- No external consequences: no hosting/provisioning, no accounts, no spend, no
  messages to real people, no real personal data, no paid APIs. Synthetic fixtures
  only. Keep secrets out of commits and Foundry records.
- Code quality bar: the repo's `make check` (lint, format, strict types, tests) and
  its browser suite must pass locally before you push. Add tests for every behaviour
  change (red first where practical). Keep docs honest: a README a human can follow
  in five minutes; historical documents get a dated banner rather than deletion.
- Facts only in reports: exact commands, pass/fail counts, SHAs, run ids. Never
  report a check you did not run.

## Foundry workflow (dogfooding is part of the job)

```bash
python3 tools/foundry_agent.py cli agent guide        # read once
python3 tools/foundry_agent.py resume                 # current state
python3 tools/foundry_agent.py start --actor implementer-<slug>-20261009 --work-id <WORK_ID>
```

`start` claims the package and saves context under `.foundry/runs/`. Read the saved
context and `cli handoff arrivals --id <CONTEXT_ID>` before editing. If the budget is
exceeded, use `--budget-bytes 60000`. If a claim fails because the work changed, run
`resume` and report; do not steal another actor's claim.

Returning a package: write `.foundry/runs/result-<pkg>.json` following
`cli agent schema --name result` (context_id, unique request_key, actor, summary,
rationale, findings with sources such as `document: path` or URLs, limits, outcome
`continue`, `complete_work` true only after the exact-SHA CI run succeeded,
`next_action`, and `next_work` only when the review lists a further package that does
not already exist as a work item). Then:

```bash
python3 tools/foundry_agent.py cli result submit --workspace-id <WS> --input .foundry/runs/result-<pkg>.json
python3 tools/foundry_agent.py cli result show --id <RESULT_ID>        # copy digest
python3 tools/foundry_agent.py cli result preview --id <RESULT_ID> --input .foundry/runs/resolution-<pkg>.json
python3 tools/foundry_agent.py cli result resolve --id <RESULT_ID> --input .foundry/runs/resolution-<pkg>.json
```

Resolution (`cli agent schema --name resolution`) pins `expected_result_digest` from
`result show` and `expected_head`, `expected_work_version`, `expected_review_revision`
from your SAVED context (never from newer live values). You are authorised to accept
your own routine local implementation results (`resolution: accept`) after checks and
CI pass; use `coverage_action: accept_limitation` with a one-line rationale when
`context_complete` is false and you have paged the arrivals. If a result comes back
`needs_reconciliation`, prepare fresh context (`start --resume-owned --actor <you>
--work-id <id>` or `cli handoff prepare --workspace-id <WS> --input ctx.json` with the
new evidence ids) and submit a superseding result with `supersedes_result_id` and
`reconciliation_rationale`; never force stale effects.

Then claim the next package in your ordered list (they already exist as work items;
`todo` work is claimable) and repeat. Stop at human-gated (`blocked`) packages.

Feedback (required at every package checkpoint, and immediately for a blocking defect):

```bash
python3 tools/foundry_agent.py feedback-template > .foundry/feedback-input-N.json
# kind bug|friction|idea|positive; actor implementer-<slug>-20261009; fill all fields
python3 tools/foundry_agent.py feedback --input .foundry/feedback-input-N.json
```

Report what hurt, what helped, and what you had to work around (CLI flags, missing
views, stale data, unclear contracts). If nothing hurt, say so in a positive report.

## Record hygiene (first package of each venture)

Your first package includes bringing the venture's Foundry record in line with the
repository, using the public CLI only:
- `cli change record --workspace-id <WS> --input evidence.json`: record today's
  merged PR (sha, run id, test counts) as `document`/`experiment_result` evidence.
- `cli decision-map show --workspace-id <WS>` then `cli decision-map revise ... --input map.json`
  (schema `cli agent schema --name map`): keep every existing node unless the review
  calls it a stale duplicate placeholder (then remove it with the rationale), add
  `work_treatments` to **cancel** superseded legacy items the review names (rationale:
  superseded by decision X) or **pause** deferred ones, and set `focus` to the real
  gate. Supply `expected_head` from the current head. Never delete evidence, decisions
  or done records.
- Verify with `resume`: no `needs_review` noise from legacy items, focus on the real
  gate, your evidence visible.

## Deliverable

Besides the code and Foundry records, write
`/home/jonathan/startup_lab/foundry/docs/inquiry/portfolio-review-2026-10-09/<slug>/DELIVERY.md`
with: packages completed (work id, result id, commit SHAs, Actions run id and
conclusion), what was intentionally not done and why, remaining human gates, feedback
UUIDs filed, and the exact final `git log -1` and `origin/main` SHA. Final reply to the
coordinator: a 12-line summary with those identifiers.
