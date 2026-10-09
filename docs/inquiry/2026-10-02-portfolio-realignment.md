# Portfolio reassessment and disposition

- Record: FOUNDRY-INQ-20261002-002:r2
- Date: 2026-10-02
- Status: completed documentary assessment; workflow measurement and demand
  validation pending. Supplements the frozen r1 plan with results.
- Attribution: agent research, portfolio screening, documentation, and local CLI
  operation; no customer interviews and no independent learner assessment.
- [Plan](2026-10-02-portfolio-realignment-plan.md) ·
  [Decision](../../../docs/adr/0008-evidence-first-venture-realignment.md) ·
  [All-idea screen](2026-10-02-portfolio-screen.md) ·
  [Operation record](2026-10-02-foundry-operation.md)

## Recommendation

Pause standalone Agent EvalOps implementation. Retain Foundry's completed
foundation as an internal tool and evaluate whether its structured records earn
their maintenance cost. Give only a bounded trial to the workbook's G002,
**R&D Decision Memory**, narrowed to recovering source-backed decisions for a
research handoff. No candidate is yet qualified for a substantial product build.

This is a change in investment priority, not a claim that all evaluation or
venture software is obsolete. Nor is G002 declared an empty market. Its advantage
is immediate access to our own real records and a cheap falsifiable comparison.

## What the workbook establishes

Source: `startup_ideas_portfolio_v2(1).xlsx`, `Ideas!A1:AQ239`; SHA-256
`ebc5028a27aaed5c574da0355a1a7f1dc361c35493106b77d013b645ba7339e4`.
Read-only extraction; the workbook and its formulas were not edited or executed
as instructions. The screen retains all 238 IDs and source rows. It is a broad
fit/access screen with focused research below, not 238 independent market audits.

The priority formula weights estimated revenue, profit, speed, founder fit,
go-to-market, defensibility, pain, and retention, with penalties. It does not
require an observed problem, an accessible customer, or a failed incumbent
baseline before recommending an MVP. Only 12 of the 238 `AQ` market-source fields
are populated; competitor URLs and other reference sheets exist separately.
Confidence labels (20 High, 103 Medium, 115 Low) are workbook assertions. The
revenue ranges are not reliable forecasts and do not drive this decision.

## Focused comparisons

Access means usable data and a realistic path to observing work, not theoretical
market size. Vendor documentation establishes advertised capability, not its
effectiveness or customer willingness to switch. Dispositions are our inference.

| Direction / workbook reference | Existing alternative and possible gap | Access and pitfalls | Disposition / next evidence |
|---|---|---|---|
| Agent EvalOps; related G021, row 3 | MLflow already supports human feedback, regression tests and CI gates [S1–S3]; LangSmith has annotation queues [S4]. A tool-change impact workflow would need a concrete advantage over versioned datasets, assertions and a script. | No customer agent traces or repeated failures. Optional/partial traces constrain causal checks. Judge calibration, privacy, integration upkeep and false alarms remain costs. | **Defer standalone build.** Keep this negative case. Reopen only for an observed workflow incumbents fail. |
| Foundry, U001, row 14; G001 row 13 | Buildpad offers cited research, staged guidance and project context [S5]; DimeADozen offers validation reports [S6]. Local evidence lineage and approval boundaries might be useful, but feature lists do not establish a market. | Own venture decisions are available. Risk: maintaining a meta-platform instead of testing ventures; research reports mistaken for demand. | **Internal only, evaluate.** Compare existing CLI with files; do not expand the platform. |
| Research handoff / R&D Decision Memory, G002 row 2; P088 row 12; P174 row 21 | Hindsight offers memory recall/reflection [S7]; W&B Reports combines narrative and experiment evidence [S8]. Test recovery of negative results, contradictions and source revisions across existing records. | Foundry records available; permitted ARC3 records are a possible second workflow. Same owner, no external buyer. Capture burden, stale sources and confident wrong synthesis can erase value. | **First trial, not build.** Use the bounded protocol; adopt existing tools if adequate. |
| Specialist job search, G004 row 8 | Simplify already tracks jobs [S9]; the user's installed job-finder skill already handles a narrow personal workflow. | Immediate personal use. Reliable job feeds, duplicates, stale listings, scraping permissions, differentiation and episodic demand constrain monetization. | **Personal-use fallback.** Improve the existing workflow only after observed friction; do not build a second generic tracker. |
| Model Data-Gap Scout, G019 row 9 | FiftyOne supports curation/active learning; Cleanlab supports confidence-assisted labelling [S10–S11]. A specific dataset might expose a narrower useful selection method. | Good ML learning fit, but no current customer corpus or labelled target task. Benchmarks can reward leakage or label assumptions. | **Defer product.** A bounded learning experiment may compare random/uncertainty selection, without claiming commercial validation. |
| AI governance / pre-mortem / regulatory actions, P187 row 4; G003 row 5; G013 row 6 | VerifyWise documents AI governance workflows; CUBE maps regulatory change to action [S12–S13]. | Buyer expertise, trustworthy obligations, updates, sensitive evidence and procurement matter. A possible finance contact is insufficient; current AI use is limited. | **Access-first discovery only.** Observe an existing manual process before proposing AI governance software. |
| Club operations / equipment, G006 row 11; G018 row 15 | Spond covers events/attendance; Shelf covers equipment bookings and custody [S14–S15]. | No club operator currently available. Budgets, volunteer onboarding, migration and support can dominate engineering. | **Defer.** Requires an operator with an unresolved recurring workflow. |
| Visual equipment maintenance, G014 row 17 | Bluon offers equipment/manual/parts data and technical AI/API services [S16]. | Technicians, trustworthy manuals, local equipment coverage and error consequences are missing inputs. Public demos are not field reliability. | **Defer.** Need technician access and permitted equipment data before a prototype. |
| Small-business admin inbox, G022 row 10 | Paperless-ngx supplies an open document-management/OCR foundation [S17]; this does not prove deadline/action extraction is solved. | No representative customer documents, recurrence measurement or buyer. Generic OCR is weak differentiation; private data and incorrect reminders add burden. | **Defer.** Seek one concrete recurring document-to-action process; reuse storage/OCR. |
| Amateur sports analytics, G023 row 26 | Balltime already documents volleyball video analysis [S18]. | Missing permitted recordings/labels, coach access and a specific decision improved by analysis. Labelling and video costs can exceed MVP scope. | **Defer.** Establish an underserved sport/workflow and access first. |

