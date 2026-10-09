"""Shared context and HTTP surface for focused workspaces and human input."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select

from startup_foundry.domain import (
    Artifact,
    AuditEvent,
    Decision,
    Evidence,
    Idea,
    IdeaAssessment,
    StepRun,
    Venture,
    WorkItem,
    Workspace,
    WorkspaceReview,
)
from startup_foundry.human_inputs import (
    ClaimInput,
    Contract,
    DependencyInput,
    HumanInputService,
    ReleaseInput,
    ResponseInput,
    ReviewResult,
)
from startup_foundry.manual_intake import (
    IntakeCompletion,
    IntakeRequest,
    ManualIntakeService,
)
from startup_foundry.proposals import (
    FusionInput,
    ProposalService,
    ResolveInput,
    ReviseInput,
)
from startup_foundry.repository import SessionFactory
from startup_foundry.scoring import ORIGINAL, REVIEWED, ScoringService
from startup_foundry.venture_scoring import (
    VentureAssessmentInput,
    VentureScoringService,
)
from startup_foundry.workspace_history import history
from startup_foundry.workspace_modules import (
    ConfigInput,
    IssueInput,
    MetricsInput,
    WorkspaceModuleService,
)
from startup_foundry.workspace_navigation import DetailQuery

JSON = dict[str, Any]


class SyncInput(Contract):
    preview: dict[str, Any]
    reconciliation: str | None = None


def card_id(request: Request) -> str:
    return DetailQuery.parse(request).card_id


def back_url(request: Request, kind: str) -> str:
    return DetailQuery.parse(request).back(kind)


def context(
    factory: SessionFactory,
    inputs: HumanInputService,
    request: Request,
    workspace: str,
    *,
    venture_id: str | None = None,
    idea_id: str | None = None,
) -> JSON:
    from startup_foundry.agent_handoffs import AgentHandoffService

    navigation = DetailQuery.parse(request)
    kind = "ventures" if venture_id else "ideas"
    base_path = "/" + kind + "/" + (venture_id or idea_id or "")

    def workspace_link(
        tab: str | None = None,
        offset: int | None = None,
        path: str | None = None,
        fragment: str = "",
    ) -> str:
        return navigation.url(
            path or base_path, kind=kind, tab=tab, offset=offset, fragment=fragment
        )

    questions = inputs.list(workspace_id=workspace)["items"]
    for question in questions:
        question["url"] = workspace_link(path="/requests/" + question["id"])
    with factory() as session:
        briefs = [
            {
                "id": a.id,
                "source": a.metadata_json.get("source"),
                "status": a.metadata_json.get("status"),
            }
            for a in session.scalars(
                select(Artifact)
                .where(
                    Artifact.workspace_id == workspace,
                    Artifact.name == "venture-followup-brief/v1",
                )
                .order_by(Artifact.created_at.desc())
                .limit(10)
            )
        ]
        switcher = [
            {
                "id": v.id,
                "title": w.title,
                "url": workspace_link(path="/ventures/" + v.id),
            }
            for v, w in session.execute(
                select(Venture, Workspace)
                .join(Workspace, Venture.workspace_id == Workspace.id)
                .order_by(Venture.id)
            ).all()
        ]
        current = session.scalar(
            select(WorkspaceReview)
            .where(WorkspaceReview.workspace_id == workspace)
            .order_by(WorkspaceReview.revision.desc())
            .limit(1)
        )
        work = [
            {
                "id": w.id,
                "title": w.title,
                "status": w.status.value,
                "owner": w.owner,
                "version": w.version_id,
                "url": workspace_link(path=base_path + "/work/" + w.id),
            }
            for w in session.scalars(
                select(WorkItem)
                .where(WorkItem.workspace_id == workspace)
                .order_by(WorkItem.created_at.desc())
                .limit(50)
            )
        ]
    waiting = next(
        (
            r
            for r in questions
            if r["status"] in ["waiting_for_answer", "needs_clarification"]
        ),
        None,
    )
    pending = next(
        (r for r in questions if r["status"] in ["ready_for_review", "reviewing"]), None
    )
    deferred = next((r for r in questions if r["status"] == "deferred"), None)
    chosen = waiting or pending or deferred
    intake = ManualIntakeService(factory).handoff(
        "venture" if venture_id else "idea", venture_id or idea_id or ""
    )
    active_work = next(
        (w for w in work if current and w["id"] == current.next_work_item_id), None
    )
    action = (
        {
            "label": (
                "Answer " + chosen["id"]
                if chosen == waiting
                else "Review answer " + chosen["id"]
                if chosen == pending
                else "Deferred by you · " + chosen["id"]
            ),
            "url": chosen["url"],
            "owner": "you"
            if chosen == waiting
            else "agent"
            if chosen == pending
            else "you",
            "status": chosen["status"],
        }
        if chosen
        else {
            "label": current.next_action
            if current
            else "Specify the next bounded task",
            "url": workspace_link("work"),
            "owner": active_work["owner"] if active_work else "agent",
            "status": active_work["status"] if active_work else "not scheduled",
        }
    )
    proposals = ProposalService(factory).list(workspace_id=workspace)["items"]
    undecided = next((p for p in proposals if p["state"] == "proposed"), None)
    if undecided and not waiting:
        action = {
            "label": "Review fusion proposal",
            "url": "/proposals/" + undecided["id"],
            "owner": "you",
            "status": "proposed",
        }
    if not chosen and not undecided and not current:
        action = {
            "label": "Queued for manual agent review"
            if intake
            else "Request initial review",
            "url": workspace_link("work", fragment="initial-review")
            if venture_id
            else workspace_link(fragment="initial-review"),
            "owner": intake["work"]["owner"] if intake else "you",
            "status": intake["work"]["status"] if intake else "not scheduled",
        }
    modules = WorkspaceModuleService(factory).show(venture_id) if venture_id else None
    if modules:
        for issue in modules["issues"]:
            issue["work_url"] = workspace_link(
                path=base_path + "/work/" + issue["work_id"]
            )
    selected_scores = (
        VentureScoringService(factory).show(venture_id, card_id(request))
        if venture_id
        else ScoringService(factory).show(idea_id or "")
    )
    if not venture_id:
        selected_scores["card_id"] = card_id(request)
        selected_scores["current"] = next(
            (
                a
                for a in selected_scores["history"]
                if a["scorecard_id"] == card_id(request)
            ),
            None,
        )
    edit_card_id = REVIEWED if card_id(request) == ORIGINAL else card_id(request)
    with factory() as session:
        ScoringService.read_card(session, navigation.card_id)
        editor_card = ScoringService.read_card(session, edit_card_id)
        editor_sequence = (
            VentureScoringService.latest(session, venture_id, edit_card_id)
            if venture_id
            else 0
        )
        if idea_id:
            idea = session.get(Idea, idea_id)
            assert idea
            editor_sequence = (
                session.scalar(
                    select(IdeaAssessment.assessment_number)
                    .where(
                        IdeaAssessment.idea_revision_id == idea.current_revision_id,
                        IdeaAssessment.scorecard_id == edit_card_id,
                    )
                    .order_by(IdeaAssessment.assessment_number.desc())
                    .limit(1)
                )
                or 0
            )
    editor = {**editor_card, "expected_sequence": editor_sequence}
    timeline = (
        history(
            factory,
            workspace,
            venture_id,
            offset=navigation.offset,
            limit=navigation.limit,
        )
        if venture_id and navigation.tab == "history"
        else None
    )
    if timeline:
        for event in timeline["items"]:
            event["url"] = workspace_link("history", path=event["url"])
    return {
        "lifecycle": AgentHandoffService(factory).resume(workspace),
        "workspace_id": workspace,
        "workspace_link": workspace_link,
        "score_editor": editor,
        "intake": intake,
        "active_work": active_work,
        "briefs": briefs,
        "related_proposals": proposals,
        "module_config": modules["config"] if modules else None,
        "metrics": modules["metrics"] if modules else None,
        "forecasts": modules["forecasts"] if modules else [],
        "metrics_revision": modules["metrics_history"][0]["revision"]
        if modules and modules["metrics_history"]
        else 0,
        "issues": modules["issues"] if modules else [],
        "history": timeline,
        "questions": questions,
        "next_action": action,
        "switcher": switcher,
        "work": work,
        "tab": navigation.tab,
        "back_url": navigation.back(kind),
        "score_view": navigation.score_view,
        "scores": selected_scores,
        "file_preview": inputs.preview(),
    }


def venture_data(factory: SessionFactory, identity: str, tab: str) -> JSON:
    from startup_foundry.application import FoundryApplication

    app = FoundryApplication(factory)
    with factory() as session:
        v, w = FoundryApplication._venture(session, identity)
        detail: JSON = {"venture": FoundryApplication._venture_json(v, w)}
    for collection in [
        "evidence",
        "decisions",
        "work_items",
        "artifacts",
        "assumptions",
        "experiments",
        "assumption_assessments",
    ]:
        detail[collection] = (
            app.list_records(identity, collection, limit=30)["items"]
            if tab == collection
            else []
        )
    return detail


def install_routes(
    app: FastAPI,
    factory: SessionFactory,
    directory: Path,
    render: Callable[..., Response],
) -> None:
    inputs = HumanInputService(factory, directory)
    scores = VentureScoringService(factory)
    proposals = ProposalService(factory)
    modules = WorkspaceModuleService(factory)
    intake = ManualIntakeService(factory)

    def scoped_record(
        request: Request, identity: str, record_id: str, subject: str, is_review: bool
    ) -> Response:
        from startup_foundry.errors import ReferenceError
        from startup_foundry.workspace_records import state_reference, work_reference

        with factory() as session:
            entity = (
                session.get(Idea, identity)
                if subject == "idea"
                else session.get(Venture, identity)
            )
            if not entity:
                raise ReferenceError("Workspace subject missing")
            data = (
                state_reference(session, entity.workspace_id, record_id)
                if is_review
                else work_reference(session, entity.workspace_id, record_id)
            )
            assert data
            next_work = (
                work_reference(
                    session, entity.workspace_id, data.get("next_work_item_id")
                )
                if is_review
                else None
            )
        kind = "ideas" if subject == "idea" else "ventures"
        return render(
            request,
            "workspace_record.html",
            nav=kind,
            subject=subject,
            subject_id=identity,
            record=data,
            is_review=is_review,
            next_work=next_work,
            workspace_url=DetailQuery.parse(request).url(
                "/" + kind + "/" + identity, kind=kind, tab="work"
            ),
        )

    @app.get("/ideas/{identity}/work/{work_id}")
    def idea_work(request: Request, identity: str, work_id: str) -> Response:
        return scoped_record(request, identity, work_id, "idea", False)

    @app.get("/ventures/{identity}/work/{work_id}")
    def venture_work(request: Request, identity: str, work_id: str) -> Response:
        return scoped_record(request, identity, work_id, "venture", False)

    @app.get("/ideas/{identity}/reviews/{review_id}")
    def idea_review(request: Request, identity: str, review_id: str) -> Response:
        return scoped_record(request, identity, review_id, "idea", True)

    @app.get("/ventures/{identity}/reviews/{review_id}")
    def venture_review(request: Request, identity: str, review_id: str) -> Response:
        return scoped_record(request, identity, review_id, "venture", True)

    @app.post("/api/ideas/{identity}/intake")
    def idea_intake(identity: str, payload: IntakeRequest) -> JSON:
        return intake.request("idea", identity, payload)

    @app.post("/api/ventures/{identity}/intake")
    def venture_intake(identity: str, payload: IntakeRequest) -> JSON:
        return intake.request("venture", identity, payload)

    @app.get("/ideas/{identity}/intake-handoff")
    def idea_intake_handoff(identity: str) -> JSON | None:
        return intake.handoff("idea", identity)

    @app.get("/ventures/{identity}/intake-handoff")
    def venture_intake_handoff(identity: str) -> JSON | None:
        return intake.handoff("venture", identity)

    @app.post("/api/ideas/{identity}/intake/claim")
    def claim_idea_intake(identity: str, payload: ClaimInput) -> JSON:
        return intake.claim("idea", identity, payload)

    @app.post("/api/ventures/{identity}/intake/claim")
    def claim_venture_intake(identity: str, payload: ClaimInput) -> JSON:
        return intake.claim("venture", identity, payload)

    @app.post("/api/ideas/{identity}/intake/release")
    def release_idea_intake(identity: str, payload: ReleaseInput) -> JSON:
        return intake.release("idea", identity, payload)

    @app.post("/api/ventures/{identity}/intake/release")
    def release_venture_intake(identity: str, payload: ReleaseInput) -> JSON:
        return intake.release("venture", identity, payload)

    @app.post("/api/ideas/{identity}/intake/complete")
    def complete_idea_intake(identity: str, payload: IntakeCompletion) -> JSON:
        return intake.complete("idea", identity, payload)

    @app.post("/api/ventures/{identity}/intake/complete")
    def complete_venture_intake(identity: str, payload: IntakeCompletion) -> JSON:
        return intake.complete("venture", identity, payload)

    @app.get("/requests/{identity}")
    def request_detail(request: Request, identity: str) -> Response:
        from startup_foundry.workspace_records import workspace_path

        detail = inputs.show(identity)
        navigation = DetailQuery.parse(request)
        with factory() as session:
            owner_path = workspace_path(session, detail["workspace_id"])
            kind = "ideas" if owner_path.startswith("/ideas/") else "ventures"
            for target in detail["targets"]:
                target["url"] = navigation.url(
                    workspace_path(session, target["workspace_id"]), kind=kind
                )
        return render(
            request,
            "request.html",
            nav="requests",
            detail=detail,
            workspace_return=navigation.url(owner_path, kind=kind, tab="work")
            if navigation.return_to
            else None,
            preview=inputs.preview(),
        )

    @app.get("/api/inputs")
    def list_inputs(
        status: str | None = None,
        workspace_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> JSON:
        return inputs.list(
            status=status, workspace_id=workspace_id, limit=limit, offset=offset
        )

    @app.get("/api/inputs/preview")
    def preview() -> JSON:
        return inputs.preview()

    @app.post("/api/inputs/sync")
    def sync(payload: SyncInput) -> JSON:
        from startup_foundry.errors import ValidationError

        if payload.reconciliation not in {None, "keep_ui", "use_file"}:
            raise ValidationError("Choose keep_ui or use_file")
        return inputs.sync(payload.preview, reconciliation=payload.reconciliation)  # type: ignore[arg-type]

    @app.get("/api/inputs/{identity}")
    def show(identity: str) -> JSON:
        return inputs.show(identity)

    @app.post("/api/inputs/{identity}/responses")
    def submit(identity: str, payload: ResponseInput) -> JSON:
        return inputs.submit(identity, payload)

    @app.post("/api/inputs/{identity}/claim")
    def claim(identity: str, payload: ClaimInput) -> JSON:
        return inputs.claim(identity, payload)

    @app.post("/api/inputs/{identity}/release")
    def release(identity: str, payload: ReleaseInput) -> JSON:
        return inputs.release(identity, payload)

    @app.post("/api/inputs/{identity}/complete")
    def complete(identity: str, payload: ReviewResult) -> JSON:
        return inputs.complete(identity, payload)

    @app.post("/api/inputs/{identity}/dependencies")
    def dependency(identity: str, payload: DependencyInput) -> JSON:
        return inputs.link_dependency(identity, payload)

    @app.get("/requests/{identity}/handoff")
    def handoff(identity: str) -> Response:
        return JSONResponse(
            inputs.handoff(identity),
            headers={
                "Content-Disposition": f'attachment; filename="{identity}-handoff.json"'
            },
        )

    @app.get("/api/ventures/{identity}/scores")
    def venture_scores(identity: str, request: Request) -> JSON:
        return scores.show(identity, DetailQuery.parse(request).card_id)

    @app.post("/api/venture-scores")
    def assess(payload: VentureAssessmentInput) -> JSON:
        return scores.assess(payload)

    @app.get("/proposals")
    def proposal_list(request: Request, state: str | None = None) -> Response:
        return render(
            request,
            "proposals.html",
            nav="proposals",
            proposals=proposals.list(state=state),
        )

    @app.get("/proposals/{identity}")
    def proposal_detail(request: Request, identity: str) -> Response:
        p = proposals.show(identity)
        sources = []
        from startup_foundry.reviews import ReviewService

        for source in p["content"]["source_state"]["sources"]:
            scored = (
                VentureScoringService(factory).show(source["id"])["current"]
                if source["kind"] == "venture"
                else next(
                    (
                        a
                        for a in ScoringService(factory).show(source["id"])["history"]
                        if a["scorecard_id"] == REVIEWED
                    ),
                    None,
                )
            )
            sources.append(
                {
                    **source,
                    "score": scored,
                    "state": ReviewService(factory).show(source["workspace_id"])[
                        "current"
                    ],
                }
            )
        return render(
            request,
            "proposal.html",
            nav="proposals",
            proposal=p,
            proposal_sources=sources,
        )

    @app.get("/api/proposals/{identity}")
    def proposal_show(identity: str) -> JSON:
        return proposals.show(identity)

    @app.post("/api/proposals")
    def proposal_create(payload: FusionInput) -> JSON:
        return proposals.create(payload)

    @app.post("/api/proposals/{identity}/revise")
    def proposal_revise(identity: str, payload: ReviseInput) -> JSON:
        return proposals.revise(identity, payload)

    @app.post("/api/proposals/{identity}/resolve")
    def proposal_resolve(identity: str, payload: ResolveInput) -> JSON:
        return proposals.resolve(identity, payload)

    @app.post("/api/ventures/{identity}/config")
    def configure(identity: str, payload: ConfigInput) -> JSON:
        return modules.configure(identity, payload)

    @app.post("/api/ventures/{identity}/metrics")
    def metrics(identity: str, payload: MetricsInput) -> JSON:
        return modules.metrics(identity, payload)

    @app.post("/api/ventures/{identity}/issues")
    def issue(identity: str, payload: IssueInput) -> JSON:
        return modules.issue(identity, payload)

    @app.get("/ventures/{identity}/events/{event_id}")
    def event_detail(request: Request, identity: str, event_id: str) -> Response:
        from fastapi.encoders import jsonable_encoder

        from startup_foundry.application import FoundryApplication
        from startup_foundry.domain import VentureAssessment
        from startup_foundry.errors import ReferenceError

        with factory() as session:
            v, w = FoundryApplication._venture(session, identity)
            record = (
                session.get(Artifact, event_id)
                or session.get(AuditEvent, event_id)
                or session.get(WorkspaceReview, event_id)
                or session.get(VentureAssessment, event_id)
                or session.get(Decision, event_id)
                or session.get(Evidence, event_id)
                or session.get(StepRun, event_id)
            )
            if record is None or (
                record.venture_id != v.id
                if isinstance(record, VentureAssessment)
                else record.workspace_id != w.id
            ):
                raise ReferenceError("Event does not belong to selected venture")
            data = jsonable_encoder(
                {c.name: getattr(record, c.name) for c in record.__table__.columns}
            )
            from startup_foundry.workspace_records import work_reference

            linked_work = (
                work_reference(session, w.id, record.next_work_item_id)
                if isinstance(record, WorkspaceReview)
                else None
            )
        return render(
            request,
            "workspace_event.html",
            nav="ventures",
            event=data,
            event_kind=type(record).__name__,
            linked_work=linked_work,
            subject_id=identity,
            history_url=DetailQuery.parse(request).url(
                "/ventures/" + identity, kind="ventures", tab="history"
            ),
        )
