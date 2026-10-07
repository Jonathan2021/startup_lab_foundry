"""Allowlisted builtins and manual, attributed business snapshots."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.domain import Artifact, Venture, WorkItem, utc_now
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.repository import SessionFactory
from startup_foundry.snapshots import snapshot, transaction

JSON = dict[str, Any]
REGISTRY = {
    "software": {
        "label": "Software",
        "required_context": "Linked repository/checkpoint",
        "renderer": "projects.ExistingProjectService",
        "actions": ["checkpoint", "technical work"],
    },
    "outreach": {
        "label": "Outreach",
        "required_context": "Venture",
        "renderer": "outreach.OutreachService",
        "actions": ["create", "edit", "export"],
    },
}


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ConfigInput(Contract):
    expected_revision: int = Field(ge=0)
    actor: str = Field(min_length=1, max_length=200)
    modules: list[str] = Field(max_length=2)


class MetricsInput(Contract):
    expected_revision: int = Field(ge=0)
    actor: str = Field(min_length=1, max_length=200)
    revenue: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    costs: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    period: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=10000)
    label: Literal["reported_actual", "estimate"] = "reported_actual"


class IssueInput(Contract):
    work_id: str
    category: Literal["bug", "security"]
    severity: Literal["unknown", "low", "medium", "high", "critical"]
    source: str = Field(min_length=1, max_length=10000)
    actor: str = Field(min_length=1, max_length=200)
    assessment: Literal["reported", "confirmed"] = "reported"


class WorkspaceModuleService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    @staticmethod
    def _venture(session: Session, identity: str) -> Venture:
        v = session.get(Venture, identity)
        if not v:
            raise ReferenceError("Venture missing")
        return v

    @staticmethod
    def history(session: Session, workspace: str, schema: str) -> list[JSON]:
        return [
            {"id": a.id, **a.metadata_json}
            for a in session.scalars(
                select(Artifact)
                .where(Artifact.workspace_id == workspace, Artifact.name == schema)
                .order_by(Artifact.created_at.desc(), Artifact.id)
            )
        ]

    def configure(self, identity: str, payload: ConfigInput) -> JSON:
        if set(payload.modules) - REGISTRY.keys() or len(set(payload.modules)) != len(
            payload.modules
        ):
            raise ValidationError("Choose unique allowlisted software/outreach modules")
        return self._append(identity, "venture-workspace-config/v1", payload)

    def metrics(self, identity: str, payload: MetricsInput) -> JSON:
        return self._append(identity, "venture-metrics/v1", payload)

    def _append(
        self, identity: str, schema: str, payload: ConfigInput | MetricsInput
    ) -> JSON:
        with transaction(self.factory) as session:
            v = self._venture(session, identity)
            history = self.history(session, v.workspace_id, schema)
            revision = history[0]["revision"] if history else 0
            if revision != payload.expected_revision:
                raise ConflictError(
                    "Workspace snapshot changed; refresh before editing"
                )
            data = {
                **payload.model_dump(mode="json", exclude={"expected_revision"}),
                "revision": revision + 1,
                "recorded_at": utc_now().isoformat(),
                "previous_id": history[0]["id"] if history else None,
                "venture_id": v.id,
            }
            artifact = snapshot(
                session, v.workspace_id, schema, data, key=str(revision + 1)
            )
            return {"id": artifact.id, **data}

    def issue(self, identity: str, payload: IssueInput) -> JSON:
        with transaction(self.factory) as session:
            v = self._venture(session, identity)
            work = session.get(WorkItem, payload.work_id)
            if not work or work.workspace_id != v.workspace_id:
                raise ReferenceError("Issue work must belong to venture")
            artifact = snapshot(
                session,
                v.workspace_id,
                "software-work-category/v1",
                {
                    **payload.model_dump(mode="json"),
                    "reported_at": utc_now().isoformat(),
                },
                work_id=work.id,
            )
            return {"id": artifact.id}

    def show(self, identity: str) -> JSON:
        with self.factory() as session:
            v = self._venture(session, identity)
            configs = self.history(
                session, v.workspace_id, "venture-workspace-config/v1"
            )
            metrics = self.history(session, v.workspace_id, "venture-metrics/v1")
            issues = self.history(session, v.workspace_id, "software-work-category/v1")
            from startup_foundry.projects import ExistingProjectService

            suggested = (
                ["software", "outreach"]
                if ExistingProjectService(self.factory).show(identity)["current"]
                else []
            )
            return {
                "config": configs[0]
                if configs
                else {"revision": 0, "modules": suggested},
                "config_history": configs,
                "metrics": next(
                    (m for m in metrics if m["label"] == "reported_actual"), None
                ),
                "metrics_history": metrics,
                "forecasts": [m for m in metrics if m["label"] == "estimate"],
                "issues": issues,
                "registry": REGISTRY,
            }
