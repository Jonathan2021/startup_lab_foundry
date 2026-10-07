# Fresh agent comparison

Date: 2026-10-06. Four invented cases, two fresh sessions with the same inherited
model configuration, no model override. Neither session received conversation
history, the fixture generator, answer key, the product recommendation or the
other session's answer. Each was instructed to read only its assigned condition,
use no browsing, and answer the same questions within 170 words per case.

Inputs were frozen before either session ran:

- `/root/blind_files`: `experiments/files_condition.md`, 7,633 UTF-8 bytes.
- `/root/blind_packet`: `experiments/packet_condition.md`, 12,223 UTF-8 bytes.

These are input-file sizes, not complete model request sizes. System instructions,
tool definitions, reasoning/output usage, cache state and billable tokens were
not measured. Agent identities identify these local experimental sessions; exact
provider/model version and per-session cost were not exposed in the result.

The parent reviewed both answers against the prewritten `experiments/oracle.json`
and the supplied source text. This is an unblinded qualitative assessment, not
an independent scored benchmark or statistical claim.

| Case | Concise file answer | Structured packet answer | Assessment |
|---|---|---|---|
| C01 lunch coverage | Stop basic waiting-time thesis; seating remains an unproven separate question; no build or reservation permission inferred | Same conclusion and limits; additionally states package coverage limit | Both preserve counterevidence and distinguish a new hypothesis from validation |
| C02 security | Hold affected r18 experiment, retain unrelated documentation, local reproduction/draft patch only; no production-breach claim | Same conclusion and limits | Both recover dependency, supersession and authority correctly |
| C04 outreach | Stop Aspen pitch, retain opt-out and restricted Birch context, no send authority | Same; explicitly leaves Birch's task intact | Both correctly separate shared identity from permission; file answer does not explicitly restate Birch's active status |
| C08 pivot | Current B2B outcome unknown, freeze new test, old consumer threshold cannot validate it, keep accessibility audit | Same conclusion and limits | Both handle stale scope and unknown evidence without inventing demand |

Both answers identified all four intended branch decisions, cited their source
records and avoided the principal unsupported factual/permission claims. No
reliable answer-quality advantage was observed. The packet session repeated its
explicit selection warning in each answer; the file brief had no equivalent
metadata. That is useful transparency but also additional output to read.

The file brief was oracle-curated. This comparison does not price the effort
needed to maintain it, nor the effort needed to maintain correct graph links.
The failed supplier-selection case C03 was deliberately excluded from the
format-only agent comparison because it would supply unequal evidence. Its
39/40 selection result remains a separate negative finding in the experiment.

## Representative retained answer excerpts

These excerpts are experimental agent outputs, not observations of real ventures.

File session, C01: “Stop the proposed waiting-time service. Verified live estimates
cover both restaurants, contradicting the founder’s unchecked assumption
(C01-E2, C01-E1). No distinct repeated decision failure is evidenced; comments
about sitting together do not establish one (C01-E3).”

Packet session, C01: “Stop the proposed waiting-time service. Verified live queue
estimates cover both restaurants, overturning the initial assumption (C01-E2,
C01-E1). Seating comments support a hypothesis, not a directly observed repeated
unmet job (C01-E3).”

File session, C08: “Treat the outstanding revision-1 research as stale for this
decision, not as pilot clearance. Keep the independent current-scope accessibility
audit active; do not revive the homeowner prototype objective or infer authorization
to execute a pilot (C08-E3, C08-E5).”

Packet session, C08: “The outstanding revision-1 research submission cannot validate
revision 3 and needs reassessment against its current question (C08-E5). Delays,
buying authority, paid commitment and repeated observations remain missing
(C08-E4). Old research completion grants no pilot approval.”

## Result for the plan

Use concise task prose with exact references as the default agent view, backed by
typed records and a machine-readable manifest. Test recurring updates and safe
reconciliation next. These four cases provide no reason to train a model or to
claim that reading JSON inherently saves tokens. They do establish that either
representation can convey the intended four decisions in this small probe.
