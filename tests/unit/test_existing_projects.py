"""Existing-project checkpoints retain history without filesystem access."""

import pytest

from startup_foundry.errors import ConflictError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.projects import ExistingProjectInput, ExistingProjectService
from startup_foundry.repository import create_db_engine, create_session_factory


def test_existing_intake_repeat_revision_and_missing_reference(tmp_path):
    url = f"sqlite:///{tmp_path / 'project.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    p = PortfolioService(factory)
    p.create_idea(
        IdeaDraft(title="Existing", description="Already code"), idea_id="P046"
    )
    service = ExistingProjectService(factory)
    payload = ExistingProjectInput(
        venture_id="project",
        source_idea_id="P046",
        name="Coopain",
        description="Retain prototype",
        product_maturity="prototype",
        reason_paused="Payer unknown",
        next_bounded_test="Review employer workflow",
        author="test",
        repositories=[
            {"local_reference": "/missing/path", "observed_at": "2026-10-04T10:00:00Z"}
        ],
    )
    first = service.intake(payload)
    assert service.intake(payload)["unchanged"]
    changed = ExistingProjectInput.model_validate(
        {
            **payload.model_dump(mode="json"),
            "description": "Changed scope",
            "expected_review_revision": 1,
        }
    )
    service.intake(changed)
    assert len(service.show("project")["history"]) == 2
    assert service.show("project")["history"][-1]["id"] == first["artifact_id"]
    with pytest.raises(ConflictError):
        service.intake(changed.model_copy(update={"description": "Stale change"}))
    assert len(service.show("project")["history"]) == 2
    assert p.show_idea("P046")["ventures"] == ["project"]
    engine.dispose()
