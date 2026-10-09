# MVP verification and Foundry upgrade

Review date: 2026-10-07. The four reported finished products meet their bounded
local technical MVP gates in the checks rerun here. No blocking defect was
reproduced. Coopain is unfinished at J03 despite green current backend tests;
Ride Options was still implementing R05 during review. None has demonstrated
real adoption or received external deployment approval through this review.

## Independent verification

The coordinator read original decisions/roadmaps, implementation/release evidence,
core calculation/aggregation/rating/planning code, auth/privacy/recovery acceptance
coverage and actual Foundry records. Existing tests were rerun against disposable
synthetic stores. Chromium tests performed real interactions. Representative fresh
mobile screenshots were visually inspected and retained in [screenshots](screenshots/).
This is scoped acceptance review, not an exhaustive security audit or a real-user study.

| Repository | Fresh checks and verdict | Next bounded work |
| --- | --- | --- |
| OfferCheck | Ruff/types and 52 backend tests; 3 Chromium tests. Local MVP passes. Manual field/source capture, EUR fixed-pack comparisons and human source review remain its scope. | [O06 handoff](../../../../offer-check/docs/mvp/NEXT_HANDOFF.md): audit capture/receipt usability and rehearse a fair quote-comparison study. |
| Volley Match | Ruff/strict types and 41 tests; Chromium at 1280/390px, three confirmed matches, historical correction and restart pass. Local MVP passes. | [V06 handoff](../../../../volley-match/docs/mvp/NEXT_HANDOFF.md): organizer rehearsal and two private-session trial preparation. |
| Crous Queue | Lint/format/types and 17 backend tests; 6 browser tests including offline/retry/expiry/moderation pass. Local MVP passes; national directory coverage is not live wait coverage. | [Q06 handoff](../../../../crous-queue/docs/mvp/NEXT_HANDOFF.md): rehearse five-lunch coverage measurements and verify queue categories through existing R011 when available. |
| Volley Coach | Ruff/strict types and 31 backend tests; 2 browser flows pass. Local scheduling MVP passes in user-provided-program mode. | [C06 handoff](../../../../volley-coach/docs/mvp/NEXT_HANDOFF.md): scheduling usability and two-week own-program trial preparation. |
| Coopain | Current working tree: 171 backend tests pass with 3 warnings. J01/J02 accepted, J03 unfinished. Frontend/browser and fresh lock-based setup were not independently rerun by this coordinator. | [Recovery handoff](../../../../coopain/docs/mvp/NEXT_HANDOFF.md): preserve J03 work, verify/accept it, then complete J04/J05 in order. |
| Ride Options | Read-only point-in-time inspection and retained evidence; active app tests not rerun. R01–R04 accepted, R05 in progress. R04 had ten frozen queries, six feasible, 58 regional warnings and no manual comparator/rider judgments. | [Continuation handoff](../../../../ride-options/docs/mvp/NEXT_HANDOFF.md): finish R05, distinguish preview from road-use acceptance, then audit warning effects and prepare measured comparisons. |

Exact fresh output: `offer-check-check.txt`, `volley-match-check.txt`,
`crous-queue-check.txt`, `volley-coach-check.txt` and each corresponding
`*-browser-or-full.txt`. Coopain diagnostic command used the existing
`/tmp/coopain-j03-security-venv/bin/python` with `PYTHONPATH=backend`, pytest on
`backend/tests`, `-q -o addopts=''`; this environment is not a portable install
certificate. The earlier retained J03 run had 170 tests; both observations remain.
OfferCheck/Coach retain an upstream TestClient deprecation warning. No test skip
or xfail was used to declare these four local app gates passed.

The four agents retained separate independent-install/recovery evidence. This
review inspected those records and reran relevant integration/recovery tests, but
did not repeat every venture's package-install or PostgreSQL matrix. Only Foundry's
new wheel was independently installed again. Later source changes require their
own appropriate checks.

## Foundry use was real and traceable

All six repositories used the permanent configured store, actual claims and saved
contexts, immutable submitted results, exact-digest previews/resolutions, and
source-attributed checkpoint evidence. The latest accepted result for every
venture has complete context and reviewed coverage. The four finished apps each
have all five implementation packages accepted. No Foundry runtime imports were
found in the four new application source trees or Ride Options; Coopain uses its
repository helper for coordination and retains its independent application stack.

| Repository | Accepted implementation packages at snapshot | Feedback reports with delivery receipts |
| --- | --- | --- |
| OfferCheck | O01–O05 | 4/4 |
| Volley Match | V01–V05 | 5/5 |
| Crous Queue | Q01–Q05 | 2/2 |
| Volley Coach | C01–C05 | 5/5 |
| Coopain | J01–J02; J03 still owned | 2/2 |
| Ride Options | R01–R04; R05 still owned | 2/2 |

The 20 child-venture reports plus two earlier Foundry reports were fetched from
Foundry through the public CLI and individually classified in
[FEEDBACK_TRIAGE.md](FEEDBACK_TRIAGE.md). Positives were retained without inventing
features. A receipt means intake, not a fix. Ride Options correctly submitted an
accepted R02 result superseding an earlier stale proposal; the stale record is
retained as history and does not invalidate the accepted replacement.

