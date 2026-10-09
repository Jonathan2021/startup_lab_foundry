# Foundry product scope and agent execution proposal

Date: 2026-10-06. Status: proposal for discussion, not an implementation plan or
replacement for the accepted current direction. No application code or live
records were changed in this review.

Foundry should help a founder and their agents decide what deserves work, carry
out a bounded investigation, and retain what changed. The useful product unit
is an independently usable venture workspace. Portfolio management coordinates
those workspaces; shared services support them. Execution can come from the
user's agent or an optional Foundry runner, using the same task and result rules.

The initial customer hypothesis is a repeat founder or small studio already using
agents across several initiatives. The recurring job is: **resume the work,
identify the next useful decision, delegate an action, and recover its result
without reconstructing the venture from chats**. Commercial demand remains
unvalidated. The current user's workflows can establish utility, not market size.

## Quick verification of the repairs

The [repair report](../revamp-fixes-2026-10-06/REPORT.md) accurately leaves browser
acceptance pending. An independent reviewer reran this command from the root:

```bash
.venv/bin/pytest -q foundry/tests/unit/test_request_dependencies.py foundry/tests/unit/test_portfolio_proposals.py foundry/tests/unit/test_score_editor.py foundry/tests/unit/test_manual_intake.py foundry/tests/unit/test_workspace_navigation.py foundry/tests/unit/test_review_interfaces.py
```

Result: **40 passed**, one existing Starlette/httpx deprecation warning, 12.88s.
Focused tests and code inspection support the original dependency, fusion,
score-editor, query/navigation, intake and review-interface repairs. The retained
`foundry/.local/revamp-fixes-2026-10-06/make-check.txt` reports 120 host passes,
one skip, five container passes and twelve workflow passes. Those wider gates,
migration/recovery and live-row preservation were not independently rerun here.
The current browser inventory again returned `apps=[]`, `browsers=[]`; no visual,
mobile, keyboard, or real browser form acceptance is claimed.

Two disposable reproductions expose remaining intake semantics:

| Finding | Evidence | Required behavior |
|---|---|---|
| Completing an investigation always continues it | `manual_intake.py:53–70` requires next work and has no disposition field; lines 370–380 always create work; line 428 hardcodes `PURSUE`. Submitting synthetic research saying the hypothesis is falsified and the next action is stop produced `disposition=pursue` and ready work. | Completion supports continue, narrow, hold and stop. Hold/stop can finish without queued investigation. Preserve unrelated current stage/maturity unless explicitly changed. |
| Promotion can duplicate an existing intake | Request an idea intake, then promote that idea. `portfolio.py:433` queues venture intake, leaving two ready tasks with identical investigation descriptions in different workspaces. | Default promotion explicitly reuses or supersedes overlapping pending work while retaining history. Distinct investigations remain possible when their scopes differ. |

These do not invalidate all the demonstrated repairs. They show why completing
the product semantics matters more than another broad feature sprint. A separate
review can currently correct the disposition, but that does not make the atomic
intake completion correct. Reproductions used a fresh migrated SQLite database in
`TemporaryDirectory(prefix='foundry-verify-')`, deleted afterward; no real venture
was altered. Relevant synthetic outputs were `pursue / ready / Stop investigation`
and two ready tasks after idea request plus promotion.

## What the landscape changes

Official product documentation inspected for this review shows several adjacent
capabilities. These are documented or marketed capabilities, not independent
quality tests, customer-demand evidence, or a complete market census.

