"""Editable manual email drafts. This module has no delivery transport."""

from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime
from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import (
    ActionRisk,
    Artifact,
    ArtifactKind,
    AuditEvent,
    ConfidenceLevel,
    Evidence,
    EvidenceArtifact,
    EvidenceKind,
    ExternalAction,
    ExternalActionStatus,
    Venture,
    WorkItem,
    WorkItemStatus,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.portfolio import stable_id
from startup_foundry.repository import SessionFactory, UnitOfWork
from startup_foundry.scoring import digest

JSON = dict[str, Any]


class DraftInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["outreach-draft/v1"] = "outreach-draft/v1"
    purpose: str = Field(min_length=1, max_length=5000)
    sender_identity: str = Field(default="", max_length=300)
    sender_status: Literal["unverified"] = "unverified"
    to: list[str] = Field(default_factory=list, max_length=30)
    cc: list[str] = Field(default_factory=list, max_length=30)
    bcc: list[str] = Field(default_factory=list, max_length=30)
    subject: str = Field(min_length=1, max_length=300)
    body_text: str = Field(min_length=1, max_length=50000)
    language: Literal["en", "fr"]
    tone: Literal["formal", "informal"]
    attachment_artifact_ids: list[str] = Field(default_factory=list, max_length=10)
    related_request_id: str | None = Field(default=None, max_length=100)
    source_evidence_ids: list[str] = Field(default_factory=list, max_length=30)
    delivery_mode: Literal["manual"] = "manual"

    @field_validator("subject", "sender_identity")
    @classmethod
    def header(cls, value: str) -> str:
        if any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise ValueError("Email headers cannot contain control characters")
        return value

    @field_validator("to", "cc", "bcc")
    @classmethod
    def addresses(cls, values: list[str]) -> list[str]:
        for value in values:
            if not re.fullmatch(
                r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}",
                value,
            ):
                raise ValueError(
                    "Use explicit email addresses, without names or header controls"
                )
        return list(dict.fromkeys(values))

    @field_validator("purpose", "subject", "body_text")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Draft text cannot be blank")
        return value


class OutcomeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["sent_manually", "reply"]
    draft_revision: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=200)
    stated_at: datetime
    summary: str = Field(min_length=1, max_length=20000)

    @field_validator("stated_at")
    @classmethod
    def aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Stated time needs a timezone")
        return value


