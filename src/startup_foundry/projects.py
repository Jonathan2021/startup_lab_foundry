"""Reference-only intake of existing work; never executes or inspects a repo."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    Disposition,
    InvestigationStage,
    ProductMaturity,
    Venture,
    VentureStage,
)
from startup_foundry.errors import ReferenceError
from startup_foundry.portfolio import PortfolioService, stable_id
from startup_foundry.repository import SessionFactory, UnitOfWork
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import digest


class RepositoryCheckpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    local_reference: str = Field(min_length=1, max_length=2000)
    remote_url: str | None = Field(default=None, max_length=2000)
    head: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    dirty_state: str = Field(default="unknown", max_length=20000)
    artifact_digests: dict[str, str] = Field(default_factory=dict)
    observed_at: datetime


class CapabilityCheckpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature: str = Field(min_length=1, max_length=300)
    documented: str = Field(max_length=5000)
    code_present: str = Field(max_length=5000)
    last_test_result: str = Field(max_length=10000)
    observed_workflow: str = Field(max_length=10000)
    limitations: str = Field(max_length=10000)
    evidence_locators: list[str] = Field(default_factory=list, max_length=30)
    verification_level: Literal["reported", "docs", "code", "mock_test", "observed"]


class ExistingProjectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["existing-project/v1"] = "existing-project/v1"
    venture_id: str = Field(min_length=1, max_length=36)
    source_idea_id: str | None = Field(default=None, max_length=36)
    name: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1, max_length=20000)
    repositories: list[RepositoryCheckpoint] = Field(
        default_factory=list, max_length=10
    )
    participants_as_reported: list[str] = Field(default_factory=list, max_length=20)
    product_maturity: ProductMaturity = ProductMaturity.UNKNOWN
    reason_paused: str = Field(min_length=1, max_length=10000)
    capabilities: list[CapabilityCheckpoint] = Field(
        default_factory=list, max_length=50
    )
    prior_decisions_constraints: list[str] = Field(default_factory=list, max_length=50)
    available_users_data: str = Field(default="unknown", max_length=10000)
    gaps: list[str] = Field(default_factory=list, max_length=50)
    next_bounded_test: str = Field(min_length=1, max_length=10000)
    ownership_license_access: str = Field(default="unknown", max_length=10000)
    expected_review_revision: int = Field(default=0, ge=0)
    author: str = Field(min_length=1, max_length=200)


class ExistingProjectService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    def intake(self, payload: ExistingProjectInput) -> dict[str, Any]:
        body = payload.model_dump(mode="json", exclude={"expected_review_revision"})
        content_digest = digest(body)
        identity = stable_id(
            "existing-project:" + payload.venture_id + ":" + content_digest
        )
        with self.factory() as lookup:
            existing = lookup.get(Artifact, identity)
            if existing:
                return {
                    "id": payload.venture_id,
                    "artifact_id": identity,
                    "unchanged": True,
                }
        portfolio = PortfolioService(self.factory)
        if payload.source_idea_id:
            portfolio.promote_idea(
                payload.source_idea_id, venture_id=payload.venture_id
            )
        else:
            with self.factory() as lookup:
                exists = lookup.get(Venture, payload.venture_id) is not None
            if not exists:
                FoundryApplication(self.factory).create_venture(
                    venture_id=payload.venture_id,
                    name=payload.name,
                    objective=payload.description,
                    stage=VentureStage.DISCOVERY,
                )
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            venture = session.get(Venture, payload.venture_id)
            assert venture is not None
            artifact = Artifact(
                id=identity,
                workspace_id=venture.workspace_id,
                kind=ArtifactKind.REPORT,
                name="Existing project checkpoint",
                location="db:existing-project/" + identity,
                content_digest=content_digest,
                semantic_version="existing-project/v1",
                metadata_json=body,
            )
            session.add(artifact)
            session.flush()
            review = ReviewService._append(
                session,
                ReviewInput(
                    workspace_id=venture.workspace_id,
                    expected_revision=payload.expected_review_revision,
                    investigation_stage=InvestigationStage.BUSINESS_VALIDATION,
                    product_maturity=payload.product_maturity,
                    disposition=Disposition.HOLD,
                    next_action=payload.next_bounded_test,
                    reason=payload.reason_paused,
                    author=payload.author,
                    source_artifact_id=artifact.id,
                ),
            )
            return {
                "id": payload.venture_id,
                "artifact_id": identity,
                "review_id": review.id,
                "unchanged": False,
            }

    def show(self, venture_id: str) -> dict[str, Any]:
        with self.factory() as session:
            venture = session.get(Venture, venture_id)
            if venture is None:
                raise ReferenceError("Venture does not exist")
            history = [
                {
                    "id": a.id,
                    "digest": a.content_digest,
                    "created_at": a.created_at.isoformat(),
                    "manifest": a.metadata_json,
                }
                for a in session.scalars(
                    select(Artifact)
                    .where(
                        Artifact.workspace_id == venture.workspace_id,
                        Artifact.name == "Existing project checkpoint",
                    )
                    .order_by(Artifact.created_at.desc(), Artifact.id)
                )
            ]
            return {"history": history, "current": history[0] if history else None}