Coopain's host error was not reproduced or diagnosed here. Its directory,
instructions and Foundry state were readable. This upgrade adds recovery for its
existing owned Foundry work; it does not claim to fix the agent host's workspace
loader. Ride Options' active claim/map were not taken over or revised by the
coordinator. Its new file is for the next checkpoint. Only coordination helper and
manifest files were upgraded there.

## Local Foundry upgrade

Delivered agent contract and bridge revision **2026-10-07.2**, described in
[ADR-0017](../../adr/0017-dogfood-contract-and-recovery-update.md) and
[EXTERNAL_AGENTS.md](../../EXTERNAL_AGENTS.md). Package version remains 0.0.1;
this is a tested local source/contract update, not a published package release.

- Static guide/schema discovery no longer reads configuration, initializes a
  database or runs migrations. Stateful missing-store checks remain.
- MapEdge JSON Schema exposes the conditional condition/outcome requirement and
  an example. The runtime guard remains strict.
- Prepared context reports selected/total map counts and the exact full-revision
  retrieval command; evidence completeness stays a separate concept.
- `start --resume-owned` prepares new context only for the exact existing owner
  of in-progress work. It neither claims again nor releases ownership on failure.
- `doctor` reports bridge/contract revision, manifest hash match and configuration;
  `resume` remains the live workspace check. Bounded timeouts have actionable
  recovery guidance; mutations never retry automatically.
- Guidance emphasizes final resolution receipts for created IDs. Stable preview
  ID allocation was deferred; preview is intentionally provisional.

Canonical bridge SHA-256:
`1e0be09cd1b537864e0b04bbc2358932b1efba7c7a5d4abb4c0b9aff0e91703f`.
All seven repositories passed doctor with this hash and the upgraded public
contract; see [bridge-rollout.json](bridge-rollout.json). No venture runtime
package was changed by this coordinator. No database migration was introduced.

Six new checks were intentionally red before implementation. Focused regressions
then passed 22/22. `make test-product` passed **152 tests**, with one PostgreSQL
integration test skipped because an explicit test database URL was absent and one
upstream TestClient warning. Ruff and strict mypy passed. Final public-contract/
console checks passed 6/6. The installed wheel outside the checkout passed the
full public handoff, exact acceptance retry, fresh-process resume and feedback
retry; a synthetic backup restored to a new path retained identical work, results,
map and review state. See `foundry-red.txt`, `foundry-green-focused.txt`,
`foundry-product.txt`, `foundry-lint.txt`, `foundry-types-final.txt`,
`foundry-final-contract.txt`, `foundry-wheel-replay.json` and
`foundry-wheel-recovery.json`. Container/cloud/CI deployment was not rerun or
performed for these local CLI/schema changes.

The original two 60-second timeout incidents were not reproduced. Three current
schema calls and three arrivals calls returned in 0.93–1.03 seconds; see
`cli-timing-after.json`. This is an observed post-change bound for those calls,
not proof of the historical cause or a measured before/after speedup.

## Ready handoffs and next decisions

Four ready agent-owned tasks now exist, with no claim taken by this coordinator:

| Repository | Ready work ID |
| --- | --- |
| OfferCheck | `5f244a1b-2f36-4eda-8ada-740446b66114` |
| Volley Match | `f0c29b5f-c9cf-4956-91da-f6431db8156b` |
| Crous Queue | `781199db-adde-4600-9a4d-4c56eed14fdc` |
| Volley Coach | `9fb8b808-9737-4083-8587-99d7e9808fbf` |

They authorize a current acceptance review, repairs justified by observed defects,
and concrete local pilot preparation. Each handoff defines required artifacts,
measurements and a stop/continue decision. Real participant recruitment/data,
sends, hosted access and consequential actions still need their exact permission.
Missing input goes into existing Foundry request records/files, preserving replies.

Coopain keeps `84e423d8-0e34-48ab-8650-4c6a0a243024` owned by
`implementer-coopain-20261007-codex-1636`. Ride Options keeps
`623bf7bb-6a0f-48d2-bc5e-74fb1be38d99` owned by
`implementer-ride-options-20261007-session-a`. Their prompts refresh current state
before acting, because the active agent may advance after this snapshot.

The real next decisions are evidence of usefulness: permitted quote comparisons,
two voluntary friends sessions, five lunch days, two weeks of existing-program
scheduling, one candidate/referrer/job flow after rights/privacy/policy review,
and route-planning comparisons with actual rider judgments. Technical completion
is not a reason to automatically add OCR, public matchmaking, predicted waits,
video coaching, payments, or social route features.

## Provenance and coordination

Protocol was frozen before checks in [PROTOCOL.md](PROTOCOL.md). Baseline commit,
status and source hashes are retained in the adjacent `*-status-before.txt` and
`*-sources-before.json` records. Compact resume snapshots retain exact result,
work, map and review IDs; full local contexts remain in ignored `.foundry/runs/`.
No credentials, production databases or real participant records are fixtures.

Foundry F01, F02 and F03 are accepted through exact-context review; `F01-r2-receipt.json`,
`F02-receipt.json` and `F03-receipt.json` retain final effects. The first F01 proposal
was refused for incomplete evidence coverage, then superseded using a fresh 40KB
context containing every fetched arrival. The refusal is preserved as a useful
coverage guard, not counted as a passed attempt. F04 records final release/handoff
verification in its final receipt. No commit, push, paid call, send, cloud resource,
external publication, Hindsight installation or learning slice was performed.
