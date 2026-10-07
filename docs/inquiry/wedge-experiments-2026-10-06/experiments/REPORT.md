# Synthetic context and decision-boundary experiment

Date: 2026-10-06. All eight ventures, records, names, thresholds and observations in this directory are invented. None updates the real Foundry database. These scripts are experimental fixtures, not product implementation or a production acceptance suite.

## Result

The proposed backbone does **not** earn a context-size advantage over strong files in this test. An oracle-curated concise Markdown brief contains the required facts in 13,605 UTF-8 bytes; the deterministic structured packets require 22,288 bytes, **63.8% more**. A backbone should be able to return concise prose with source IDs; making the agent read the storage schema is not itself a benefit.

Against the full organized dossier the aggregate packet is only 0.66% smaller. That apparent saving includes one materially incomplete case. On the seven cases where all required source records were selected, packets are **0.94% larger** than the full dossier. Six of eight packets are larger than their full dossier. This is a negative result for a general claim that dependency selection plus JSON automatically reduces context cost in small, organized workspaces.

Deterministic dependency selection retained **39 of 40 required source records**. It missed a late supplier cancellation because that fact was not linked to the current question or existing evidence. The strong file brief includes it. This is the intended adversarial ingestion failure, not an irrelevant exclusion. Metadata-based selection needs a way to detect or review newly arrived/unlinked evidence; perfect relationship metadata cannot be assumed.

The ten test-only transition simulations passed their frozen expectations. They illustrate explicit stale-result, duplicate, scope, uncertainty, contradiction and stop semantics. They do not establish that the existing application implements those rules or that a reasoning agent will select the right branch.

## Scope and conditions

The eight cases cover lunch discovery, a software-security interrupt, physical supply, outreach permissions, pricing, negative competition, sports-venture fusion and a customer pivot. Each has an objective, scope and question revision, current question, four explicit outcome criteria, five required source records, and six additional historical/sibling/portfolio records. Contradictions, corrections and supersession are retained as evidence rather than erased. The supplier case deliberately contains a relevant unlinked late fact.

The three conditions use the same underlying fixture facts:

1. **Full organized dossier:** readable Markdown, complete record text, source IDs, scopes, revisions and relationships; includes historical/unrelated records. This is not a deliberately disorganized conversation dump.
2. **Strong concise file baseline:** all five oracle-required source records, verbatim source text and relationships, plus the same objective, question, revisions and outcome criteria. It includes no oracle recommendation. Its perfect relevance selection is privileged and should be treated as an upper-bound file brief, not a measured automatic summarizer.
3. **Dependency packet:** JSON containing the same objective/question/criteria, explicit allowed scopes, provenance and selection metadata, and verbatim records selected by bidirectional explicit-link closure from the current question's source IDs. Reverse links retain later contradictions/supersession. Scope filtering happens before selection. There is no semantic retrieval, generated summary, trained model or automatic relationship extraction.

Bytes include serialization overhead. The packet's source text accounts for only part of its size; repeated field names, selection metadata, criteria, IDs, revisions, indentation and relationships are retained in the reported totals. The two displays need not be equally verbose in a product: an application can store structured records and export concise Markdown.

| Case | Full dossier bytes | Concise files bytes | Packet bytes | Required source records recovered |
|---|---:|---:|---:|---:|
| C01 Local lunch discovery | 2,771 | 1,667 | 2,773 | 5/5 |
| C02 Software security | 2,861 | 1,757 | 2,928 | 5/5 |
| C03 Supplier dependency | 2,708 | 1,604 | 2,374 | **4/5** |
| C04 Outreach privacy | 2,884 | 1,780 | 2,878 | 5/5 |
| C05 Pricing | 2,716 | 1,612 | 2,721 | 5/5 |
| C06 Negative competition | 2,654 | 1,550 | 2,661 | 5/5 |
| C07 Sports fusion | 2,898 | 1,794 | 2,945 | 5/5 |
| C08 Customer pivot | 2,945 | 1,841 | 3,008 | 5/5 |
| **Total** | **22,437** | **13,605** | **22,288** | **39/40** |

Whitespace-delimited word totals are 3,172, 1,996 and 2,498 respectively. These are exact byte/word measurements of these artifacts, **not token counts, inference bills, cost savings or latency measurements**. UTF-8 bytes and whitespace words do not reliably determine a provider's token count.

