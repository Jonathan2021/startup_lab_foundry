# Foundry — agent handoff

Prepared 2026-10-07. Current scope: Let independent implementation agents resume the right venture, claim bounded work, return source-backed results and report friction without losing context or silently widening scope.

Repository: `/home/jonathan/startup_lab/foundry`. Venture `v-foundry`; workspace `68afabed-a744-47df-94c1-7402f5c7b3b0`.
First ready work: `a3e3b218-144f-403d-9227-e0ec9cd26207`. That ID is a starting reference; current
Foundry state wins if a later accepted decision changes the queue.

## Start

Read root/repository AGENTS and the decision, architecture and roadmap in this
folder. Preserve any dirty state. Then from this repository:

```bash
python3 tools/foundry_agent.py cli agent guide
python3 tools/foundry_agent.py resume
python3 tools/foundry_agent.py start --actor implementer-foundry-YOUR_SESSION_ID
```

The third command claims the current reviewed next work and saves context under
`.foundry/runs/`. Use a unique actor per agent session. It does not launch a model.
If the current work is already claimed, do not steal it or reset the database.
If preparation exceeds its 24KB budget, the bridge retries once at the exact
reported size, capped at 100000 bytes, without claiming again. Successful output
includes `budget_retry`; nothing is silently truncated. Larger contexts and other
errors fail and release the exact unchanged new claim. Recovery with
`--resume-owned` preserves ownership on failure. A crash after a claim can leave work owned: inspect resume and
use `handoff release` with the same actor/current version and a reason. There is
no lease expiry or claim authentication; the store is trusted local coordination.

The CLI executable and store are explicit argv in `.foundry/project.json`; if the
machine differs, update those paths to the installed Foundry CLI and operator's
chosen store. Never create a new empty store just because the configured one is
unavailable. The app's runtime must remain independent of Foundry.

## Check context coverage before implementation

Use `python3 tools/foundry_agent.py cli` followed by any CLI arguments below.
This forwards the configured executable/store; it is not a workspace permission
boundary. Use the saved context ID:

```text
handoff arrivals --id CONTEXT_ID
handoff fetch --id CONTEXT_ID --kind evidence --record-id EVIDENCE_ID
```

`agent schema --name context` publishes the full preparation contract. Published
schema choices are `map`, `context`, `claim`, `release`, `result`, `resolution`,
`change` and `work`; no Foundry source-code knowledge is needed. To include extra evidence, prepare a new context
using expected work version and map head from the live state, plus `evidence_ids`.
Fetch every relevant arrival and page using `--offset` with `next_offset` until null; unselected records are not
proved irrelevant. Read source files referenced by the roadmap. Prepared context
is a coordination summary, not a substitute for actual code/source inspection.

One writer per venture at a time is the initial operating policy. Different
ventures can run in parallel in separate repositories. More than one agent in the
same repository needs separate worktrees and agreed file ownership. A map revision
may require explicit keep/pause/cancel/revise treatment of current work before a
new claim; report and review the change instead of bypassing the guard.

## Return the checkpoint

Use the configured CLI prefix for all commands below (arguments shown after it).
Save JSON inputs under `.foundry/runs/`; inspect schemas rather than guessing enums.

```text
agent schema --name result
result submit --workspace-id 68afabed-a744-47df-94c1-7402f5c7b3b0 --input .foundry/runs/result.json
result show --id RESULT_ID
agent schema --name resolution
result preview --id RESULT_ID --input .foundry/runs/resolution.json
result resolve --id RESULT_ID --input .foundry/runs/resolution.json
```

Result requires context_id, unique request_key, actor, summary, rationale, limits,
outcome and next_action. Include source-attributed findings, changed files and
exact test evidence. `complete_work=true` only after the package's required checks
pass. Use `next_work` for the next dependency-satisfied roadmap package (ready,
owner agent, kind execution), and preserve later packages as conditional map nodes.
Work-scoped no_change/continue is appropriate for ordinary implementation; a
venture-level pivot needs explicit proposed objective and treatment of other work.
Hold needs a revisit trigger and cannot queue ready continuation in the same result.

