# Foundry 0.1.0 — local MVP delivery

Agent contract and repository helper: **2026-10-09.1**. Distribution version:
**0.1.0**. Intended use: one trusted local operator, SQLite console/CLI, optional
PostgreSQL/Compose, existing external agents through the documented local bridge.
No provider account, parent workspace or model service is required.

## What changed

2026-10-09.1 ([ADR-0020](adr/0020-truthful-venture-state-requests-and-drift.md)):
published discovery input schemas and `close`; one derived venture state; superseded
work closure; stale proposal labels; request-file registration; bridge drift report
(`doctor` reads the store unless `--offline`); `--id` selectors and venture aliases
(additive migration `b10261009002`); JSON newline and WARNING-default logging.
Upgrade venture repositories by copying the bridge and its SHA-256 into each
manifest, then run `doctor`.


Static CLI discovery avoids database startup; conditional-map requirements are
published; prepared context distinguishes focused map and evidence coverage;
bridge doctor/timeout and same-owner recovery are explicit. Accepted superseding
results now link their historical ancestors without mutating original records.
Pending/rejected/deferred proposals retain normal review behavior. The console
shows accepted replacements instead of repeated reconciliation prompts.

Feedback from real venture operations motivated these changes. Runtime tests use
synthetic isolated cases. Detailed operator/venture context and local configuration
remain outside the public change. ADRs [0017](adr/0017-dogfood-contract-and-recovery-update.md)
and [0018](adr/0018-accepted-result-lineage-and-standalone-release.md) preserve the
decisions, limits and revisit criteria.

## Reproduce verification

From a standalone clone:

```bash
make bootstrap
make check
uv run playwright install chromium
make test-browser
make verify-distribution
# Docker/Compose available:
make workflow-lint
make test-container
```

The distribution target creates a fresh `.local/distribution-check`, builds wheel
and sdist, exports hash-locked runtime dependencies and installs the wheel in a
new venv. `scripts/verify_distribution.py` runs from an empty cwd using the installed
package and synthetic data. It checks migrations, CLI lifecycle resume, consistent
backup, overwrite refusal, restore/integrity, packaged HTML/CSS/JS and process restart.
It refuses reused output paths. Choose another `DIST_VERIFY_ROOT` for a repeat.

`make check` covers lint, strict typing, product behavior and workflow contracts.
PostgreSQL integration uses an explicit disposable database and CI checks migration
drift. Browser tests exercise desktop/mobile create/map/context/result/review flows.
Image checks validate non-root execution and Compose lifecycle. See exact commands
in [DEVELOPMENT.md](../DEVELOPMENT.md) and [.github/workflows/ci.yml](../.github/workflows/ci.yml).

CI runs on main/PR commits, with a required aggregate `ci` job. Verify the complete
SHA and conclusion in [GitHub Actions](https://github.com/Jonathan2021/startup_lab_foundry/actions/workflows/ci.yml);
a previous green commit does not verify a later one. CI retains synthetic test,
coverage and installed-distribution evidence. Source pushes validate images but
never publish them or deploy the application. No GitHub release/PyPI publication
is implied by this repository version.

Local verification on 2026-10-08: Ruff and strict mypy passed; 156 product tests
passed with one explicit PostgreSQL-URL skip; 12 CI contract, 5 browser and 6
container tests passed. The container suite exercised disposable PostgreSQL.
Actionlint and installed-wheel backup/restore/restart checks passed. Hosted CI
must independently pass for the delivered SHA, including its dedicated PostgreSQL
test and both Python versions; local results do not substitute for that check.

## Use, upgrade and recovery

Follow [the usage guide](LIFECYCLE_MVP.md) and [outside-agent contract](EXTERNAL_AGENTS.md).
Run `foundry storage info` before using an existing store. Back up with
`foundry storage backup --output /absolute/new-backup.local.db` before upgrade.
Migrations run on normal CLI/UI startup; the backup command itself does not migrate.
Stop the UI before restoring, preserve the current database, copy a selected
backup to a new path and verify it using `--store` before switching defaults.
Never overwrite a live database or merge stores by copying files.

For agent configuration, copy `.foundry/project.example.json` into ignored
`.foundry/project.json` and set your actual executable/store/workspace IDs. Retain
current operator config across Git updates. Older checkouts tracked that file:
copy it outside the checkout before pulling this update, then restore your copy
to the now-ignored path. Application runtime does not import
or require the bridge. Doctor checks version/hash/configuration; resume verifies
actual workspace state. No prepared private venture database is shipped.

## Limits

This is a trusted loopback application, not an authenticated hosted multi-user
service. Actor labels are not credentials. There is no unattended worker, paid
model fallback, email sender, commercial validation or approved public deployment.
Optional PostgreSQL tests skip locally without a configured test URL; CI supplies
one. Browser and Docker prerequisites are explicit, not silently bypassed.

Seven currently open dependency alerts concern the frozen historical
`docs/inquiry/portfolio-campaign/trials/change-requirements.txt` experiment; it is
not a supported install manifest or runtime dependency. Historical evidence stays
immutable and must not be installed as the current product. Active dependency
constraints/lock retain the previously reviewed patched minimums. Recheck current
advisories when releasing; this statement is dated 2026-10-08.
