"""Agent-owned structural contract for the Foundry CI workflow."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FOUNDRY_ROOT = Path(__file__).parents[2]
WORKFLOW_PATH = FOUNDRY_ROOT / ".github" / "workflows" / "ci.yml"
SHA_PIN = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    assert isinstance(value, dict), f"{label} must be a YAML mapping"
    return value


def _sequence(value: Any, label: str) -> list[Any]:
    if isinstance(value, str):
        return [value]
    assert isinstance(value, list), f"{label} must be a YAML sequence"
    return value


def _workflow() -> dict[str, Any]:
    assert WORKFLOW_PATH.is_file(), (
        "create .github/workflows/ci.yml for L-001"
    )
    parsed = yaml.load(WORKFLOW_PATH.read_text(), Loader=yaml.BaseLoader)
    return _mapping(parsed, "workflow")


def _jobs(workflow: dict[str, Any]) -> dict[str, Any]:
    return _mapping(workflow.get("jobs"), "jobs")


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    raw_steps = _sequence(job.get("steps"), "job steps")
    return [_mapping(step, "workflow step") for step in raw_steps]


def _commands(job: dict[str, Any]) -> str:
    return "\n".join(str(step.get("run", "")) for step in _steps(job))


def _external_actions(jobs: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    actions: list[tuple[str, dict[str, Any]]] = []
    for job_id, raw_job in jobs.items():
        job = _mapping(raw_job, f"job {job_id}")
        for step in _steps(job):
            uses = str(step.get("uses", ""))
            if uses and not uses.startswith(("./", "docker://")):
                actions.append((uses, step))
    return actions


def _action_steps(
    jobs: dict[str, Any], action_name: str
) -> list[dict[str, Any]]:
    return [
        step
        for uses, step in _external_actions(jobs)
        if uses.split("@", maxsplit=1)[0].endswith(action_name)
    ]


def _find_job_with(
    jobs: dict[str, Any], predicate: Any, label: str
) -> tuple[str, dict[str, Any]]:
    for job_id, raw_job in jobs.items():
        job = _mapping(raw_job, f"job {job_id}")
        if predicate(job):
            return str(job_id), job
    raise AssertionError(f"workflow needs {label}")


def test_events_permissions_concurrency_and_action_pins() -> None:
    workflow = _workflow()
    events = _mapping(workflow.get("on"), "on")
    assert {"pull_request", "push"}.issubset(events), (
        "CI must validate pull requests and pushes to the protected branch"
    )
    push = _mapping(events["push"], "on.push")
    assert "main" in _sequence(push.get("branches"), "on.push.branches")

    permissions = _mapping(workflow.get("permissions"), "permissions")
    assert permissions.get("contents") == "read", (
        "declare read-only contents permission and leave other scopes disabled"
    )
    assert not any(str(value).endswith("write") for value in permissions.values())

    jobs = _jobs(workflow)
    for job_id, raw_job in jobs.items():
        job = _mapping(raw_job, f"job {job_id}")
        if "permissions" not in job:
            continue
        job_permissions = _mapping(
            job["permissions"], f"job {job_id} permissions"
        )
        assert not any(
            str(value).endswith("write") for value in job_permissions.values()
        ), f"job {job_id} must not escalate token write authority"

    concurrency = _mapping(workflow.get("concurrency"), "concurrency")
    group = str(concurrency.get("group", ""))
    assert "github.workflow" in group and (
        "github.ref" in group or "github.event.pull_request.number" in group
    )
    assert concurrency.get("cancel-in-progress") == "true"

    actions = _external_actions(jobs)
    assert actions, "use reviewed actions for checkout/setup/cache/artifact work"
    mutable = [uses for uses, _ in actions if not SHA_PIN.fullmatch(uses)]
    assert not mutable, f"pin external actions to full commit SHAs: {mutable}"


def test_quality_matrix_uses_lock_cache_and_test_evidence() -> None:
    workflow = _workflow()
    jobs = _jobs(workflow)

    def has_python_matrix(job: dict[str, Any]) -> bool:
        strategy = job.get("strategy")
        if not isinstance(strategy, dict):
            return False
        matrix = strategy.get("matrix")
        return isinstance(matrix, dict) and "python-version" in matrix

    _, quality = _find_job_with(jobs, has_python_matrix, "a Python matrix job")
    strategy = _mapping(quality["strategy"], "quality.strategy")
    matrix = _mapping(strategy["matrix"], "quality.strategy.matrix")
    versions = {
        str(version)
        for version in _sequence(
            matrix["python-version"], "matrix.python-version"
        )
    }
    assert {"3.11", "3.13"}.issubset(versions), (
        "exercise the minimum supported Python and container runtime Python"
    )

    commands = _commands(quality)
    for required in ("uv lock --check", "ruff", "mypy", "pytest"):
        assert required in commands, f"quality matrix must run {required!r}"
    for suite in (
        "tests/unit",
        "tests/integration",
        "tests/acceptance/test_cli_workspace.py",
        "tests/contract/test_package_boundary.py",
        "tests/contract/test_ci_workflow.py",
    ):
        assert suite in commands, f"quality pytest command must include {suite}"

    quality_actions = [
        (uses, step)
        for uses, step in _external_actions({"quality": quality})
    ]
    assert _action_steps({"quality": quality}, "/checkout"), (
        "quality job must check out the exact event revision"
    )
    assert "matrix.python-version" in yaml.dump(quality), (
        "quality job must install/use each selected matrix Python"
    )
    has_explicit_cache = any("/cache@" in uses for uses, _ in quality_actions)
    has_uv_cache = any(
        "setup-uv@" in uses
        and _mapping(step.get("with", {}), "setup-uv.with").get(
            "enable-cache", "true"
        )
        != "false"
        for uses, step in quality_actions
    )
    assert has_explicit_cache or has_uv_cache, (
        "cache locked uv dependencies and be able to explain the cache key"
    )

    uploads = _action_steps({"quality": quality}, "/upload-artifact")
    assert uploads, "upload test evidence from the quality job"
    assert any(
        any(
            condition in str(step.get("if", ""))
            for condition in ("always()", "!cancelled()")
        )
        for step in uploads
    ), "retain diagnostic evidence when tests fail"


def test_uv_dependency_cache_has_one_matrix_writer() -> None:
    """Parallel 3.13 jobs must not race to reserve the same cache key."""
    jobs = _jobs(_workflow())
    setup_steps: list[tuple[str, dict[str, Any]]] = []
    for job_id, raw_job in jobs.items():
        job = _mapping(raw_job, f"job {job_id}")
        if "steps" not in job:
            continue
        for uses, step in _external_actions({str(job_id): job}):
            if uses.split("@", maxsplit=1)[0].endswith("/setup-uv"):
                setup_steps.append((str(job_id), step))

    assert setup_steps, "CI jobs must install uv through the reviewed setup action"
    writers = []
    readers = []
    for job_id, step in setup_steps:
        options = _mapping(step.get("with", {}), f"{job_id} setup-uv.with")
        assert options.get("enable-cache", "true") != "false"
        if options.get("save-cache", "true") == "false":
            readers.append(job_id)
        else:
            writers.append(job_id)

    assert writers == ["python-quality"], (
        "the Python matrix must be the sole cache writer; otherwise parallel "
        "3.13 jobs race to reserve the same setup-uv cache key"
    )
    assert {"postgres-integration", "image"}.issubset(readers), (
        "PostgreSQL and image jobs should restore but not save the shared cache"
    )


def test_postgresql_service_job_exercises_migration_and_cli() -> None:
    workflow = _workflow()
    jobs = _jobs(workflow)

    def has_postgres_service(job: dict[str, Any]) -> bool:
        services = job.get("services")
        return isinstance(services, dict) and "postgres" in services

    _, integration = _find_job_with(
        jobs, has_postgres_service, "a PostgreSQL service-container job"
    )
    services = _mapping(integration["services"], "integration.services")
    postgres = _mapping(services["postgres"], "services.postgres")
    image = str(postgres.get("image", ""))
    assert re.fullmatch(r"postgres:[^\s]+", image) and not image.endswith(
        ":latest"
    ), "use an explicit PostgreSQL image version"
    assert "pg_isready" in str(postgres.get("options", ""))
    ports = _sequence(postgres.get("ports"), "services.postgres.ports")
    assert any("5432" in str(port) for port in ports), (
        "runner jobs reach service containers through a mapped localhost port"
    )

    rendered = yaml.dump(integration)
    assert "POSTGRES_PASSWORD" in rendered
    assert "FOUNDRY_DATABASE_URL" in rendered
    assert "secrets." not in rendered, (
        "CI integration uses synthetic credentials, not repository secrets"
    )
    commands = _commands(integration)
    for required in (
        "uv lock --check",
        "alembic upgrade head",
        "alembic check",
    ):
        assert required in commands, f"integration job must run {required!r}"
    has_cli_commands = "venture create" in commands and "venture show" in commands
    has_cli_test = "tests/integration/test_postgresql_cli.py" in commands
    assert has_cli_commands or has_cli_test, (
        "integration job must exercise venture create/show against PostgreSQL"
    )


def test_image_evidence_and_stable_gate_cover_all_jobs() -> None:
    workflow = _workflow()
    jobs = _jobs(workflow)

    def builds_image(job: dict[str, Any]) -> bool:
        commands = _commands(job)
        return "docker build" in commands and "docker run" in commands

    image_id, image_job = _find_job_with(
        jobs, builds_image, "an image build/runtime evidence job"
    )
    image_commands = _commands(image_job)
    has_uid_check = "id -u" in image_commands or (
        "--entrypoint id" in image_commands
        and (
            "uid=" in image_commands
            or (" -u" in image_commands and "10001" in image_commands)
        )
    )
    assert has_uid_check, "retain non-root runtime evidence"
    assert "--help" in image_commands, "prove the built image executes the CLI"

    def has_python_matrix(job: dict[str, Any]) -> bool:
        strategy = job.get("strategy")
        return isinstance(strategy, dict) and isinstance(
            strategy.get("matrix"), dict
        ) and "python-version" in strategy["matrix"]

    quality_id, _ = _find_job_with(jobs, has_python_matrix, "a Python matrix job")

    def has_postgres_service(job: dict[str, Any]) -> bool:
        services = job.get("services")
        return isinstance(services, dict) and "postgres" in services

    integration_id, _ = _find_job_with(
        jobs, has_postgres_service, "a PostgreSQL service-container job"
    )

    uploads = _action_steps(jobs, "/upload-artifact")
    assert uploads, "upload bounded test or image evidence"
    for step in uploads:
        options = _mapping(step.get("with"), "upload-artifact.with")
        retention = int(str(options.get("retention-days", "0")))
        assert 1 <= retention <= 14, "bound CI evidence retention to 1-14 days"

    gate = _mapping(jobs.get("ci"), "stable ci gate job")
    needs = {str(value) for value in _sequence(gate.get("needs"), "ci.needs")}
    assert {quality_id, integration_id, image_id}.issubset(needs), (
        "stable gate must depend on quality, integration, and image"
    )
    assert "always()" in str(gate.get("if", "")), (
        "the stable gate must evaluate every dependency result"
    )
    gate_text = yaml.dump(gate)
    assert "needs" in gate_text and "result" in gate_text, (
        "stable gate must fail unless every required job succeeds"
    )
