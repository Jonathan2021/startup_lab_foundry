# Verification of local operation

Date: 2026-10-02. Agent product work; no learner credit. Effective code is
identified in `verification-manifest.json`, not by HEAD alone. Trees were already
dirty and no commit/push was made. Earlier campaign hashes remain historical.

| Check | Result |
|---|---|
| Final unit/integration/CLI/package/CI/delivery/repository regression | 53 passed, one PostgreSQL test skipped without an explicit URL; one Starlette TestClient deprecation warning |
| Ruff: product source, tests, parent tests and two new support scripts | Passed |
| mypy: product source | Passed, 15 files |
| Pinned actionlint | Passed |
| Container acceptance | Two passed, two failed: GHCR token endpoint returns 403 for pinned `astral-sh/uv`; no full deployment pass |
| Wheel package | 15 templates, two static assets, new Alembic migration packaged; installed-wheel CLI migration and HTTP/static-page smoke passed from `/tmp` (see `installed-wheel-smoke.json`) |
| Persistent state | 250 ideas, five ventures, 99 sources, eight runs; integrity and foreign keys pass |
| Import/reconciliation | All six CSVs retained exactly; earlier source DB hashes unchanged; their record IDs still present |
| Backup | Final non-overwriting online backup checked; canonical/source stores preserved |
| Browser | Main console desktop/mobile browsing and named rider readiness; disposable creation, derivation, promotion and blocked-agent handoff passed |

Reproduce the final regression from the root:

```bash
.venv/bin/pytest -q tests/repository foundry/tests/unit foundry/tests/integration foundry/tests/acceptance/test_cli_workspace.py foundry/tests/contract
.venv/bin/ruff check foundry/src foundry/tests tests foundry/scripts/adopt_local_workspace.py foundry/scripts/record_console_investigations.py
.venv/bin/mypy foundry/src
make workflow-lint
```

Meaningful new checks cover atomic invalid lineage/import handling, changed-import
conflicts, claim reuse without overwriting revisions, cross-venture isolation,
idempotent step submission, adapter failure redaction, review-required successful
adapter results, interruption recovery without replacing terminal outcomes,
backup preservation, cwd-independent defaults and protected/escaped local HTTP.
The initial tests failed before implementation. A later command referenced a
nonexistent `test_config.py`, ran zero tests and is retained as a harness error;
the final complete suite above supersedes that invalid invocation.

`browser-r1/` retains an automation failure: the installed pyppeteer-ng
waitForFunction wrapper returned an unawaited coroutine. The application's first
readiness run had completed. `browser-r2/` uses a bounded URL check and passed.
`browser-final/` contains successful form and restart checks; its temporary database
and inbox were separate from real portfolio data. Their server and browser were
stopped. The main server is manually started at loopback port 8765.

`verify_state.py` is read-only and writes `state-verification.json`. It verifies
original hashes, retained IDs, raw CSV row equality, schema revision, SQLite
integrity/foreign keys, derived parents and matching backup counts. Its exact
counts describe this snapshot; later legitimate user changes need a new record.
It is not a production constraint that the portfolio always contain 250 ideas.

The first adopted backup and the final backup both live under
`~/.local/share/startup-foundry/backups/`. Keep them off-machine separately if
needed; this work configured no replication. No Hindsight runtime, local-model
training, paid LLM call, remote hosting or outgoing communication was tested.
