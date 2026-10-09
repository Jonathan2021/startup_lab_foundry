"""Command adapter for the first Foundry venture workflow."""

from __future__ import annotations

import json
import logging
import os
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Mapping, Sequence
from enum import StrEnum
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from startup_foundry.application import FoundryApplication, JsonObject, required_text
from startup_foundry.config import Settings, load_settings
from startup_foundry.console_commands import (
    add_console_parsers,
    add_pagination,
    add_portfolio_filters,
    check_idea_create,
    dispatch,
    requests_directory,
)
from startup_foundry.domain import (
    ArtifactKind,
    AssessmentOutcome,
    AssumptionKind,
    ConfidenceLevel,
    DecisionKind,
    EvidenceKind,
    VentureStage,
    WorkItemKind,
    WorkItemStatus,
)
from startup_foundry.errors import (
    ConfigurationError,
    StartupFoundryError,
    ValidationError,
)
from startup_foundry.logging_config import configure_logging, correlation_id_var
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory

logger = logging.getLogger(__name__)


def _enum_values(enum_type: type[StrEnum]) -> list[str]:
    return [str(item) for item in enum_type]


def build_parser() -> ArgumentParser:
    """Build the documented Foundry command grammar."""

    parser = ArgumentParser(prog="foundry", description="Foundry CLI")
    parser.add_argument("--store", help="SQLite database path", default=None)
    parser.add_argument(
        "--debug", help="Enable debug logging", action="store_true", default=None
    )
    parser.add_argument(
        "--sql-echo",
        "--sql_echo",
        dest="sql_echo",
        help="Enable SQL echo",
        action="store_true",
        default=None,
    )
    resources = parser.add_subparsers(dest="resource", required=True)

    venture = resources.add_parser("venture", help="Manage ventures")
    venture_actions = venture.add_subparsers(dest="action", required=True)
    venture_create = venture_actions.add_parser("create")
    _identity(venture_create)
    venture_create.add_argument("--name", required=True)
    venture_create.add_argument("--objective", required=True)
    venture_create.add_argument(
        "--stage", required=True, choices=_enum_values(VentureStage)
    )
    venture_show = venture_actions.add_parser("show")
    _identity(venture_show)

    assumption = resources.add_parser("assumption", help="Manage assumptions")
    assumption_actions = assumption.add_subparsers(dest="action", required=True)
    assumption_add = assumption_actions.add_parser("add")
    _identity(assumption_add)
    assumption_add.add_argument("--venture-id", required=True)
    assumption_add.add_argument("--statement", required=True)
    assumption_add.add_argument(
        "--kind", required=True, choices=_enum_values(AssumptionKind)
    )
    assumption_add.add_argument(
        "--importance", required=True, type=int, choices=range(1, 6)
    )
    assumption_add.add_argument(
        "--uncertainty", required=True, type=int, choices=range(1, 6)
    )
    assumption_assess = assumption_actions.add_parser("assess")
    _identity(assumption_assess)
    assumption_assess.add_argument("--assumption-id", required=True)
    assumption_assess.add_argument(
        "--evidence-id", required=True, action="append", dest="evidence_ids"
    )
    assumption_assess.add_argument(
        "--outcome", required=True, choices=_enum_values(AssessmentOutcome)
    )
    assumption_assess.add_argument(
        "--confidence", required=True, choices=_enum_values(ConfidenceLevel)
    )
    assumption_assess.add_argument("--rationale", required=True)

    evidence = resources.add_parser("evidence", help="Manage evidence")
    evidence_actions = evidence.add_subparsers(dest="action", required=True)
    evidence_add = evidence_actions.add_parser("add")
    _identity(evidence_add)
    evidence_add.add_argument("--venture-id", required=True)
    evidence_add.add_argument("--origin-work-item-id")
    evidence_add.add_argument(
        "--kind", required=True, choices=_enum_values(EvidenceKind)
    )
    evidence_add.add_argument(
        "--confidence", required=True, choices=_enum_values(ConfidenceLevel)
    )
    evidence_add.add_argument("--summary", required=True)

    decision = resources.add_parser("decision", help="Manage decisions")
    decision_actions = decision.add_subparsers(dest="action", required=True)
    decision_add = decision_actions.add_parser("add")
    _identity(decision_add)
    decision_add.add_argument("--venture-id", required=True)
    decision_add.add_argument(
        "--kind", required=True, choices=_enum_values(DecisionKind)
    )
    decision_add.add_argument("--summary", required=True)
    decision_add.add_argument("--rationale", required=True)
    decision_add.add_argument(
        "--assessment-id", required=True, action="append", dest="assessment_ids"
    )

    work_item = resources.add_parser("work-item", help="Manage work items")
    work_actions = work_item.add_subparsers(dest="action", required=True)
    work_add = work_actions.add_parser("add")
    _identity(work_add)
    work_add.add_argument("--venture-id", required=True)
    work_add.add_argument("--decision-id")
    work_add.add_argument("--title", required=True)
    work_add.add_argument("--kind", required=True, choices=_enum_values(WorkItemKind))
    work_add.add_argument("--acceptance-criteria")
    work_add.add_argument("--method")
    work_add.add_argument("--success-criteria")
    work_add.add_argument("--failure-criteria")
    work_add.add_argument(
        "--assumption-id", action="append", default=[], dest="assumption_ids"
    )
    work_status = work_actions.add_parser("set-status")
    _identity(work_status)
    work_status.add_argument(
        "--status", required=True, choices=_enum_values(WorkItemStatus)
    )

    artifact = resources.add_parser("artifact", help="Manage artifacts")
    artifact_actions = artifact.add_subparsers(dest="action", required=True)
    artifact_add = artifact_actions.add_parser("add")
    _identity(artifact_add)
    artifact_add.add_argument("--venture-id", required=True)
    artifact_add.add_argument("--work-item-id")
    artifact_add.add_argument(
        "--kind", required=True, choices=_enum_values(ArtifactKind)
    )
    artifact_add.add_argument("--name", required=True)
    artifact_add.add_argument("--location", required=True)

    agent_run = resources.add_parser(
        "agent-run", help="Record and link versioned agent runs"
    )
    agent_run_actions = agent_run.add_subparsers(dest="action", required=True)
    agent_run_record = agent_run_actions.add_parser("record")
    agent_run_record.add_argument("--input", required=True)
    agent_run_show = agent_run_actions.add_parser("show")
    _identity(agent_run_show)
    agent_run_link = agent_run_actions.add_parser("link-evalops")
    _identity(agent_run_link)
    agent_run_link.add_argument("--trace-id", required=True)
    listing = venture_actions.add_parser("list")
    listing.add_argument("--query", default="")
    listing.add_argument("--stage", choices=_enum_values(VentureStage))
    add_pagination(listing)
    add_portfolio_filters(listing)
    for actions in [
        assumption_actions,
        evidence_actions,
        decision_actions,
        work_actions,
        artifact_actions,
    ]:
        listing = actions.add_parser("list")
        listing.add_argument("--venture-id", required=True)
        add_pagination(listing)
    experiments = resources.add_parser("experiment").add_subparsers(
        dest="action", required=True
    )
    listing = experiments.add_parser("list")
    listing.add_argument("--venture-id", required=True)
    add_pagination(listing)
    add_console_parsers(resources)
    return parser


