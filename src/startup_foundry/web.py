"""Loopback-only operator console; all mutations use application services."""

from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as ContractError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from startup_foundry.application import FoundryApplication
from startup_foundry.console_commands import attachment_roots
from startup_foundry.decision_console import portfolio_attention
from startup_foundry.domain import (
    Disposition,
    InvestigationStage,
    ProductMaturity,
    VentureStage,
)
from startup_foundry.errors import (
    ConflictError,
    ReferenceError,
    StartupFoundryError,
    VentureNotFoundError,
)
from startup_foundry.human_inputs import HumanInputService
from startup_foundry.outreach import DraftInput, OutcomeInput, OutreachService
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.projects import ExistingProjectInput, ExistingProjectService
from startup_foundry.proposals import ProposalService
from startup_foundry.repository import SessionFactory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService
from startup_foundry.steps import STEP_CATALOG, StepService
from startup_foundry.views import PortfolioQuery, PortfolioViewService
from startup_foundry.workspace_console import (
    context as workspace_context,
)
from startup_foundry.workspace_console import (
    install_routes,
    venture_data,
)


class IdeaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=20_000)
    customer: str = Field(default="", max_length=5000)
    validation_test: str = Field(default="", max_length=5000)
    parent_ids: list[str] = Field(default_factory=list, max_length=10)
    derivation_reason: str = Field(default="", max_length=5000)


class VentureInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=240)
    objective: str = Field(min_length=1, max_length=20_000)


class PromotionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # An explicit distinct ID means a deliberately separate venture.
    venture_id: str | None = Field(default=None, min_length=1, max_length=36)


class StepInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject: str
    subject_id: str = Field(min_length=1, max_length=36)
    kind: str
    request_key: str = Field(min_length=1, max_length=160)


class DraftCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    venture_id: str
    request_key: str
    draft: DraftInput


class DraftRevisionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=200)
    draft: DraftInput


def safe_link(value: str) -> str | None:
    return value if urlsplit(value).scheme in {"http", "https"} else None


