"""Readable lifecycle workflows; HTTP is a thin adapter over the local services."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import func, select

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.decision_commands import GUIDE, SCHEMAS
from startup_foundry.decision_contracts import (
    CaptureInput,
    ContextInput,
    MapInput,
    NewWorkInput,
    ResolveResultInput,
    ResultInput,
    WorkClaimInput,
    WorkReleaseInput,
)
from startup_foundry.decision_maps import (
    RECORD_MODELS,
    DecisionMapService,
    row_json,
    workspace_scope,
)
from startup_foundry.domain import (
    Artifact,
    Assumption,
    Decision,
    DecisionMap,
    Evidence,
    WorkItem,
)
from startup_foundry.errors import ReferenceError, ValidationError
from startup_foundry.repository import SessionFactory
from startup_foundry.scoring import ScoringService
from startup_foundry.venture_scoring import VentureScoringService
from startup_foundry.workspace_navigation import DetailQuery

JSON = dict[str, Any]


def portfolio_attention(factory: SessionFactory) -> JSON:
    """A bounded portfolio projection; each venture remains the owner of its work."""
    with factory() as session:
        heads = list(
            session.scalars(
                select(DecisionMap).order_by(DecisionMap.updated_at.desc()).limit(30)
            )
        )
        total = session.scalar(select(func.count()).select_from(DecisionMap)) or 0
    items = []
    for head in heads:
        current = AgentHandoffService(factory).resume(head.workspace_id)
        pending = [
            r for r in current["results"] if r["state"] not in {"accept", "reject"}
        ]
        if pending or current["needs_review"] or current["unreviewed_change_count"]:
            scope = current["scope"]
            items.append(
                {
                    "title": scope["title"],
                    "url": "/"
                    + ("ventures" if scope["subject"] == "venture" else "ideas")
                    + "/"
                    + scope["subject_id"],
                    "changes": current["unreviewed_change_count"],
                    "affected": len(current["needs_review"]),
                    "results": pending,
                }
            )
    return {"items": items, "total": total, "inspected": len(heads)}


def install_decision_routes(
    app: FastAPI, factory: SessionFactory, render: Callable[..., Response]
) -> None:
    maps, handoffs = DecisionMapService(factory), AgentHandoffService(factory)

    def page_context(workspace: str, request: Request) -> JSON:
        with factory() as session:
            scope = workspace_scope(session, workspace)
        navigation = DetailQuery.parse(request)
        with factory() as session:
            ScoringService.read_card(session, navigation.card_id)
        venture = scope["subject"] == "venture"
        scores = (
            VentureScoringService(factory).show(scope["subject_id"], navigation.card_id)
            if venture
            else ScoringService(factory).show(scope["subject_id"])
        )
        if not venture:
            scores["card_id"] = navigation.card_id
            scores["current"] = next(
                (
                    a
                    for a in scores.get("history", [])
                    if a["scorecard_id"] == navigation.card_id
                ),
                None,
            )
        navigation = DetailQuery.parse(request)
        kind = "ventures" if venture else "ideas"
        subject_url = "/" + kind + "/" + scope["subject_id"]

        def workspace_link(
            tab: str | None = None, *, fragment: str = "", path: str | None = None
        ) -> str:
            return navigation.url(
                path or subject_url, kind=kind, tab=tab, fragment=fragment
            )

        return {
            "scope": scope,
            "workspace_id": workspace,
            "subject": scope["subject"],
            "subject_id": scope["subject_id"],
            "scores": scores,
            "nav": kind,
            "subject_url": subject_url,
            "workspace_link": workspace_link,
        }

    @app.get("/api/agent-guide")
    def agent_guide() -> JSON:
        return {"markdown": GUIDE, "schemas": list(SCHEMAS)}

    @app.get("/api/decision-schemas/{name}")
    def schema(name: str) -> JSON:
        if name not in SCHEMAS:
            raise ReferenceError("Unknown contract")
        return SCHEMAS[name].model_json_schema()

    @app.get("/api/workspaces/{workspace}/resume")
    def resume(workspace: str) -> JSON:
        return handoffs.resume(workspace)

    @app.get("/api/workspaces/{workspace}/decision-map")
    def show_map(workspace: str, revision: str | None = None) -> JSON:
        return maps.show(workspace, revision=revision)

    @app.get("/api/workspaces/{workspace}/decision-map/draft")
    def starter(workspace: str) -> JSON:
        return maps.starter(workspace)

    @app.post("/api/workspaces/{workspace}/decision-map")
    def revise_map(workspace: str, payload: MapInput) -> JSON:
        return maps.revise(workspace, payload)

    @app.post("/api/workspaces/{workspace}/decision-map/preview")
    def preview_map(workspace: str, payload: MapInput) -> JSON:
        with factory() as session:
            try:
                return maps._revise(session, workspace, payload)
            finally:
                session.rollback()

    @app.get("/api/workspaces/{workspace}/decision-records")
    def records(
        workspace: str,
        kind: str = "evidence",
        q: str = "",
        offset: int = 0,
        limit: int = 50,
    ) -> JSON:
        if kind not in {
            "work",
            "assumption",
            "evidence",
            "decision",
            "artifact",
            "review",
        }:
            raise ValidationError(
                "Choose work, assumption, evidence, decision, artifact or review"
            )
        if not 0 <= offset <= 1000000 or not 1 <= limit <= 200 or len(q) > 300:
            raise ValidationError("Invalid record search bounds")
        model: Any = RECORD_MODELS[kind]
        label = getattr(model, "title", None)
        if label is None:
            label = getattr(model, "summary", None)
        if label is None:
            label = getattr(model, "statement", None)
        if label is None:
            label = getattr(model, "name", None)
        if label is None:
            label = model.next_action
        with factory() as session:
            workspace_scope(session, workspace)
            query = select(model).where(model.workspace_id == workspace)
            if q:
                query = query.where(label.icontains(q, autoescape=True))
            total = session.scalar(select(func.count()).select_from(query.subquery()))
            rows = session.scalars(
                query.order_by(model.created_at.desc(), model.id)
                .offset(offset)
                .limit(limit)
            )
            return {
                "items": [
                    {
                        "kind": kind,
                        "id": row.id,
                        "label": getattr(row, label.key),
                    }
                    for row in rows
                ],
                "total": total,
                "offset": offset,
                "limit": limit,
            }

    @app.post("/api/workspaces/{workspace}/contexts")
    def prepare(workspace: str, payload: ContextInput) -> JSON:
        return handoffs.prepare(workspace, payload)

    @app.get("/api/contexts/{identity}")
    def show_context(identity: str) -> JSON:
        return handoffs.show_context(identity)

    @app.get("/api/contexts/{identity}/arrivals")
    def arrivals(identity: str, offset: int = 0) -> JSON:
        return handoffs.arrivals(identity, offset=offset)

    @app.get("/api/contexts/{identity}/records/{kind}/{record_id}")
    def fetch_record(identity: str, kind: str, record_id: str) -> JSON:
        return handoffs.fetch(identity, kind, record_id)

    @app.post("/api/workspaces/{workspace}/results")
    def submit_result(workspace: str, payload: ResultInput) -> JSON:
        return handoffs.submit(workspace, payload)

    @app.get("/api/decision-results/{identity}")
    def result(identity: str) -> JSON:
        return handoffs.show_result(identity)

    @app.post("/api/decision-results/{identity}/preview")
    def preview_result(identity: str, payload: ResolveResultInput) -> JSON:
        return handoffs.preview(identity, payload)

    @app.post("/api/decision-results/{identity}/resolve")
    def resolve(identity: str, payload: ResolveResultInput) -> JSON:
        return handoffs.resolve(identity, payload)

    @app.post("/api/workspaces/{workspace}/changes")
    def capture(workspace: str, payload: CaptureInput) -> JSON:
        return handoffs.capture(workspace, payload)

    @app.post("/api/workspaces/{workspace}/work")
    def new_work(workspace: str, payload: NewWorkInput) -> JSON:
        return handoffs.create_work(workspace, payload)

    @app.post("/api/workspaces/{workspace}/work/{work_id}/claim")
    def claim(workspace: str, work_id: str, payload: WorkClaimInput) -> JSON:
        return handoffs.claim(workspace, work_id, payload)

    @app.post("/api/workspaces/{workspace}/work/{work_id}/release")
    def release(workspace: str, work_id: str, payload: WorkReleaseInput) -> JSON:
        return handoffs.release(workspace, work_id, payload)

    @app.get("/workspaces/{workspace}/decision-map")
    def map_page(
        request: Request, workspace: str, revision: str | None = None
    ) -> Response:
        current = maps.show(workspace, revision=revision)
        resume_data = handoffs.resume(workspace)
        with factory() as session:
            catalog = []
            catalog_models: list[tuple[str, Any]] = [
                ("work", WorkItem),
                ("assumption", Assumption),
                ("evidence", Evidence),
                ("decision", Decision),
                ("artifact", Artifact),
            ]
            for kind, model in catalog_models:
                for item in session.scalars(
                    select(model)
                    .where(model.workspace_id == workspace)
                    .order_by(model.created_at.desc())
                    .limit(100)
                ):
                    row = row_json(item)
                    catalog.append(
                        {
                            "kind": kind,
                            "id": item.id,
                            "label": row.get("title")
                            or row.get("summary")
                            or row.get("statement")
                            or row.get("name"),
                        }
                    )
        draft = current["map"] if current["id"] else maps.starter(workspace)
        return render(
            request,
            "decision_map.html",
            **page_context(workspace, request),
            decision_map=current,
            draft_map=draft,
            lifecycle=resume_data,
            record_catalog=catalog,
        )

    # Register .md before the catch-all identity page.
    @app.get("/handoffs/{identity}.md", response_class=PlainTextResponse)
    def download_context(identity: str) -> Response:
        data = handoffs.show_context(identity)
        return PlainTextResponse(
            data["markdown"],
            headers={
                "Content-Disposition": 'attachment; filename="foundry-context.md"'
            },
        )

    @app.get("/handoffs/{identity}")
    def context_page(request: Request, identity: str) -> Response:
        data = handoffs.show_context(identity)
        return render(
            request,
            "agent_context.html",
            **page_context(data["workspace_id"], request),
            context=data,
            lifecycle=handoffs.resume(data["workspace_id"]),
        )

    @app.get("/decision-results/{identity}")
    def result_page(request: Request, identity: str) -> Response:
        data = handoffs.show_result(identity)
        ctx = handoffs.show_context(data["context_id"])
        return render(
            request,
            "decision_result.html",
            **page_context(data["workspace_id"], request),
            result=data,
            context=ctx,
            lifecycle=handoffs.resume(data["workspace_id"]),
        )

    @app.get("/agent-guide")
    def guide_page(request: Request) -> Response:
        return render(request, "agent_guide.html", nav="help", guide=GUIDE)
