"""Versioned explanations of current decisions, with exact record ownership."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from startup_foundry.decision_contracts import (
    DecisionMapDraft,
    MapInput,
    RecordRef,
    WorkTreatment,
)
from startup_foundry.domain import (
    Artifact,
    ArtifactRelation,
    ArtifactRelationKind,
    Assumption,
    AssumptionAssessment,
    Base,
    Decision,
    DecisionMap,
    Evidence,
    EvidenceSource,
    Experiment,
    HumanRequestDependency,
    Idea,
    IdeaRevision,
    ReferenceSource,
    Venture,
    WorkItem,
    WorkItemStatus,
    Workspace,
    WorkspaceReview,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.portfolio import stable_id
from startup_foundry.repository import SessionFactory
from startup_foundry.scoring import digest
from startup_foundry.snapshots import audit, read_snapshot, snapshot, transaction

JSON = dict[str, Any]
MAP_SCHEMA = "decision-map/v1"
ACTIVE = {
    WorkItemStatus.TODO,
    WorkItemStatus.READY,
    WorkItemStatus.IN_PROGRESS,
    WorkItemStatus.BLOCKED,
}
RECORD_MODELS: dict[str, type[Base]] = {
    "work": WorkItem,
    "assumption": Assumption,
    "evidence": Evidence,
    "decision": Decision,
    "experiment": Experiment,
    "artifact": Artifact,
    "review": WorkspaceReview,
    "assessment": AssumptionAssessment,
}
DEPENDENCIES = {"depends_on", "tests", "contributes_to"}


def json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        # SQLite drops tzinfo; the domain persists UTC on both supported stores.
        return (
            value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
        ).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def row_json(row: Base) -> JSON:
    return {
        c.key: json_value(getattr(row, c.key)) for c in inspect(type(row)).column_attrs
    }


def record_snapshot(session: Session, workspace: str, ref: RecordRef) -> JSON:
    row = session.get(RECORD_MODELS[ref.kind], ref.id)
    owner = getattr(row, "workspace_id", None)
    if isinstance(row, Experiment):
        work = session.get(WorkItem, row.work_item_id)
        owner = work.workspace_id if work else None
    if isinstance(row, AssumptionAssessment):
        assumption = session.get(Assumption, row.assumption_id)
        owner = assumption.workspace_id if assumption else None
    if row is None or owner != workspace:
        raise ReferenceError(
            f"{ref.kind} {ref.id} is missing or belongs to another workspace"
        )
    value = row_json(row)
    if isinstance(row, Evidence):
        value["sources"] = [
            {
                "source": row_json(source),
                "excerpt": link.excerpt,
                "source_location": link.source_location,
            }
            for link in session.scalars(
                select(EvidenceSource)
                .where(EvidenceSource.evidence_id == row.id)
                .order_by(EvidenceSource.id)
            )
            if (source := session.get(ReferenceSource, link.source_id)) is not None
        ]
    semantic = {
        k: v
        for k, v in value.items()
        if k not in {"created_at", "updated_at", "version_id"}
    }
    if ref.kind == "work":
        # Claim/release/completion does not change the purpose of a map node.
        semantic = {
            k: v
            for k, v in semantic.items()
            if k not in {"status", "owner", "blocked_reason"}
        }
    return {"kind": ref.kind, "id": ref.id, "record": value, "digest": digest(semantic)}


def workspace_scope(session: Session, workspace: str) -> JSON:
    ws = session.get(Workspace, workspace)
    if ws is None:
        raise ReferenceError("Workspace does not exist")
    venture = session.scalar(select(Venture).where(Venture.workspace_id == workspace))
    idea = session.scalar(select(Idea).where(Idea.workspace_id == workspace))
    revision = (
        session.get(IdeaRevision, idea.current_revision_id)
        if idea and idea.current_revision_id
        else None
    )
    return {
        "workspace_id": workspace,
        "title": ws.title,
        "subject": "venture" if venture else "idea",
        "subject_id": venture.id if venture else idea.id if idea else workspace,
        "objective": venture.objective
        if venture
        else revision.cleaned_description
        if revision
        else ws.description,
        "stage": venture.stage.value if venture else None,
        "focus": venture.current_focus if venture else None,
        "idea_revision_id": revision.id if revision else None,
    }


def map_head(
    session: Session, workspace: str, *, lock: bool = False
) -> DecisionMap | None:
    query = select(DecisionMap).where(DecisionMap.workspace_id == workspace)
    return session.scalar(query.with_for_update() if lock else query)


def map_payload(session: Session, head: DecisionMap) -> JSON:
    return read_snapshot(
        session, head.current_revision_artifact_id, head.workspace_id, MAP_SCHEMA
    )


def stale_references(session: Session, workspace: str, data: JSON) -> list[str]:
    stale = []
    if data["scope"] != workspace_scope(session, workspace):
        stale.append("scope")
    for key, ref in data["references"].items():
        try:
            now = record_snapshot(
                session, workspace, RecordRef(kind=ref["kind"], id=ref["id"])
            )
        except ReferenceError:
            stale.append(key)
            continue
        if now["digest"] != ref["digest"]:
            stale.append(key)
    return stale


def dependent_work(draft: JSON, changed: set[str]) -> set[str]:
    affected = set(changed)
    while True:
        more = {
            e["source"]
            for e in draft["edges"]
            if e["kind"] in DEPENDENCIES and e["target"] in affected
        }
        # A changed supporting or opposing source affects its explicit question.
        more |= {
            e["target"]
            for e in draft["edges"]
            if e["kind"] in {"informs", "supports", "contradicts"}
            and e["source"] in affected
        }
        if more <= affected:
            break
        affected |= more
    return {
        n["ref"]["id"]
        for n in draft["nodes"]
        if n["id"] in affected and n.get("ref") and n["ref"]["kind"] == "work"
    }


def derived_reviews(session: Session, workspace: str, data: JSON) -> dict[str, str]:
    reviews = dict(data.get("needs_review", {}))
    stale = stale_references(session, workspace, data)
    changed = {
        n["id"]
        for n in data["map"]["nodes"]
        if "scope" in stale
        or n.get("ref")
        and n["ref"]["kind"] + ":" + n["ref"]["id"] in stale
    }
    for work_id in dependent_work(data["map"], changed):
        reviews[work_id] = "Referenced context changed; review the affected decision"
    return {
        wid: reason
        for wid, reason in reviews.items()
        if (work := session.get(WorkItem, wid)) is not None and work.status in ACTIVE
    }


def execution_blockers(session: Session, work: WorkItem) -> list[str]:
    reasons = []
    if work.status == WorkItemStatus.BLOCKED:
        reasons.append(work.blocked_reason or "Work is blocked")
    dependencies = session.scalars(
        select(HumanRequestDependency).where(
            HumanRequestDependency.work_item_id == work.id
        )
    )
    if any(not d.satisfied_response_id or d.other_causes for d in dependencies):
        reasons.append("Required human input has not been reviewed")
    head = map_head(session, work.workspace_id)
    if head:
        data = map_payload(session, head)
        pending = derived_reviews(session, work.workspace_id, data)
        if work.id in pending:
            reasons.append("Decision review required: " + pending[work.id])
        nodes = {n["id"]: n for n in data["map"]["nodes"]}
        for edge in data["map"]["edges"]:
            source, target = nodes[edge["source"]], nodes[edge["target"]]
            if edge["kind"] == "depends_on" and source.get("ref") == {
                "kind": "work",
                "id": work.id,
            }:
                ref = target.get("ref")
                prerequisite = (
                    session.get(WorkItem, ref["id"])
                    if ref and ref["kind"] == "work"
                    else None
                )
                if prerequisite and prerequisite.status != WorkItemStatus.DONE:
                    reasons.append(
                        "Prerequisite work is not complete: " + prerequisite.title
                    )
    return reasons


def require_execution_eligible(session: Session, work: WorkItem) -> None:
    reasons = execution_blockers(session, work)
    if reasons:
        raise ConflictError("; ".join(reasons))


def apply_treatments(
    session: Session,
    workspace: str,
    treatments: list[WorkTreatment],
    pending: dict[str, str],
) -> None:
    ids = [t.work_id for t in treatments]
    if len(set(ids)) != len(ids):
        raise ValidationError("Each work item has one reviewed treatment")
    for treatment in treatments:
        work = session.get(WorkItem, treatment.work_id)
        if work is None or work.workspace_id != workspace:
            raise ReferenceError("Work treatment belongs to another workspace")
        if work.version_id != treatment.expected_version or work.status not in ACTIVE:
            raise ConflictError("Work treatment is stale; refresh the exact work item")
        if treatment.action == "pause":
            if work.status != WorkItemStatus.BLOCKED:
                work.blocked_reason = "changed_context"
            work.status = WorkItemStatus.BLOCKED
            pending[work.id] = treatment.rationale
        else:
            pending.pop(work.id, None)
            if treatment.action == "cancel":
                work.status = WorkItemStatus.CANCELLED
            elif (
                work.status == WorkItemStatus.BLOCKED
                and work.blocked_reason == "changed_context"
            ):
                work.status, work.blocked_reason = WorkItemStatus.READY, None
            if treatment.action == "revise":
                if treatment.title:
                    work.title = treatment.title
                if treatment.description:
                    work.description = treatment.description
        work.version_id += 1
    session.flush()


class DecisionMapService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    @staticmethod
    def _view(
        session: Session, workspace: str, identity: str, *, live: bool = True
    ) -> JSON:
        data = read_snapshot(session, identity, workspace, MAP_SCHEMA)
        artifact = session.get(Artifact, identity)
        assert artifact is not None
        head = map_head(session, workspace)
        return {
            **data,
            "id": identity,
            "digest": artifact.content_digest,
            "head_version": head.version_id if head else 0,
            "historical": head is None or head.current_revision_artifact_id != identity,
            "stale_references": stale_references(session, workspace, data)
            if live
            else [],
            "needs_review": derived_reviews(session, workspace, data)
            if live
            else data.get("needs_review", {}),
        }

    def show(self, workspace: str, *, revision: str | None = None) -> JSON:
        with self.factory() as session:
            scope = workspace_scope(session, workspace)
            head = map_head(session, workspace)
            identity = revision or (head.current_revision_artifact_id if head else None)
            if identity is None:
                return {
                    "id": None,
                    "scope": scope,
                    "map": {"nodes": [], "edges": [], "focus": []},
                    "history": [],
                    "needs_review": {},
                    "stale_references": [],
                    "head_version": 0,
                }
            data = self._view(
                session,
                workspace,
                identity,
                live=not revision
                or bool(head and head.current_revision_artifact_id == identity),
            )
            data["history"] = [
                {
                    "id": a.id,
                    "sequence": a.metadata_json["sequence"],
                    "rationale": a.metadata_json["rationale"],
                    "actor": a.metadata_json["actor"],
                    "created_at": a.created_at.isoformat(),
                }
                for a in session.scalars(
                    select(Artifact)
                    .where(
                        Artifact.workspace_id == workspace, Artifact.name == MAP_SCHEMA
                    )
                    .order_by(Artifact.created_at.desc(), Artifact.id)
                )
            ]
            return data

    def revise(self, workspace: str, payload: MapInput) -> JSON:
        with transaction(self.factory) as session:
            return self._revise(session, workspace, payload)

    @classmethod
    def _revise(
        cls,
        session: Session,
        workspace: str,
        payload: MapInput,
        *,
        reviewed_evidence: dict[str, str] | None = None,
    ) -> JSON:
        request_digest = digest(payload.model_dump(mode="json"))
        identity = stable_id(MAP_SCHEMA + ":" + workspace + ":" + payload.request_key)
        prior = session.get(Artifact, identity)
        if prior:
            if prior.metadata_json.get("request_digest") != request_digest:
                raise ConflictError(
                    "Map request key already used with different content"
                )
            return cls._view(session, workspace, identity)
        if len(payload.model_dump_json().encode()) > 100000:
            raise ValidationError("Map exceeds 100 KB; narrow its scope")
        scope = workspace_scope(session, workspace)
        head = map_head(session, workspace, lock=True)
        current_id = head.current_revision_artifact_id if head else None
        if current_id != payload.expected_head:
            raise ConflictError("Decision map changed; refresh before revising")
        old = map_payload(session, head) if head else None
        draft = payload.map.model_dump(mode="json")
        references = {
            node.ref.kind + ":" + node.ref.id: record_snapshot(
                session, workspace, node.ref
            )
            for node in payload.map.nodes
            if node.ref
        }
        pending: dict[str, str] = (
            derived_reviews(session, workspace, old) if old else {}
        )
        affected: set[str] = set()
        if old:
            before = {n["id"]: n for n in old["map"]["nodes"]}
            after = {n["id"]: n for n in draft["nodes"]}
            changed = {
                key
                for key in before.keys() | after.keys()
                if before.get(key) != after.get(key)
            }
            if old["scope"] != scope:
                changed |= before.keys() | after.keys()
            old_edges = {json.dumps(e, sort_keys=True): e for e in old["map"]["edges"]}
            new_edges = {json.dumps(e, sort_keys=True): e for e in draft["edges"]}
            for key in old_edges.keys() ^ new_edges.keys():
                edge = old_edges.get(key) or new_edges[key]
                changed.add(edge["source"])
                if edge["kind"] in {"informs", "supports", "contradicts"}:
                    changed.add(edge["target"])
            for key, value in references.items():
                if (
                    key in old["references"]
                    and old["references"][key]["digest"] != value["digest"]
                ):
                    changed |= {
                        n["id"]
                        for n in draft["nodes"]
                        if n.get("ref") == {"kind": value["kind"], "id": value["id"]}
                    }
            affected = dependent_work(old["map"], changed) | dependent_work(
                draft, changed
            )
            affected &= {
                n["ref"]["id"]
                for n in old["map"]["nodes"]
                if n.get("ref") and n["ref"]["kind"] == "work"
            }
            for wid in affected:
                work = session.get(WorkItem, wid)
                if work and work.status in ACTIVE:
                    pending[wid] = payload.rationale
        apply_treatments(session, workspace, payload.work_treatments, pending)
        treated = {t.work_id for t in payload.work_treatments}
        for wid in affected - treated:
            work = session.get(WorkItem, wid)
            if work and work.status in ACTIVE:
                work.version_id += 1
        session.flush()
        # Capture post-treatment values so a historical revision is self-contained.
        references = {
            node.ref.kind + ":" + node.ref.id: record_snapshot(
                session, workspace, node.ref
            )
            for node in payload.map.nodes
            if node.ref
        }
        data = {
            "schema_version": 1,
            "workspace_id": workspace,
            "scope": scope,
            "sequence": old["sequence"] + 1 if old else 1,
            "previous_revision_id": current_id,
            "actor": payload.actor,
            "rationale": payload.rationale,
            "request_digest": request_digest,
            "map": draft,
            "references": references,
            "needs_review": pending,
            "reviewed_evidence": {
                **(old.get("reviewed_evidence", {}) if old else {}),
                **(reviewed_evidence or {}),
            },
            "work_treatments": [
                t.model_dump(mode="json") for t in payload.work_treatments
            ],
        }
        revision = snapshot(
            session, workspace, MAP_SCHEMA, data, key=payload.request_key
        )
        if head:
            head.current_revision_artifact_id = revision.id
            session.add(
                ArtifactRelation(
                    source_artifact_id=revision.id,
                    target_artifact_id=current_id,
                    kind=ArtifactRelationKind.SUPERSEDES,
                    rationale=payload.rationale,
                )
            )
        else:
            head = DecisionMap(
                workspace_id=workspace, current_revision_artifact_id=revision.id
            )
            session.add(head)
        audit(
            session,
            workspace,
            revision.id,
            "decision_map_revised",
            payload.actor,
            {"previous_revision_id": current_id, "affected_work_ids": sorted(affected)},
        )
        session.flush()
        return cls._view(session, workspace, revision.id)

    def starter(self, workspace: str) -> JSON:
        """A clearly unaccepted draft from stored scope/work, no invented evidence."""
        with self.factory() as session:
            scope = workspace_scope(session, workspace)
            nodes: list[JSON] = [
                {
                    "id": "goal",
                    "kind": "goal",
                    "title": str(scope["objective"] or scope["title"])[:300],
                    "detail": "Current recorded objective",
                }
            ]
            edges: list[JSON] = []
            focus: list[str] = []
            for work in session.scalars(
                select(WorkItem)
                .where(WorkItem.workspace_id == workspace, WorkItem.status.in_(ACTIVE))
                .order_by(WorkItem.created_at.desc(), WorkItem.id)
                .limit(8)
            ):
                key = "work_" + work.id
                nodes.append(
                    {
                        "id": key,
                        "kind": "record",
                        "title": work.title,
                        "ref": {"kind": "work", "id": work.id},
                    }
                )
                edges.append(
                    {"source": key, "target": "goal", "kind": "contributes_to"}
                )
                if not focus:
                    focus.append(key)
            return DecisionMapDraft.model_validate(
                {"nodes": nodes, "edges": edges, "focus": focus or ["goal"]}
            ).model_dump(mode="json")
