# Three venture release readiness review

Frozen 2026-10-08 before fresh test/launch runs. Scope: Ride Options, Volley Match,
and Coopain after their prior handoffs. Verify local acceptance, actual commit and
remote/CI provenance, reproducible startup, code/usage documentation, privacy and
recovery instructions. Produce targeted agent handoffs for unresolved gates.

Hypothesis: latest accepted Foundry results establish bounded local MVP progress
but do not establish committed, remotely tested and portable releases. Check each
claim against files, current tests and GitHub read-only API state. Preserve the
current dirty repositories, application data, checkpoints and historical evidence.
No implementation takeover, commit, push, repository creation or remote CI dispatch
is authorized by this audit. New handoffs may specify those exact actions for the
user to authorize by a subsequent prompt.

Use disposable synthetic data for fresh core checks; use independent source copies
for README/startup checks, without .local state or Foundry installed. Run existing
browser checks where practical and retain exact logs. Distinguish environmental
failures, technical defects, documentation contradictions, absent CI and missing
real-use evidence. Do not demand deployment or user trials to pass a local preview.

Local baselines: Ride Options and Volley Match have no HEAD and no remote.
Coopain HEAD aa382779b79951f843f37b8080f6f0972efe7e3c is dirty;
GitHub main 4f6899287dea2c10236d6293d77d6240587b6703 has the October 6 cleanup merge.
Foundry retains its previous local contract update 2026-10-07.2, uncommitted.

Targeted CI runner check: backend/run_tests.sh lacks failure propagation. Hypothesis: a failing pytest command can be masked by a succeeding coverage report check. Reproduce with a copied runner, a fake pytest returning 7, and a synthetic 100% coverage JSON; no product tests or source will be modified. Expected correct exit is nonzero.
