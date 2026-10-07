"""Builtin module preferences preserve data and report unknown business state."""

import pytest

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import VentureStage
from startup_foundry.errors import ConflictError, ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.workspace_modules import (
    ConfigInput,
    MetricsInput,
    WorkspaceModuleService,
)


def test_config_metrics_unknown_and_no_forecast_as_actual(tmp_path):
    url = f"sqlite:///{tmp_path / 'modules.db'}"
    upgrade_database(url)
    factory = create_session_factory(create_db_engine(url))
    FoundryApplication(factory).create_venture(
        venture_id="coopain",
        name="Coopain",
        objective="Test",
        stage=VentureStage.DISCOVERY,
    )
    service = WorkspaceModuleService(factory)
    assert service.show("coopain")["metrics"] is None
    saved = service.configure(
        "coopain",
        ConfigInput(
            expected_revision=0, actor="operator", modules=["software", "outreach"]
        ),
    )
    assert saved["revision"] == 1
    with pytest.raises(ConflictError):
        service.configure(
            "coopain", ConfigInput(expected_revision=0, actor="operator", modules=[])
        )
    service.metrics(
        "coopain",
        MetricsInput(
            expected_revision=0,
            actor="operator",
            revenue=None,
            costs=0,
            currency="EUR",
            period="2026-10",
            source="Operator report",
        ),
    )
    service.configure(
        "coopain", ConfigInput(expected_revision=1, actor="operator", modules=[])
    )
    detail = service.show("coopain")
    assert detail["metrics"]["revenue"] is None and detail["metrics"]["costs"] == "0"
    assert detail["config"]["modules"] == []
    with pytest.raises(ValidationError):
        service.configure(
            "coopain",
            ConfigInput(expected_revision=2, actor="operator", modules=["suppliers"]),
        )
