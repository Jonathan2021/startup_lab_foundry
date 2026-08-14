"""Hosted-service integration for the real PostgreSQL CLI path."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any
from uuid import uuid4

import pytest

DATABASE_URL = os.environ.get("FOUNDRY_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg://")),
    reason="requires an explicit PostgreSQL FOUNDRY_DATABASE_URL",
)


def _run_foundry(*arguments: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "startup_foundry", *arguments],
        check=False,
        capture_output=True,
        env=os.environ.copy(),
        text=True,
    )
    assert completed.returncode == 0, (
        f"Foundry exited {completed.returncode}\n"
        f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )
    parsed = json.loads(completed.stdout)
    assert isinstance(parsed, dict)
    return parsed


def test_create_and_reconstruct_venture_on_postgresql() -> None:
    venture_id = f"ci-{uuid4().hex}"
    created = _run_foundry(
        "venture",
        "create",
        "--id",
        venture_id,
        "--name",
        "CI PostgreSQL Venture",
        "--objective",
        "Prove the hosted service-container path.",
        "--stage",
        "discovery",
    )

    shown = _run_foundry("venture", "show", "--id", venture_id)

    assert created["id"] == venture_id
    assert shown["venture"] == created
