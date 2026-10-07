# Foundry alternatives and the selected wedge

Date: 2026-10-06. Primary-source desk comparison. Documented/marketed capabilities
are not independent quality tests. No account trial or absent-feature claim is
made. This extends the earlier product-boundary review with closer competitors.

## Alternatives that materially affect the decision

| Candidate direction | Relevant alternative and observed overlap | Judgment for Foundry |
|---|---|---|
| Generic product context and internal agents | Productboard Spark describes persistent product context, specialized work and MCP handoff. Its current product page also discusses model/evaluation and token optimization. [Launch](https://www.productboard.com/blog/introducing-spark-agentic-product-system/), [product](https://www.productboard.com/product/spark/) | Too broad as an initial positioning. Persistent context and specialization alone are already offered. |
| Dynamic discovery graph | Vistaly documents typed outcome/opportunity/solution/assumption/test cards, linked evidence, shared cards across spaces and delivery connections. [Canvas](https://vistaly.com/product/ost-canvas) | A useful interface, with direct competition. Do not treat a graph as differentiation. |
| Agents updating discovery graphs | Vistaly exposes search/create/update and evidence/metric intake through MCP. [Integrations](https://vistaly.com/product/integrations) | BYO-agent access is an integration requirement, not a novelty claim. |
| AI-maintained graph edits | Teresa Torres describes Vistaly's proposed tree changes, review and semantic operations with validation. [Primary account](https://www.producttalk.org/behind-the-scenes-ai-osts/) | Graph maintenance and review also overlap. Our exact behavioral advantage must be demonstrated. |
| Agent task memory | Beads documents a dependency-aware task graph, ready work, claims and persistent agent memory. [Repository](https://github.com/gastownhall/beads) | Rebuilding a generic agent issue tracker would have a strong free substitute. |
| Relevant competitor alerts | Visualping already offers prompt-defined important changes, structured extraction and agent workflows. [Product](https://visualping.io/ai) | Reuse monitoring inputs; do not build a general crawler or sell generic alerts as new. |
| Competition feeds into agents | Crayon's October 1 announcement describes source-linked competitive changes exposed through an API for existing tools. [Announcement](https://www.crayon.co/blog/insights-api) | Source collection is another replaceable input, not the proposed unique value. |
| Generic long-term memory | Existing local records compare Hindsight, Graphiti, Mem0 and Letta. [Selection record](../../../../docs/adr/0007-shared-inquiry-memory-pilot.md) | Keep the optional adapter boundary. This review does not establish current feature parity or run a new memory benchmark. |
| Autonomous company execution | NanoCorp markets agents building, selling and operating businesses. [Product](https://www.nanocorp.so/) | Much broader operational scope and authority than our current useful workflow. |

Older Productboard beta support descriptions conflict with newer launch material;
the recommendation does not rely on old limitations. We did not establish that
any competitor lacks decision invalidation or transactional result handling.
That remains an explicit comparison question for a later live trial.

## Selected direction

**Keep venture decisions and their next work coherent as evidence changes, through
the agents users already use.** The initial job is the recurring handoff after a
research result, source change or test: recover the rationale, identify what needs
review, and continue the right work with an explicit owner.

Target hypothesis: a small studio or repeat operator handling several initiatives
and frequent agent handoffs. The current local workflow provides access for
engineering validation. It is not an independent customer sample. Single-venture
use remains complete; large-company product management is not the first target.

The distinction to test is behavioral: can Foundry correctly identify which
decisions need review, retain unaffected work, and provide a small sufficient
context to the next executor? It must do this with less maintenance than files
plus an agent and with a useful advantage over Vistaly/Productboard or Beads plus
a small adapter. Explicit stop/hold branches and permission boundaries belong
in this comparison. None is presumed exclusive to Foundry.

The proposed first paid specialty is **source-change impact review**: given
specific source versions and the current venture context, identify sourced changes
and propose which assumptions/decisions deserve re-review. The product connects
the finding to current commitments and can run the check without an open user
session. Broad competitor research remains available to an external capable agent.

Cheap-model execution is a second advantage to measure. A tiny model's low
inference cost is valuable only if source access, escalation, checking, failures
and upkeep leave room for a lower price at acceptable quality. The work unit
should be an accepted useful result; deterministic record operations should not
each become billable microtasks.

## Specialization evidence and its limit

The user's premise has technical support. The authors of
[Distilling Step-by-Step](https://arxiv.org/abs/2305.02301) report improvements
from small task-trained models on selected NLP benchmarks. Those results do not
establish open-web venture-research quality. [RouteLLM](https://arxiv.org/abs/2406.18665)
reports cost reductions from routing between models on its benchmark tasks;
it likewise does not establish Foundry economics.

Official OpenAI guidance describes small-model prompting and specialization as
optimization options and recommends evaluations before training.
[Latency guidance](https://developers.openai.com/api/docs/guides/latency-optimization),
[supervised fine-tuning](https://developers.openai.com/api/docs/guides/supervised-fine-tuning).
The current training documentation also says its hosted fine-tuning platform is
winding down and is closed to new users. Do not write a roadmap assuming that
particular service is available. Keep the training/inference provider replaceable
and verify availability at the actual funded experiment.

## Consequence for investment

Proceed with one bounded local decision-maintenance loop, then measure it.
Defer a graph editor platform, new memory engine, generic monitoring infrastructure
and proprietary autonomous-company runner. If an incumbent plus a small adapter
passes the same practical tests with less upkeep, integrate it and keep only the
useful Foundry boundary. The direction is a chosen engineering/product bet,
not a proven commercial gap.
