"""Agent-owned structural contract for guarded Foundry image delivery."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FOUNDRY_ROOT = Path(__file__).parents[2]
CALLER_PATH = FOUNDRY_ROOT / ".github" / "workflows" / "delivery.yml"
REUSABLE_PATH = (
    FOUNDRY_ROOT / ".github" / "workflows" / "reusable-image-delivery.yml"
)
ACTION_PATH = (
    FOUNDRY_ROOT / ".github" / "actions" / "release-metadata" / "action.yml"
)
SHA_PIN = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    assert isinstance(value, dict), f"{label} must be a YAML mapping"
    return value


def _sequence(value: Any, label: str) -> list[Any]:
    if isinstance(value, str):
        return [value]
    assert isinstance(value, list), f"{label} must be a YAML sequence"
    return value


def _yaml(path: Path, label: str) -> dict[str, Any]:
    assert path.is_file(), f"create {path.relative_to(FOUNDRY_ROOT)}"
    parsed = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    return _mapping(parsed, label)


def _jobs(workflow: dict[str, Any]) -> dict[str, Any]:
    return _mapping(workflow.get("jobs"), "jobs")


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    raw_steps = _sequence(job.get("steps"), "job steps")
    return [_mapping(step, "workflow step") for step in raw_steps]


def _commands(job: dict[str, Any]) -> str:
    return "\n".join(str(step.get("run", "")) for step in _steps(job))


def _permissions(container: dict[str, Any], label: str) -> dict[str, Any]:
    return _mapping(container.get("permissions", {}), f"{label} permissions")


def _has_write_permission(container: dict[str, Any], label: str) -> bool:
    return any(
        str(value) == "write"
        for value in _permissions(container, label).values()
    )


def _external_actions(jobs: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    for job_id, raw_job in jobs.items():
        job = _mapping(raw_job, f"job {job_id}")
        if "steps" not in job:
            continue
        for step in _steps(job):
            uses = str(step.get("uses", ""))
            if uses and not uses.startswith(("./", "docker://")):
                actions.append(uses)
    return actions


def _assert_immutable_actions(jobs: dict[str, Any]) -> None:
    mutable = [uses for uses in _external_actions(jobs) if not SHA_PIN.fullmatch(uses)]
    assert not mutable, f"pin every external action to a full commit SHA: {mutable}"


def test_typed_manual_and_scheduled_callers_separate_authority() -> None:
    workflow = _yaml(CALLER_PATH, "delivery caller")
    events = _mapping(workflow.get("on"), "on")
    assert {"workflow_dispatch", "schedule"}.issubset(events), (
        "delivery needs a typed manual trigger and a scheduled validation trigger"
    )
    assert not {"pull_request", "pull_request_target", "push", "release"}.intersection(
        events
    ), "no unreviewed event may publish a package"

    dispatch = _mapping(events["workflow_dispatch"], "on.workflow_dispatch")
    dispatch_inputs = _mapping(dispatch.get("inputs"), "workflow_dispatch.inputs")
    boolean_inputs = {
        name: _mapping(spec, f"dispatch input {name}")
        for name, spec in dispatch_inputs.items()
        if isinstance(spec, dict) and spec.get("type") == "boolean"
    }
    assert boolean_inputs, "add an explicit boolean publish/no-publish decision"
    publish_name, publish_input = next(iter(boolean_inputs.items()))
    assert publish_input.get("required") == "true"
    assert publish_input.get("default") == "false", (
        "manual delivery must default to validation without publication"
    )
    assert any(
        isinstance(spec, dict) and spec.get("type") in {"environment", "choice"}
        for spec in dispatch_inputs.values()
    ), "make the target a constrained environment or choice input"

    schedules = _sequence(events["schedule"], "on.schedule")
    assert any(
        isinstance(entry, dict) and str(entry.get("cron", "")).strip()
        for entry in schedules
    ), "declare an intentional, reviewed schedule"

    permissions = _permissions(workflow, "delivery workflow")
    assert not any(str(value) == "write" for value in permissions.values()), (
        "the caller must deny write authority by default"
    )

    jobs = _jobs(workflow)
    calls = [
        (str(job_id), _mapping(raw_job, f"job {job_id}"))
        for job_id, raw_job in jobs.items()
        if isinstance(raw_job, dict)
        and str(raw_job.get("uses", "")).startswith("./.github/workflows/")
    ]
    assert len(calls) >= 2, (
        "use separate reusable-workflow calls for validation and publication"
    )

    scheduled = [
        (job_id, job)
        for job_id, job in calls
        if "schedule" in str(job.get("if", ""))
    ]
    assert scheduled, "route scheduled runs through an explicit validation-only call"
    for job_id, job in scheduled:
        assert not _has_write_permission(job, f"scheduled job {job_id}"), (
            "scheduled validation must have no write token scope"
        )
        assert "false" in yaml.dump(job.get("with", {})).lower(), (
            "scheduled validation must pass publication=false"
        )

    manual_publish = [
        job
        for _, job in calls
        if f"inputs.{publish_name}" in yaml.dump(job)
        and _has_write_permission(job, "manual publication job")
    ]
    assert manual_publish, (
        "only an explicit manual publish decision may grant delivery write scopes"
    )
    _assert_immutable_actions(jobs)


def test_reusable_workflow_exposes_typed_inputs_outputs_and_image_evidence() -> None:
    workflow = _yaml(REUSABLE_PATH, "reusable delivery workflow")
    events = _mapping(workflow.get("on"), "on")
    call = _mapping(events.get("workflow_call"), "on.workflow_call")
    inputs = _mapping(call.get("inputs"), "workflow_call.inputs")
    assert any(
        isinstance(spec, dict) and spec.get("type") == "boolean"
        for spec in inputs.values()
    ), "the reusable workflow needs a typed publication input"
    assert any(
        isinstance(spec, dict) and spec.get("type") == "string"
        for spec in inputs.values()
    ), "the reusable workflow needs a typed target/environment input"
    outputs = _mapping(call.get("outputs"), "workflow_call.outputs")
    assert outputs, "return bounded image identity/digest evidence to callers"

    permissions = _permissions(workflow, "reusable workflow")
    assert not any(str(value) == "write" for value in permissions.values()), (
        "the reusable workflow must deny write authority by default"
    )

    jobs = _jobs(workflow)
    all_commands = "\n".join(
        _commands(_mapping(job, f"job {job_id}"))
        for job_id, job in jobs.items()
        if isinstance(job, dict) and "steps" in job
    )
    rendered = yaml.dump(workflow)
    assert "./.github/actions/release-metadata" in rendered, (
        "reuse the local composite action for validated image metadata"
    )
    assert "docker build" in all_commands or "build-push-action@" in rendered, (
        "build the existing Foundry image as the release candidate"
    )
    assert "docker run" in all_commands and "--help" in all_commands, (
        "validate the candidate's runtime identity and CLI before publication"
    )
    assert "GITHUB_OUTPUT" in rendered, "pass bounded data through job/action outputs"
    assert "GITHUB_STEP_SUMMARY" in rendered, (
        "write a small operator-facing delivery summary"
    )
    _assert_immutable_actions(jobs)


def test_composite_action_validates_inputs_without_shell_interpolation() -> None:
    action = _yaml(ACTION_PATH, "release metadata action")
    inputs = _mapping(action.get("inputs"), "action inputs")
    assert len(inputs) >= 2, (
        "accept enough metadata to validate and construct an immutable image reference"
    )
    outputs = _mapping(action.get("outputs"), "action outputs")
    assert outputs, "publish validated metadata through declared action outputs"

    runs = _mapping(action.get("runs"), "runs")
    assert runs.get("using") == "composite"
    steps = [
        _mapping(step, "composite step")
        for step in _sequence(runs.get("steps"), "composite steps")
    ]
    run_steps = [step for step in steps if "run" in step]
    assert run_steps, "implement validation in one or more composite run steps"
    assert all(step.get("shell") for step in run_steps), (
        "composite run steps must select their shell explicitly"
    )
    assert all("${{ inputs." not in str(step["run"]) for step in run_steps), (
        "do not interpolate caller-controlled input directly into shell source"
    )
    assert any("inputs." in yaml.dump(step.get("env", {})) for step in run_steps), (
        "pass caller-controlled values through environment variables before validation"
    )
    commands = "\n".join(str(step["run"]) for step in run_steps)
    assert "GITHUB_OUTPUT" in commands, "emit the validated result via GITHUB_OUTPUT"
    assert "exit" in commands, "reject malformed or disallowed release metadata"


def test_publication_is_guarded_scoped_and_attested() -> None:
    caller = _yaml(CALLER_PATH, "delivery caller")
    reusable = _yaml(REUSABLE_PATH, "reusable delivery workflow")
    caller_jobs = _jobs(caller)
    jobs = _jobs(reusable)

    privileged_calls: list[tuple[str, dict[str, Any]]] = []
    for job_id, raw_job in caller_jobs.items():
        job = _mapping(raw_job, f"job {job_id}")
        if _permissions(job, f"job {job_id}").get("packages") == "write":
            privileged_calls.append((str(job_id), job))
    assert privileged_calls, (
        "add one explicit GHCR publication call with packages: write"
    )

    for job_id, call in privileged_calls:
        permissions = _permissions(call, f"caller job {job_id}")
        assert permissions.get("contents") == "read"
        assert permissions.get("packages") == "write"
        assert permissions.get("attestations") == "write"
        assert permissions.get("id-token") == "write"

    publication_jobs: list[tuple[str, dict[str, Any]]] = []
    for job_id, raw_job in jobs.items():
        job = _mapping(raw_job, f"job {job_id}")
        rendered_job = yaml.dump(job)
        if "docker push" in rendered_job and "attest" in rendered_job.lower():
            publication_jobs.append((str(job_id), job))
    assert publication_jobs, "the reusable workflow needs one publication job"

    for job_id, job in publication_jobs:
        assert "permissions" not in job, (
            f"called publication job {job_id} must inherit the caller ceiling; "
            "declaring write scopes here makes the shared workflow invalid for "
            "the read-only CI caller before its input-gated job can be skipped"
        )
        assert "inputs." in str(job.get("if", "")), (
            f"publication job {job_id} must require the typed publication input"
        )
        assert "inputs." in yaml.dump(job.get("environment", {})), (
            f"publication job {job_id} must target the selected protected environment"
        )

    rendered = yaml.dump(reusable)
    assert "ghcr.io" in rendered, "publish only to GitHub Container Registry"
    assert "GITHUB_TOKEN" in rendered or "github.token" in rendered, (
        "use the ephemeral repository token rather than a long-lived registry secret"
    )
    secret_names = set(re.findall(r"secrets\.([A-Za-z_][A-Za-z0-9_]*)", rendered))
    assert secret_names.issubset({"GITHUB_TOKEN"}), (
        f"no custom long-lived delivery secret is needed: {sorted(secret_names)}"
    )
    has_push = "docker push" in rendered or re.search(
        r"push:\s*[\"']?true", rendered, re.IGNORECASE
    )
    assert has_push, "the privileged path must publish the validated image"
    assert "attest" in rendered.lower() and "subject-digest" in rendered, (
        "attest the exact published digest rather than only a mutable tag"
    )

    all_jobs = {**caller_jobs, **jobs}
    _assert_immutable_actions(all_jobs)
