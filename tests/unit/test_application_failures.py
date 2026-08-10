"""Application rollback and command error-boundary tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from startup_foundry.application import FoundryApplication
from startup_foundry.cli import main
from startup_foundry.domain import VentureStage, WorkItem, WorkItemKind
from startup_foundry.errors import ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory


def test_failed_experiment_command_rolls_back_its_work_item(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'application.db'}"
    upgrade_database(database_url)
    engine = create_db_engine(database_url)
    application = FoundryApplication(create_session_factory(engine))
    application.create_venture(
        venture_id="venture-1",
        name="Venture",
        objective="Test atomic experiment creation.",
        stage=VentureStage.DISCOVERY,
    )

    with pytest.raises(ValidationError, match="experiment work requires"):
        application.add_work_item(
            work_item_id="work-invalid",
            venture_id="venture-1",
            title="Invalid experiment",
            kind=WorkItemKind.EXPERIMENT,
            decision_id=None,
            acceptance_criteria=None,
            method=None,
            success_criteria=None,
            failure_criteria=None,
            assumption_ids=[],
        )

    with Session(engine) as session:
        assert session.get(WorkItem, "work-invalid") is None
    engine.dispose()


def test_corrupt_sqlite_is_reported_without_traceback_or_replacement(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    database = tmp_path / "corrupt.db"
    original = b"this is not sqlite"
    database.write_bytes(original)

    status = main(["--store", str(database), "venture", "show", "--id", "v1"])

    captured = capsys.readouterr()
    assert status != 0
    assert captured.out == ""
    assert "traceback" not in captured.err.lower()
    assert "database" in captured.err.lower()
    assert database.read_bytes() == original


def test_blank_required_input_fails_before_database_creation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    database = tmp_path / "must-not-exist.db"
    status = main(
        [
            "--store",
            str(database),
            "venture",
            "create",
            "--id",
            "v1",
            "--name",
            "   ",
            "--objective",
            "Valid objective",
            "--stage",
            "discovery",
        ]
    )

    captured = capsys.readouterr()
    assert status == 2
    assert captured.out == ""
    assert "name" in captured.err
    assert not database.exists()


def test_expected_error_logs_correlation_without_sensitive_payload(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    database = tmp_path / "logging.db"
    arguments = [
        "--store",
        str(database),
        "venture",
        "create",
        "--id",
        "venture-1",
        "--name",
        "Venture",
        "--objective",
        "secret-like-value-must-not-be-logged",
        "--stage",
        "discovery",
    ]
    assert main(arguments) == 0
    capsys.readouterr()

    assert main(arguments) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "correlation_id=" in captured.err
    assert "ConflictError" in captured.err
    assert "secret-like-value-must-not-be-logged" not in captured.err
    assert "Traceback" not in captured.err
