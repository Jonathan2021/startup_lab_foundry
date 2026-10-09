# Volley Coach, Crous Queue and OfferCheck readiness — 2026-10-08

All three have working bounded local MVPs and accepted post-review Foundry
checkpoints. **None is yet a committed release with GitHub Actions verification.**
This audit also reproduced an OfferCheck clean-checkout lint defect and clarified
that Crous Queue's complete distribution is its source kit, not its bare wheel.

The user requested the same audit/handoff treatment as the first three projects.
No application source was changed, and no commit, push, remote creation, deployment
or real-user action occurred. Earlier handoffs prohibited commits/pushes. The
copyable continuation prompts separately authorize scoped private Git delivery.

## Fresh evidence

| Project | Core and browser checks | Setup/distribution | Verdict |
| --- | --- | --- | --- |
| Volley Coach v0.1.1 | Ruff/strict mypy; 37 core + 4 browser tests pass | Fresh migration/demo; installed wheel outside checkout migrates, serves HTTP 200, backs up/restores without Foundry | Local scheduling MVP works; commit/remote/CI and current release/developer documentation remain |
| Crous Queue v0.1.1 | Ruff/format/strict mypy; 22 core + 7 browser tests pass | Fresh config/migration/directory/demo pass; full source kit passes independent setup/recovery/HTTP smoke; bare wheel migration fails | Source-distribution MVP works; packaging contract, commit/remote/CI remain |
| OfferCheck v0.1.0 | Direct strict mypy and 54 core + 6 browser tests pass; fresh `make check` fails at Ruff | Fresh migration/demo and installed-wheel HTTP/backup/restore pass without Foundry | Runtime works; clean-checkout lint defect and commit/remote/CI remain |

Commands, working directories, exits and timings are in `*-commands.json` and
`*-wheel-commands.json`; stdout is retained in adjacent text files. OfferCheck's
separate types/core command completed successfully after make stopped at lint;
`offer-check-types.txt` and `offer-check-core.txt` retain the output. The six browser
tests were deselected only in the explicit non-browser command, then run separately.
Volley Coach/OfferCheck retain an upstream TestClient deprecation warning; it is
not suppressed or presented as a failed application behavior.

### OfferCheck: hidden directory changes lint behavior

A fresh copy of Git-eligible source fails `make check` with four Ruff `I001` errors:
`src/offer_check/db.py`, `migrations/env.py`, `migrations/versions/0001_capture.py`
and `0002_retention.py`. Original-workspace lint passes. The original contains an
empty, untracked root `alembic/versions` directory, which Git cannot preserve.

A controlled experiment kept source bytes unchanged and ran
`uv run ruff check --no-cache src tests scripts examples`:

| Condition | Exit |
| --- | --- |
| Original workspace, empty Alembic directory present | 0 |
| Independent copy, directory absent | 1 |
| Same copy, only that empty directory added | 0 |
| Same copy, directory removed again | 1 |

This supports filesystem-dependent import classification as the cause. The first
toggle without `--no-cache` misleadingly retained a green result after removal;
that failed diagnostic is retained separately and does not establish a pass.
Evidence: `offer-check-lint-portability-no-cache.json`, `offer-check-check.txt`.
O07 requires an explicit/correct third-party import policy and a clean-checkout
acceptance guard, not an empty-directory workaround or blanket lint suppression.

### Crous Queue: source kit passes, bare wheel is incomplete

The wheel contains templates/static assets but **no Alembic revisions**. Its CLI
uses cwd-relative `alembic.ini`; directory import defaults to a repository fixture.
After a fresh wheel-only install with valid synthetic configuration, from an empty
working directory, `crous-queue migrate` exits 1:

```text
alembic.util.exc.CommandError: No 'script_location' key found in configuration.
```

Evidence: `wheel-contents.json`, `crous-queue-wheel-migrate.txt` and wheel command
metadata. HTTP startup was not claimed after the failed migration.

The explicitly packaged **source release kit** independently passes its real
verification harness: install, migrate, retained directory import, 22 tests,
backup/restore, retention, separate demo and HTTP smoke (unknown waits, search,
privacy and denied unauthenticated admin access). Evidence:
`crous-queue-source-release.txt` and its command metadata, exit 0.

