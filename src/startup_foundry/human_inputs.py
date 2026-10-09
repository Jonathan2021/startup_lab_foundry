"""Explicit file synchronization, immutable answers and manually claimed reviews."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as ContractError
from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    Artifact,
    Disposition,
    HumanRequest,
    HumanRequestDependency,
    HumanRequestTarget,
    Idea,
    IdeaAssessment,
    IdeaRevision,
    InvestigationStage,
    ProductMaturity,
    Venture,
    VentureAssessment,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    Workspace,
    WorkspaceReview,
    utc_now,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.portfolio import stable_id
from startup_foundry.repository import SessionFactory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import digest
from startup_foundry.snapshots import audit, read_snapshot, snapshot, transaction

JSON = dict[str, Any]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RequestInput(Contract):
    id: str = Field(pattern=r"^R[0-9]{3,6}$")
    workspace_id: str = Field(min_length=1, max_length=36)
    target_workspace_ids: list[str] = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=300)
    question: str = Field(min_length=1, max_length=20000)
    file_path: str | None = Field(default=None, max_length=300)
    actor: str = Field(default="operator", min_length=1, max_length=200)
    expected_version: int = Field(default=0, ge=0)


class ResponseInput(Contract):
    expected_version: int = Field(ge=1)
    text: str = Field(min_length=1, max_length=20000)
    author: str = Field(min_length=1, max_length=200)
    submission_key: str = Field(min_length=1, max_length=160)


class PreviewRow(Contract):
    request_id: str
    version: int = Field(ge=1)
    file_path: str
    workspace_id: str
    diagnostic: Literal[
        "empty", "unchanged", "conflict", "unsynced", "source_needs_attention"
    ]
    text: str | None = Field(default=None, max_length=100000)
    section: str | None = Field(default=None, max_length=100000)
    answer_hash: str | None = None
    question_hash: str | None = None
    file_hash: str | None = None
    error: str | None = None


class PreviewInput(Contract):
    items: list[PreviewRow] = Field(max_length=1000)


class ClaimInput(Contract):
    expected_version: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=200)


class ReleaseInput(ClaimInput):
    work_id: str
    reason: str = Field(min_length=1, max_length=20000)


class DependencyInput(ClaimInput):
    workspace_id: str
    work_id: str
    reason: str = Field(min_length=1, max_length=10000)
    other_causes: list[str] = Field(default_factory=list, max_length=30)


class TargetChange(Contract):
    workspace_id: str
    expected_revision: int = Field(ge=0)
    next_action: str = Field(min_length=1, max_length=10000)
    investigation_stage: InvestigationStage = InvestigationStage.COMPARISON
    product_maturity: ProductMaturity = ProductMaturity.CONCEPT
    disposition: Disposition = Disposition.PURSUE
    next_work_title: str | None = Field(default=None, max_length=300)
    # Only this single input dependency is closed; other causes stay blocked.
    close_input_work_ids: list[str] = Field(default_factory=list, max_length=30)


class ReviewResult(Contract):
    work_id: str
    response_id: str
    actor: str = Field(min_length=1, max_length=200)
    interpretation: str = Field(min_length=1, max_length=20000)
    outcome: Literal["sufficient", "partial", "deferred", "no_change"]
    rationale: str = Field(min_length=1, max_length=20000)
    remaining_unknowns: list[str] = Field(default_factory=list, max_length=50)
    changes: list[TargetChange] = Field(default_factory=list, max_length=50)
    score_explanation: str = Field(
        default=(
            "No factor judgment changed during intake; source estimates"
            " remain provisional."
        ),
        min_length=1,
        max_length=10000,
    )


class HumanInputService:
    def __init__(self, factory: SessionFactory, directory: Path) -> None:
        self.factory = factory
        self.directory = directory.resolve()

    def read_source(self, relative: str) -> tuple[str, str]:
        path = Path(relative)
        if path.is_absolute() or len(path.parts) != 1 or path.name in {".", ".."}:
            raise ValidationError(
                "Request source must be a regular file directly under "
                "FOUNDRY_REQUESTS_DIR"
            )
        try:
            descriptor = os.open(
                self.directory / path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            )
            with os.fdopen(descriptor, "rb") as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size > 100000:
                    raise ValidationError(
                        "Request source must be a regular UTF-8 file of at most 100 KB"
                    )
                body = stream.read(100001)
                if len(body) > 100000:
                    raise ValidationError("Request source exceeds 100 KB")
            return body.decode("utf-8"), hashlib.sha256(body).hexdigest()
        except (OSError, UnicodeError) as exc:
            raise ValidationError(
                "Request source missing, unsafe or invalid UTF-8"
            ) from exc

    def link_dependency(self, identity: str, payload: DependencyInput) -> JSON:
        """Register an exact cause before review; completion cannot invent links."""
        with transaction(self.factory) as session:
            item = self._request(session, identity)
            self._version(item, payload.expected_version)
            target = session.scalar(
                select(HumanRequestTarget).where(
                    HumanRequestTarget.request_id == identity,
                    HumanRequestTarget.workspace_id == payload.workspace_id,
                )
            )
            work = session.get(WorkItem, payload.work_id)
            if (
                not target
                or not work
                or work.workspace_id != target.workspace_id
                or work.status != WorkItemStatus.BLOCKED
                or work.blocked_reason != "human_input"
            ):
                raise ReferenceError(
                    "Dependency must be this target's blocked human input"
                )
            if any(
                not cause.strip() or len(cause) > 1000 for cause in payload.other_causes
            ):
                raise ValidationError(
                    "Other causes must be nonblank bounded descriptions"
                )
            existing = session.scalar(
                select(HumanRequestDependency).where(
                    HumanRequestDependency.target_id == target.id,
                    HumanRequestDependency.work_item_id == work.id,
                )
            )
            if existing:
                if existing.other_causes != payload.other_causes:
                    raise ConflictError(
                        "Dependency causes changed; retain and explicitly review them"
                    )
                return {"id": existing.id, "version": item.version_id}
            dependency = HumanRequestDependency(
                target_id=target.id,
                work_item_id=work.id,
                other_causes=payload.other_causes,
            )
            session.add(dependency)
            item.version_id += 1
            audit(
                session,
                item.workspace_id,
                item.id,
                "request_dependency_registered",
                payload.actor,
                payload.model_dump(mode="json"),
            )
            session.flush()
            return {"id": dependency.id, "version": item.version_id}

    @staticmethod
    def _dependencies(session: Session, work_id: str) -> list[HumanRequestDependency]:
        # Preserve earlier explicit target links; never infer a link from a title
        # or merely being in the same workspace.
        for target in session.scalars(
            select(HumanRequestTarget).where(HumanRequestTarget.work_item_id == work_id)
        ):
            if not session.scalar(
                select(HumanRequestDependency.id).where(
                    HumanRequestDependency.target_id == target.id,
                    HumanRequestDependency.work_item_id == work_id,
                )
            ):
                session.add(
                    HumanRequestDependency(
                        target_id=target.id, work_item_id=work_id, other_causes=[]
                    )
                )
        session.flush()
        return list(
            session.scalars(
                select(HumanRequestDependency)
                .where(HumanRequestDependency.work_item_id == work_id)
                .order_by(HumanRequestDependency.id)
            )
        )

    @staticmethod
    def section(content: str, identity: str) -> JSON:
        content = re.split(r"^## (?!R[0-9])", content, flags=re.M)[0]
        headings = list(re.finditer(r"^##\s+(R\d+)\s*(?:[—–-]|$).*$", content, re.M))
        matches = [i for i, h in enumerate(headings) if h.group(1) == identity]
        if len(matches) != 1:
            raise ValidationError("Missing or duplicate request heading " + identity)
        i = matches[0]
        start = headings[i].start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(content)
        section = content[start:end]
        blocks = list(
            re.finditer(
                r"^(?:\*\*)?(My answer|Response)(?:\*\*)?:\s*", section, re.M | re.I
            )
        )
        choices = []
        for j, b in enumerate(blocks):
            text = section[
                b.end() : blocks[j + 1].start() if j + 1 < len(blocks) else len(section)
            ].rstrip("\r\n")
            # Preserve author spelling/whitespace; reject unfilled helper prompts.
            if text.strip() and not all(
                not line.strip() or re.match(r"^\s*-.*:\s*$", line)
                for line in text.splitlines()
            ):
                choices.append((b.group(1).lower(), text, b.start()))
        selected = next(
            (x for x in choices if x[0] == "my answer"), choices[0] if choices else None
        )
        text = selected[1] if selected else ""
        question = section[: blocks[0].start()] if blocks else section
        return {
            "text": text,
            "section": section,
            "answer_hash": digest(text.replace("\r\n", "\n")),
            "question_hash": digest(question.replace("\r\n", "\n")),
        }

    @staticmethod
    def _request(session: Session, identity: str) -> HumanRequest:
        item = session.get(HumanRequest, identity)
        if item is None:
            raise ReferenceError("Request does not exist")
        return item

    @staticmethod
    def _version(item: HumanRequest, expected: int) -> None:
        if item.version_id != expected:
            raise ConflictError("Request changed; refresh before submitting")

    @staticmethod
    def _invalidate_dependencies(session: Session, identity: str) -> None:
        with session.no_autoflush:
            for dependency in session.scalars(
                select(HumanRequestDependency).where(
                    HumanRequestDependency.target_id.in_(
                        select(HumanRequestTarget.id).where(
                            HumanRequestTarget.request_id == identity
                        )
                    )
                )
            ):
                dependency.satisfied_response_id = None

    def register(self, payload: RequestInput) -> JSON:
        with transaction(self.factory) as session:
            return self._register(session, payload)

    def _register(self, session: Session, payload: RequestInput) -> JSON:
        if payload.file_path:
            path = Path(payload.file_path)
            if path.is_absolute() or len(path.parts) != 1:
                raise ValidationError("Unsafe request source path")
        owner = session.get(Workspace, payload.workspace_id)
        if owner is None:
            raise ReferenceError("Owner workspace missing")
        targets = set(payload.target_workspace_ids) | {owner.id}
        for identity in targets:
            w = session.get(Workspace, identity)
            if w is None or w.portfolio_id != owner.portfolio_id:
                raise ReferenceError("Targets must belong to owner portfolio")
        existing = session.get(HumanRequest, payload.id)
        definition = payload.model_dump(
            mode="json", exclude={"expected_version", "actor"}
        )
        if existing:
            prior = read_snapshot(
                session,
                existing.definition_artifact_id,
                owner.id,
                "human-request/v1",
            )
            if prior["definition"] == definition:
                return {"id": existing.id, "version": existing.version_id}
            self._version(existing, payload.expected_version)
            if existing.workspace_id != owner.id:
                raise ValidationError("Request owner cannot change")
            existing.definition_revision += 1
            existing.status = "waiting_for_answer"
            self._invalidate_dependencies(session, existing.id)
            item = existing
        else:
            item = HumanRequest(
                id=payload.id,
                workspace_id=owner.id,
                title=payload.title,
                question=payload.question,
                definition_revision=1,
                status="waiting_for_answer",
            )
        artifact = snapshot(
            session,
            owner.id,
            "human-request/v1",
            {
                "request_id": item.id,
                "revision": item.definition_revision,
                "definition": definition,
                "actor": payload.actor,
            },
        )
        item.definition_artifact_id = artifact.id
        item.title = payload.title
        item.question = payload.question
        item.file_path = payload.file_path
        session.add(item)
        session.flush()
        for identity in targets:
            if not session.scalar(
                select(HumanRequestTarget.id).where(
                    HumanRequestTarget.request_id == item.id,
                    HumanRequestTarget.workspace_id == identity,
                )
            ):
                session.add(
                    HumanRequestTarget(request_id=item.id, workspace_id=identity)
                )
        return {"id": item.id, "version": item.version_id}

    @staticmethod
    def _responses(session: Session, item: HumanRequest) -> list[Artifact]:
        # Stable immutable ancestry; only this request's bounded history is loaded.
        return list(
            session.scalars(
                select(Artifact)
                .where(
                    Artifact.workspace_id == item.workspace_id,
                    Artifact.name == "human-response/v1",
                )
                .order_by(Artifact.created_at, Artifact.id)
            )
        )

    def _save(
        self,
        session: Session,
        item: HumanRequest,
        payload: ResponseInput,
        *,
        source: str = "ui",
        details: JSON | None = None,
    ) -> JSON:
        if not payload.text.strip():
            raise ValidationError("Answer must be nonblank")
        receipt_id = stable_id(
            "human-response/v1:"
            + item.workspace_id
            + ":"
            + item.id
            + ":"
            + payload.submission_key
        )
        old = session.get(Artifact, receipt_id)
        fingerprint = digest(
            {
                "text": payload.text,
                "author": payload.author,
                "source": source,
                "definition": item.definition_revision,
            }
        )
        if old:
            if old.metadata_json.get("submission_digest") != fingerprint:
                raise ConflictError("Submission key reused with different answer")
            return {
                "id": old.id,
                "request_id": item.id,
                "version": item.version_id,
                "saved": False,
            }
        self._version(item, payload.expected_version)
        current = (
            read_snapshot(
                session,
                item.response_artifact_id,
                item.workspace_id,
                "human-response/v1",
            )
            if item.response_artifact_id
            else None
        )
        if (
            current
            and current["definition_revision"] == item.definition_revision
            and current["text"] == payload.text
        ):
            return {
                "id": item.response_artifact_id,
                "request_id": item.id,
                "version": item.version_id,
                "saved": False,
            }
        if current:
            previous_work = session.get(WorkItem, current["work_id"])
            if previous_work and previous_work.status == WorkItemStatus.READY:
                previous_work.status = WorkItemStatus.CANCELLED
                audit(
                    session,
                    item.workspace_id,
                    previous_work.id,
                    "answer_review_superseded",
                    payload.author,
                    {"next_response_id": receipt_id},
                )
        work = WorkItem(
            id=stable_id("review:" + receipt_id),
            workspace_id=item.workspace_id,
            title="Review " + item.id + " answer",
            description=receipt_id,
            kind=WorkItemKind.EXECUTION,
            status=WorkItemStatus.READY,
            owner="agent",
            acceptance_criteria=(
                "Record interpretation and explicit next owner; no "
                "automatic external action"
            ),
        )
        session.add(work)
        session.flush()
        response = snapshot(
            session,
            item.workspace_id,
            "human-response/v1",
            {
                "request_id": item.id,
                "definition_revision": item.definition_revision,
                "definition_artifact_id": item.definition_artifact_id,
                "sequence": current["sequence"] + 1 if current else 1,
                "text": payload.text,
                "author": payload.author,
                "source": source,
                "received_at": utc_now().isoformat(),
                "previous_response_id": item.response_artifact_id,
                "submission_key": payload.submission_key,
                "submission_digest": fingerprint,
                "work_id": work.id,
                **(details or {}),
            },
            key=item.id + ":" + payload.submission_key,
            work_id=work.id,
        )
        item.response_artifact_id = response.id
        self._invalidate_dependencies(session, item.id)
        item.status = "ready_for_review"
        if source == "file":
            item.source_diagnostics = {
                "last_file_answer_hash": details["answer_hash"] if details else None
            }
        audit(
            session,
            item.workspace_id,
            item.id,
            "answer_saved",
            payload.author,
            {"response_id": response.id, "work_id": work.id},
        )
        session.flush()
        return {
            "id": response.id,
            "request_id": item.id,
            "version": item.version_id,
            "saved": True,
            "work_id": work.id,
        }

    def submit(self, identity: str, payload: ResponseInput) -> JSON:
        with transaction(self.factory) as session:
            return self._save(session, self._request(session, identity), payload)

    def preview(self) -> JSON:
        items = []
        with self.factory() as session:
            for item in session.scalars(select(HumanRequest).order_by(HumanRequest.id)):
                if not item.file_path:
                    continue
                row = {
                    "request_id": item.id,
                    "version": item.version_id,
                    "file_path": item.file_path,
                    "workspace_id": item.workspace_id,
                }
                try:
                    content, hash_ = self.read_source(item.file_path)
                    parsed = self.section(content, item.id)
                    current = (
                        read_snapshot(
                            session,
                            item.response_artifact_id,
                            item.workspace_id,
                            "human-response/v1",
                        )
                        if item.response_artifact_id
                        else None
                    )
                    same = (
                        current
                        and digest(current["text"].replace("\r\n", "\n"))
                        == parsed["answer_hash"]
                    )
                    last = item.source_diagnostics.get("last_file_answer_hash")
                    diagnostic = (
                        "empty"
                        if not parsed["text"]
                        else "unchanged"
                        if same or last == parsed["answer_hash"]
                        else "conflict"
                        if current and current["source"] == "ui"
                        else "unsynced"
                    )
                    row.update(parsed, file_hash=hash_, diagnostic=diagnostic)
                except ValidationError as exc:
                    row.update(diagnostic="source_needs_attention", error=str(exc))
                items.append(row)
        return {"items": items}

    def sync(
        self,
        preview: JSON,
        *,
        reconciliation: Literal["keep_ui", "use_file"] | None = None,
    ) -> JSON:
        try:
            PreviewInput.model_validate(preview)
        except ContractError as exc:
            raise ValidationError(
                "Invalid file-sync preview; obtain a fresh preview"
            ) from exc
        if digest(preview) != digest(self.preview()):
            raise ConflictError("Sources or requests changed; refresh sync preview")
        imported = 0
        with transaction(self.factory) as session:
            for row in preview["items"]:
                item = self._request(session, row["request_id"])
                if row["diagnostic"] in {"empty", "source_needs_attention"}:
                    continue
                content, hash_ = self.read_source(item.file_path or "")
                if hash_ != row["file_hash"]:
                    raise ConflictError(
                        "File changed since preview; refresh before syncing"
                    )
                self._version(item, row["version"])
                if row["diagnostic"] == "unchanged":
                    continue
                if row["diagnostic"] == "conflict" and reconciliation is None:
                    raise ConflictError(
                        "File/UI answers diverged; explicitly keep UI or use file"
                    )
                if row["diagnostic"] == "conflict" and reconciliation == "keep_ui":
                    candidate = snapshot(
                        session,
                        item.workspace_id,
                        "human-response-candidate/v1",
                        row,
                        key=item.id + ":" + hash_,
                    )
                    item.source_diagnostics = {
                        "last_file_answer_hash": row["answer_hash"],
                        "candidate_id": candidate.id,
                        "resolution": "keep_ui",
                    }
                    continue
                parsed = self.section(content, item.id)
                result = self._save(
                    session,
                    item,
                    ResponseInput(
                        expected_version=item.version_id,
                        text=parsed["text"],
                        author="operator (imported file; authored time unknown)",
                        submission_key="file:"
                        + str(item.response_artifact_id)
                        + ":"
                        + parsed["answer_hash"],
                    ),
                    source="file",
                    details={"file_path": item.file_path, "file_hash": hash_, **parsed},
                )
                imported += int(result["saved"])
        return {"imported": imported}

    def show(self, identity: str) -> JSON:
        with self.factory() as session:
            item = self._request(session, identity)
            responses = [
                {"id": a.id, **a.metadata_json}
                for a in self._responses(session, item)
                if a.metadata_json.get("request_id") == identity
            ]
            reviews = [
                {"id": a.id, **a.metadata_json}
                for a in session.scalars(
                    select(Artifact)
                    .where(
                        Artifact.workspace_id == item.workspace_id,
                        Artifact.name == "human-response-review/v1",
                    )
                    .order_by(Artifact.created_at.desc())
                )
                if a.metadata_json.get("request_id") == identity
            ]
            targets = [
                {"workspace_id": w.id, "title": w.title, "key": w.key}
                for w in session.scalars(
                    select(Workspace)
                    .join(
                        HumanRequestTarget,
                        HumanRequestTarget.workspace_id == Workspace.id,
                    )
                    .where(HumanRequestTarget.request_id == identity)
                )
            ]
            answer = next(
                (a for a in responses if a["id"] == item.response_artifact_id), None
            )
            from startup_foundry.workspace_records import (
                state_reference,
                work_reference,
            )

            effects = {
                a.metadata_json["review_id"]: a.metadata_json["effects"]
                for a in session.scalars(
                    select(Artifact).where(
                        Artifact.workspace_id == item.workspace_id,
                        Artifact.name == "human-review-effects/v1",
                    )
                )
            }
            for review in reviews:
                response = next(
                    (r for r in responses if r["id"] == review["response_id"]), None
                )
                review["historical"] = (
                    review["response_id"] != item.response_artifact_id
                    or not response
                    or response["definition_revision"] != item.definition_revision
                )
                review["effects"] = []
                for effect in effects.get(review["id"], []):
                    w = effect["workspace_id"]
                    current = session.scalar(
                        select(WorkspaceReview)
                        .where(WorkspaceReview.workspace_id == w)
                        .order_by(WorkspaceReview.revision.desc())
                        .limit(1)
                    )
                    review["effects"].append(
                        {
                            "workspace_id": w,
                            "state": state_reference(session, w, effect["review_id"]),
                            "work": work_reference(session, w, effect.get("work_id")),
                            "current_work": work_reference(
                                session, w, current.next_work_item_id
                            )
                            if current
                            else None,
                        }
                    )
            current_review = next(
                (
                    r
                    for r in reviews
                    if not r["historical"] and r["id"] == item.review_artifact_id
                ),
                None,
            )
            return {
                "current_review": current_review,
                "historical_reviews": [r for r in reviews if r["historical"]],
                "id": item.id,
                "title": item.title,
                "question": item.question,
                "version": item.version_id,
                "definition_revision": item.definition_revision,
                "workspace_id": item.workspace_id,
                "status": item.status,
                "file_path": item.file_path,
                "answer": answer,
                "responses": responses,
                "reviews": reviews,
                "targets": targets,
                "source_diagnostics": item.source_diagnostics,
            }

    def list(
        self,
        *,
        status: str | None = None,
        workspace_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> JSON:
        if not 1 <= limit <= 500 or offset < 0:
            raise ValidationError("Invalid pagination")
        statement = select(HumanRequest)
        if status == "needs_you":
            statement = statement.where(
                HumanRequest.status.in_(["waiting_for_answer", "needs_clarification"])
            )
        elif status == "awaiting_review":
            statement = statement.where(
                HumanRequest.status.in_(["ready_for_review", "reviewing"])
            )
        elif status and status != "history":
            statement = statement.where(HumanRequest.status == status)
        if workspace_id:
            statement = statement.join(HumanRequestTarget).where(
                HumanRequestTarget.workspace_id == workspace_id
            )
        from sqlalchemy import func

        with self.factory() as session:
            total = (
                session.scalar(select(func.count()).select_from(statement.subquery()))
                or 0
            )
            rows = session.scalars(
                statement.order_by(HumanRequest.id).limit(limit).offset(offset)
            )
            return {
                "items": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "status": r.status,
                        "workspace_id": r.workspace_id,
                        "version": r.version_id,
                    }
                    for r in rows
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

    def claim(self, identity: str, payload: ClaimInput) -> JSON:
        with transaction(self.factory) as session:
            item = self._request(session, identity)
            self._version(item, payload.expected_version)
            if item.status != "ready_for_review" or not item.response_artifact_id:
                raise ConflictError("Current answer is not ready for review")
            answer = read_snapshot(
                session,
                item.response_artifact_id,
                item.workspace_id,
                "human-response/v1",
            )
            work = session.get(WorkItem, answer["work_id"])
            assert work is not None
            if work.status != WorkItemStatus.READY:
                raise ConflictError("Review already claimed")
            work.status = WorkItemStatus.IN_PROGRESS
            work.owner = payload.actor
            item.status = "reviewing"
            audit(
                session,
                item.workspace_id,
                work.id,
                "answer_review_claimed",
                payload.actor,
                {
                    "response_id": item.response_artifact_id,
                    "claimed_at": utc_now().isoformat(),
                },
            )
            session.flush()
            return {
                "work_id": work.id,
                "response_id": item.response_artifact_id,
                "version": item.version_id,
            }

    def release(self, identity: str, payload: ReleaseInput) -> JSON:
        with transaction(self.factory) as session:
            item = self._request(session, identity)
            self._version(item, payload.expected_version)
            work = session.get(WorkItem, payload.work_id)
            receipt = session.scalar(
                select(Artifact).where(
                    Artifact.work_item_id == payload.work_id,
                    Artifact.name == "human-response/v1",
                )
            )
            if receipt is None or receipt.metadata_json.get("request_id") != identity:
                raise ReferenceError("Review work belongs to a different request")
            if (
                not work
                or work.workspace_id != item.workspace_id
                or work.owner != payload.actor
                or work.status != WorkItemStatus.IN_PROGRESS
                or not session.scalar(
                    select(Artifact.id).where(
                        Artifact.work_item_id == work.id,
                        Artifact.name == "human-response/v1",
                    )
                )
            ):
                raise ConflictError("Only the claimant may release this review")
            work.status = WorkItemStatus.READY
            work.owner = "agent"
            if (
                item.response_artifact_id
                and read_snapshot(
                    session,
                    item.response_artifact_id,
                    item.workspace_id,
                    "human-response/v1",
                )["work_id"]
                == work.id
            ):
                item.status = "ready_for_review"
            audit(
                session,
                item.workspace_id,
                work.id,
                "review_requeued",
                payload.actor,
                {"reason": payload.reason},
            )
            return {"work_id": work.id, "released": True}

    def complete(self, identity: str, payload: ReviewResult) -> JSON:
        with transaction(self.factory) as session:
            item = self._request(session, identity)
            answer = read_snapshot(
                session, payload.response_id, item.workspace_id, "human-response/v1"
            )
            work = session.get(WorkItem, payload.work_id)
            if (
                answer["request_id"] != identity
                or answer["work_id"] != payload.work_id
                or not work
                or work.status != WorkItemStatus.IN_PROGRESS
                or work.owner != payload.actor
            ):
                raise ConflictError(
                    "Review must reference the exact answer and be owned by reviewer"
                )
            current = (
                item.response_artifact_id == payload.response_id
                and item.definition_revision == answer["definition_revision"]
            )
            if not current and payload.changes:
                raise ConflictError(
                    "New answer/question arrived; historical review cannot "
                    "change current state"
                )
            if payload.outcome == "no_change" and payload.changes:
                raise ValidationError("No-change review cannot mutate targets")
            if payload.outcome != "sufficient" and any(
                change.close_input_work_ids for change in payload.changes
            ):
                raise ValidationError(
                    "Only sufficient review can satisfy input dependencies"
                )
            if payload.outcome == "deferred" and any(
                c.next_work_title or c.disposition != Disposition.HOLD
                for c in payload.changes
            ):
                raise ValidationError(
                    "Deferred review retains holds and cannot queue investigation"
                )
            result = payload.model_dump(mode="json")
            result.update(
                request_id=identity,
                reviewed_at=utc_now().isoformat(),
                historical=not current,
            )
            artifact = snapshot(
                session,
                item.workspace_id,
                "human-response-review/v1",
                result,
                work_id=work.id,
            )
            effects = []
            targets = set(
                session.scalars(
                    select(HumanRequestTarget.workspace_id).where(
                        HumanRequestTarget.request_id == identity
                    )
                )
            )
            if len({c.workspace_id for c in payload.changes}) != len(payload.changes):
                raise ValidationError("Duplicate target changes")
            for change in payload.changes:
                if change.workspace_id not in targets:
                    raise ReferenceError("Review change is outside request targets")
                provenance = snapshot(
                    session,
                    change.workspace_id,
                    "human-response-reference/v1",
                    {
                        "request_id": identity,
                        "response_id": payload.response_id,
                        "review_id": artifact.id,
                        "interpretation": payload.interpretation,
                        "source_workspace_id": item.workspace_id,
                    },
                )
                next_work = None
                if change.next_work_title:
                    next_work = WorkItem(
                        workspace_id=change.workspace_id,
                        title=change.next_work_title,
                        kind=WorkItemKind.INVESTIGATION,
                        status=WorkItemStatus.READY,
                        owner="agent",
                        description=change.next_action,
                        acceptance_criteria=change.next_action,
                    )
                    session.add(next_work)
                    session.flush()
                for work_id in change.close_input_work_ids:
                    blocked = session.scalar(
                        select(WorkItem).where(WorkItem.id == work_id).with_for_update()
                    )
                    if (
                        not blocked
                        or blocked.workspace_id != change.workspace_id
                        or blocked.status != WorkItemStatus.BLOCKED
                        or blocked.blocked_reason != "human_input"
                    ):
                        raise ReferenceError(
                            "Only this target human-input dependency can close"
                        )
                    dependencies = self._dependencies(session, work_id)
                    target = session.scalar(
                        select(HumanRequestTarget).where(
                            HumanRequestTarget.request_id == identity,
                            HumanRequestTarget.workspace_id == change.workspace_id,
                        )
                    )
                    own = next(
                        (
                            d
                            for d in dependencies
                            if target and d.target_id == target.id
                        ),
                        None,
                    )
                    if not own:
                        raise ReferenceError(
                            "Work is not an explicit dependency of this request/target"
                        )
                    own.satisfied_response_id = payload.response_id
                    session.flush()
                    cleared = all(
                        d.satisfied_response_id and not d.other_causes
                        for d in dependencies
                    )
                    if cleared:
                        blocked.status = WorkItemStatus.DONE
                    audit(
                        session,
                        change.workspace_id,
                        blocked.id,
                        "input_dependency_closed"
                        if cleared
                        else "input_cause_satisfied",
                        payload.actor,
                        {
                            "review_id": artifact.id,
                            "reason": payload.rationale,
                            "request_id": identity,
                            "response_id": payload.response_id,
                            "other_causes_remain": not cleared,
                        },
                    )
                state = ReviewService._append(
                    session,
                    ReviewInput(
                        workspace_id=change.workspace_id,
                        expected_revision=change.expected_revision,
                        investigation_stage=change.investigation_stage,
                        product_maturity=change.product_maturity,
                        disposition=change.disposition,
                        next_action=change.next_action,
                        next_work_item_id=next_work.id if next_work else None,
                        reason=payload.rationale,
                        author=payload.actor,
                        source_artifact_id=provenance.id,
                    ),
                )
                effects.append(
                    {
                        "workspace_id": change.workspace_id,
                        "review_id": state.id,
                        "work_id": next_work.id if next_work else None,
                    }
                )
            snapshot(
                session,
                item.workspace_id,
                "human-review-effects/v1",
                {"review_id": artifact.id, "effects": effects},
            )
            work.status = WorkItemStatus.DONE
            if current:
                item.review_artifact_id = artifact.id
                item.status = {
                    "sufficient": "resolved",
                    "partial": "needs_clarification",
                    "deferred": "deferred",
                    "no_change": "resolved",
                }[payload.outcome]
            audit(
                session,
                item.workspace_id,
                work.id,
                "answer_review_completed",
                payload.actor,
                {"review_id": artifact.id, "historical": not current},
            )
            return {"id": artifact.id, "historical": not current, "effects": effects}

    def handoff(self, identity: str) -> JSON:
        detail = self.show(identity)
        score_ids = {}
        with self.factory() as session:
            for target in detail["targets"]:
                w = target["workspace_id"]
                venture_scores = list(
                    session.scalars(
                        select(VentureAssessment.id)
                        .join(Venture, VentureAssessment.venture_id == Venture.id)
                        .where(Venture.workspace_id == w)
                        .order_by(VentureAssessment.created_at.desc())
                        .limit(20)
                    )
                )
                idea_scores = list(
                    session.scalars(
                        select(IdeaAssessment.id)
                        .join(
                            IdeaRevision,
                            IdeaAssessment.idea_revision_id == IdeaRevision.id,
                        )
                        .join(Idea, IdeaRevision.idea_id == Idea.id)
                        .where(Idea.workspace_id == w)
                        .order_by(IdeaAssessment.created_at.desc())
                        .limit(20)
                    )
                )
                score_ids[w] = {
                    "venture_assessment_ids": venture_scores,
                    "idea_assessment_ids": idea_scores,
                }
        return {
            "prior_score_ids": score_ids,
            "request": detail,
            "prior_states": {
                t["workspace_id"]: ReviewService(self.factory).show(t["workspace_id"])[
                    "current"
                ]
                for t in detail["targets"]
            },
            "held_tracks": [r["id"] for r in self.list(status="deferred")["items"]],
            "allowed_actions": (
                "Local review/drafting only. Claim the exact response/work,"
                " record interpretation, outcome, next owner and score "
                "change or explanation. Release with reason after "
                "interruption. External actions need exact human approval. "
                "Copying does not start an agent."
            ),
        }