## Adversarial transition checks

Frozen inputs specify ten isolated checks, each starting with its own state:

- Old scope/question revision: reject the result without effects.
- Exact repeated result ID and payload: return the prior result, apply one effect.
- Cross-scope evidence: reject; shared visibility is not authority.
- Inconclusive/unknown outcome: hold, without scheduling a success branch.
- Stop outcome: stop this inquiry, without scheduling a successor.
- Later contradictory evidence: retain accepted history, require review and block the affected successor.
- Stop with an unrelated active sibling: leave the sibling active.
- Scope revision after a result: preserve old history, mark the new scope unresolved and block the old successor.
- Continue without required evidence: reject insufficient support.
- Same result ID with changed payload: reject key conflict.

The experiment's `submit` function uses a deliberately simple predefined evidence requirement. It does not judge substantive source quality or prove criteria are valid. Contradiction and scope-change events are explicit fixture events, not automatically inferred semantics. All ten pass; no negative runtime result is hidden.

## Independent agent evaluation inputs

`files_condition.md` and `packet_condition.md` contain identical instructions and four cases: C01, C02, C04 and C08. Each condition contains exactly the same five source texts per case and outcome criteria. They do **not** expose the oracle's recommended answers. The file condition is 7,633 bytes / 1,122 whitespace words; packet condition is 12,223 bytes / 1,403 words, including the identical instructions and display wrappers.

Evaluator agents must read only their assigned condition and answer without browsing or inspecting the fixture generator/oracle. Grade against `oracle.json`, with separate checks for supported facts, next action, scope/permission, supersession, unknown/stop handling and unsupported claims. A scorer should not reward wording agreement over defensible reasoning. A result of equal quality would support interoperability, not superiority or savings. Any resulting agent answers/grades should be saved separately and identified by evaluator session/model where available.

No independent-agent quality result is claimed in this report; the parent investigation manages that comparison separately.

## Limits and implications

- Synthetic cases demonstrate possible correctness failures, not their prevalence in real customer work or willingness to pay. Selection was handcrafted, and most fixtures have clean relevant edges; this is unusually favorable to the packet selector.
- Oracle curation hides the cost of maintaining a perfect brief. The dependency condition hides the cost of assigning good scope/relationship metadata. Neither cost was measured. A fair recurring-work study must include updates, agent tool calls, exception handling and human review on both sides.
- The seven complete packets and file briefs contain the same substantive selected facts. A tiny same-model answer comparison will principally measure display differences, not large-scale retrieval quality.
- Six unrelated records per case are modest context. Benefits could grow with history, or disappear with good file indexes; neither scale effect was tested. Do not extrapolate to a large portfolio.
- The C03 failure suggests a concrete requirement: relevant new intake must be surfaced even when it has no existing decision edge. A compact packet must disclose completeness limits, reference its selection revision and offer expansion to recent unreviewed sources. This is a proposed response to the observed synthetic failure, not a tested fix.
- The decision map's plausible value is explicit branch criteria, retained rationale, visible dependencies and stale-result handling. A dynamic map must not turn guessed thresholds into automatic business truth, or erase scope changes and negative results.
- No trained cheap executor, price, customer demand, inference token count, elapsed task latency, willingness to pay, real-world success, model training or live application correctness was tested here.

## Reproduction and retained artifacts

From the repository root:

```bash
python3 foundry/docs/inquiry/wedge-experiments-2026-10-06/experiments/run_experiment.py
```

The run validates the SHA-256 hashes of the frozen fixtures, oracle, transition expectations and generation script before executing. `results.json` contains exact sizes, selection outcomes and full final transition states. `cases/` retains all three representations for each case. `output_hashes.sha256.json` records output and runner hashes.

The generator is retained for provenance and deliberately refuses to overwrite frozen inputs. Do not rerun it in this directory; use a new versioned experiment directory to change scenarios. Fixtures and expected outputs were frozen before the first measurement run. The initial launcher used `python`, which resolved to a legacy interpreter and failed at Python 3 type syntax before writing any fixture; rerunning with `python3` created the frozen fixtures. This environment-launch failure did not change inputs or results.
