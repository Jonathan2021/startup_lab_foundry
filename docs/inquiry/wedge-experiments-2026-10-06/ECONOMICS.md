# Specialized execution economics

Date: 2026-10-06. **Illustrative sensitivity analysis, not observed model prices,
training costs, product pricing, or a Foundry inference benchmark.** No training,
paid inference or provisioning was performed.

The user's proposal is plausible: specialized small-model execution can offer
comparable quality at a lower price than a general agent doing the whole task.
The relevant denominator is an accepted useful result. Smaller prompts and
models are inputs to the calculation, not the result of it.

## Cost model

Let:

- `s` = small-model inference per attempt;
- `r` = fraction escalated, and `l` = additional large-model inference per escalation;
- `t`, `v`, `o` = source/tool, validation and serving/operations cost per attempt;
- `q` = accepted-result fraction, counting rejected attempts as costs;
- `F` = fixed data/training/evaluation investment; `N` = accepted jobs over which
  it is amortized.

Then illustrative cost per accepted job is:

`C = (s + r*l + t + v + o) / q + F/N`

To offer a customer saving fraction `a` against their appropriate DIY alternative
`D`, while retaining contribution fraction `m` after these modeled costs:

`C/(1-m) <= price <= D*(1-a)`

Use the cheapest adequate DIY alternative, with realistic caching and existing
subscriptions. Do not compare only against a deliberately expensive flagship
agent. Customer time is a separate value claim, not an invented cash saving.

## A numerical stress test

All amounts below are hypothetical US dollars. Chosen assumptions: `s=0.006`,
`l=0.20`, `t=0.020`, `v=0.006`, `o=0.008`, `q=0.95`, `F=3000`;
desired modeled contribution `m=60%`, customer cash saving `a=30%`.
Salary, acquisition, taxes and general company overhead are outside this model.
These values are deliberately transparent variables, not quoted provider rates.

| Scenario | Accepted volume N | Escalation r | DIY per result D | Modeled cost C | Minimum price | Customer price ceiling | Room for both goals |
|---|---:|---:|---:|---:|---:|---:|---|
| Sufficient recurring volume | 300,000 | 10% | $0.30 | $0.0732 | $0.1829 | $0.2100 | Yes, narrow |
| Customer already uses a cheap adequate model | 300,000 | 10% | $0.08 | $0.0732 | $0.1829 | $0.0560 | No |
| Frequent escalation | 300,000 | 30% | $0.30 | $0.1153 | $0.2882 | $0.2100 | No |
| Low task volume | 10,000 | 10% | $0.30 | $0.3632 | $0.9079 | $0.2100 | No |

In the first scenario, satisfying both targets requires roughly **143,940 accepted
jobs** to amortize the hypothetical fixed investment. The inputs could differ by
orders of magnitude; this is an explanation of sensitivity, not a volume forecast.
A customer whose agent subscription has zero marginal cash cost cannot receive
a cash inference saving from a positive per-job fee. They may still value scheduled
completion, shared state, fewer mistakes or preserved usage capacity.

## Product implications

1. Make the backbone useful with the user's agent. It is also the context and
   evaluation foundation for a future cheap executor.
2. Start specialty evaluation with source-change impact review, a narrow input
   and reviewable output. Retrieval/fetching can come from existing sources and
   monitoring tools; do not require a new crawler.
3. Compare a prompted small model, a stronger model and a specialized candidate
   on held-out scenario families. Measure cited factual accuracy, missed/false
   affected decisions, abstention, cost per accepted job and human corrections.
4. Train only if the observed error pattern is learnable, sufficient volume exists
   and training beats better prompting, deterministic preprocessing and routing.
   Source facts still come from current evidence; training is not a store for
   current competitor facts.
5. Include failures, checking and expensive fallback in the customer price. Show
   a budget and stop condition; no unapproved escalation or paid fallback.

Recommended packaging hypothesis: portable local/BYO-agent use, with paid managed
continuity, collaboration and bounded scheduled jobs. Whether the local package
is open source and its license are separate decisions. No publication/license
change is made here. Avoid pricing each record write or charging for access to
the user's own history.

## Data without manual work by the user

Agents can generate source versions, contradictory updates and expected outcomes
from explicit synthetic world state; an independent critic checks the labels.
Hold out entire scenario families and source templates, not only random rows.
Keep invented material visibly synthetic and outside real venture assessments.
Collect later corrections from normal use with permission; do not ask the user
to populate a training spreadsheet. The current eight-case suite is a mechanics
probe, not a sufficient training or economic benchmark.

The first paid model experiment would require an exact provider/model, a fixed
evaluation set, a stated spend cap and authorization before execution. That
future requirement does not block the current no-spend synthetic work or plan.