def create_app(factory: SessionFactory, requests_directory: Path) -> FastAPI:
    app = FastAPI(
        title="Foundry local console", docs_url=None, redoc_url=None, openapi_url=None
    )
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]"]
    )
    token = secrets.token_urlsafe(32)
    root = Path(__file__).parent
    templates = Jinja2Templates(directory=root / "templates")
    templates.env.filters["safe_link"] = safe_link
    templates.env.filters["pretty"] = lambda value: (
        str(value).replace("_", " ").capitalize()
    )
    app.mount("/static", StaticFiles(directory=root / "static"), name="static")
    ventures = FoundryApplication(factory)
    portfolio = PortfolioService(factory)
    steps = StepService(factory, requests_directory)
    scores = ScoringService(factory)
    reviews = ReviewService(factory)
    views = PortfolioViewService(factory)
    human_inputs = HumanInputService(factory, requests_directory)
    projects = ExistingProjectService(factory)
    outreach = OutreachService(factory, attachment_roots())

    def venture_workspace(identity: str) -> str:
        with factory() as session:
            return FoundryApplication._venture(session, identity)[1].id

    def query_for(request: Request, limit: int) -> PortfolioQuery:
        values = {k: v for k, v in request.query_params.items() if v != ""}
        values.setdefault("limit", str(limit))
        return PortfolioQuery.model_validate(values)

    @app.exception_handler(ContractError)
    async def contract_error(request: Request, exc: ContractError) -> Response:
        return JSONResponse({"error": str(exc)}, status_code=400)

    @app.middleware("http")
    async def local_boundary(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            expected_origin = str(request.base_url).rstrip("/")
            if (
                origin is not None and origin != expected_origin
            ) or not secrets.compare_digest(
                request.headers.get("x-foundry-token", ""), token
            ):
                return JSONResponse(
                    {"error": "Local mutation token and same origin required"},
                    status_code=403,
                )
            length = request.headers.get("content-length", "0")
            if (
                not length.isdigit()
                or int(length) > 100_000
                or len(await request.body()) > 100_000
            ):
                return JSONResponse(
                    {"error": "Request body too large"}, status_code=413
                )
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "object-src 'none'; frame-ancestors 'none'; "
            "base-uri 'none'; form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(StartupFoundryError)
    async def domain_error(request: Request, exc: StartupFoundryError) -> Response:
        status = (
            409
            if isinstance(exc, ConflictError)
            else 404
            if isinstance(exc, (ReferenceError, VentureNotFoundError))
            else 400
        )
        if request.url.path.startswith("/api/"):
            return JSONResponse({"error": str(exc)}, status_code=status)
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"token": token, "message": str(exc), "nav": ""},
            status_code=status,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError) -> Response:
        return JSONResponse(
            {
                "error": "Record conflict"
                if isinstance(exc, IntegrityError)
                else "Database operation failed; retry or inspect local configuration"
            },
            status_code=409 if isinstance(exc, IntegrityError) else 500,
        )

    def render(request: Request, name: str, **context: Any) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=name,
            context={
                "token": token,
                "request_key": str(uuid4()),
                "review_options": {
                    "investigation_stage": [e.value for e in InvestigationStage],
                    "product_maturity": [e.value for e in ProductMaturity],
                    "disposition": [e.value for e in Disposition],
                },
                "factor_options": FACTORS,
                "scorecards": scores.list_scorecards(),
                "pagination_url": lambda offset: str(
                    request.url.include_query_params(offset=offset)
                ),
                **context,
            },
        )

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> Response:
        return render(
            request,
            "dashboard.html",
            nav="overview",
            attention=portfolio_attention(factory),
            ventures=views.list("venture", PortfolioQuery(limit=6)),
            needs_you=human_inputs.list(status="needs_you"),
            pending_proposals=len(
                ProposalService(factory).list(state="proposed")["items"]
            ),
            pending_answers=human_inputs.list(status="awaiting_review"),
            ready_work=views.list(
                "venture", PortfolioQuery(blocker="ready", continued="exclude", limit=1)
            )["total"],
            ideas=portfolio.list_ideas(limit=1),
            sources=portfolio.list_sources(limit=1),
            runs=steps.list_runs(limit=6),
        )

    @app.get("/ideas", response_class=HTMLResponse)
    def idea_list(request: Request) -> Response:
        query = query_for(request, 30)
        return render(
            request,
            "ideas.html",
            nav="ideas",
            q=query.q,
            page=views.list("idea", query),
            filters=query.model_dump(mode="json"),
        )

    @app.get("/new", response_class=HTMLResponse)
    def new(request: Request, parent_id: str = "") -> Response:
        parent = portfolio.show_idea(parent_id) if parent_id else None
        return render(request, "new.html", nav="ideas", parent=parent)

    @app.get("/ideas/{identity}", response_class=HTMLResponse)
    def idea_detail(request: Request, identity: str) -> Response:
        return render(
            request,
            "idea.html",
            nav="ideas",
            idea=portfolio.show_idea(identity),
            **workspace_context(
                factory,
                human_inputs,
                request,
                portfolio.show_idea(identity)["workspace_id"],
                idea_id=identity,
            ),
            subject="idea",
            subject_id=identity,
            catalog=STEP_CATALOG,
            runs=steps.list_runs("idea", identity, limit=10),
        )

    @app.get("/ventures", response_class=HTMLResponse)
    def venture_list(request: Request) -> Response:
        query = query_for(request, 30)
        return render(
            request,
            "ventures.html",
            nav="ventures",
            q=query.q,
            page=views.list("venture", query),
            filters=query.model_dump(mode="json"),
        )

    @app.get("/ventures/{identity}", response_class=HTMLResponse)
    def venture_detail(request: Request, identity: str) -> Response:
        return render(
            request,
            "venture.html",
            nav="ventures",
            detail=venture_data(
                factory, identity, request.query_params.get("tab", "overview")
            ),
            **workspace_context(
                factory,
                human_inputs,
                request,
                venture_workspace(identity),
                venture_id=identity,
            ),
            review=reviews.show(venture_workspace(identity)),
            checkpoint=projects.show(identity),
            drafts=outreach.list(identity),
            subject="venture",
            subject_id=identity,
            catalog=STEP_CATALOG,
            runs=steps.list_runs("venture", identity, limit=10),
        )

    @app.get("/ventures/{identity}/records/{collection}", response_class=HTMLResponse)
    def records(
        request: Request, identity: str, collection: str, offset: int = 0
    ) -> Response:
        return render(
            request,
            "records.html",
            nav="ventures",
            subject_id=identity,
            collection=collection,
            page=ventures.list_records(identity, collection, offset=offset, limit=30),
        )

    @app.get("/sources", response_class=HTMLResponse)
    def sources(request: Request, q: str = "", offset: int = 0) -> Response:
        return render(
            request,
            "sources.html",
            nav="sources",
            q=q,
            page=portfolio.list_sources(query=q, offset=offset, limit=30),
        )

    @app.get("/steps", response_class=HTMLResponse)
    def step_list(request: Request, offset: int = 0) -> Response:
        return render(
            request,
            "steps.html",
            nav="steps",
            page=steps.list_runs(offset=offset, limit=30),
        )

    @app.get("/steps/{identity}", response_class=HTMLResponse)
    def step_detail(request: Request, identity: str) -> Response:
        return render(request, "step.html", nav="steps", run=steps.show_run(identity))

    @app.get("/requests", response_class=HTMLResponse)
    def requests(request: Request) -> Response:
        status = request.query_params.get("status", "needs_you")
        return render(
            request,
            "requests.html",
            nav="requests",
            status=status,
            page=human_inputs.list(status=status),
            preview=human_inputs.preview(),
        )

    @app.get("/api/ventures")
    def api_ventures(request: Request) -> dict[str, Any]:
        return views.list("venture", query_for(request, 50))

    @app.get("/api/ideas")
    def api_ideas(request: Request) -> dict[str, Any]:
        return views.list("idea", query_for(request, 50))

    @app.get("/help", response_class=HTMLResponse)
    def help_page(request: Request) -> Response:
        return render(request, "help.html", nav="help")

    @app.get("/existing-project", response_class=HTMLResponse)
    def project_form(
        request: Request, idea_id: str = "", venture_id: str = ""
    ) -> Response:
        idea = portfolio.show_idea(idea_id) if idea_id else None
        detail = ventures.show_venture(venture_id) if venture_id else None
        current = (
            reviews.show(venture_workspace(venture_id))["current"] if detail else None
        )
        return render(
            request,
            "existing_project.html",
            nav="ventures",
            idea=idea,
            detail=detail,
            expected_revision=current["revision"] if current else 0,
        )

    @app.get("/outreach", response_class=HTMLResponse)
    def outreach_list(request: Request) -> Response:
        return render(request, "outreach.html", nav="outreach", drafts=outreach.list())

    @app.get("/outreach/new", response_class=HTMLResponse)
    def outreach_new(request: Request, venture_id: str = "") -> Response:
        return render(
            request,
            "draft.html",
            nav="outreach",
            draft=None,
            ventures=ventures.list_ventures(limit=500),
            selected_venture=venture_id,
            attachment_choices=[],
        )

    @app.get("/outreach/{identity}", response_class=HTMLResponse)
    def outreach_detail(request: Request, identity: str) -> Response:
        draft = outreach.show(identity)
        detail = ventures.show_venture(draft["venture_id"])
        return render(
            request,
            "draft.html",
            nav="outreach",
            draft=draft,
            attachment_choices=detail["artifacts"],
            selected_venture=draft["venture_id"],
        )

    @app.get("/outreach/{identity}/export")
    def outreach_export(identity: str, format: str = "text") -> Response:
        if format not in {"text", "eml"}:
            from startup_foundry.errors import ValidationError

            raise ValidationError("Choose text or eml export")
        content = outreach.export(identity, format="eml" if format == "eml" else "text")
        return Response(
            content,
            media_type="message/rfc822"
            if format == "eml"
            else "text/plain; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="draft-{identity}.'
                    f'{"eml" if format == "eml" else "txt"}"'
                )
            },
        )

    @app.post("/api/reviews", status_code=201)
    def append_review(payload: ReviewInput) -> dict[str, Any]:
        return reviews.append(payload)

    @app.post("/api/scores", status_code=201)
    def assess_idea(payload: AssessmentInput) -> dict[str, Any]:
        return scores.assess(payload)

    @app.post("/api/existing-projects", status_code=201)
    def intake_project(payload: ExistingProjectInput) -> dict[str, Any]:
        return projects.intake(payload)

    @app.post("/api/outreach", status_code=201)
    def create_draft(payload: DraftCreateInput) -> dict[str, Any]:
        return outreach.create(
            payload.venture_id, payload.draft, request_key=payload.request_key
        )

    @app.post("/api/outreach/{identity}")
    def revise_draft(identity: str, payload: DraftRevisionInput) -> dict[str, Any]:
        return outreach.revise(
            identity,
            payload.draft,
            expected_version=payload.expected_version,
            actor=payload.actor,
        )

    @app.post("/api/outreach/{identity}/outcomes", status_code=201)
    def draft_outcome(identity: str, payload: OutcomeInput) -> dict[str, Any]:
        return outreach.record_outcome(identity, payload)

    @app.get("/api/steps")
    def api_steps(limit: int = 50, offset: int = 0) -> dict[str, Any]:
        return steps.list_runs(limit=limit, offset=offset)

    @app.post("/api/ideas", status_code=201)
    def create_idea(payload: IdeaInput) -> dict[str, Any]:
        return portfolio.create_idea(IdeaDraft(**payload.model_dump()))

    @app.post("/api/ventures", status_code=201)
    def create_venture(payload: VentureInput) -> dict[str, object]:
        return ventures.create_venture(
            venture_id=str(uuid4()),
            name=payload.name,
            objective=payload.objective,
            stage=VentureStage.DISCOVERY,
        )

    @app.post("/api/ideas/{identity}/promote", status_code=201)
    def promote(identity: str, payload: PromotionInput | None = None) -> dict[str, Any]:
        return portfolio.promote_idea(
            identity, venture_id=payload.venture_id if payload else None
        )

    @app.post("/api/steps")
    def start_step(payload: StepInput) -> dict[str, Any]:
        return steps.start(
            payload.subject,
            payload.subject_id,
            payload.kind,
            request_key=payload.request_key,
        )

    install_routes(app, factory, requests_directory, render)
    from startup_foundry.decision_console import install_decision_routes

    install_decision_routes(app, factory, render)
    return app