def _identity(parser: ArgumentParser) -> None:
    parser.add_argument("--id", required=True)


def _clean_command_text(arguments: Namespace) -> None:
    """Validate textual command fields before opening or creating a database."""

    for name, value in vars(arguments).items():
        if isinstance(value, str) and name not in {"resource", "action", "query"}:
            setattr(arguments, name, required_text(name.replace("_", " "), value))
        elif isinstance(value, list):
            cleaned = [
                required_text(name.replace("_", " "), item)
                if isinstance(item, str)
                else item
                for item in value
            ]
            setattr(arguments, name, cleaned)


def get_settings(
    arguments: Namespace,
    *,
    environment: Mapping[str, str] | None = None,
    dotenv: Mapping[str, str | None] | None = None,
) -> Settings:
    """Resolve CLI, process, dotenv, and default configuration precedence."""

    dotenv_source = dotenv_values() if dotenv is None else dotenv
    environment_source = os.environ if environment is None else environment
    values = {key: value for key, value in dotenv_source.items() if value is not None}
    values.update(environment_source)
    if arguments.store is not None:
        values["FOUNDRY_DATABASE_URL"] = f"sqlite:///{arguments.store}"
    if arguments.debug is not None:
        values["FOUNDRY_DEBUG"] = str(arguments.debug)
    if arguments.sql_echo is not None:
        values["FOUNDRY_SQL_ECHO"] = str(arguments.sql_echo)
    return load_settings(values)