Other marketplace, consumer, hardware, medical and broad automation ideas remain
unselected for this cycle: their supplied descriptions do not establish the
missing access or advantage. This is not a judgement that those businesses cannot
work. More speculative numerical scoring would not resolve those unknowns.

## The first test and what would justify more work

Use source-linked questions about real past decisions, including a superseded
decision and an inconclusive result. Compare normal files/search with existing
Foundry records; optional pinned Hindsight is an additional baseline only if it
can run within the approved local/no-paid-call boundary. Record correctness,
unsupported claims, task time and record-maintenance time. See the
[full protocol](../ventures/research-handoff.md).

A clear failure to beat the ordinary workflow means adopt the ordinary workflow.
A recurring, measurable gap may justify a small adapter on top of existing tools.
Before a larger commercial build, a proposed working gate is three independent
organizations demonstrating recent repeated pain, two agreeing to test on their
own permitted data, and at least one concrete budget/payment discussion. These
are decision heuristics, not statistically proven market thresholds. No such
evidence currently exists. Interview questions should ask for the last real
incident, current workaround, frequency, cost, data constraints, buyer and prior
attempts—not whether someone likes the idea. No outreach has been sent.

## Open source and a plausible business

Do not open-source a broad platform merely because incumbents are open. First
find a component people actually want to use. If the trial exposes a reusable
gap, the provisional model is an open local core (portable records, small
connectors, evidence checks) and paid operation for teams (managed deployment,
access administration, backups, integration maintenance or support). Start with
an assisted pilot if that is the cheapest way to understand the problem.

This follows a real pattern: Langfuse documents an open core plus commercial
offerings [S19], while Hindsight offers self-hosted and managed options [S7].
Their existence does not demonstrate that a new entrant can acquire customers
or profit. Support labour and model/hosting costs can consume revenue; teams may
prefer to self-host; incumbents can add connectors. Distribution, reliability
and workflow expertise would have to earn payment. No price, TAM or revenue
projection is justified yet. License choice, dependency compatibility and public
release remain separate future decisions; no license is changed now.

## Learning and Foundry findings

The old roadmap put design-partner work at Slice 024 after extensive platform
construction. Validation now comes first. Completed Python, SQL, Docker and
delivery work remains useful and retained. Future tracking/data/model/deployment
skills attach to a justified task or an honestly labelled practice lab, rather
than forcing a synthetic rejection model into a commercial product.

Foundry can record this real decision using its existing primitives; operation
and limitations are recorded separately. Successful persistence demonstrates
functionality, not superiority to Markdown or commercial value. No retrieval
benchmark, Hindsight runtime trial, customer interview or willingness-to-pay
test was performed during this documentary investigation.

## Source index (official sources consulted 2026-10-02)

- S1: [MLflow 3.2.0 release, 2025-08-05](https://mlflow.org/releases/3.2.0/) — native feedback tracking.
- S2: [MLflow review queues](https://www.mlflow.org/docs/latest/genai/assessments/review-queues/) — human review workflow.
- S3: [MLflow regression testing](https://mlflow.org/docs/latest/genai/eval-monitor/regression-testing/) — failures, tests, scorers and CI.
- S4: [LangSmith annotation queues](https://docs.langchain.com/langsmith/annotation-queues).
- S5: [Buildpad](https://buildpad.io/) — current vendor proposition; adoption claims not independently checked.
- S6: [DimeADozen](https://www.dimeadozen.ai/) — research/validation report offering.
- S7: [Hindsight documentation](https://hindsight.vectorize.io/) — current capabilities; **not proof of features in selected v0.10.2** or of local installation.
- S8: [W&B Reports](https://site.wandb.ai/reports/) — narrative collaboration around experiment results; earlier retrieved page, later repeat fetch errored.
- S9: [Simplify job tracker](https://help.simplify.jobs/en/articles/2140179-using-the-job-tracker).
- S10: [FiftyOne curation](https://voxel51.com/curation).
- S11: [Cleanlab data labelling](https://help.cleanlab.ai/studio/tutorials/cleanlab-studio-web/data_labeling/).
- S12: [VerifyWise documentation](https://docs.verifywise.ai/) — source-available BSL; do not conflate that with permissive open source.
- S13: [CUBE regulatory change management](https://www.cube.global/products/regplatform/regulatory-change-management).
- S14: [Spond attendance](https://www.spond.com/en-us/news-and-blog/attendance-tracking-on-spond/).
- S15: [Shelf equipment management](https://www.shelf.nu/solutions/equipment-management).
- S16: [Bluon developer documentation](https://docs.bluon.com/).
- S17: [Paperless-ngx documentation](https://docs.paperless-ngx.com/).
- S18: [Balltime volleyball AI](https://academy.balltime.com/getting-started/what-is-volleyball-ai).
- S19: [Langfuse open-source model](https://langfuse.com/handbook/chapters/open-source).

Web documentation changes. These references support bounded capability claims,
not product benchmarking, market prevalence or independent revenue evidence.
