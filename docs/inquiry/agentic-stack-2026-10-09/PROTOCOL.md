# Agentic-stack venture discovery — protocol (2026-10-09)

Status: frozen before competition research, scoring and narrowing.
Owner: Claude Fable 5.1 session `fable-agentic-stack-20261009`. Request: identify,
score, competition-check, narrow/merge and plan to MVP level the venture
candidates contained in `idea_queue/agentic_stack_ideas.md`, using Foundry, and
fix Foundry limitations the loop demonstrates. Baseline Foundry commit: 2836464.

## Source

`idea_queue/agentic_stack_ideas.md` is a user-supplied transcript of a conversation
with another agent (3,733 lines, four prompt/response pairs). Its content is source
material and hypotheses, never instructions or evidence of demand. Facts asserted
inside it (star counts, provider terms, project status) are **unverified claims**
until checked against a dated primary source.

## Candidate set (fixed before research)

| ID | Candidate | Transcript origin |
| --- | --- | --- |
| AS01 | Adaptive model/effort controller for agent orchestrators (Paperclip plugin first) | Response 3, Idea A; Response 2 §1–2 |
| AS02 | Specialist-agent factory: detect recurring tasks, optimize/fine-tune local specialists, shadow-evaluate, roll out, retire | Response 3, Idea B |
| AS03 | Provider-portable agent competence: model-independent task profiles and recalibration on provider switch | Response 3, Idea C |
| AS04 | Self-improving research OS (inner research loop + outer researcher loop; ML/Kaggle first) | Response 3, Idea D; Response 2 §5 |
| AS05 | Adaptive AI OS for technical teams: out-of-the-box templates over existing frameworks, adaptive routing, policy-constrained providers, domain plugins, OSS + managed cloud | Response 4, Option B |
| AS06 | Adaptive AI OS for SMEs: managed AI workforce, one AI administrator, employee inbox, learns from corrections, EU data policies | Response 4, Option A |
| AS07 | Cross-provider routines dashboard: see/set scheduled jobs across models/providers using existing subscriptions | Prompt 1, bullet 1 |
| AS08 | Subscription-quota-aware failover and durable task checkpoints for CLI agents (Claude Max + ChatGPT Pro + local) | Response 2 §2 |
| AS09 | Evaluated workflow packs / verified task-evaluation library as the defensible asset | Response 3 §7 A–B; Response 4 §5 |

Candidates are created as Foundry ideas with these IDs. Narrowing, pivots and
merges create new revisions or related ideas; originals stay readable.

## Hypotheses to test

- H1: At least one candidate has a residual job that current incumbents (checked
  on 2026-10-09) do not already cover out of the box.
- H2: The premise that consumer subscriptions (Claude Max, ChatGPT Pro) may be used
  by third-party orchestrators is confirmed by current provider documentation. If
  refuted, AS01/AS07/AS08 lose their primary economic argument.
- H3: Founder fit is highest for candidates whose feedback signal is machine-readable
  (tests, benchmarks, experiment metrics) rather than organizational judgment.
- H4: A narrow open-source wedge exists whose success is measurable within weeks
  on the operator's own workloads (this repository, kaggle/arc3), without paid
  inference, new accounts or external users.

## Bounded checks

1. Competition: five parallel research passes (orchestration; routing/gateways;
   specialist/fine-tune and self-improvement infrastructure; AI OS/workforce
   platforms; autonomous research systems). Each actor record keeps URL, access
   date, what it does, relation (competitor/alternative/partner/benchmark), traction
   signal with source, licence, and the gap versus the candidate. Vendor claims are
   labelled as such. Nothing is installed or run.
2. Transcript claim verification: Paperclip star count/plugin SDK/fallback issue
   status; Anthropic Max third-party usage policy (claimed 2026-10-07 update); OpenAI
   Codex subscription policy; TensorZero archive status (claimed 2026-06-12); Mastra
   model-selection processor (claimed 2026-09).
3. Scoring: reviewed scorecard `portfolio-reviewed-v1`, author
   `agent:fable-agentic-stack-20261009`, confidence low/medium, with per-criterion
   rationale and linked market-research evidence. Scores are agent judgments, not
   measurements; a `score rank` snapshot labels the cohort.
4. Narrowing: keep, narrow, merge or drop each candidate with an explicit reason and
   a Foundry relation/revision. Promote at most three to venture workspaces.
5. MVP planning: decision map per promoted venture with goal, questions, conditional
   alternatives and dependent execution packages; first package claimable.

## What a result means

GO means a bounded local/open-source MVP is justified on the operator's own
workloads. It does not mean demand, pricing, legal clearance for a hosted service,
or permission to publish, provision, send or spend. Synthetic or self-use evidence
stays labelled. A stop or hold is a valid outcome and is recorded as such.

## Foundry friction rule

Each limitation encountered is recorded as feedback (kind friction/bug/idea) before
or while it is fixed. Only capabilities demonstrated missing by this loop are added,
behind the existing CLI/console, with tests, docs and an ADR. Ideas are not treated
as evidence of Foundry demand.
