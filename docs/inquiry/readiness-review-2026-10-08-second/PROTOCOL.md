# Second three-venture readiness audit

Frozen before fresh runs on 2026-10-08. Audit Volley Coach, Crous Queue and OfferCheck after accepted C06/Q06/O06. Hypothesis: local accepted MVPs can still lack committed, remotely tested and reproducible releases. Verify current Foundry records, Git/GitHub provenance, documentation, fresh setup/demo/migration, core/browser checks and an independent packaged runtime. Retain failures and distinguish harness/environment defects from application defects.

Use only disposable synthetic stores/source copies, retained directory data and localhost servers. No implementation changes, commits, pushes, GitHub repo creation/CI dispatch, real users, quote intake, queue submissions, physical coaching or deployment. Write concrete agent handoffs and copyable prompts for unresolved gates. External Git delivery requires the explicit future prompt. Existing human gates and claims remain intact.

Evidence includes exact commands/exit statuses, source hashes, runtime versions and package contents. A wheel alone is judged against its documented distribution contract; a source bundle may be required. Any advertised setup path must specify that distinction. No Foundry runtime import is allowed.

Targeted OfferCheck follow-up: fresh lint reports four I001 errors while the original workspace has an empty untracked alembic/versions directory absent from Git candidates. Hypothesis: Ruff filesystem inference treats that name as first-party locally, hiding clean-checkout import-order failures. Create only the same empty directories in the disposable copy, rerun lint, remove them and rerun; source stays unchanged.

The first empty-directory toggle produced cached green results after removal. Repeat the causal comparison with Ruff --no-cache in both states; do not interpret cache reuse as a fresh pass.
