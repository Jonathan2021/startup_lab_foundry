# MVP review and Foundry feedback upgrade protocol

Frozen before verification on 2026-10-07. Coordinator actor:
`coordinator-mvp-review-20261007`; Foundry F01 claim/context:
`b532f566-3bae-54b9-8463-e4e311d0083e`.

Hypotheses: the four reported finished ventures meet their bounded local MVP
contracts; all six ventures used persistent Foundry claims/results and feedback;
small public-contract improvements can resolve observed friction without changing
venture runtime dependencies or taking over active claims.

Review each roadmap, accepted checkpoint, actual implementation and test coverage.
Run fresh local lint/types/tests for the four finished apps against disposable
synthetic data, then their existing browser replay where available. Preserve exact
commands, exit codes, output and source hashes. For Coopain inspect J03 interrupted
state and verify the existing safe baseline; for active Ride Options inspect an
explicit point-in-time snapshot and retained evidence without modifying its app or
claim. Distinguish technical build acceptance, real use, and release permission.

Triage every local feedback report and receipt against Foundry records. Reproduce
accepted defects with failing tests before changing the CLI/bridge. Target schema
clarity, context/full-map distinction, timeout diagnostics and safe resume recovery
only if supported by inspected evidence. Keep validation and stale/claim guards.
Use existing schemas and the permanent store; no replacement database.

Pass: traceable verdict per venture, actionable verification/remediation plus next
package handoff in each repository, tested Foundry changes available through every
configured bridge, and durable Foundry results/feedback triage. A missing user
trial remains an explicit gate, not a synthetic pass. No commits, pushes, paid
calls, cloud provisioning, sends, public deployment or learner work.

Baseline: parent HEAD e6a83e470d052439e5c8d4a943428f5bbd132f7f;
Foundry HEAD e0b477d903b6b22af9d72bb35306e9a0a25deae8. Both dirty before review.
Other venture baselines and file hashes are recorded alongside verification logs.
