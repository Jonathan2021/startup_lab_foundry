# Notes for the next cleanup pass

## Records, not junk

- `docs/inquiry/**`, `docs/plans/**`, `docs/adr/`, `docs/sources/*.csv`, `requests/`
  and `feedback/` are evidence, decisions and operator inputs. Their scripts, logs,
  screenshots and absolute paths are historical provenance; do not "fix" or delete.
  Dependabot security PRs against `docs/inquiry/**/requirements.txt` would rewrite
  historical probe records.
- Root `foundry.db` is the original Slice 1 store, cited as preserved by inquiry
  records. Never open it read-write; removing it is a human decision.
- `scripts/*.py` other than `verify_distribution.py` are one-time operator scripts
  cited by records and `DEVELOPMENT.md`. They are not linted/typed by CI.

## Looks dead, is intentional

- `tools/foundry_agent.py` is byte-identical to `scripts/agent-kit/foundry_agent.py`
  (Foundry dogfoods its own bridge). `.foundry/project.example.json` pins the kit
  SHA-256 and contract version. `tests/contract/test_package_boundary.py` enforces
  all three; update them together.
- `tests/acceptance/test_agent_run_evalops_contract.py` is intentionally red
  (deferred EvalOps boundary) and excluded from Makefile/CI.
- Vulture flags FastAPI routes, pydantic validators and ORM enum members/tables;
  those are used. `PortfolioService.link_venture_idea` has no caller but a plan
  names it for reuse; kept pending a decision.

## Running the CI equivalent locally

`testpaths = ["tests"]`, so bare `pytest` also runs the red EvalOps, Docker and
browser suites. Use: `make check`, `make test-browser`, `make verify-distribution
DIST_VERIFY_ROOT=<new dir>`, `make workflow-lint`, `make test-container` (Docker).
PostgreSQL CLI tests need a disposable `FOUNDRY_DATABASE_URL`.

When other pytest runs share the machine user, pass `--basetemp=<private dir>`:
pytest rotates `/tmp/pytest-of-$USER` and can delete a live run's stores
(seen as a spurious `OperationalError`). Keep it on tmpfs; per-test SQLite
migrations are many times slower on a busy disk.

## Coverage gaps left on purpose

In-process coverage under-reports `cli.py` and `*_commands.py`; they are exercised
through subprocess acceptance tests. `revamp_bootstrap.py` (0%) is a one-time
import for one preserved campaign and needs that operator data to test.
