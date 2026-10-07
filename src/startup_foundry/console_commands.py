"""CLI extensions for the local operator workflow."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any

from sqlalchemy.engine import make_url

from startup_foundry.application import FoundryApplication
from startup_foundry.config import data_directory
from startup_foundry.inputs import read_input
from startup_foundry.outreach import DraftInput, OutcomeInput, OutreachService
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.projects import ExistingProjectInput, ExistingProjectService
from startup_foundry.repository import SessionFactory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import (
    ORIGINAL,
    AssessmentInput,
    ScorecardInput,
    ScoringService,
)
from startup_foundry.steps import STEP_CATALOG, StepService
from startup_foundry.views import PortfolioQuery, PortfolioViewService


def requests_directory() -> Path:
    import os

    checkout = Path(__file__).resolve().parents[2]
    default = (
        checkout / "requests"
        if (checkout / "pyproject.toml").is_file()
        else data_directory() / "requests"
    )
    return (
        Path(os.environ.get("FOUNDRY_REQUESTS_DIR", str(default)))
        .expanduser()
        .resolve()
    )


def add_console_parsers(resources: Any) -> None:
    from startup_foundry.decision_commands import add_parsers as add_decision_parsers
    from startup_foundry.revamp_commands import add_parsers

    add_decision_parsers(resources)
    add_parsers(resources)
    idea = resources.add_parser(
        "idea", help="Create, derive, inspect and promote ideas"
    )
    actions = idea.add_subparsers(dest="action", required=True)
    listing = actions.add_parser("list")
    add_pagination(listing)
    listing.add_argument("--query", default="")
    add_portfolio_filters(listing)
    show = actions.add_parser("show")
    show.add_argument("--id", required=True)
    create = actions.add_parser("create")
    create.add_argument("--id")
    create.add_argument("--title", required=True)
    create.add_argument("--description", required=True)
    create.add_argument("--customer", default=None)
    create.add_argument("--validation-test", default=None)
    create.add_argument("--parent-id", action="append", default=[])
    create.add_argument("--derivation-reason", default=None)
    promote = actions.add_parser("promote")
    promote.add_argument("--id", required=True)
    promote.add_argument("--venture-id")
    source = resources.add_parser("source")
    source_actions = source.add_subparsers(dest="action", required=True)
    listing = source_actions.add_parser("list")
    listing.add_argument("--query", default="")
    add_pagination(listing)
    portfolio = resources.add_parser("portfolio")
    imports = portfolio.add_subparsers(dest="action", required=True).add_parser(
        "import"
    )
    imports.add_argument("--csv-directory", required=True)
    imports.add_argument("--campaign-directory", required=True)
    steps = resources.add_parser("step")
    step_actions = steps.add_subparsers(dest="action", required=True)
    step_actions.add_parser("catalog")
    listing = step_actions.add_parser("list")
    listing.add_argument("--subject", choices=["idea", "venture"])
    listing.add_argument("--subject-id")
    add_pagination(listing)
    show = step_actions.add_parser("show")
    show.add_argument("--id", required=True)
    start = step_actions.add_parser("start")
    start.add_argument("--subject", choices=["idea", "venture"], required=True)
    start.add_argument("--subject-id", required=True)
    start.add_argument("--kind", choices=list(STEP_CATALOG), required=True)
    start.add_argument("--request-key", required=True)
    recover = step_actions.add_parser("recover")
    recover.add_argument("--id", required=True)
    recover.add_argument("--reason", required=True)
    storage = resources.add_parser("storage")
    storage_actions = storage.add_subparsers(dest="action", required=True)
    storage_actions.add_parser("info")
    backup = storage_actions.add_parser("backup")
    backup.add_argument("--output", required=True)
    for resource in ("score", "scorecard", "review", "existing-project", "outreach"):
        parser = resources.add_parser(resource)
        actions = parser.add_subparsers(dest="action", required=True)
        if resource == "score":
            imports = actions.add_parser("import-original")
            imports.add_argument("--sources-directory", required=True)
            show = actions.add_parser("show")
            show.add_argument("--idea-id", required=True)
            assess = actions.add_parser("assess")
            assess.add_argument("--input", required=True)
            sensitivity = actions.add_parser("sensitivity")
            sensitivity.add_argument("--idea-id", required=True)
            sensitivity.add_argument("--scorecard-id", default=ORIGINAL)
            rank = actions.add_parser("rank")
            rank.add_argument("--scorecard-id", required=True)
            rank.add_argument("--label", required=True)
        elif resource == "scorecard":
            actions.add_parser("list")
            actions.add_parser("import").add_argument("--input", required=True)
        elif resource == "review":
            actions.add_parser("import-legacy")
            actions.add_parser("append").add_argument("--input", required=True)
            actions.add_parser("show").add_argument("--workspace-id", required=True)
        elif resource == "existing-project":
            actions.add_parser("intake").add_argument("--input", required=True)
            actions.add_parser("show").add_argument("--venture-id", required=True)
        else:
            listing = actions.add_parser("list")
            listing.add_argument("--venture-id")
            create = actions.add_parser("create")
            create.add_argument("--venture-id", required=True)
            create.add_argument("--request-key", required=True)
            create.add_argument("--input", required=True)
            show = actions.add_parser("show")
            show.add_argument("--id", required=True)
            revise = actions.add_parser("revise")
            revise.add_argument("--id", required=True)
            revise.add_argument("--input", required=True)
            revise.add_argument("--expected-version", required=True, type=int)
            revise.add_argument("--actor", required=True)
            export = actions.add_parser("export")
            export.add_argument("--id", required=True)
            export.add_argument("--format", choices=["text", "eml"], default="text")
            export.add_argument("--output", required=True)
            outcome = actions.add_parser("record-outcome")
            outcome.add_argument("--id", required=True)
            outcome.add_argument("--input", required=True)
    ui = resources.add_parser("ui", help="Serve the local human console on loopback")
    ui.set_defaults(action="serve")
    ui.add_argument("--port", type=int, default=8765)


def add_pagination(parser: ArgumentParser) -> None:
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)


def attachment_roots() -> list[Path]:
    import os

    default = str(data_directory() / "outreach-attachments")
    return [
        Path(p)
        for p in os.environ.get("FOUNDRY_ATTACHMENT_ROOTS", default).split(os.pathsep)
        if p
    ]


def add_portfolio_filters(parser: ArgumentParser) -> None:
    for field in (
        "disposition",
        "investigation-stage",
        "product-maturity",
        "blocker",
        "min-score",
    ):
        parser.add_argument("--" + field, type=float if field == "min-score" else str)
    parser.add_argument("--continued", choices=["all", "exclude"], default="all")
    parser.add_argument("--score-view", default="reviewed")
    parser.add_argument("--criterion", default="priority")
    parser.add_argument("--sort", default="score")
    parser.add_argument("--direction", default="desc")


def portfolio_query(args: Namespace) -> PortfolioQuery:
    from pydantic import ValidationError as InputError

    from startup_foundry.errors import ValidationError

    values = {
        key: getattr(args, key)
        for key in PortfolioQuery.model_fields
        if hasattr(args, key)
    }
    values["q"] = getattr(args, "query", "")
    try:
        return PortfolioQuery.model_validate(values)
    except InputError as exc:
        raise ValidationError(str(exc)) from exc


def dispatch(
    factory: SessionFactory, args: Namespace, database_url: str
) -> dict[str, Any]:
    from startup_foundry.decision_commands import (
        RESOURCES,
    )
    from startup_foundry.decision_commands import (
        dispatch as decision_dispatch,
    )

    if args.resource in RESOURCES:
        return decision_dispatch(factory, args)
    if args.resource in {"input", "venture-score", "proposal", "workspace", "intake"}:
        from startup_foundry.revamp_commands import dispatch as revamp_dispatch

        return revamp_dispatch(factory, args, requests_directory())
    portfolio = PortfolioService(factory)
    steps = StepService(factory, requests_directory())
    action = (args.resource, args.action)
    scores = ScoringService(factory)
    reviews = ReviewService(factory)
    projects = ExistingProjectService(factory)
    outreach = OutreachService(factory, attachment_roots())
    if action == ("score", "import-original"):
        return scores.import_original(Path(args.sources_directory))
    if action == ("score", "show"):
        return scores.show(args.idea_id)
    if action == ("score", "assess"):
        return scores.assess(read_input(AssessmentInput, args.input))
    if action == ("score", "sensitivity"):
        return scores.sensitivity(args.idea_id, args.scorecard_id)
    if action == ("score", "rank"):
        return scores.rank(args.scorecard_id, args.label)
    if action == ("scorecard", "list"):
        return scores.list_scorecards()
    if action == ("scorecard", "import"):
        return scores.import_scorecard(read_input(ScorecardInput, args.input))
    if action == ("review", "show"):
        return reviews.show(args.workspace_id)
    if action == ("review", "append"):
        return reviews.append(read_input(ReviewInput, args.input))
    if action == ("review", "import-legacy"):
        return reviews.import_legacy()
    if action == ("existing-project", "intake"):
        return projects.intake(read_input(ExistingProjectInput, args.input))
    if action == ("existing-project", "show"):
        return projects.show(args.venture_id)
    if action == ("outreach", "list"):
        return outreach.list(args.venture_id)
    if action == ("outreach", "show"):
        return outreach.show(args.id)
    if action == ("outreach", "create"):
        return outreach.create(
            args.venture_id,
            read_input(DraftInput, args.input),
            request_key=args.request_key,
        )
    if action == ("outreach", "revise"):
        return outreach.revise(
            args.id,
            read_input(DraftInput, args.input),
            expected_version=args.expected_version,
            actor=args.actor,
        )
    if action == ("outreach", "record-outcome"):
        return outreach.record_outcome(args.id, read_input(OutcomeInput, args.input))
    if action == ("outreach", "export"):
        from startup_foundry.errors import ConflictError, ValidationError

        content = outreach.export(args.id, format=args.format)
        try:
            with Path(args.output).open("xb") as stream:
                stream.write(content)
        except FileExistsError as exc:
            raise ConflictError("Export file exists; choose a new output") from exc
        except OSError as exc:
            raise ValidationError("Could not write export") from exc
        return {"output": args.output, "mode": "manual", "sent": False}
    if action == ("idea", "list"):
        return PortfolioViewService(factory).list("idea", portfolio_query(args))
    if action == ("idea", "show"):
        return portfolio.show_idea(args.id)
    if action == ("idea", "create"):
        return portfolio.create_idea(
            IdeaDraft(
                title=args.title,
                description=args.description,
                customer=args.customer or "",
                validation_test=args.validation_test or "",
                parent_ids=args.parent_id,
                derivation_reason=args.derivation_reason or "",
            ),
            idea_id=args.id,
        )
    if action == ("idea", "promote"):
        return portfolio.promote_idea(args.id, venture_id=args.venture_id)
    if action == ("source", "list"):
        return portfolio.list_sources(
            query=args.query, limit=args.limit, offset=args.offset
        )
    if action == ("portfolio", "import"):
        return portfolio.import_campaign(
            Path(args.csv_directory), Path(args.campaign_directory)
        )
    if action == ("step", "catalog"):
        return {"steps": STEP_CATALOG}
    if action == ("step", "list"):
        return steps.list_runs(
            args.subject, args.subject_id, limit=args.limit, offset=args.offset
        )
    if action == ("step", "show"):
        return steps.show_run(args.id)
    if action == ("step", "start"):
        return steps.start(
            args.subject, args.subject_id, args.kind, request_key=args.request_key
        )
    if action == ("step", "recover"):
        return steps.recover_interrupted(args.id, args.reason)
    if action == ("storage", "info"):
        url = make_url(database_url)
        return {
            "database": url.render_as_string(hide_password=True),
            "backend": url.get_backend_name(),
            "requests_directory": str(requests_directory()),
        }
    if action == ("venture", "list"):
        return PortfolioViewService(factory).list("venture", portfolio_query(args))
    if args.action == "list" and args.resource in {
        "evidence",
        "assumption",
        "decision",
        "work-item",
        "artifact",
        "experiment",
    }:
        collection = {
            "evidence": "evidence",
            "assumption": "assumptions",
            "decision": "decisions",
            "work-item": "work_items",
            "artifact": "artifacts",
            "experiment": "experiments",
        }[args.resource]
        return FoundryApplication(factory).list_records(
            args.venture_id, collection, limit=args.limit, offset=args.offset
        )
    raise RuntimeError("Unhandled console command")
