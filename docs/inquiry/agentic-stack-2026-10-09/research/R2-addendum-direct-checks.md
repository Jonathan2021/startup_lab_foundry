# R2 addendum — direct checks by the coordinating session (2026-10-09)

Two uncertainties left open by R2 were checked against primary pages. Web reads only.

## LiteLLM Auto Router v2 — no documented outcome-reward API

- [Auto Router v2 blog](https://docs.litellm.ai/blog/autorouter-v2) and the
  [auto-routing docs](https://docs.litellm.ai/docs/proxy/auto_routing) describe
  "Adaptive" Thompson-sampled pools and say only: "Feedback from a later turn
  attributes back to the model that actually served the previous response."
- Neither page documents an endpoint, header, SDK method or callback for an
  application to submit a reward (for example a test pass/fail), nor defines the
  reward signal. Routing keys on classifier tier, keyword rules and message text;
  reasoning effort is not a classifier input (each effort level is a separate
  `model_list` entry). Escalation caps/cooldowns are listed as future work.
- Reading: as documented today, LiteLLM does not take machine-verifiable task
  outcomes keyed by task category as a routing reward. Absence in docs is not proof
  of absence in code; recheck the source before any build decision.

## Not Diamond Code — hosted, gated, Claude Code harness, API/gateway based

- [Launch post](https://www.notdiamond.ai/blog/not-diamond-code-intelligent-model-routing-for-coding-agents),
  [docs](https://code.notdiamond.ai/docs/), [CEO announcement](https://x.com/tomas_hk/status/2084669945150062619):
  a router "for long-horizon coding agents" that selects "the best model and
  reasoning effort for each step" (vendor claim). Evaluations used Claude Code as
  the harness routing across Haiku 4.5 / Sonnet 4.6 / Opus 4.8 effort levels and,
  in a SWE-PolyBench-Verified run, GLM 5.2 and DeepSeek V4 Flash; savings claims of
  20%+ (blog) and 20–65% (posts) are self-reported.
- A local proxy computes routing metadata; only metadata goes to Not Diamond's
  optimisation service, the model request goes through the user's own provider or
  gateway (docs). Access is a gated waitlist; an enterprise early-access program is
  mentioned. The landing page `/code` returned 404 on 2026-10-09.
- Reading: a direct hosted competitor for the "per-step model + effort" part of
  AS01, built on API keys/gateways rather than subscription CLIs, with learning
  signals unspecified. It does not address quota-as-constraint across vendor CLIs,
  durable cross-provider handover, or an open local evidence ledger.
