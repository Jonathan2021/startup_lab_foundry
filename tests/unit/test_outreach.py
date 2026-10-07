"""Draft history, exact manual outcomes and bounded attachment access."""

import hashlib
import socket
from email import policy
from email.parser import BytesParser

import pytest
from pydantic import ValidationError as InputError
from sqlalchemy import func, select

from startup_foundry.domain import (
    ActionAttempt,
    Artifact,
    ArtifactKind,
    ExternalAction,
    Venture,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.outreach import DraftInput, OutcomeInput, OutreachService
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory


@pytest.fixture
def outreach(tmp_path):
    url = f"sqlite:///{tmp_path / 'drafts.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    p = PortfolioService(factory)
    p.create_idea(IdeaDraft(title="Receipt", description="Review sample"), idea_id="n")
    p.promote_idea("n", venture_id="receipt")
    root = tmp_path / "attachments"
    root.mkdir()
    with factory() as s:
        workspace = s.get(Venture, "receipt").workspace_id
    yield OutreachService(factory, [root]), factory, root, workspace
    engine.dispose()


def payload(**changes):
    return DraftInput.model_validate(
        {
            "purpose": "Review fictional sample",
            "subject": "Avis sur exercice",
            "body_text": "Bonjour\nRésumé fictif — aucune certification.\nMerci !",
            "language": "fr",
            "tone": "formal",
            **changes,
        }
    )


def test_edit_export_exact_outcome_no_network_and_stale_conflict(outreach, monkeypatch):
    service, factory, root, workspace = outreach
    monkeypatch.setattr(
        socket, "create_connection", lambda *a, **k: pytest.fail("network forbidden")
    )
    draft = service.create("receipt", payload(), request_key="test")
    assert service.create("receipt", payload(), request_key="test")["id"] == draft["id"]
    assert draft["unresolved_fields"] == ["recipient", "sender"]
    edited = service.revise(
        draft["id"],
        payload(to=["receiver@example.invalid"], body_text="Bonjour\nRévision 2"),
        expected_version=draft["version"],
        actor="operator",
    )
    with pytest.raises(ConflictError):
        service.revise(
            draft["id"], payload(), expected_version=draft["version"], actor="operator"
        )
    assert edited["draft_revision"] == 2
    exported = service.export(draft["id"], format="eml")
    assert b"X-Unsent: 1" in exported and b"Revision: 2" in exported
    outcome = service.record_outcome(
        draft["id"],
        OutcomeInput(
            kind="sent_manually",
            draft_revision=1,
            actor="human",
            stated_at="2026-10-04T14:00:00+02:00",
            summary="Sent earlier revision manually",
        ),
    )
    assert outcome["attribution"] == "user-reported"
    restored = OutreachService(factory, [root]).show(draft["id"])
    assert len(restored["history"]) == 2 and restored["state"] == "Draft"
    assert restored["outcomes"][0]["draft_revision"] == 1
    with factory() as s:
        assert s.scalar(select(func.count()).select_from(ActionAttempt)) == 0
        assert s.get(ExternalAction, draft["id"]).approval_required


@pytest.mark.parametrize(
    "changes",
    [
        {"subject": "Hello\r\nBcc: leak@example.invalid"},
        {"to": ["x@example.invalid\nCc: y@example.invalid"]},
        {"sender_identity": "x\r\nInjected"},
        {"language": "unsafe"},
        {"delivery_mode": "smtp"},
    ],
)
def test_header_injection_and_transport_rejected(changes):
    with pytest.raises((InputError, ValidationError)):
        payload(**changes)


def test_attachment_scope_bytes_digest_and_symlink_rejection(outreach, tmp_path):
    service, factory, root, workspace = outreach
    sample = root / "sample.txt"
    sample.write_text("Fictional example\n")
    with factory.begin() as s:
        s.add(
            Artifact(
                id="sample",
                workspace_id=workspace,
                kind=ArtifactKind.DOCUMENT,
                name="Sample",
                location=str(sample),
                content_digest=hashlib.sha256(sample.read_bytes()).hexdigest(),
                media_type="text/plain",
            )
        )
    draft = service.create(
        "receipt", payload(attachment_artifact_ids=["sample"]), request_key="sample"
    )
    message = BytesParser(policy=policy.default).parsebytes(
        service.export(draft["id"], format="eml")
    )
    assert (
        next(message.iter_attachments()).get_payload(decode=True) == sample.read_bytes()
    )
    sample.write_text("Changed bytes")
    with pytest.raises(ValidationError):
        service.export(draft["id"], format="eml")
    outside = tmp_path / "private.txt"
    outside.write_text("Never export")
    link = root / "linked.txt"
    link.symlink_to(outside)
    with factory.begin() as s:
        s.add(
            Artifact(
                id="link",
                workspace_id=workspace,
                kind=ArtifactKind.DOCUMENT,
                name="Linked",
                location=str(link),
                content_digest=hashlib.sha256(outside.read_bytes()).hexdigest(),
            )
        )
    draft = service.create(
        "receipt", payload(attachment_artifact_ids=["link"]), request_key="link"
    )
    with pytest.raises(ValidationError):
        service.export(draft["id"], format="eml")
    with pytest.raises(ReferenceError):
        service.create(
            "receipt",
            payload(attachment_artifact_ids=["missing"]),
            request_key="missing",
        )
