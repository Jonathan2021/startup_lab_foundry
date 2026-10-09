UV ?= uv
PYTHON_VERSION ?= 3.13
FOUNDRY_ARGS ?= --help
FOUNDRY_STORE ?= .local/demo.local.db
FOUNDRY_PORT ?= 8765
DIST_VERIFY_ROOT ?= $(CURDIR)/.local/distribution-check
PRODUCT_TESTS := tests/unit tests/integration tests/acceptance/test_cli_workspace.py tests/acceptance/test_cli_lifecycle.py tests/acceptance/test_agent_kit.py tests/contract/test_package_boundary.py
COMPOSE := docker compose --file docker-compose.yaml

.PHONY: help bootstrap install lint typecheck check test test-product test-browser test-container test-ci workflow-lint build verify-distribution seed-demo foundry-ui foundry-local foundry-up foundry foundry-down foundry-reset

help:
	@echo "bootstrap/install: locked development environment; check: lint, types, product and CI contracts"
	@echo "seed-demo: NEW synthetic store (FOUNDRY_STORE); foundry-ui: permanent local store"
	@echo "test-browser, test-container, workflow-lint: explicit browser/Docker checks"
	@echo "verify-distribution: build and exercise an isolated installed wheel (new DIST_VERIFY_ROOT)"

bootstrap install:
	$(UV) sync --locked --group dev --python $(PYTHON_VERSION)
lint:
	$(UV) run ruff check src tests scripts/agent-kit scripts/verify_distribution.py
typecheck:
	$(UV) run mypy src scripts/agent-kit scripts/verify_distribution.py
test test-product:
	$(UV) run pytest -q $(PRODUCT_TESTS)
test-ci:
	$(UV) run pytest -q tests/contract/test_ci_workflow.py tests/contract/test_delivery_workflows.py
check: lint typecheck test-product test-ci
test-browser:
	$(UV) run pytest -q tests/acceptance/test_lifecycle_browser.py tests/acceptance/test_revamp_browser.py
test-container:
	$(UV) run pytest -q tests/acceptance/test_container_stack.py
workflow-lint:
	docker run --rm -v "$(CURDIR):/repo" -w /repo rhysd/actionlint@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667
build:
	$(UV) build
verify-distribution:
	test ! -e "$(DIST_VERIFY_ROOT)"
	mkdir -p "$(DIST_VERIFY_ROOT)"
	$(UV) build --out-dir "$(DIST_VERIFY_ROOT)/dist"
	$(UV) export --frozen --no-dev --no-emit-project --output-file "$(DIST_VERIFY_ROOT)/requirements.txt"
	$(UV) venv --python $(PYTHON_VERSION) "$(DIST_VERIFY_ROOT)/venv"
	$(UV) pip install --python "$(DIST_VERIFY_ROOT)/venv/bin/python" --require-hashes -r "$(DIST_VERIFY_ROOT)/requirements.txt"
	$(UV) pip install --python "$(DIST_VERIFY_ROOT)/venv/bin/python" --no-deps "$(DIST_VERIFY_ROOT)"/dist/*.whl
	$(UV) run python scripts/verify_distribution.py --python "$(DIST_VERIFY_ROOT)/venv/bin/python" --output-dir "$(DIST_VERIFY_ROOT)/smoke"
seed-demo:
	$(UV) run python -m startup_foundry.demo --store "$(FOUNDRY_STORE)"
foundry-ui:
	$(UV) run foundry ui --port $(FOUNDRY_PORT)
foundry-local:
	$(UV) run foundry $(FOUNDRY_ARGS)
foundry-up:
	$(COMPOSE) up --build --wait db
	$(COMPOSE) run --rm migrate
foundry:
	$(COMPOSE) run --rm foundry $(FOUNDRY_ARGS)
foundry-down:
	$(COMPOSE) down
foundry-reset:
	@test "$(CONFIRM)" = yes || { echo "Set CONFIRM=yes only for disposable data"; exit 2; }
	$(COMPOSE) down --volumes
