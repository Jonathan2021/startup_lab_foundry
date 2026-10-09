"""Agent-owned structural contract for the Foundry CI workflow."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from workflow_yaml import (
    FOUNDRY_ROOT,
    SHA_PIN,
    as_mapping,
    as_sequence,
    external_actions,
    job_commands,
    job_steps,
    load_yaml,
    workflow_jobs,
)

WORKFLOW_PATH = FOUNDRY_ROOT / ".github" / "workflows" / "ci.yml"
REUSABLE_IMAGE_WORKFLOW_PATH = (
    FOUNDRY_ROOT / ".github" / "workflows" / "reusable-image-delivery.yml"
)
REUSABLE_IMAGE_WORKFLOW_USES = (
    "./.github/workflows/reusable-image-delivery.yml"
)


def _workflow(path: Path = WORKFLOW_PATH) -> dict[str, Any]:
    return load_yaml(path, "workflow")


def _action_steps(
    jobs: dict[str, Any], action_name: str
) -> list[dict[str, Any]]:
    return [
        step
        for uses, step in external_actions(jobs)
        if uses.split("@", maxsplit=1)[0].endswith(action_name)
    ]


def _find_job_with(
    jobs: dict[str, Any], predicate: Any, label: str
) -> tuple[str, dict[str, Any]]:
    for job_id, raw_job in jobs.items():
        job = as_mapping(raw_job, f"job {job_id}")
        if predicate(job):
            return str(job_id), job
    raise AssertionError(f"workflow needs {label}")


def _called_image_workflow(
    workflow: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    jobs = workflow_jobs(workflow)
    call_id, call = _find_job_with(
        jobs,
        lambda job: job.get("uses") == REUSABLE_IMAGE_WORKFLOW_USES,
        "a call to the local reusable image workflow",
    )
    inputs = as_mapping(call.get("with"), f"job {call_id} inputs")
    assert inputs.get("publish") == "false", (
        "CI must call the reusable image workflow in validation-only mode"
    )
    return call_id, workflow_jobs(_workflow(REUSABLE_IMAGE_WORKFLOW_PATH))


def _prefixed_jobs(
    prefix: str, jobs: dict[str, Any]
) -> dict[str, Any]:
    return {f"{prefix}/{job_id}": job for job_id, job in jobs.items()}


def test_events_permissions_concurrency_and_action_pins() -> None:
    workflow = _workflow()
    events = as_mapping(workflow.get("on"), "on")
    assert {"pull_request", "push"}.issubset(events), (
        "CI must validate pull requests and pushes to the protected branch"
    )
    push = as_mapping(events["push"], "on.push")
    assert "main" in as_sequence(push.get("branches"), "on.push.branches")

    permissions = as_mapping(workflow.get("permissions"), "permissions")
    assert permissions.get("contents") == "read", (
        "declare read-only contents permission and leave other scopes disabled"
    )
    assert not any(str(value).endswith("write") for value in permissions.values())

    jobs = workflow_jobs(workflow)
    for job_id, raw_job in jobs.items():
        job = as_mapping(raw_job, f"job {job_id}")
        if "permissions" not in job:
            continue
        job_permissions = as_mapping(
            job["permissions"], f"job {job_id} permissions"
        )
        assert not any(
            str(value).endswith("write") for value in job_permissions.values()
        ), f"job {job_id} must not escalate token write authority"

    concurrency = as_mapping(workflow.get("concurrency"), "concurrency")
    group = str(concurrency.get("group", ""))
    assert "github.workflow" in group and (
        "github.ref" in group or "github.event.pull_request.number" in group
    )
    assert concurrency.get("cancel-in-progress") == "true"

    image_call_id, image_jobs = _called_image_workflow(workflow)
    actions = external_actions(jobs) + external_actions(
        _prefixed_jobs(image_call_id, image_jobs)
    )
    assert actions, "use reviewed actions for checkout/setup/cache/artifact work"
    mutable = [uses for uses, _ in actions if not SHA_PIN.fullmatch(uses)]
    assert not mutable, f"pin external actions to full commit SHAs: {mutable}"


def test_quality_matrix_uses_lock_cache_and_test_evidence() -> None:
    workflow = _workflow()
    jobs = workflow_jobs(workflow)

    def has_python_matrix(job: dict[str, Any]) -> bool:
        strategy = job.get("strategy")
        if not isinstance(strategy, dict):
            return False
        matrix = strategy.get("matrix")
        return isinstance(matrix, dict) and "python-version" in matrix

    _, quality = _find_job_with(jobs, has_python_matrix, "a Python matrix job")
    strategy = as_mapping(quality["strategy"], "quality.strategy")
    matrix = as_mapping(strategy["matrix"], "quality.strategy.matrix")
    versions = {
        str(version)
        for version in as_sequence(
            matrix["python-version"], "matrix.python-version"
        )
    }
    assert {"3.11", "3.13"}.issubset(versions), (
        "exercise the minimum supported Python and container runtime Python"
    )

    commands = job_commands(quality)
    for required in (
        "uv lock --check",
        "ruff",
        "mypy",
        "pytest",
    ):
        assert required in commands, f"quality matrix must run {required!r}"

    actionlint_steps = [
        step
        for step in job_steps(quality)
        if str(step.get("uses", "")).startswith(
            "docker://rhysd/actionlint@sha256:"
        )
    ]
    assert actionlint_steps, (
        "quality job must run the digest-pinned actionlint container"
    )
    for suite in (
        "tests/unit",
        "tests/integration",
        "tests/acceptance/test_cli_workspace.py",
        "tests/contract/test_package_boundary.py",
        "tests/contract/test_ci_workflow.py",
        "tests/contract/test_delivery_workflows.py",
    ):
        assert suite in commands, f"quality pytest command must include {suite}"

    quality_actions = [
        (uses, step)
        for uses, step in external_actions({"quality": quality})
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
        and as_mapping(step.get("with", {}), "setup-uv.with").get(
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
    workflow = _workflow()
    jobs = workflow_jobs(workflow)
    image_call_id, image_jobs = _called_image_workflow(workflow)
    inspected_jobs = {
        **jobs,
        **_prefixed_jobs(image_call_id, image_jobs),
    }
    setup_steps: list[tuple[str, dict[str, Any]]] = []
    for job_id, raw_job in inspected_jobs.items():
        job = as_mapping(raw_job, f"job {job_id}")
        if "steps" not in job:
            continue
        for uses, step in external_actions({str(job_id): job}):
            if uses.split("@", maxsplit=1)[0].endswith("/setup-uv"):
                setup_steps.append((str(job_id), step))

    assert setup_steps, "CI jobs must install uv through the reviewed setup action"
    writers = []
    readers = []
    for job_id, step in setup_steps:
        options = as_mapping(step.get("with", {}), f"{job_id} setup-uv.with")
        assert options.get("enable-cache", "true") != "false"
        if options.get("save-cache", "true") == "false":
            readers.append(job_id)
        else:
            writers.append(job_id)

    assert writers == ["python-quality"], (
        "the Python matrix must be the sole cache writer; otherwise parallel "
        "3.13 jobs race to reserve the same setup-uv cache key"
    )
    assert {
        "postgres-integration",
        f"{image_call_id}/image",
    }.issubset(readers), (
        "PostgreSQL and image jobs should restore but not save the shared cache"
    )


def test_postgresql_service_job_exercises_migration_and_cli() -> None:
    workflow = _workflow()
    jobs = workflow_jobs(workflow)

    def has_postgres_service(job: dict[str, Any]) -> bool:
        services = job.get("services")
        return isinstance(services, dict) and "postgres" in services

    _, integration = _find_job_with(
        jobs, has_postgres_service, "a PostgreSQL service-container job"
    )
    services = as_mapping(integration["services"], "integration.services")
    postgres = as_mapping(services["postgres"], "services.postgres")
    image = str(postgres.get("image", ""))
    assert re.fullmatch(r"postgres:[^\s]+", image) and not image.endswith(
        ":latest"
    ), "use an explicit PostgreSQL image version"
    assert "pg_isready" in str(postgres.get("options", ""))
    ports = as_sequence(postgres.get("ports"), "services.postgres.ports")
    assert any("5432" in str(port) for port in ports), (
        "runner jobs reach service containers through a mapped localhost port"
    )

    rendered = yaml.dump(integration)
    assert "POSTGRES_PASSWORD" in rendered
    assert "FOUNDRY_DATABASE_URL" in rendered
    assert "secrets." not in rendered, (
        "CI integration uses synthetic credentials, not repository secrets"
    )
    configure_steps = [
        step
        for step in job_steps(integration)
        if "FOUNDRY_DATABASE_URL" in str(step.get("run", ""))
    ]
    assert len(configure_steps) == 1
    configure = configure_steps[0]
    assert "${{" not in str(configure.get("run", "")), (
        "pass expression results through env instead of interpolating shell source"
    )
    assert "job.services.postgres.ports" in yaml.dump(configure.get("env", {}))
    commands = job_commands(integration)
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
    jobs = workflow_jobs(workflow)
    image_call_id, image_jobs = _called_image_workflow(workflow)

    def builds_image(job: dict[str, Any]) -> bool:
        commands = job_commands(job)
        return "docker build" in commands and "docker run" in commands

    _, image_job = _find_job_with(
        image_jobs, builds_image, "an image build/runtime evidence job"
    )
    image_commands = job_commands(image_job)
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

    inspected_jobs = {
        **jobs,
        **_prefixed_jobs(image_call_id, image_jobs),
    }
    uploads = _action_steps(inspected_jobs, "/upload-artifact")
    assert uploads, "upload bounded test or image evidence"
    for step in uploads:
        options = as_mapping(step.get("with"), "upload-artifact.with")
        retention = int(str(options.get("retention-days", "0")))
        assert 1 <= retention <= 14, "bound CI evidence retention to 1-14 days"

    gate = as_mapping(jobs.get("ci"), "stable ci gate job")
    needs = {str(value) for value in as_sequence(gate.get("needs"), "ci.needs")}
    assert {quality_id, integration_id, image_call_id}.issubset(needs), (
        "stable gate must depend on quality, integration, and image"
    )
    assert "always()" in str(gate.get("if", "")), (
        "the stable gate must evaluate every dependency result"
    )
    gate_text = yaml.dump(gate)
    assert "needs" in gate_text and "result" in gate_text, (
        "stable gate must fail unless every required job succeeds"
    )
