# Candidate G002: source-backed research handoff

- Record: FOUNDRY-INQ-20261002-003:r1
- Status: proposed bounded trial; protocol frozen before measurement
- Source: workbook `Ideas!B2:W2`, G002, R&D Decision Memory
- Owner: Foundry venture investigation; no standalone runtime product yet
- Budget: at most eight learner hours for active Slice 005, with no paid calls
  or infrastructure. An optional existing-tool setup gets at most two of those
  hours; unavailable tools are reported as untested, never as defeated.

## Problem hypothesis and intended user

A researcher or small technical team returning to a project needs to answer:
what was attempted, why did the decision change, which evidence supports it,
which contradictions remain, and what should be tried next? Scattered Markdown,
experiment trackers and chat context may make this expensive. We do not yet know
how frequent or costly that problem is outside this user's projects.

The proposed job is **recovering a trustworthy handoff from records already
created**. It is not another universal memory database, experiment tracker, or
autonomous researcher. Useful output would be a short answer with exact source
references, revision/status distinctions and explicit missing evidence.

## Inputs and scope

Start with 10–20 permitted, small canonical Foundry inquiry/decision records.
Select records written before the test questions wherever possible; do not
rewrite source notes to make a tool look good. Optionally repeat a small part on
permitted ARC3 planning/handoff records after reading that project's rules.
Do not inspect frozen evaluation results, private customer material, or bulk
human gameplay datasets. ARC3 and Foundry data remain separate.

Freeze paths, SHA-256 hashes, IDs, revisions and tool versions before timing.
Retain a short list of exactly what was unavailable. Both projects share an
owner; cross-project recurrence provides engineering evidence, not market proof.

## Baselines and procedure

1. Establish the ordinary workflow: Markdown/Git plus search and any already
   authorized assistant workflow, with the same input corpus and model access
   in each comparable arm. Do not compare unaided search to an assistant and
   attribute the whole difference to Foundry or memory tooling.
2. Use existing Foundry records/CLI to reconstruct the same kinds of decisions.
   Count one-off setup and ongoing entry/revision work separately. No schema or
   application changes are needed to start the comparison.
3. If available locally within the budget, compare pinned Hindsight v0.10.2
   following the central pilot rules. Inspect configuration first; no paid
   provider fallback. Latest vendor docs do not guarantee pinned-version features.
4. Prepare ten questions with an answer rubric/source references before running:
   include current decision, rejected option, negative result, evidence chain,
   superseded revision, contradiction, and an unanswerable question. The learner
   judges source fidelity; agent-generated expected answers require checking.
5. Split questions into balanced sets and alternate which workflow is tried
   first; record order and prior familiarity. Repeating identical questions
   teaches the answer, so label any repeated-query timing as biased. Report raw
   per-question results and medians; ten questions are a screening exercise,
   not a statistical claim. A result too confounded to compare is inconclusive.
6. Record task seconds, correct decision/status, correct evidence reference,
   unsupported claims, setup minutes, capture/update minutes, and observed
   recurrence. Have the learner explain one wrong or missing result from source.

## Precommitted interpretation

- Safety/fidelity gate: zero unsupported consequential decision claims; at least
  9/10 answers correctly distinguish what evidence establishes, including
  abstaining on the unanswerable case. LLM fluency is not a correctness metric.
- Utility signal: at least 30% lower median recovery time than ordinary workflow
  at no worse fidelity. Also show positive estimated weekly time savings after
  measured capture/update overhead using **observed** recovery frequency. If
  frequency is unknown, label net utility unproven. Report setup break-even
  separately; do not hide it in amortization assumptions.
- These thresholds are pragmatic selection rules for a tiny local trial, not
  validated market benchmarks. A smaller but valuable benefit can be discussed
  explicitly; do not silently move the threshold after observing results.
- **Use existing tools** if they meet the need. **Adapt narrowly** only if a
  concrete gap recurs and a small adapter plausibly closes it. Freeze a separate
  bounded test before implementation. No new memory engine.
- **Defer/stop** if pain is rare, overhead cancels benefit, fidelity fails, or a
  baseline suffices. A missing Hindsight arm limits the verdict; it cannot justify
  claiming superiority over Hindsight. Stop at the timebox if still inconclusive.

## Commercial hypothesis and next gate

Potential offer, if utility survives: an open local evidence connector/checker
with paid managed team operation or integration/support. Candidate buyers are
small research/engineering teams with repeated handoffs, not every AI user.
No license, pricing, customer count, or revenue is decided.

Before a larger build, independently observe the workflow in three organizations,
seek two concrete tests on permitted data, and discuss budget with a buyer. A
finance introduction can be used for neutral problem discovery if the user later
authorizes outreach; do not presume interest in agents or compliance software.

## Deliverables and learning boundary

Save a source manifest, per-question measurements, error analysis, one concise
learner verdict and a Foundry evidence→assessment→decision record. Routine
transcription and support tooling are agent-owned. No trial has passed yet.
See the [active acceptance contract](../../../learning/slices/005-venture-evidence-gate/ACCEPTANCE.md).