def run_cli(application: FoundryApplication, arguments: Namespace) -> JsonObject:
    """Dispatch parsed command input to one application transaction."""

    command = (arguments.resource, arguments.action)
    if command == ("venture", "create"):
        return application.create_venture(
            venture_id=arguments.id,
            name=arguments.name,
            objective=arguments.objective,
            stage=VentureStage(arguments.stage),
        )
    if command == ("venture", "show"):
        return application.show_venture(arguments.id)
    if command == ("assumption", "add"):
        return application.add_assumption(
            assumption_id=arguments.id,
            venture_id=arguments.venture_id,
            statement=arguments.statement,
            kind=AssumptionKind(arguments.kind),
            importance=arguments.importance,
            uncertainty=arguments.uncertainty,
        )
    if command == ("assumption", "assess"):
        return application.assess_assumption(
            assessment_id=arguments.id,
            assumption_id=arguments.assumption_id,
            evidence_ids=arguments.evidence_ids,
            outcome=AssessmentOutcome(arguments.outcome),
            confidence=ConfidenceLevel(arguments.confidence),
            rationale=arguments.rationale,
        )
    if command == ("evidence", "add"):
        return application.add_evidence(
            evidence_id=arguments.id,
            venture_id=arguments.venture_id,
            origin_work_item_id=arguments.origin_work_item_id,
            kind=EvidenceKind(arguments.kind),
            confidence=ConfidenceLevel(arguments.confidence),
            summary=arguments.summary,
        )
    if command == ("decision", "add"):
        return application.add_decision(
            decision_id=arguments.id,
            venture_id=arguments.venture_id,
            kind=DecisionKind(arguments.kind),
            summary=arguments.summary,
            rationale=arguments.rationale,
            assessment_ids=arguments.assessment_ids,
        )
    if command == ("work-item", "add"):
        return application.add_work_item(
            work_item_id=arguments.id,
            venture_id=arguments.venture_id,
            decision_id=arguments.decision_id,
            title=arguments.title,
            kind=WorkItemKind(arguments.kind),
            acceptance_criteria=arguments.acceptance_criteria,
            method=arguments.method,
            success_criteria=arguments.success_criteria,
            failure_criteria=arguments.failure_criteria,
            assumption_ids=arguments.assumption_ids,
        )
    if command == ("work-item", "set-status"):
        return application.set_work_item_status(
            arguments.id, WorkItemStatus(arguments.status)
        )
    if command == ("artifact", "add"):
        return application.add_artifact(
            artifact_id=arguments.id,
            venture_id=arguments.venture_id,
            work_item_id=arguments.work_item_id,
            kind=ArtifactKind(arguments.kind),
            name=arguments.name,
            location=arguments.location,
        )
    if command == ("agent-run", "record"):
        return application.record_agent_run(_read_json_object(arguments.input))
    if command == ("agent-run", "show"):
        return application.show_agent_run(arguments.id)
    if command == ("agent-run", "link-evalops"):
        return application.link_evalops_trace(arguments.id, arguments.trace_id)
    raise RuntimeError(f"Unhandled command: {command!r}")


