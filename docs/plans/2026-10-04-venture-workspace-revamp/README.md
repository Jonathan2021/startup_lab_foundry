# Foundry venture workspace revamp handoff

Prepared 2026-10-04 as a planning-only handoff. The user subsequently authorized
execution on 2026-10-05. Implementation and permanent-store intake are now applied;
desktop/mobile browser acceptance and the official container build remain pending.
See [STATE.md](STATE.md) and the [execution report](../../inquiry/revamp-2026-10-05/REPORT.md)
for actual checks and canonical records. The specifications below preserve the
original implementation contract. The real sports fusion remains undecided.

Keep the existing local FastAPI/Jinja/SQLAlchemy application. Organize Foundry
around portfolio decisions and focused venture workspaces. Add independent venture
scores, contextual answers with a durable review queue, and reversible fusion
decisions. Use a small selection of built-in workspace modules; defer a plugin
platform. The sports case below is the first concrete fusion proposal, not an
accepted merger or authorization to build a sports product.

## Read only what the task needs

Read root and Foundry AGENTS.md, this index, and [STATE.md](STATE.md). Then read
the relevant specification:

| File | Decisions and implementation contract |
|---|---|
| [Baseline and answers](00-BASELINE-AND-ANSWERS.md) | Verified gaps, exact sports identities, R005–R009 interpretation and follow-up work |
| [Workspace and scores](01-WORKSPACE-AND-SCORES.md) | Navigation, wireframes, score selection, history and independent venture assessment |
| [Input and agent handoff](02-INPUT-AND-HANDOFF.md) | File/UI answers, revision detection, review, queue, manual agent pickup and completion |
| [Fusion proposal](03-FUSION.md) | Volleyball proposal, scope comparison, accept/edit/reject, safe application and lineage |
| [Modules and delivery](04-MODULES-AND-DELIVERY.md) | Common and optional components, schema boundaries, ordered tasks and validation |
| [Architecture decision](../../adr/0011-venture-workspaces-inputs-and-fusion.md) | Context, implemented decisions, consequences and revisit conditions |

These documents supersede conflicting UX and next-action recommendations in the
[earlier handoff](../2026-10-04-portfolio-and-venture-handoff/README.md). Its
implementation and inquiry reports remain historical evidence. Do not rerun its
T00–T10 campaign or repeat already answered questions.

## Decisions the executor should not rediscover

- Put ID, score, current focus and one contextual primary action at the top of
  every idea/venture detail. A venture score evaluates that venture independently
  of its source idea. A starting idea estimate must say where it came from.
- Separate **Answer a question**, **Review an answer**, **Update venture state**,
  and **Start work**. They are different actions. A reply is not validation or an
  instruction to send outreach.
- Editing a file does not wake an agent. Explicit synchronization records new
  answers and queues review. A manually started agent picks them up and records
  what changed; the UI shows each transition. No unattended worker in this plan.
- Recommend one volleyball-first sports venture, keeping both original ideas
  and workspaces as readable history. Show included, deferred and excluded scope
  before a user accepts, modifies or rejects the proposal with rationale.
- An agent can draft, revise and recommend a proposal. Applying this particular
  fusion requires an explicit decision on its exact revision. Future delegated
  decision authority must be separately recorded; an agent actor string is not
  authority.
- A venture workspace is a focused operating area within the modular monolith.
  It does not imply a new deployed app or database per venture. Venture product
  code stays in its own linked repository/product boundary.
- R008 and R009 are explicit holds. Do not nag for the same feedback or queue
  investigation on those tracks while waiting. R005–R007 contain usable new
  information, with remaining uncertainties specified in the baseline document.

## Execution order after authorization

| Task | Deliverable | Depends on |
|---|---|---|
| V00 | Recheck dirty state, input digests and backup; freeze baseline and meaningful failing acceptance cases | None |
| V01a | Durable requests and immutable file/UI responses with conflicts and repeat-safe synchronization | V00 |
| V01b | Manual answer review queue; ingest R005–R009 and apply the documented outcomes | V01a |
| V02 | Independent venture scoring and shared score summaries | V00 |
| V03 | Portfolio/venture navigation and contextual input UI; demonstrate the P103 flow | V01b, V02 |
| V04a | Reviewable sports proposal, revision comparison and decisions | V01b, V03 |
| V04b | Atomic fusion application and preserved lineage, tested on disposable records | V04a |
| V05 | Built-in module selection; Software view for existing projects; bounded follow-up briefs | V03; proposal can remain undecided |
| V06 | Migration rehearsal, regression and actual desktop/mobile browser acceptance | All implementation tasks |

Task dependencies permit independent work, not automatic subagent delegation.
Do one vertical task at a time. No learning slice is prepared by this plan.

## Copyable execution prompt

> Implement the local Foundry revamp in
> `/home/jonathan/startup_lab/foundry/docs/plans/2026-10-04-venture-workspace-revamp/README.md`.
> Read root/Foundry AGENTS.md and the plan's STATE.md, then execute the first
> pending task using its linked specification. Preserve all unrelated edits,
> original evidence and inline replies. Write meaningful acceptance tests before
> implementation where practical. Keep the current stack and use backed-up or
> disposable stores for migration tests. Do not create a generic plugin/agent
> framework. Seed the sports proposal as pending; do not accept it for me.
> Preserve R008/R009 holds. Update STATE.md with files, commands, outcomes and
> exact next task. Do not commit, push, publish, spend, provision, send messages,
> create accounts, train/download models or change learning ownership. An
> undecided proposal blocks only its application to my real portfolio, not
> independent implementation or disposable-fixture tests.