| Alternative | Established from its official source | Consequence for our positioning |
|---|---|---|
| Linear | External agents can receive delegated issues while the human remains the owner. [Agent documentation](https://linear.app/docs/agents-in-linear) | Agent assignment and task tracking alone are insufficient differentiation. |
| Notion | External assistants can read/write through MCP; Custom Agents support recurring background work with configured access. [MCP](https://www.notion.com/help/notion-mcp), [Custom Agents](https://www.notion.com/help/custom-agents) | Both execution modes already coexist in a general workspace product. |
| Attio | Its internal assistant and external MCP access are explicitly complementary. [Attio MCP](https://attio.com/help/reference/attio-ai/attio-mcp) | Hybrid execution is a sound product pattern, not a unique advantage. |
| DimeADozen | Markets idea-validation reports, competition research and build/no-build recommendations. [Product](https://www.dimeadozen.ai/) | Generic research reports and startup scores face direct substitutes. |
| NanoCorp | Markets agents that build, sell, advertise and report on businesses. [Product](https://www.nanocorp.so/) | A broad autonomous-company promise creates a much larger execution race. Its marketing does not validate our demand or establish its effectiveness. |

My inference: model access and agent connectivity are becoming easier to obtain
from existing products. Foundry's plausible opportunity is the recurring decision
workflow between research, experiments and execution: what is supported, what
changed, why we continued or stopped, and where to spend the next week. Evidence
must remain useful when the agent or execution tool changes.

This is still vulnerable to an agent plus ordinary files, Notion or Linear. A
structured database, history and MCP endpoint are capabilities, not a commercial
advantage by themselves. Foundry has to save repeated founder effort or prevent
consequential coordination mistakes with less upkeep than those alternatives.

The original [brief](../../startup_foundry_project.md) already calls for a thin
coordination and memory layer. The current confusion is partly the exposure of
storage concepts and overlapping lifecycles, rather than proof that the database
or whole application must be replaced.

## One product with explicit ownership

Own the venture decision and coordination workflow. Keep the existing modular
monolith and one application. Make portfolio use optional for someone with one
venture. An independent venture workspace does not mean Foundry hosts the
venture's customer-facing application or implements all its business departments.

| Scope | Authoritative responsibilities | What its interface shows |
|---|---|---|
| Venture | Current customer/problem/scope, uncertainties, experiments, evidence, decisions, assigned work, approvals and venture-specific relationships | What matters now, next action, results, history and relevant integrations |
| Portfolio | Idea backlog, comparison, allocation of attention/budget, venture membership, fusion/split proposals and lineage | Which initiatives deserve attention and the consequences of combining or stopping them |
| Shared services | Reusable services and permitted contact/source identities, execution adapters, notifications and aggregate attention views | Cross-venture views of records whose scope remains explicit |
| Connected systems | Code and issue details, email transport, accounting, analytics or supplier operations | Linked operational facts and actions relevant to a venture decision |

The portfolio has real records of its own, such as allocation and fusion decisions;
it is more than a dashboard. It must not maintain a second editable copy of each
venture's state. Each mutation identifies its owning scope. A portfolio operation
that affects several ventures names those effects explicitly.

**Outreach resolves the grey zone.** A person may have a shared identity within
an organization. A relationship, purpose, draft, conversation and follow-up belong
to a particular venture or an explicitly shared initiative. The global inbox
aggregates authorized records; the venture page filters those same records.
Sending has one payload, one approval and one receipt. Contact visibility never
automatically grants visibility into another venture's private correspondence.
Attio's distinction between a record and process-specific list entries is a useful
analogy, without adopting its whole CRM. [Data model](https://attio.com/help/reference/attio-101/attios-data-model/understanding-lists)

Likewise, several ventures can cite one public source, but each owns its assessment
of that source's relevance. Reused evidence is not independent corroboration.
An input that unblocks several ventures needs explicit affected targets, not
workspace proximity or an agent's assumption.

A venture should eventually export its brief, evidence, decisions, work and
permitted referenced material without pulling in private sibling ventures. Do
not make runtime operation depend on a portfolio overview, another venture's
database, or a particular model. This is a boundary to preserve; export and team
permissions are not claimed implemented by this proposal.

Portfolio-only would be smaller, but risks being a dashboard users visit once
before doing all useful work elsewhere. A full venture operating suite would be
large and duplicate mature tools. Separate products now would create the same
context synchronization problem we want to solve. One focused workbench with
optional portfolio coordination gives us a testable middle scope.

## External agents first with optional Foundry execution

Separate three questions: what task is needed, who executes it, and who may accept
its proposed effects. Deterministic application rules handle records, permissions,
versions, transitions and receipts. Agents supply judgment, research and drafts.
Foundry does not need an agent to perform its own ordinary bookkeeping.

| Execution choice | Good fit | Cost and responsibility |
|---|---|---|
| User's existing agent | Interactive investigation, coding with existing repository context, specialized tools/accounts | User controls the agent; Foundry receives scoped results. External usage cost may be unknown, never falsely zero. |
| Optional Foundry runner | A bounded repeatable job the user wants done without keeping a session open | Foundry owns scheduling, failures, cancellation, permissions, run visibility and a declared usage budget. |
| Human/manual | Field observations, judgment, unavailable access, ordinary work | Same durable task and result; no need to pretend a worker is running. |

Start with the external/manual route. Add one hosted workflow only after demand
for unattended completion or demonstrated quality/cost benefit. A hosted agent
moves inference cost; it does not eliminate it. Compare accepted-result cost,
including retries, duplicated research and human review, rather than token price
alone. Reusing applicable evidence can help more than adding another agent.

For the user's competition example:

1. Foundry provides the precise question, venture revision, prior findings,
   counterevidence, open gaps, allowed actions and completion requirements.
2. The selected executor does the research. An external agent can perform it
   itself or explicitly request a configured Foundry runner for that task.
3. The executor submits findings, sources, limitations, recommendation and proposed
   changes together. Foundry checks scope/version/references and retains provenance.
4. An authorized reviewer accepts, edits or rejects consequential changes. Routine
   evidence recording can proceed under existing authority without an extra human
   click for every row. Structural validation does not prove the research true.
5. A completed investigation can lead to continue, narrow, hold or stop. It need
   not create more work or increase a score.

Both executors use the same contract. A task has one accountable executor at a
time, bounded authority and an identifiable result. Requested, queued, running,
waiting for input, result submitted and accepted must remain distinguishable.
Claims need expiry/recovery when a worker disappears. Repeated submissions must
not duplicate effects, and results based on obsolete context need reconciliation.

Expose a few operations matching user intentions: retrieve context, claim work,
submit an investigation, request input, and propose a scope/portfolio change.
One validated submission can create several records atomically. Do not make an
external agent stitch together fifty microscopic database writes. Optional runner
dispatch is a separate explicit operation with a durable job ID, status and result;
avoid hidden agent chains and automatic paid fallback.

CLI, HTTP and eventually MCP should wrap the same application operations. MCP
provides a context/tool exchange protocol; it does not prescribe a product's
business rules or agent orchestration. [Official architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)
An MCP adapter is justified when a real external-agent session needs it, not as a
prerequisite for testing the workflow with the existing CLI.

## A simpler application to use

Global navigation can be **Today, Ventures, Portfolio**. Portfolio contains the
lightweight idea backlog, comparisons and fusion proposals. A person using one
venture can stay within it. Today shows only meaningful attention: decisions to
make, questions to answer, results to review and failures needing intervention.
It distinguishes waiting work from actual running work.

A venture has **Now, Work, Evidence, History**, plus relevant connections.
Now begins with its name, copyable ID, stage and qualified score, followed by the
current scope, most important uncertainty, and one clear next action with owner.
Answering an input shows the saved answer and whether review is queued, claimed
or complete. File replies remain supported inputs; they should not force the
user to understand synchronization artifacts to find out what happens next.

For Crous, the main content should be approximately:

> Crous queue information — investigation; partial assessment 3/12, total unknown.
> Determine whether Cuvier and Châtelet have a useful information gap.
> Existing research and counterevidence are saved. Exact local app coverage and
> queue type remain open. Answer R011 or inspect the coverage task and its owner.

This uses the [existing Crous assessment](../crous-2026-10-06/REPORT.md); it does
not reopen the answered venue selection or claim new field observations.

Scores remain visible at the top as requested, with coverage, date, basis and
uncertainty. Portfolio attractiveness and operating health answer different
questions. Revenue, retention or an unresolved security issue should not be
compressed into a universal number that rises when agents complete forms. A
score can fall after useful research; stopping can be successful work.

Sports fusion is a portfolio decision with a clear combined description, retained
and dropped scope, alternatives, evidence, work treatment and rationale. Accepting
it changes exactly the shown revision and retains source histories. A rejected
fusion does not invalidate either venture. Similar titles alone are insufficient.

WorkItem, StepRun, WorkspaceReview, HumanRequest and assessment are useful storage
distinctions. They should support one visible flow—question, action, result,
decision—rather than appear as competing concepts the user must learn.

## Venture differences without a platform project

Keep common scope, evidence, decisions, work and history. Add optional views and
connections for a demonstrated need: code/issues/security for a software venture,
contacts/outreach for a sales experiment, supplier references for physical work,
or sourced business metrics for an operating venture. A venture can combine them;
an exhaustive venture-type taxonomy is unnecessary.

External tools remain authoritative for detailed operational data. Foundry stores
the relevant link, observation/as-of time, decision and follow-up responsibility.
A stale synchronization must not look like a clean bill of health. A security
issue can appear in Today because it changes priorities while remediation stays
in the repository and issue system.

Use built-in optional views before a plugin runtime. Keep the existing Python,
database and UI foundation. Do not build an agent marketplace, generalized workflow
designer, full CRM, accounting, supplier suite, autonomous CEO or new frontend
framework for this proposal. Add an adapter only when an actual task needs it.

## Validate the product before another broad implementation

The next work should test this workflow with the existing application and files.
The following is a proposed trial, not a result or an invitation to invent user
observations. Freeze case selection and success criteria before running it.

1. Use the available Crous coverage decision, sports fusion decision and a real
   Coopain follow-up as distinct first-party cases, respecting their existing
   access gates. Include a counterevidence/stop case. Record cases blocked on
   access as blocked; do not manufacture progress for the experiment.
2. Across ten bounded handoffs, compare fresh sessions receiving Foundry context
   with sessions receiving the same facts through ordinary files/current tools.
   Use matched frozen cases and alternate order; do not let a richer dossier or
   an agent's memory of the first attempt explain the result. Replay outcomes are
   usability evidence, not new venture evidence. Track actual decisions separately.
3. Measure human reconstruction and bookkeeping minutes, omitted counterevidence,
   repeated investigations, incorrect effects, and accepted decisions reached.
   Record model/tool conditions and known usage costs. Keep the existing workflow
   available so preference is observed through repeated use.
4. Proposed internal continuation gate: at least 30% lower median reconstruction
   time, net human time saved after upkeep, zero incorrect scope/authority effects,
   and three actual decisions advanced. These are chosen practical thresholds,
   not statistical or commercial proof. Investigate a failure rather than polishing
   the dashboard to obscure it.
5. Only after internal utility, seek three independent repeat founders/studios for
   a short pilot with their own work. Meaningful evidence is voluntary repeat use
   over several weeks and a concrete commitment to continue or pay. Recruiting,
   outreach, hosting and billing are future separately authorized work.

If files and existing tools are sufficient, keep a small internal tool or adapter.
If only venture continuity wins, reduce portfolio prominence. If only allocation
and comparison win, narrow the product to that job. If people repeatedly need
unattended completion, trial one bounded runner. None of these results justifies
building every business function.

Possible commercial packaging, if validated, is paid shared workspace operation,
integrations and reliable optional execution. Execution usage should be explicit;
charging for a generic idea score or relying on trapping venture history is a
weak thesis. Distribution through an agent integration is a channel, not proof
that anyone needs the product.

The next implementation agent should first address the two intake semantics above
and the retained browser gate, then implement only a demonstrated missing piece
of the chosen workflow. This proposal does not queue a redesign or authorize a
schema migration. The architecture recommendation is captured as
[proposed ADR 0013](../../adr/0013-venture-coordination-and-executor-boundaries.md).
