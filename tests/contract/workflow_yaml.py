"""Shared YAML accessors for the CI and delivery workflow contract tests."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FOUNDRY_ROOT = Path(__file__).parents[2]
SHA_PIN = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")


def as_mapping(value: Any, label: str) -> dict[str, Any]:
    assert isinstance(value, dict), f"{label} must be a YAML mapping"
    return value


def as_sequence(value: Any, label: str) -> list[Any]:
    if isinstance(value, str):
        return [value]
    assert isinstance(value, list), f"{label} must be a YAML sequence"
    return value


def load_yaml(path: Path, label: str) -> dict[str, Any]:
    """Parse with BaseLoader so `on`, booleans and versions stay literal strings."""
    assert path.is_file(), f"{label} does not exist: {path.relative_to(FOUNDRY_ROOT)}"
    parsed = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    return as_mapping(parsed, label)


def workflow_jobs(workflow: dict[str, Any]) -> dict[str, Any]:
    return as_mapping(workflow.get("jobs"), "jobs")


def job_steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    """Steps of a job; a job that calls a reusable workflow has none."""
    if "steps" not in job:
        assert "uses" in job, "job must define steps or call a reusable workflow"
        return []
    raw_steps = as_sequence(job.get("steps"), "job steps")
    return [as_mapping(step, "workflow step") for step in raw_steps]


def job_commands(job: dict[str, Any]) -> str:
    return "\n".join(str(step.get("run", "")) for step in job_steps(job))


def external_actions(jobs: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """(uses, step) for every marketplace action; local and docker:// excluded."""
    actions: list[tuple[str, dict[str, Any]]] = []
    for job_id, raw_job in jobs.items():
        job = as_mapping(raw_job, f"job {job_id}")
        for step in job_steps(job):
            uses = str(step.get("uses", ""))
            if uses and not uses.startswith(("./", "docker://")):
                actions.append((uses, step))
    return actions
