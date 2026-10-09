# Conversation-derived MVP and outside-agent readiness

2026-10-07. **OfferCheck is ready for implementation handover.** The application
has not been built. Foundry supports trusted local shell-capable agents through
its public CLI; it is not yet a remote service or an MCP server.

## Source and selection

The user supplied `/home/jonathan/Downloads/Generate Startup Ideas.md` after the
earlier missing-source checkpoint. Its seven B2A/B2S proposals and economic
arguments are source material, not active instructions or evidence of buyers.
[source.json](source.json) retains the file hash; the original stays local.
The complete attachment was read. It is unrelated to the previously guessed
N001 physical-task conversation; that separate hold remains unchanged.

The useful thesis is that checking a bounded commercial result can be cheaper and
more reliable than asking an agent to reconstruct the rules, terms and prior
decision each time. Agent activity alone does not create paying demand. We chose
a workflow useful to a human or their existing agent, without a proprietary agent
or marketplace being a prerequisite.

| Source direction | Current assessment | Decision for this handoff |
| --- | --- | --- |
| Vertical transaction infrastructure | Potential recurring value, but a broad RFQ-to-purchase service immediately needs supplier access and operational responsibility. | Retain a narrow pre-purchase check; defer transaction execution. |
| Reliable commercial facts | Sources, missing terms and revisions are tractable; live availability and fulfilment cannot be inferred from a quote. | Combine with bounded outcome checking as OfferCheck. |
| Shared commitments/budget ledger | [LiteLLM](https://docs.litellm.ai/docs/proxy/users) documents pre-call budget reservations; [Cycles](https://github.com/runcycles/cycles-protocol) documents reserve/commit/release/extend. These are not a universal inventory or payment hold. | Do not build a generic ledger without a concrete uncovered resource/race. No runtime comparison was performed. |
| Verified-outcome clearing | Broad arbitration and guarantees are difficult. Structured-data acceptance has mature [Pandera](https://pandera.readthedocs.io/en/stable/), [Great Expectations](https://docs.greatexpectations.io/docs/reference/learn/data_quality_use_cases/integrity/) and [Soda](https://docs.soda.io/reference/contract-language-reference) primitives. | Reuse validation; narrow the outcome to an explainable quote comparison. No escrow, generic agent evaluator or correctness guarantee. |
| Conditional coordinated purchasing | A local ledger cannot reserve real stock or enforce suppliers' cancellation terms. | Defer until real agreements and a repeated coordination case exist. |
| Pooled purchasing | Requires a buyer channel, committed demand and fulfilment economics; synthetic demand cannot establish them. | Defer; no purchasing cooperative or marketplace cold start. |
| Physical execution network | Requires operators, local density and operational verification, none supplied here. | Defer; no fabricated access or field results. |

A second concrete interpretation—checking product-catalog imports—was weaker as
a generic wedge: [Matrixify already documents dry runs](https://matrixify.app/documentation/matrixify-import-export-job-options/),
and [Shopify's CSV behavior](https://help.shopify.com/en/manual/products/import-export/using-csv)
is platform-specific. We did not test those products or infer that undocumented
capabilities were absent. The selection is a bounded build judgment, not a market
ranking with invented precision.

## OfferCheck

**Job:** given an exact-SKU purchase request and several supplier quotes, expose
which offers can be compared, their actual quoted totals, missing terms, source
references and changes since the last review. Keep a readable, versioned decision
receipt. Initial profile: domestic EUR, fixed packs, exact items, no substitutions.

Example: twelve cables at €4 each plus €12 shipping total €60 before tax. A second
quote sells ten-packs for €35 including shipping: two packs cost €70 and leave eight
spares. The cheaper per-unit equivalent is not the cheaper request total. Missing
shipping stays unknown. Source correspondence is distinct from stock or delivery
truth, and a shortlist is never a purchase order.

[QuoteWerks VendorRFQ](https://quotewerks.com/features/vendor-rfq-software/) and
[Fairmarkit's bid comparison](https://help.fairmarkit.com/product-guides/compare-bids)
already cover supplier comparison; [Fairmarkit has an RFQ API](https://developers.fairmarkit.com/reference/rfq).
Neither comparison nor agent access is novel. Our unvalidated hypothesis is an
independent local checker for small teams that use documents and their own agent,
without migrating their procurement process. Adoption may fail because these
incumbents, a spreadsheet or a well-configured agent are sufficient.

GO means build a bounded private MVP with synthetic data. It does not mean fund
a procurement company or claim a defensible market. A real comparison study must
measure setup, extraction/review, correction time, material misses and repeat use
against a competent baseline using the same permitted inputs. If there is no
advantage after that total effort, keep a template/adapter or stop. Customer
documents and field participation are not prerequisites for local implementation.

## Evidence and limits

The [protocol](PROTOCOL.md) preceded probes. OfferCheck's frozen synthetic fixtures
exercise 13 exact outcomes: pack rounding, missing shipping, currency/tax mismatch,
expiry boundary, late/unknown delivery, wrong SKU, offered quantity, unsupported
pricing, unreviewed source extraction and malformed negative price.
[All passed](quote-probe.json), alongside 1,000 seeded pack-boundary checks and five
canonical-input digest checks. Twelve inputs passed typed shape validation; only
two were comparable under the declared business rules. This isolates the value of
domain rules, not superiority over a configured validator or procurement product.

The probe is intentionally smaller than the planned application. It does not test
real extraction, multi-line duplication, transaction races, persistence, UI, tenant
isolation, supplier truth or demand. Those are explicit O01–O05 acceptance items.
Its source-review boolean is a fixture shortcut; production review must bind an
authorized actor, field locator and exact artifact hash. Do not port the probe
as the application's security or persistence design.

## Implementation pack and live state

Independent repository: `/home/jonathan/startup_lab/offer-check`, initialized on
`main`, no application implementation, commit or remote. Entry points:

- [Decision and boundaries](../../../../offer-check/docs/mvp/DECISION.md).
- [Dependent roadmap](../../../../offer-check/docs/mvp/ROADMAP.md) and
  [data/API/UI contract](../../../../offer-check/docs/mvp/ARCHITECTURE.md).
- [Agent handoff](../../../../offer-check/docs/mvp/AGENT_HANDOFF.md) and
  [first task](../../../../offer-check/docs/mvp/FIRST_TASK.md).
- Machine-readable `spec.json`, behavioral acceptance cases, synthetic fixtures,
  executable probe, ADR, sources, configured helper and feedback outbox.

| Package | Depends on | Exit checkpoint |
| --- | --- | --- |
| O01: capture | — | Authenticated workspace isolation, immutable request/offer revisions, bounded attachments, retries and restart. |
| O02: checks | O01 | Explainable matching, packs, quote-level charges counted once, unknowns and eligibility. |
| O03: review | O02 | Source correspondence, stale/conflicting review refusal, history and decision receipts. |
| O04: interaction | O03 | Desktop/mobile comparison flow and an HTTP-only agent replay with scoped tokens. |
| O05: release | O04 | Independent install, backup/restore, retention/export/deletion and a reproducible local demo. |

The map branches after the local MVP: demonstrated repeated use with an unmet need
can justify one integration; no advantage leads to narrowing or stopping. No
automatic extraction, supplier sourcing, email sending, negotiation, order, payment,
currency conversion or guarantee is part of this MVP. Each accepted package queues
only its dependency-satisfied successor and reports Foundry friction.

Permanent Foundry identifiers are retained in [live-receipt.json](live-receipt.json):

- Idea `conversation-offer-check-20261007`; venture `v-offer-check`.
- Workspace `546ed36a-a8be-4639-b88c-1b3bcf96c7d8`.
- Accepted investigation result `f758721d-8d12-5b5a-9a36-6e65314be1f4`.
- Ready O01 work `8647e0b4-7e98-4e56-a095-7703e1730b13`.
- R012 resolved from the actual attachment/request, attributed as user material
  transcribed by Codex. No numerical market score was invented.

The [public-CLI operator procedure](record_handoff.py) was rehearsed on a verified
backup before live writes. The first rehearsal stopped on the automatic initial
review task; the corrected procedure explicitly cancels that redundant task with
rationale and retains history. A second rehearsal passed before live application.
Source recovery does not authorize supplier contact or public deployment.

## Foundry readiness and fixes

An outside agent needs a task brief and configuration, but not Codex state, a
Codex-specific API or Foundry Python knowledge. The
[public contract](../../EXTERNAL_AGENTS.md) and each repository's handoff describe
discovery, claims, sufficient context, stale result recovery, preview/review,
fresh-process continuation and feedback.

Actual fixes from this audit:

1. A nonexistent configured SQLite path created an empty DB before failing.
   The new helper rejects it before invoking Foundry and passes the exact checked
   expanded path. The missing-store regression was red before the fix.
2. Handoffs referred to internal ContextInput code despite its existing public
   schema. Corrected all seven prepared repositories; published claim/release
   schemas too. Context publication itself was already implemented.
3. Added `python3 tools/foundry_agent.py cli …`, which forwards the configured
   executable/store so agents can use the public commands directly.
4. Added a stdlib-only client replay and acceptance coverage. The full cycle also
   passed against an installed wheel in an isolated environment outside the
   checkout. [Recorded replay](public-wheel-replay.json). This is contract testing,
   not an independent LLM comprehension test.

The OfferCheck outbox recorded onboarding feedback in Foundry as evidence
`b0336bb0-8104-4dcf-87a3-039d89a7fe1e`, with the findings and remaining usability
question. This is dogfooding the integration; it does not count as a completed
implementation package or satisfy Foundry F01's repeated real-agent test.

## MCP decision

| Agent environment | Ready now? | Integration |
| --- | --- | --- |
| Trusted agent with shell on this machine | Yes, after repository/configuration setup | Public CLI plus helper; no internal imports. |
| Another trusted machine | Not automatically | Install Foundry and deliberately configure the appropriate store/paths. Do not copy a live SQLite file as multi-writer synchronization. |
| Local host that only exposes MCP tools | No direct support | Add a narrow stdio MCP adapter when that host is selected. |
| Remote or untrusted agent | No | Requires authenticated identities, workspace authorization, revocation and a reviewed deployment. |

Recommendation: preserve the CLI and postpone MCP until a named client needs
host-native discovery or cannot run shell commands. MCP's
[architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)
provides standard tool/resource discovery; its
[authorization specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
does not replace our domain authorization. A thin adapter should call the same
services and expose specific operations, not an unrestricted shell command.
[ADR-0016](../../adr/0016-public-agent-contract-before-additional-transports.md)
defines the actual-host checkpoint and remote prerequisites. No MCP server was
implemented or independent model-use success claimed.

## Verification and delivery

The product/CLI/package/workflow selection passed **158 tests**, with the explicit
PostgreSQL-only test skipped locally. A further path-normalization regression was
added and the final four agent-kit tests rerun. Ruff and strict mypy cover the
product and both agent-kit scripts. Wheel/public replay and all seven prepared
manifests are checked separately. See `verification.json` for final evidence,
including store integrity and file hashes; remote CI is reported at delivery.

Only Foundry is committed/pushed under the standing instruction. The new venture
and updated sibling handoffs stay in their independent local repositories. No
paid model, cloud resource, external message, supplier request or new public
venture repository was created.
