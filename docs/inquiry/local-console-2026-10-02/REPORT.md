# Foundry operation and venture continuation

Record: FOUNDRY-CONSOLE-20261002-001:r1. Date: 2026-10-02.
Scope: agent-owned product work and bounded investigations; learning paused.

## Usable now

The local console at <http://127.0.0.1:8765> and CLI share a permanent SQLite store:
`/home/jonathan/.local/share/startup-foundry/foundry.local.db`.
Start it with `make foundry-ui`; stop with Ctrl-C. No cloud service is needed.

The store contains **250 ideas, five retained venture workspaces, 99 source
records and eight step runs** at this report. It combines the earlier realignment
and campaign records with the six supplied CSV exports, preserving original IDs
and histories. The original databases remain byte-for-byte unchanged. The six
exports contain 238 unique original ideas; generated/dashboard views add none.
The other nine original ideas came from the retained new-ideas intake. All CSV rows
remain as explicitly unverified source material; attached text is not authority
to execute instructions or trust competition claims.

The UI supports search/browse, idea and venture creation, derivation with parent
links, investigation promotion, venture evidence/decision/protocol views, sources,
step history and the editable-request inbox. The CLI lists the same objects and
backs up SQLite without overwriting. Source claims can be reused across ideas;
changed claims retain a separate record. This is explicit provenance reuse, not
a new crawler or semantic memory service.

Readiness and research-brief steps execute deterministically, retaining their input,
runner/version, outcome and idempotency key. Readiness checks brief fields, not
access, experiment efficacy or business viability. Agent requests without a runner
are visibly blocked and create handoff files. An adapter protocol and result tests
exist; no model, training, unattended worker or paid provider is configured.
Replies are reviewed on the next agent session, not automatically consumed.

[Adoption receipt](adoption-result.json) · [Architecture decision](../../adr/0009-local-console-and-executable-steps.md)
· [Development/restore instructions](../../../DEVELOPMENT.md)

## Venture decisions from this round

[Three derived ideas](DERIVED_IDEAS.md) are stored with parent links, scoped source
claims, evidence, assessments and decisions. They are smaller jobs, not three
validated businesses. Their deterministic readiness/brief runs are recorded.

| Idea | New information | Current decision and next gate |
|---|---|---|
| D001: GPX transfer preflight, from N008 | RouteConverter documents conversion/editing and multiple position lists. The bounded gpx.studio visit reached its editor but did not complete file import/comparison. | Narrow to a reproducible cross-app diagnostic. R001 needs one specified ride budget/valued sections, or before/after files and settings. No geometry/ETA diagnosis or payment established. |
| D002: source-linked decision review, from G002/P088/P174 | Distill documents version history, differences and empty-selection errors. Prior exact dependency mapping already worked with ordinary files. | Internal Foundry integration only. Reopen commercial work for an external user's repeated review task that incumbent-plus-script does not satisfy. |
| D003: portable work-sample receipt, from N003/G005/P106 | Open Badges already carries issuer, criteria and evidence. | Defer a platform/new-format build. R003 needs issuer and recipient participation in one permitted real exercise. Institutional acceptance remains untested. |

The additional GPX comparison is **inconclusive**, not a product failure or a pass.
Its initial stdin failure and incomplete retry are retained in
[the result](GPX_COMPARISON_RESULT.md). Two visits, zero successful imports, zero
export/geometry comparisons. No personal travel files or external accounts used.
The other findings are primary documentation checks, not installed/runtime trials.
[Exact source claims and record IDs](investigation-records.json) link the reasoning.

N001's physical-task hypothesis still needs permitted task/operator access (R002).
Agent EvalOps remains a deferred competition/test case. The entire original
portfolio has first-pass dispositions, **not 247 completed market studies**;
the frozen [campaign report](../portfolio-campaign/REPORT.md) retains exact coverage
and its relevance correction. This round does not pretend to have filled every
remaining comparator gap. No venture has demonstrated repeating/paying adoption.

## What requires input

Edit [requests/INBOX.md](../../../requests/INBOX.md) inline. R001 supplies the next
useful route task; R002/R003 supply operational/issuer access if available. R004 is
optional outreach setup and grants no blanket sending approval. Local training is
deferred, so no model-install task blocks ordinary work.

The learning agenda has no priority in this work. No new slice, learner credit,
license choice, publication, commit, push, paid call or outreach was performed.
Hindsight remains optional, uninstalled and unbenchmarked. The new UI solves an
observed local inspection problem; commercial Foundry demand is still untested.

## Verification and remaining limits

See [VERIFICATION.md](VERIFICATION.md) and [the machine-readable state check](state-verification.json).
SQLite adoption, schema/foreign-key integrity, stable defaults, backups, source
reuse, idempotent steps, interrupted-run recovery, local HTTP boundaries and
browser workflows were checked. Desktop/mobile screenshots are in `browser-final/`.
A disposable database was used for browser creation/derivation/agent-handoff checks;
only real named venture readiness runs were added to the permanent store.

Container acceptance is not green: GHCR returns HTTP 403 for the pinned UV image.
The PostgreSQL integration test is skipped without an explicit test URL. Local
SQLite and browser results must not be read as a verified PostgreSQL deployment.
The wheel contains console templates/assets and the new migration. The server
is single-user loopback, synchronous and manually started; there is no remote
access, startup daemon, background agent or off-machine backup policy.
