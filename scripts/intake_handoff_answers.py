"""Explicit October 4 inbox intake; safe to repeat, no Markdown action execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sqlalchemy import select

from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    ConfidenceLevel,
    Evidence,
    EvidenceArtifact,
    EvidenceKind,
    Idea,
    IdeaRelation,
    IdeaRelationKind,
    ReferenceSource,
    Venture,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
)
from startup_foundry.portfolio import PortfolioService, stable_id
from startup_foundry.repository import SessionFactory, UnitOfWork

TARGETS = {
    "R001": (
        "N008",
        "v-route-repair",
        "Specify maximum riding time and must-keep areas.",
    ),
    "R002": (
        "N001",
        "v-physical",
        "Obtain one observable task with competent labels, or retain field-data hold.",
    ),
    "R003": (
        "N003",
        "v-receipt",
        "Choose a receiving practitioner and obtain review of the fictional sample.",
    ),
    "R004": ("D002", "v-foundry", ""),
}


def intake(factory: SessionFactory, inbox: Path) -> dict[str, object]:
    content = inbox.read_text(encoding="utf-8")
    file_digest = hashlib.sha256(inbox.read_bytes()).hexdigest()
    portfolio = PortfolioService(factory)
    portfolio.promote_idea("P046", venture_id="v-coopain")
    portfolio.promote_idea("P023", venture_id="v-sports-ranking")
    portfolio.promote_idea("P103", venture_id="v-sports-session")
    outputs = []
    for request, (idea_id, venture_id, followup) in TARGETS.items():
        # Only these four explicitly named sections; attachments are data.
        section = content.split("## " + request + " — ", 1)[1].split("\n## ", 1)[0]
        digest = hashlib.sha256(section.encode()).hexdigest()
        if request in ("R002", "R003"):
            portfolio.promote_idea(idea_id, venture_id=venture_id)
        with UnitOfWork(factory) as unit:
            session = unit.session
            assert session is not None
            idea = session.get(Idea, idea_id)
            assert idea is not None
            venture = session.get(Venture, venture_id)
            assert venture is not None
            workspace = venture.workspace_id
            identity = stable_id(f"inbox:{request}:{digest}:{workspace}")
            existing = session.get(Artifact, identity)
            if existing:
                outputs.append(
                    {
                        "request": request,
                        "artifact_id": identity,
                        "state": "already_reviewed",
                    }
                )
                continue
            artifact = Artifact(
                id=identity,
                workspace_id=workspace,
                kind=ArtifactKind.DOCUMENT,
                name=f"{request} answer receipt",
                location=str(inbox),
                content_digest=digest,
                semantic_version="inbox-answer/v1",
                metadata_json={
                    "schema_version": "inbox-answer/v1",
                    "request_id": request,
                    "file_sha256": file_digest,
                    "section_sha256": digest,
                    "reported_on": "2026-10-04",
                    "source_section": request,
                    "text": section,
                    "review_state": "reviewed",
                    "limits": "User-reported; no interviews, consent or send approval.",
                },
            )
            session.add(artifact)
            session.flush()
            evidence = Evidence(
                id=stable_id(identity + ":evidence"),
                workspace_id=workspace,
                kind=EvidenceKind.DOCUMENT,
                confidence=ConfidenceLevel.MEDIUM,
                summary=(
                    f"{request}: supplied inbox answer reviewed; attributed to user, "
                    "not independent validation."
                ),
                details=json.dumps(
                    {
                        "artifact_id": identity,
                        "reported_on": "2026-10-04",
                        "ride_date": "2026-09-16" if request == "R001" else None,
                        "permission": "Drafts only; no sending"
                        if request == "R004"
                        else None,
                    }
                ),
                captured_by="agent:handoff-intake-v1",
            )
            session.add(evidence)
            session.flush()
            session.add(
                EvidenceArtifact(
                    evidence_id=evidence.id, artifact_id=identity, role="source answer"
                )
            )
            # Explicit supplied-answer criteria; follow-ups remain separately blocked.
            task_id = stable_id("inbox-question:" + request + ":" + workspace)
            task = session.get(WorkItem, task_id)
            if task is None:
                task = WorkItem(
                    id=task_id,
                    workspace_id=workspace,
                    title=request + " supplied answer review",
                    kind=WorkItemKind.INVESTIGATION,
                    owner="human",
                    status=WorkItemStatus.DONE,
                    acceptance_criteria=(
                        "Supplied answer reviewed with attribution and limitations."
                    ),
                    description=(
                        "Answer now available; historical absent-input hold superseded."
                    ),
                )
                session.add(task)
            else:
                task.status = WorkItemStatus.DONE
                task.blocked_reason = None
            if followup:
                next_id = stable_id("inbox-followup:" + request + ":" + workspace)
                if session.get(WorkItem, next_id) is None:
                    session.add(
                        WorkItem(
                            id=next_id,
                            workspace_id=workspace,
                            title=followup,
                            question=followup,
                            description=(
                                "See requests/2026-10-04-followups.md. Unknown is "
                                "acceptable."
                            ),
                            kind=WorkItemKind.INVESTIGATION,
                            status=WorkItemStatus.BLOCKED,
                            owner="human",
                            blocked_reason="human_input",
                            acceptance_criteria=followup,
                        )
                    )
            outputs.append(
                {
                    "request": request,
                    "artifact_id": identity,
                    "evidence_id": evidence.id,
                    "state": "reviewed",
                }
            )
    with UnitOfWork(factory) as unit:
        session = unit.session
        assert session is not None
        relation = session.scalar(
            select(IdeaRelation).where(
                IdeaRelation.source_idea_id == "P103",
                IdeaRelation.target_idea_id == "P023",
                IdeaRelation.kind == IdeaRelationKind.COMBINED_WITH,
            )
        )
        if relation is None:
            session.add(
                IdeaRelation(
                    source_idea_id="P103",
                    target_idea_id="P023",
                    kind=IdeaRelationKind.COMBINED_WITH,
                    rationale=(
                        "Shared friends-group comparison; ranking and rotating-team "
                        "jobs stay distinct."
                    ),
                )
            )
    with UnitOfWork(factory) as unit:
        session = unit.session
        assert session is not None
        venture = session.get(Venture, "v-foundry")
        assert venture is not None
        for path in sorted((inbox.parents[1] / "docs/sources").glob("*.csv")):
            content_sha = hashlib.sha256(path.read_bytes()).hexdigest()
            source = session.scalar(
                select(ReferenceSource).where(
                    ReferenceSource.content_digest == content_sha
                )
            )
            if source is None:
                raise ValueError("Expected retained CSV source: " + path.name)
            identity = stable_id(
                "handoff-availability:" + content_sha + ":" + str(path.resolve())
            )
            if session.get(Artifact, identity) is None:
                session.add(
                    Artifact(
                        id=identity,
                        workspace_id=venture.workspace_id,
                        kind=ArtifactKind.DOCUMENT,
                        name="Source availability",
                        location=str(path.resolve()),
                        content_digest=content_sha,
                        metadata_json={
                            "source_id": source.id,
                            "availability_only": True,
                            "checked_on": "2026-10-04",
                        },
                    )
                )
    return {"file_sha256": file_digest, "answers": outputs}


if __name__ == "__main__":
    from startup_foundry.config import load_settings
    from startup_foundry.repository import create_db_engine, create_session_factory

    engine = create_db_engine(load_settings().database_url)
    try:
        print(
            json.dumps(
                intake(
                    create_session_factory(engine),
                    Path(__file__).resolve().parents[1] / "requests/INBOX.md",
                ),
                indent=2,
            )
        )
    finally:
        engine.dispose()