Result show exposes a `resolution_pins` object. It pins the result digest and saved
context versions, not newer live state. Resolution pins `expected_result_digest` from result show, and expected map head,
work version and review revision from the *saved result context*. Never fill stale
fields with newer values just to pass validation. Explain coverage limits if any.
The authorized coordinating agent may accept routine local implementation results
after reviewing actual diffs/tests and previewed effects. This does not approve a
send, purchase, public deployment, payment or Git push. If a result is stale,
prepare fresh context and submit a superseding result with reconciliation rationale.

## Report Foundry feedback

```bash
python3 tools/foundry_agent.py feedback-template > .foundry/feedback-input.json
# Keep the generated UUID and scope IDs; fill the descriptive fields and sources.
python3 tools/foundry_agent.py feedback --input .foundry/feedback-input.json
```

Report a blocking defect immediately and ideas/friction/positive evidence at each
package checkpoint. The local immutable report is retained before sync; retry the
same file after failure. A receipt means recorded, not fixed. Feedback goes to
Foundry's own workspace, preserving source venture/workspace identity; it should
not clutter another venture's decision map. Coordinator review is via Foundry
Now/unreviewed evidence and `agent resume --venture-id v-foundry`. Triage recurring
issues into bounded work, with explicit accepted/deferred/rejected rationale.

## First package

F01 — Run one complete agent handoff per venture

Use prepared configs and maps; one writer per venture at a time, parallelism across venture repositories. Verify claim, prepare, result preview/accept, resume and feedback receipt. No production model service.

Acceptance: Every prepared repo resolves its own workspace and current work; stale/conflicting claims fail; failed feedback send is retained and retry is idempotent.

Do not claim the app is built because its specification or synthetic fixture passes.
Only add current-package tests. Keep real user trial gates distinct from build gates.


## Current upgrade (2026-10-11.1)

Use the current canonical bridge and update its manifest hash. `doctor` also warns
if Git ignores the feedback outbox. Work-scoped acceptance preserves map focus;
an explicit proposed map can move it, with before/after focus in preview.
Unchanged evidence classified by an accepted revision is not a new arrival.
All evidence remains pinned for change detection. Resume's `needs_review` is an
array of `{work_id, reason}`. `venture show` includes `version_id` for updates.

A claimant's own irrelevant map edit can preserve its context; changed task
dependencies, scope, work or another actor's revision still require fresh context.
Map work treatments can revise `question` and `acceptance_criteria`. The console
shows scheduled package action separately from the retained venture HOLD/action;
scores identify imported estimates versus reviewed judgments. `score ranking-show
--id SNAPSHOT_ID` reads a retained ranking without recomputing it. Alias reads keep
the original URL. Source locators accept HTTP(S), `observation:` or `document:`;
an observation needs an attributable locator or record reference.

## Previous upgrade (2026-10-09.1)

Record every delivery in a result finding as `Delivery: main=<sha> ci=<run id>`.
`resume`, `start` and `doctor` print a `repository` block (local HEAD, local
`origin/main`, latest recorded delivery) and warn when the repository moved past
it; the bridge never fetches. Legacy items paused as "Superseded ..." appear under
`superseded`; close one with `cli venture-work close --workspace-id WS --input
close.json` (`cli agent schema --name close`). Read commands accept `--id` with a
venture ID, alias, workspace ID/key or idea ID.

## Upgrade and delivery evidence (2026-10-08.1)

Use the current `doctor` and CLI guide; historical initial-task IDs do not override
resume. An unresolved result with `state=superseded` links its accepted replacement
in `superseded_by`; do not repeat completed reconciliation. Originals remain
immutable and pending/rejected/deferred replacements do not count as acceptance.

For a Git delivery include canonical path, delivery worktree, branch, local HEAD,
remote branch SHA, residual local changes and the matching CI URL/head/conclusion.
Report commit, push, merge and original-checkout synchronization independently.
See [EXTERNAL_AGENTS.md](../../EXTERNAL_AGENTS.md) for the current upgrade contract.
