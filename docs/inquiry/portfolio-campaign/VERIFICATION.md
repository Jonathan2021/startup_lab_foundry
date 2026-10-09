# Verification — campaign revision 3

Date: 2026-10-02. Effective working trees were already dirty. No commit or push.
This record distinguishes green checks from environmental and investigation limits.

## Product/support checks

| Check | Result |
|---|---|
| Pinned actionlint | Passed |
| Ruff over Foundry source/tests and repository tests | Passed |
| mypy over Foundry source | Passed, ten source files |
| Repository boundary check | 1 passed |
| Foundry fast unit/integration/CLI/package checks | 29 passed, 1 skipped; PostgreSQL integration needs its explicit test URL |
| New experiment-protocol reconstruction/isolation | Failed before change; passed after change; included in fast checks |
| CI/delivery workflow contracts, run separately after Docker failure | 12 passed |
| Discovery support target, run separately | CLI 9 passed; protocol reconstruction 1 passed; overlapping coverage, not 10 additional unique tests |
| Container acceptance | 2 passed, 2 failed fetching the pinned uv image: GHCR token endpoint HTTP 403 |
| Campaign integrity and both supported CLI snapshots | Passed; result linked below |
| Modified trial-script compilation and replay guards | Passed; result linked below |
| Offline T3/T6 replay against frozen inputs | Passed, new local outputs; original result files unchanged |
| Git diff whitespace checks | Passed for staged and unstaged diffs in root, Foundry, EvalOps and learning |

`make check` is **not fully green**. Container runtime behavior requiring the image
pull was not revalidated. The image pin was preserved; no bypass or new registry
credential was introduced. Local checks do not prove PostgreSQL or container parity.
See [full check log](trials/logs/campaign-product-check.log),
[remaining checks](trials/logs/campaign-remaining-checks.log),
[red test](trials/logs/campaign-foundry-red.log), and
[green test](trials/logs/campaign-foundry-green.log).

## Evidence integrity

[Read-only verification script](trials/verify_campaign.py) checks unique coverage
of P001–P212, G001–G025, U001 and N001–N009; source reference integrity; original
attachment hashes; 17 persisted artifact hashes; campaign input/code provenance;
frozen T6 inputs; and both current CLI views against portable snapshots. It also
checks the key negative/access-limited outcomes and local document links.
Results: [integrity](trials/integrity-result.json),
[replay/compilation checks](trials/replay-verification.json).

The campaign snapshot has 249 assumptions, 253 evidence records, 249 assessments,
249 decisions, 253 work items, two experiment protocols and 12 artifact references.
The separate route venture has three assumptions/assessments, four evidence
records, one decision/work item and five artifacts. Their records are isolated.
The two campaign experiment lifecycle values remain `planned`; result evidence
and completed work do not silently rewrite that separate state.

Both original attachments match intake hashes. The four protected source
project/reference documents match their existing committed versions. The earlier
G002 frozen protocol matches its previous manifest. Original `foundry.db` and
prior inquiry databases were preserved. Campaign dependencies, databases and
browser profiles are ignored, and no campaign browser/service remains running.

The [final manifest](verification-manifest.json) records evidence, script,
screenshot and effective code/guidance hashes. It excludes itself and generated
Python caches. This is a dirty-tree provenance record, not a clean commit snapshot.
Future document corrections require a revision and a fresh manifest; the frozen
trial outcomes must remain available.

## Checkout context and limits

- Startup Lab: `e6a83e470d052439e5c8d4a943428f5bbd132f7f`
- Foundry: `3b082507062838df4009d4b636c4f320436f3b41`
- Learning: `5ed2b8a8c0aa34fdbff4253150cb54b66be1484e`
- Agent EvalOps: `662d033dc1202359e8bcd0bf0de7120da2bd8854`

Foundry's deterministic read change was agent support, not learner certification
work. No next slice was prepared. Hindsight was neither installed nor benchmarked.
Public vendor claims, selected reports and synthetic tests do not establish market
size, willingness to pay, operational accuracy or commercial-build qualification.