class OutreachService:
    def __init__(self, factory: SessionFactory, approved_roots: list[Path]) -> None:
        self.factory = factory
        self.roots = [p.expanduser().resolve() for p in approved_roots]

    @staticmethod
    def _action(session: Session, identity: str) -> ExternalAction:
        action = session.get(ExternalAction, identity)
        if (
            action is None
            or action.action_type != "email"
            or action.adapter != "manual"
        ):
            raise ReferenceError("Manual email draft does not exist")
        return action

    @staticmethod
    def _validate_references(
        session: Session, workspace: str, payload: DraftInput
    ) -> None:
        for model, ids in [
            (Artifact, payload.attachment_artifact_ids),
            (Evidence, payload.source_evidence_ids),
        ]:
            for identity in ids:
                row = session.get(model, identity)
                if row is None or getattr(row, "workspace_id", None) != workspace:
                    raise ReferenceError(
                        "Draft references must belong to the same workspace"
                    )

    @staticmethod
    def _snapshot(
        session: Session, action: ExternalAction, actor: str, old_digest: str | None
    ) -> Artifact:
        revision = action.payload["draft_revision"]
        artifact = Artifact(
            id=stable_id(action.id + ":draft:" + str(revision)),
            workspace_id=action.workspace_id,
            kind=ArtifactKind.DOCUMENT,
            name="Outreach draft revision",
            location="db:external_actions/" + action.id,
            content_digest=action.payload_digest,
            semantic_version=str(revision),
            metadata_json={
                "action_id": action.id,
                "payload": action.payload,
                "revision": revision,
            },
        )
        session.add(artifact)
        session.flush()
        session.add(
            AuditEvent(
                workspace_id=action.workspace_id,
                entity_type="external_action",
                entity_id=action.id,
                event_type="draft_created" if old_digest is None else "draft_revised",
                actor=actor,
                payload={
                    "old_digest": old_digest,
                    "new_digest": action.payload_digest,
                    "artifact_id": artifact.id,
                    "revision": revision,
                },
            )
        )
        return artifact

    def create(
        self,
        venture_id: str,
        payload: DraftInput,
        *,
        request_key: str,
        actor: str = "local operator",
        work_item_id: str | None = None,
    ) -> JSON:
        if not request_key.strip() or len(request_key) > 160:
            raise ValidationError("Draft request key must be 1–160 characters")
        identity = stable_id("outreach:" + venture_id + ":" + request_key)
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            _, workspace = FoundryApplication._venture(session, venture_id)
            self._validate_references(session, workspace.id, payload)
            if work_item_id:
                work = session.get(WorkItem, work_item_id)
                if work is None or work.workspace_id != workspace.id:
                    raise ReferenceError("Work item belongs to a different workspace")
            body = {**payload.model_dump(mode="json"), "draft_revision": 1}
            existing = session.get(ExternalAction, identity)
            if existing:
                first = session.get(Artifact, stable_id(identity + ":draft:1"))
                if (
                    first is None
                    or first.content_digest != digest(body)
                    or existing.work_item_id != work_item_id
                ):
                    raise ConflictError(
                        "Request key was used with a different draft; choose a new key"
                    )
                return self._json(session, existing)
            action = ExternalAction(
                id=identity,
                workspace_id=workspace.id,
                work_item_id=work_item_id,
                action_type="email",
                adapter="manual",
                payload=body,
                payload_digest=digest(body),
                idempotency_key="manual-draft:" + identity,
                risk=ActionRisk.EXTERNAL_COMMUNICATION,
                approval_required=True,
                status=ExternalActionStatus.PROPOSED,
            )
            session.add(action)
            session.flush()
            self._snapshot(session, action, actor, None)
            return self._json(session, action)

    def revise(
        self, identity: str, payload: DraftInput, *, expected_version: int, actor: str
    ) -> JSON:
        try:
            with UnitOfWork(self.factory) as unit:
                session = unit.session
                assert session is not None
                action = self._action(session, identity)
                if action.version_id != expected_version:
                    raise ConflictError("Draft changed; reload before editing")
                if action.status != ExternalActionStatus.PROPOSED:
                    raise ConflictError("Only proposed manual drafts can be edited")
                self._validate_references(session, action.workspace_id, payload)
                old = action.payload_digest
                action.payload = {
                    **payload.model_dump(mode="json"),
                    "draft_revision": action.payload["draft_revision"] + 1,
                }
                action.payload_digest = digest(action.payload)
                session.flush()
                self._snapshot(session, action, actor, old)
                return self._json(session, action)
        except StaleDataError as exc:
            raise ConflictError(
                "Draft changed concurrently; reload before editing"
            ) from exc

    @staticmethod
    def _json(session: Session, action: ExternalAction) -> JSON:
        artifacts = session.scalars(
            select(Artifact)
            .where(
                Artifact.workspace_id == action.workspace_id,
                Artifact.location == "db:external_actions/" + action.id,
            )
            .order_by(Artifact.created_at.desc(), Artifact.id)
        ).all()
        history = [
            {"id": a.id, "digest": a.content_digest, **a.metadata_json}
            for a in artifacts
            if a.name == "Outreach draft revision"
        ]
        history.sort(key=lambda r: -r["revision"])
        outcomes = [a.metadata_json for a in artifacts if a.name == "Outreach outcome"]
        current_outcomes = [
            o
            for o in outcomes
            if o["draft_revision"] == action.payload["draft_revision"]
        ]
        state = (
            "Reply recorded (user-reported)"
            if any(o["kind"] == "reply" for o in current_outcomes)
            else "Sent manually (user-reported)"
            if current_outcomes
            else "Draft"
        )
        venture = session.scalar(
            select(Venture).where(Venture.workspace_id == action.workspace_id)
        )
        attachments = [
            {"id": a.id, "name": a.name, "digest": a.content_digest}
            for a in session.scalars(
                select(Artifact).where(
                    Artifact.workspace_id == action.workspace_id,
                    Artifact.id.in_(action.payload.get("attachment_artifact_ids", [])),
                )
            )
        ]
        return {
            "id": action.id,
            "venture_id": venture.id if venture else None,
            "workspace_id": action.workspace_id,
            "version": action.version_id,
            "digest": action.payload_digest,
            "updated_at": action.updated_at.isoformat(),
            **action.payload,
            "unresolved_fields": ([] if action.payload.get("to") else ["recipient"])
            + ([] if action.payload.get("sender_identity") else ["sender"]),
            "state": state,
            "history": history,
            "outcomes": outcomes,
            "attachments": attachments,
            "next_action": "Select recipient and export for manual sending"
            if not current_outcomes
            else "Review response as evidence; decide next test",
        }

    def show(self, identity: str) -> JSON:
        with self.factory() as session:
            return self._json(session, self._action(session, identity))

    def list(self, venture_id: str | None = None) -> JSON:
        with self.factory() as session:
            statement = select(ExternalAction).where(
                ExternalAction.action_type == "email",
                ExternalAction.adapter == "manual",
            )
            if venture_id:
                _, workspace = FoundryApplication._venture(session, venture_id)
                statement = statement.where(ExternalAction.workspace_id == workspace.id)
            return {
                "items": [
                    self._json(session, a)
                    for a in session.scalars(
                        statement.order_by(
                            ExternalAction.updated_at.desc(), ExternalAction.id
                        )
                    )
                ]
            }

    def _attachment(self, artifact: Artifact) -> tuple[str, bytes, str]:
        path = Path(artifact.location)
        if not path.is_absolute() or not artifact.content_digest:
            raise ValidationError(
                "Attachment needs an authorized absolute file reference and digest"
            )
        try:
            resolved = path.resolve(strict=True)
            root = next((r for r in self.roots if resolved.is_relative_to(r)), None)
            if root is None:
                raise ValidationError("Attachment is outside approved export roots")
            # Reject symlink components, including a final file link.
            if path != resolved or any(p.is_symlink() for p in [path, *path.parents]):
                raise ValidationError("Symlink attachments are not exportable")
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                import stat

                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size > 2_000_000:
                    raise ValidationError("Attachment must be a regular file <=2 MB")
                data = stream.read(2_000_001)
            if (
                len(data) > 2_000_000
                or hashlib.sha256(data).hexdigest() != artifact.content_digest
            ):
                raise ValidationError(
                    "Attachment bytes changed; register a new artifact revision"
                )
            return path.name, data, artifact.media_type or "application/octet-stream"
        except OSError as exc:
            raise ValidationError("Attachment is unavailable or unreadable") from exc

    def export(
        self, identity: str, *, format: Literal["text", "eml"] = "text"
    ) -> bytes:
        with self.factory() as session:
            action = self._action(session, identity)
            p = action.payload
            if format == "text":
                output: str = (
                    "MANUAL DRAFT — revision "
                    + str(p["draft_revision"])
                    + "\nUnresolved: "
                    + ", ".join(self._json(session, action)["unresolved_fields"])
                    + "\nTo: "
                    + ", ".join(p["to"])
                    + "\nCc: "
                    + ", ".join(p["cc"])
                    + "\nBcc: "
                    + ", ".join(p["bcc"])
                    + "\nSubject: "
                    + p["subject"]
                    + "\nAttachments: "
                    + ", ".join(p["attachment_artifact_ids"])
                    + "\n\n"
                    + p["body_text"]
                )
                return output.encode("utf-8")
            message = EmailMessage(policy=SMTP)
            message["X-Unsent"] = "1"
            message["X-Foundry-Draft-Revision"] = str(p["draft_revision"])
            for key in ["to", "cc", "bcc"]:
                if p[key]:
                    message[key.title()] = ", ".join(p[key])
            if p["sender_identity"]:
                message["From"] = p["sender_identity"]
            message["Subject"] = p["subject"]
            message.set_content(p["body_text"])
            for identity in p["attachment_artifact_ids"]:
                artifact = session.get(Artifact, identity)
                if artifact is None or artifact.workspace_id != action.workspace_id:
                    raise ReferenceError(
                        "Attachment does not belong to draft workspace"
                    )
                name, data, mime = self._attachment(artifact)
                major, _, minor = mime.partition("/")
                message.add_attachment(
                    data, maintype=major, subtype=minor or "octet-stream", filename=name
                )
            return message.as_bytes()

    def record_outcome(self, identity: str, payload: OutcomeInput) -> JSON:
        body = {
            **payload.model_dump(mode="json"),
            "attribution": "user-reported",
            "action_id": identity,
        }
        receipt_id = stable_id("manual-outcome:" + digest(body))
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            action = self._action(session, identity)
            snapshot = session.get(
                Artifact, stable_id(identity + ":draft:" + str(payload.draft_revision))
            )
            if snapshot is None or snapshot.workspace_id != action.workspace_id:
                raise ReferenceError("Draft revision does not exist")
            existing = session.get(Artifact, receipt_id)
            if existing:
                return existing.metadata_json
            evidence = Evidence(
                id=stable_id(receipt_id + ":evidence"),
                workspace_id=action.workspace_id,
                kind=EvidenceKind.EXTERNAL_OUTCOME,
                confidence=ConfidenceLevel.LOW,
                summary=payload.summary,
                details="User-reported "
                + payload.kind
                + " for exact draft revision "
                + str(payload.draft_revision),
                captured_by=payload.actor,
            )
            session.add(evidence)
            session.flush()
            body.update(
                {"evidence_id": evidence.id, "draft_digest": snapshot.content_digest}
            )
            session.add(
                Artifact(
                    id=receipt_id,
                    workspace_id=action.workspace_id,
                    kind=ArtifactKind.DOCUMENT,
                    name="Outreach outcome",
                    location="db:external_actions/" + identity,
                    content_digest=digest(body),
                    metadata_json=body,
                )
            )
            session.add(
                EvidenceArtifact(
                    evidence_id=evidence.id,
                    artifact_id=snapshot.id,
                    role="exact reported draft",
                )
            )
            session.add(
                AuditEvent(
                    workspace_id=action.workspace_id,
                    entity_type="external_action",
                    entity_id=identity,
                    event_type="manual_outcome_reported",
                    actor=payload.actor,
                    payload=body,
                )
            )
            if payload.kind == "sent_manually" and action.work_item_id:
                work = session.get(WorkItem, action.work_item_id)
                assert work is not None
                work.status = WorkItemStatus.DONE
                work.blocked_reason = None
            return body
