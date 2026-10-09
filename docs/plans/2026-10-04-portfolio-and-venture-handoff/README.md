# Foundry implementation and venture handoff

Prepared 2026-10-04 for a smaller coding/research model. **This is a plan, not an
implementation report.** The user asked for a detailed handoff after supplying
inbox answers, repository-local CSVs and an existing Coopain project. Product
work, venture progress and practical usefulness take priority; learning is paused.

Execution update: the authorized local T00–T10 work is now recorded in
[STATE.md](STATE.md) and the [dated implementation report](../../inquiry/handoff-2026-10-04/REPORT.md).
The planning text below remains historical. Real browser QA and human/access-dependent
venture trials remain explicit gates in the execution report.

Later operator feedback and R005–R009 replies are addressed in the
[venture workspace revamp handoff](../2026-10-04-venture-workspace-revamp/README.md).
That follow-on document is planning only; it does not report implementation or
acceptance of the proposed sports fusion.

## Start here

Read root and Foundry `AGENTS.md`, this page, `STATE.md`, and only the subplan for
the current task. Use [BASELINE.md](BASELINE.md) to avoid reconstructing the previous
conversation. Consult original sources when a claim affects a decision. All paths
below are relative to `/home/jonathan/startup_lab` unless absolute.

The recommended order alternates useful Foundry changes and actual venture work:

| Task | Small deliverable | Dependencies | Subplan |
|---|---|---|---|
| T00 | Record inbox answers and source provenance; protect current data | None | [Baseline and intake](BASELINE.md) |
| T01 | Import all original criterion scores and reproduce the workbook formula | T00 | [Scoring](01-SCORING.md) |
| T02 | Represent advancement, disposition, blockers and next action | T00 | [Progress and UI](02-PROGRESS-AND-UI.md) |
| T03 | Filterable/sortable list views with score and state at a glance | T01, T02 | [Progress and UI](02-PROGRESS-AND-UI.md) |
| T04 | Private, local comparison of the supplied GPX files | T00; use T02 when ready | [Venture trials](04-VENTURE-TRIALS.md) |
| T05 | Register and assess Coopain as an existing project | T00, T02 | [Existing projects](03-COOPAIN-AND-EXISTING-PROJECTS.md) |
| T06 | Compare P023/P103 against the actual friends-group job | T00; T01 for revised scores | [Venture trials](04-VENTURE-TRIALS.md) |
| T07 | Editable outreach drafts, manual export and response recording | T00, T02; T05/T06 supply real context | [Outreach and guide](05-OUTREACH-AND-GUIDE.md) |
| T08 | Built-in help, workflow examples and clear empty/blocked states | T03, T05, T07 | [Outreach and guide](05-OUTREACH-AND-GUIDE.md) |
| T09 | Bounded N001 public-data screen and N003 sample/reviewer package | T00, T07 | [Venture trials](04-VENTURE-TRIALS.md) |
| T10 | Rescore investigated cases, review portfolio, verify and hand off | Completed preceding tasks; unresolved access stays visible | [Acceptance](06-ACCEPTANCE.md) |

T04/T06 can proceed while a product task is blocked. Do not complete every platform
feature before learning something new about a venture. T01–T03 should produce a
usable portfolio list; T05 should produce a usable existing-project intake, not
merely a Coopain essay. No model training, autonomous worker or Hindsight dependency.

## Decisions made for this plan

- Scores are useful provisional judgments. Expose the original 12 factors, a
  reproducible priority score, their source/version and confidence. Start tuning
  through explicit new assessments; do not wait for a statistically perfect model.
- A high score does not mean a task is unblocked or a venture is validated. Keep
  score, investigation stage, product maturity, disposition and blocker separate.
- Foundry must support joining a project already in progress. Retain code, past
  decisions, constraints and gaps; restarting ideation is optional, never mandatory.
- P023/P103 now have founder interest and possible friends-group access. Test that
  job directly, including team balance; a club-administration comparison alone is
  insufficient. Useful personal/community software is a valid outcome even while
  commercial demand is unproven. Do not conflate those outcomes.
- Outreach begins with drafts the user can edit and send manually. A later provider
  adapter must approve the exact payload revision. No current task sends a message.
- Source reuse should avoid duplicate work. Recheck sources only when scope,
  freshness or a consequential decision requires it; reuse claim IDs and limits.

## How to run each task cheaply

1. Read its allowed files and acceptance criteria. Inspect current code before editing.
2. Write a short task plan and meaningful tests first when practical. Make one
   vertical change at a time, keeping the current API and domain boundaries.
3. Use a temporary SQLite database or backed-up copy for tests and migrations.
4. Record findings and results in the owning Foundry workspace and a short artifact.
5. Run affected checks. Update `STATE.md` with files, commands, result IDs and the
   exact next task; keep the handoff under roughly 30 lines per task.
6. If blocked, retain the failure and a precise file-based request. Continue an
   independent task. Do not fabricate data, interviews, feature absence or approval.

A single turn can finish one task or a named subtask. Do not silently reduce scope
because the model is smaller. Do not keep rereading all 247 idea descriptions.
No automatic subagent spawning is requested by this handoff.

## Copyable prompt for the next model

> Continue the authorized Foundry product and venture work in
> `/home/jonathan/startup_lab`. Read root/Foundry AGENTS.md and
> `foundry/docs/plans/2026-10-04-portfolio-and-venture-handoff/README.md` and `STATE.md`.
> Execute the first pending task (initially T00), loading only its linked subplan
> and relevant sources. The plan contains defaults, file locations, tests and stop
> conditions; do not replace it with another generic plan. Preserve user edits,
> inbox answers, historical evidence and original databases. Work locally, use
> temporary test stores, and update STATE.md with concrete results. Do not commit,
> push, send outreach, provision, spend, publish, train/download a model or change
> learning tasks. If one branch needs human input, record it in Foundry's requests
> and continue independent authorized work. Return completed checks and the next task.

## Scope of this planning pass

Read-only inspection of Foundry, source CSVs, workbook formulas, GPX structure and
selected Coopain code/docs, plus bounded primary-source research. No production
code, database, inbox reply, GPX file or Coopain file was changed. No application
benchmark or Coopain test suite was run. The files in this directory are the new
handoff artifacts; proposed future states are not already implemented.
