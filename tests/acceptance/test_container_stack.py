"""End-to-end acceptance checks for the containerized Foundry stack."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import uuid4

import pytest

FOUNDRY_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = FOUNDRY_ROOT / "docker-compose.yaml"
DOCKERFILE = FOUNDRY_ROOT / "Dockerfile"
DOCKERIGNORE = FOUNDRY_ROOT / ".dockerignore"
REQUIRED_SERVICES = frozenset({"db", "migrate", "foundry"})


@dataclass(frozen=True, slots=True)
class ComposeProject:
    name: str
    environment: dict[str, str] = field(repr=False)
    password: str = field(repr=False)


def _redact(value: str, secrets_to_redact: Sequence[str]) -> str:
    for secret in secrets_to_redact:
        value = value.replace(secret, "<redacted>")
    return value


def _run(
    command: Sequence[str],
    *,
    environment: Mapping[str, str],
    secrets_to_redact: Sequence[str] = (),
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=FOUNDRY_ROOT,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
    )
    if check and completed.returncode != 0:
        rendered_command = " ".join(command)
        stdout = _redact(completed.stdout, secrets_to_redact)
        stderr = _redact(completed.stderr, secrets_to_redact)
        pytest.fail(
            f"command failed ({completed.returncode}): {rendered_command}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    return completed


def _compose_command(project_name: str, *arguments: str) -> list[str]:
    return [
        "docker",
        "compose",
        "--progress",
        "quiet",
        "--project-name",
        project_name,
        "--file",
        str(COMPOSE_FILE),
        "--profile",
        "cli",
        *arguments,
    ]


@pytest.fixture(scope="module")
def compose_project() -> Iterator[ComposeProject]:
    password = secrets.token_urlsafe(24)
    environment = dict(os.environ)
    environment.update(
        {
            "POSTGRES_DB": "foundry_acceptance",
            "POSTGRES_USER": "foundry_acceptance",
            "POSTGRES_PASSWORD": password,
            "FOUNDRY_DATABASE_URL": (
                "postgresql+psycopg://foundry_acceptance:"
                f"{password}@db:5432/foundry_acceptance"
            ),
            "FOUNDRY_DEBUG": "false",
            "FOUNDRY_SQL_ECHO": "false",
        }
    )
    project_name = f"foundry-acceptance-{uuid4().hex[:12]}"
    with TemporaryDirectory(prefix=f"{project_name}-") as temporary_directory:
        env_file = Path(temporary_directory) / "acceptance.env"
        env_file.write_text(
            "\n".join(
                f"{name}={environment[name]}"
                for name in (
                    "POSTGRES_DB",
                    "POSTGRES_USER",
                    "POSTGRES_PASSWORD",
                    "FOUNDRY_DATABASE_URL",
                    "FOUNDRY_DEBUG",
                    "FOUNDRY_SQL_ECHO",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        environment["FOUNDRY_ENV_FILE"] = str(env_file)
        project = ComposeProject(project_name, environment, password)
        try:
            yield project
        finally:
            if COMPOSE_FILE.exists() and shutil.which("docker") is not None:
                _run(
                    _compose_command(
                        project_name,
                        "down",
                        "--volumes",
                        "--remove-orphans",
                        "--timeout",
                        "5",
                    ),
                    environment=environment,
                    secrets_to_redact=(password,),
                    check=False,
                )


@pytest.fixture(scope="module")
def compose_config(
    compose_project: ComposeProject,
) -> dict[str, Any]:
    if shutil.which("docker") is None:
        pytest.fail("Docker is required for container-stack acceptance")
    missing = [
        str(path.relative_to(FOUNDRY_ROOT))
        for path in (DOCKERFILE, DOCKERIGNORE, COMPOSE_FILE)
        if not path.is_file()
    ]
    if missing:
        pytest.fail(f"learner-owned container files are missing: {', '.join(missing)}")
    completed = _run(
        _compose_command(compose_project.name, "config", "--format", "json"),
        environment=compose_project.environment,
        secrets_to_redact=(compose_project.password,),
    )
    loaded = json.loads(_redact(completed.stdout, (compose_project.password,)))
    assert isinstance(loaded, dict)
    return loaded


def _services(config: Mapping[str, Any]) -> Mapping[str, Any]:
    services = config.get("services")
    assert isinstance(services, dict), "Compose config must define services"
    return services


def _dependency_condition(service: Mapping[str, Any], dependency: str) -> str | None:
    dependencies = service.get("depends_on", {})
    assert isinstance(dependencies, dict)
    dependency_config = dependencies.get(dependency, {})
    assert isinstance(dependency_config, dict)
    condition = dependency_config.get("condition")
    return condition if isinstance(condition, str) else None


def test_compose_declares_safe_ordered_cli_topology(
    compose_config: Mapping[str, Any],
) -> None:
    services = _services(compose_config)
    assert REQUIRED_SERVICES <= services.keys()

    db = services["db"]
    migrate = services["migrate"]
    foundry = services["foundry"]
    assert isinstance(db, dict)
    assert isinstance(migrate, dict)
    assert isinstance(foundry, dict)

    assert "postgres" in str(db.get("image", "")).lower()
    assert isinstance(db.get("healthcheck"), dict)
    assert not db.get("ports"), "the learning database must not publish a host port"
    mounts = db.get("volumes", [])
    assert any(
        isinstance(mount, dict)
        and mount.get("type") == "volume"
        and str(mount.get("target", "")).startswith("/var/lib/postgresql")
        for mount in mounts
    ), "PostgreSQL data must use a named volume"

    assert _dependency_condition(migrate, "db") == "service_healthy"
    assert (
        _dependency_condition(foundry, "migrate")
        == "service_completed_successfully"
    )
    assert "build" in foundry, "a fresh clone must be able to build Foundry"
    assert foundry.get("image"), "declare a stable local image reference"
    assert migrate.get("image") == foundry.get("image"), (
        "migration and CLI services must use the same application image"
    )


def test_runtime_image_is_non_root_lean_and_does_not_bake_secrets(
    compose_config: Mapping[str, Any],
    compose_project: ComposeProject,
) -> None:
    environment = compose_project.environment
    password = compose_project.password
    compose = partial(_compose_command, compose_project.name)
    foundry_service = _services(compose_config)["foundry"]
    assert isinstance(foundry_service, dict)
    image_name = foundry_service.get("image")
    assert isinstance(image_name, str) and image_name

    _run(
        compose("build", "foundry"),
        environment=environment,
        secrets_to_redact=(password,),
    )
    uid = _run(
        compose("run", "--rm", "--no-deps", "--entrypoint", "id", "foundry", "-u"),
        environment=environment,
        secrets_to_redact=(password,),
    ).stdout.strip()
    assert uid.isdigit() and uid != "0", "the runtime image must not run as root"

    help_result = _run(
        compose(
            "run",
            "--rm",
            "--no-deps",
            "--entrypoint",
            "foundry",
            "foundry",
            "--help",
        ),
        environment=environment,
        secrets_to_redact=(password,),
    )
    assert "Foundry CLI" in help_result.stdout

    modules_result = _run(
        compose(
            "run",
            "--rm",
            "--no-deps",
            "--entrypoint",
            "python",
            "foundry",
            "-c",
            (
                "import importlib.util,json;"
                "print(json.dumps({n:importlib.util.find_spec(n) is not None "
                "for n in ('startup_foundry','pytest','ruff','mypy')}))"
            ),
        ),
        environment=environment,
        secrets_to_redact=(password,),
    )
    modules = json.loads(modules_result.stdout)
    assert modules == {
        "startup_foundry": True,
        "pytest": False,
        "ruff": False,
        "mypy": False,
    }

    image_environment = _run(
        [
            "docker",
            "image",
            "inspect",
            image_name,
            "--format",
            "{{json .Config.Env}}",
        ],
        environment=environment,
        secrets_to_redact=(password,),
    ).stdout
    assert password not in image_environment
    assert environment["FOUNDRY_DATABASE_URL"] not in image_environment


def test_one_command_migrates_cli_and_postgres_then_volume_persists(
    compose_config: Mapping[str, Any],
    compose_project: ComposeProject,
) -> None:
    del compose_config
    environment = compose_project.environment
    password = compose_project.password
    compose = partial(_compose_command, compose_project.name)
    common = {
        "environment": environment,
        "secrets_to_redact": (password,),
    }

    _run(compose("up", "--build", "--detach", "--wait", "db"), **common)
    _run(compose("run", "--rm", "migrate"), **common)
    migration_revision = _run(
        compose(
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            environment["POSTGRES_USER"],
            "-d",
            environment["POSTGRES_DB"],
            "-Atc",
            "SELECT version_num FROM alembic_version",
        ),
        **common,
    ).stdout.strip()
    assert migration_revision, "the one-shot migration must reach Alembic head"
    _run(
        compose("down", "--volumes", "--remove-orphans", "--timeout", "5"),
        **common,
    )

    created = _run(
        compose(
            "run",
            "--build",
            "--rm",
            "foundry",
            "venture",
            "create",
            "--id",
            "venture-container-contract",
            "--name",
            "Container Contract",
            "--objective",
            "Prove migration, networking, and persistence.",
            "--stage",
            "build",
        ),
        **common,
    )
    payload = json.loads(created.stdout)
    assert payload["id"] == "venture-container-contract"

    database_container = _run(compose("ps", "--quiet", "db"), **common).stdout.strip()
    assert database_container
    health = _run(
        [
            "docker",
            "container",
            "inspect",
            database_container,
            "--format",
            "{{.State.Health.Status}}",
        ],
        **common,
    ).stdout.strip()
    assert health == "healthy"

    command_revision = _run(
        compose(
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            environment["POSTGRES_USER"],
            "-d",
            environment["POSTGRES_DB"],
            "-Atc",
            "SELECT version_num FROM alembic_version",
        ),
        **common,
    ).stdout.strip()
    assert command_revision == migration_revision

    _run(compose("down", "--remove-orphans", "--timeout", "5"), **common)

    shown = _run(
        compose(
            "run",
            "--rm",
            "foundry",
            "venture",
            "show",
            "--id",
            "venture-container-contract",
        ),
        **common,
    )
    restored = json.loads(shown.stdout)
    assert restored["venture"]["id"] == "venture-container-contract"


def test_postgres_rejects_an_orphan_without_leaving_a_row(
    compose_project: ComposeProject,
) -> None:
    """Representative service test: exercise a real PostgreSQL constraint."""

    environment = compose_project.environment
    compose = partial(_compose_command, compose_project.name)
    common = {
        "environment": environment,
        "secrets_to_redact": (compose_project.password,),
    }
    _run(compose("up", "--detach", "--wait", "db"), **common)
    _run(compose("run", "--rm", "migrate"), **common)

    sql = """
        INSERT INTO ventures (
            workspace_id, objective, stage, budget_currency, id,
            created_at, updated_at, version_id
        ) VALUES (
            'missing-workspace', 'must fail', 'build', 'EUR',
            'orphan-venture', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1
        );
    """
    rejected = _run(
        compose(
            "exec",
            "-T",
            "db",
            "psql",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            environment["POSTGRES_USER"],
            "-d",
            environment["POSTGRES_DB"],
            "-c",
            sql,
        ),
        **common,
        check=False,
    )
    assert rejected.returncode != 0
    assert "foreign key constraint" in rejected.stderr.lower()

    count = _run(
        compose(
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            environment["POSTGRES_USER"],
            "-d",
            environment["POSTGRES_DB"],
            "-Atc",
            "SELECT count(*) FROM ventures WHERE id = 'orphan-venture'",
        ),
        **common,
    ).stdout.strip()
    assert count == "0"