README already specifies source/local archive use, so the bare-wheel limitation
does not invalidate that working path. Q07 may package the missing runtime resources
and test a standalone wheel, or explicitly designate the complete source kit as
the sole supported distribution and stop implying wheel independence. It must
state and test whichever artifact contract it ships.

## GitHub, documentation and code review

Every audited repository has an unborn `main`, no commits, no configured remote
and no `.github` workflow. Read-only authenticated GitHub inventory found no
matching `Jonathan2021/volley-coach`, `crous-queue` or `offer-check` repository.
`*-baseline.json` and `github-inventory.json` retain these observations. No remote
CI therefore verifies these current sources.

The user guides are more complete than the first group: Volley Coach has an
own-program walkthrough/API/privacy/recovery guide; Crous has a French first-use
flow, demo separation and detailed operations; OfferCheck has a current operator
walkthrough/API workflow/recovery/retention guide. Audited local entry-point links
resolve (`documentation-links.json`). This is not a claim that every historical
evidence link is portable to a new clone.

Remaining documentation work is specific: current versus historical release labels,
an actual developer/module entry point where architecture still reads as initial
scaffolding, the Crous distribution contract, and portable current release evidence
instead of reliance on ignored `.foundry/runs`. Preserve substantive existing docs;
do not replace them with generic boilerplate or add an arbitrary license.

Each handoff requires locked clean-checkout CI, current core/browser tests, installed
artifact/source-kit checks, fresh migration/demo, recovery and appropriate dependency
and secret/data review. CI needs minimal permissions, bounded jobs and synthetic
fixtures. Completion requires the actual final pushed SHA's successful Actions
runs, not merely a workflow file. No real programs, wait reports or commercial
quotes belong in CI or its artifacts.

## Foundry and audit boundaries

All three doctor reports verify bridge/contract **2026-10-07.2** and canonical
SHA-256 `1e0be09cd1b537864e0b04bbc2358932b1efba7c7a5d4abb4c0b9aff0e91703f`.
Accepted complete-context results:

- C06: `4a847ef9-1baf-5151-ab8b-46cf0efa36f6`.
- Q06: `ce2d0fb8-aa40-5c41-8a76-ab0b68bdd74d`.
- O06: `09009845-1946-510e-b767-bac6646a68d5`.

Their positive feedback confirms upgraded doctor/map/evidence coverage behavior.
No new blocking Foundry defect was observed and no platform change is needed for
these release tasks. Foundry coordination is actually used, not an app dependency.

Coordinator audit work: `32d1895f-6a58-4a86-ab05-f5e9a51c9e74`. Initial complete
context `4208a993-d584-57db-a5e2-410bfa99fb08` covers 46 evidence records, including
the new O06 feedback and first-group release feedback. Final result/context and
resolution receipts are recorded in `foundry-checkpoint.json`.

No active implementation claims existed in these three ventures. Ready unclaimed
follow-ups preserve their human gates:

| Package | Work ID | Handoff |
| --- | --- | --- |
| C07 | `71764075-5c90-446c-9cb3-d3e6b65a3f9d` | `volley-coach/docs/mvp/READINESS_HANDOFF.md` |
| Q07 | `d608000e-df62-4005-a1fc-c74080e5f7e2` | `crous-queue/docs/mvp/READINESS_HANDOFF.md` |
| O07 | `ccb572cc-2da2-4604-8ce1-dbf7af1db90a` | `offer-check/docs/mvp/READINESS_HANDOFF.md` |

`PROTOCOL.md` was frozen before fresh tests and extended before the bounded lint
causality checks. Copies came from Git-eligible files without original databases,
environments or Foundry state. Wheel environments use runtime dependencies exported
from each lock, with hash-checked installation; Foundry absence was checked directly.
Source hashes in `source-and-handoff-validation.json` confirm the 58/60/59 captured
application/test/build files remain unchanged. The temporary Alembic directories
were created/removed only in the owned copy. Own smoke servers were terminated by
their harnesses; original services and stores were untouched.

This was a bounded technical audit, not an exhaustive security review. No fresh
dependency-wide advisory scan, PostgreSQL/public deployment, real participant trial,
queue accuracy measurement or operator commercial comparison was performed. Those
limits remain explicit. Real program guidance/intake, R011 access/voluntary field
observations and R013 owner-authorized quotes/reviewer are not silently cleared by
local tests or Git delivery. `PROMPTS.md` provides the exact scoped continuations.