def _read_json_object(path_value: str) -> JsonObject:
    """Load one local integration payload with actionable input errors."""

    from pathlib import Path

    try:
        payload = json.loads(Path(path_value).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValidationError(f"input file could not be read: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"input file is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError("input file must contain one JSON object")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command and return a process exit status."""

    arguments = build_parser().parse_args(argv)
    try:
        _clean_command_text(arguments)
        check_idea_create(arguments)
        # Discovery is a static public contract, including during store outages.
        if arguments.resource == "agent" and arguments.action in {"guide", "schema"}:
            from startup_foundry.decision_commands import GUIDE, public_schema

            if arguments.action == "guide":
                print(GUIDE, end="")
            else:
                print(json.dumps(public_schema(arguments.name), sort_keys=True))
            return 0
        settings = get_settings(arguments)
    except (ConfigurationError, StartupFoundryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    correlation_id_var.set(str(uuid4()))
    configure_logging(debug=settings.debug)
    engine = None
    try:
        logger.info(
            "command_started resource=%s action=%s",
            arguments.resource,
            arguments.action,
        )
        if arguments.resource == "ui" and not 1 <= arguments.port <= 65535:
            raise ValidationError("port must be between 1 and 65535")
        if (arguments.resource, arguments.action) == ("storage", "backup"):
            from pathlib import Path

            from startup_foundry.storage import backup_sqlite

            print(
                json.dumps(backup_sqlite(settings.database_url, Path(arguments.output)))
            )
            return 0
        if (arguments.resource, arguments.action) != ("storage", "info"):
            upgrade_database(settings.database_url, sql_echo=settings.sql_echo)
        engine = create_db_engine(settings.database_url, echo=settings.sql_echo)
        application = FoundryApplication(create_session_factory(engine))
        if arguments.resource == "ui":
            import uvicorn

            from startup_foundry.web import create_app

            uvicorn.run(
                create_app(create_session_factory(engine), requests_directory()),
                host="127.0.0.1",
                port=arguments.port,
                proxy_headers=False,
                access_log=False,
            )
            return 0
        if (
            arguments.resource
            in {
                "idea",
                "source",
                "market-actor",
                "portfolio",
                "step",
                "storage",
                "experiment",
                "score",
                "scorecard",
                "review",
                "existing-project",
                "outreach",
                "input",
                "venture-score",
                "proposal",
                "workspace",
                "intake",
                "agent",
                "decision-map",
                "handoff",
                "result",
                "change",
                "venture-work",
            }
            or arguments.action == "list"
        ):
            result = dispatch(
                create_session_factory(engine), arguments, settings.database_url
            )
        else:
            result = run_cli(application, arguments)
        if getattr(arguments, "format", None) == "markdown" or (
            arguments.resource == "agent" and arguments.action == "guide"
        ):
            print(result["markdown"], end="")
        else:
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        logger.info(
            "command_completed resource=%s action=%s",
            arguments.resource,
            arguments.action,
        )
        return 0
    except StartupFoundryError as exc:
        logger.warning("expected_application_error error_type=%s", type(exc).__name__)
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except IntegrityError:
        logger.warning("database_constraint_error")
        print(
            "error: command conflicts with existing or related records",
            file=sys.stderr,
        )
        return 2
    except SQLAlchemyError as exc:
        logger.warning("database_error error_type=%s", type(exc).__name__)
        print(
            "error: the Foundry database could not be read or updated",
            file=sys.stderr,
        )
        return 2
    except Exception:
        logger.exception("unexpected_application_error")
        print("error: an unexpected internal error occurred", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()
