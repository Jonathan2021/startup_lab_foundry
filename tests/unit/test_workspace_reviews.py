"""Review history, stale updates and workspace boundaries."""

import pytest
from sqlalchemy import select

from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    Disposition,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
)
from startup_foundry.errors import ConflictError, ReferenceError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.reviews import ReviewInput, ReviewService


@pytest.fixture
def services(tmp_path):
    url = f"sqlite:///{tmp_path / 'review.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    portfolio = PortfolioService(factory)
    a = portfolio.create_idea(
        IdeaDraft(title="Prototype", description="Business uncertainty"), idea_id="a"
    )
    b = portfolio.create_idea(
        IdeaDraft(title="Other", description="Different workspace"), idea_id="b"
    )
    yield ReviewService(factory), factory, a, b, url
    engine.dispose()


def payload(workspace, **kwargs):
    return ReviewInput(
        workspace_id=workspace,
        expected_revision=0,
        investigation_stage="business_validation",
        product_maturity="prototype",
        disposition="hold",
        reason="Buyer unknown",
        author="operator",
        next_action="Interview buyer",
        **kwargs,
    )


def test_history_conflict_reopen_and_restart(services):
    service, factory, a, _, url = services
    first = service.append(payload(a["workspace_id"]))
    assert (
        first["product_maturity"] == "prototype"
        and first["work_state"] == "not_scheduled"
    )
    with pytest.raises(ConflictError):
        service.append(payload(a["workspace_id"]))
    service.append(
        payload(a["workspace_id"]).model_copy(
            update={"expected_revision": 1, "disposition": Disposition.DROPPED}
        )
    )
    third = service.append(
        payload(a["workspace_id"]).model_copy(
            update={
                "expected_revision": 2,
                "disposition": Disposition.PURSUE,
                "reason": "Reopen: a buyer offered to review",
            }
        )
    )
    assert third["revision"] == 3
    engine = create_db_engine(url)
    try:
        assert (
            len(
                ReviewService(create_session_factory(engine)).show(a["workspace_id"])[
                    "history"
                ]
            )
            == 3
        )
    finally:
        engine.dispose()


def test_cross_workspace_reference_rejected_and_legacy_repeat_preserves_new(services):
    service, factory, a, b, _ = services
    with factory.begin() as s:
        artifact = Artifact(
            id="other",
            workspace_id=b["workspace_id"],
            kind=ArtifactKind.DOCUMENT,
            name="Ref",
            location="db:ref",
        )
        work = WorkItem(
            id="work",
            workspace_id=b["workspace_id"],
            kind=WorkItemKind.INVESTIGATION,
            status=WorkItemStatus.BLOCKED,
            title="Question",
        )
        s.add_all([artifact, work])
    for key, value in [("source_artifact_id", "other"), ("next_work_item_id", "work")]:
        with pytest.raises(ReferenceError):
            service.append(payload(a["workspace_id"], **{key: value}))
    with factory.begin() as s:
        s.add(
            Artifact(
                workspace_id=a["workspace_id"],
                kind=ArtifactKind.REPORT,
                name="Campaign disposition",
                location="db:campaign",
                metadata_json={
                    "disposition": "HOLD_DOMAIN_ACCESS",
                    "rationale": "Need records",
                },
            )
        )
    assert service.import_legacy()["imported"] == 1
    service.append(
        payload(a["workspace_id"]).model_copy(
            update={
                "expected_revision": 1,
                "disposition": Disposition.PURSUE,
                "reason": "New evidence",
            }
        )
    )
    assert service.import_legacy()["imported"] == 0
    assert service.show(a["workspace_id"])["current"]["disposition"] == "pursue"
    with factory() as s:
        assert len(list(s.scalars(select(Artifact)))) == 2


def test_new_answer_is_visible_without_changing_review_state(services):
    import hashlib

    service, factory, a, _, _ = services
    content = "## R001 — question\nMy answer:\nnew files supplied\n"
    section = content.split("## R001 — ", 1)[1]
    with factory.begin() as s:
        s.add(
            Artifact(
                workspace_id=a["workspace_id"],
                kind=ArtifactKind.DOCUMENT,
                name="R001 answer receipt",
                location="local:INBOX",
                metadata_json={
                    "request_id": "R001",
                    "section_sha256": hashlib.sha256(section.encode()).hexdigest(),
                },
            )
        )
    service.append(payload(a["workspace_id"]))
    assert service.inbox_status(content)[0]["state"] == "Reviewed"
    assert (
        service.inbox_status(content + "Edited answer\n")[0]["state"]
        == "New answer awaiting review"
    )
    assert service.show(a["workspace_id"])["current"]["disposition"] == "hold"
