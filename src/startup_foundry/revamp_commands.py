"""Typed CLI adapters for the revamp services; JSON input avoids shell quoting."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from startup_foundry.errors import ValidationError
from startup_foundry.human_inputs import (
    ClaimInput,
    DependencyInput,
    HumanInputService,
    ReleaseInput,
    RequestInput,
    ResponseInput,
    ReviewResult,
)
from startup_foundry.inputs import read_input
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
    SupersedeInput,
)
from startup_foundry.repository import SessionFactory
from startup_foundry.venture_scoring import (
    VentureAssessmentInput,
    VentureScoringService,
)
from startup_foundry.workspace_modules import (
    ConfigInput,
    IssueInput,
    MetricsInput,
    WorkspaceModuleService,
)


def add_parsers(resources: Any) -> None:
    intake = resources.add_parser("intake").add_subparsers(dest="action", required=True)
    for name in ["request", "handoff", "claim", "release", "complete"]:
        parser = intake.add_parser(name)
        parser.add_argument("--subject", choices=["idea", "venture"], required=True)
        parser.add_argument("--id", required=True)
        if name != "handoff":
            parser.add_argument("--input", required=True)
    for namespace, operations in {
        "input": {
            "register": "input",
            "list": "list",
            "show": "id",
            "preview": "none",
            "sync": "sync",
            "submit": "both",
            "claim": "both",
            "release": "both",
            "complete": "both",
            "link-dependency": "both",
            "handoff": "id",
        },
        "venture-score": {"bootstrap": "none", "show": "venture", "assess": "input"},
        "proposal": {
            "list": "none",
            "show": "id",
            "create": "input",
            "revise": "both",
            "resolve": "both",
            "supersede": "both",
        },
        "workspace": {
            "show": "id",
            "configure": "both",
            "metrics": "both",
            "issue": "both",
            "bootstrap": "bootstrap",
        },
    }.items():
        actions = resources.add_parser(namespace).add_subparsers(
            dest="action", required=True
        )
        for name, kind in operations.items():
            p = actions.add_parser(name)
            if kind in {"id", "both", "venture"}:
                p.add_argument("--id", required=True)
            if kind in {"input", "both"}:
                p.add_argument("--input", required=True)
            if kind == "list":
                p.add_argument("--status")
                p.add_argument("--workspace-id")
                p.add_argument("--limit", type=int, default=50)
                p.add_argument("--offset", type=int, default=0)
            if kind == "venture":
                p.add_argument("--scorecard-id", default="portfolio-reviewed-v1")
            if kind == "sync":
                p.add_argument(
                    "--preview", required=True, help="Saved output of input preview"
                )
                p.add_argument("--reconciliation", choices=["keep_ui", "use_file"])
            if kind == "bootstrap":
                p.add_argument("--review-latest", action="store_true")


def dispatch(
    factory: SessionFactory, args: Namespace, directory: Path
) -> dict[str, Any]:
    inputs = HumanInputService(factory, directory)
    if args.resource == "intake":
        intake = ManualIntakeService(factory)
        if args.action == "handoff":
            return intake.handoff(args.subject, args.id) or {}
        if args.action == "request":
            return intake.request(
                args.subject, args.id, read_input(IntakeRequest, args.input)
            )
        if args.action == "claim":
            return intake.claim(
                args.subject, args.id, read_input(ClaimInput, args.input)
            )
        if args.action == "release":
            return intake.release(
                args.subject, args.id, read_input(ReleaseInput, args.input)
            )
        if args.action == "complete":
            return intake.complete(
                args.subject, args.id, read_input(IntakeCompletion, args.input)
            )
    if args.resource == "input":
        if args.action == "list":
            return inputs.list(
                status=args.status,
                workspace_id=args.workspace_id,
                limit=args.limit,
                offset=args.offset,
            )
        if args.action == "preview":
            return inputs.preview()
        if args.action == "sync":
            try:
                raw = Path(args.preview).read_bytes()
                if len(raw) > 100000:
                    raise ValidationError("Sync preview exceeds 100 KB")
                preview = json.loads(raw)
            except (OSError, ValueError) as exc:
                raise ValidationError("Cannot read sync preview JSON") from exc
            return inputs.sync(preview, reconciliation=args.reconciliation)
        if args.action == "register":
            return inputs.register(read_input(RequestInput, args.input))
        if args.action == "show":
            return inputs.show(args.id)
        if args.action == "handoff":
            return inputs.handoff(args.id)
        if args.action == "submit":
            return inputs.submit(args.id, read_input(ResponseInput, args.input))
        if args.action == "claim":
            return inputs.claim(args.id, read_input(ClaimInput, args.input))
        if args.action == "release":
            return inputs.release(args.id, read_input(ReleaseInput, args.input))
        if args.action == "complete":
            return inputs.complete(args.id, read_input(ReviewResult, args.input))
        if args.action == "link-dependency":
            return inputs.link_dependency(
                args.id, read_input(DependencyInput, args.input)
            )
    if args.resource == "venture-score":
        scores = VentureScoringService(factory)
        if args.action == "show":
            return scores.show(args.id, args.scorecard_id)
        if args.action == "bootstrap":
            return scores.bootstrap()
        return scores.assess(read_input(VentureAssessmentInput, args.input))
    if args.resource == "proposal":
        p = ProposalService(factory)
        if args.action == "list":
            return p.list()
        if args.action == "show":
            return p.show(args.id)
        if args.action == "create":
            return p.create(read_input(FusionInput, args.input))
        if args.action == "revise":
            return p.revise(args.id, read_input(ReviseInput, args.input))
        if args.action == "resolve":
            return p.resolve(args.id, read_input(ResolveInput, args.input))
        if args.action == "supersede":
            return p.supersede(args.id, read_input(SupersedeInput, args.input))
    if args.resource == "workspace":
        m = WorkspaceModuleService(factory)
        if args.action == "show":
            return m.show(args.id)
        if args.action == "configure":
            return m.configure(args.id, read_input(ConfigInput, args.input))
        if args.action == "metrics":
            return m.metrics(args.id, read_input(MetricsInput, args.input))
        if args.action == "issue":
            return m.issue(args.id, read_input(IssueInput, args.input))
        if args.action == "bootstrap":
            from startup_foundry.revamp_bootstrap import (
                bootstrap,
                retain_briefs,
                seed_sports,
            )

            root = Path(__file__).resolve().parents[2]
            campaign_intake = bootstrap(
                factory, directory, review_latest=args.review_latest
            )
            briefs = retain_briefs(factory, root)
            proposal = seed_sports(factory, root)
            return {
                "intake": campaign_intake,
                "briefs": briefs,
                "proposal_id": proposal["id"],
                "proposal_state": proposal["state"],
            }
    raise ValidationError("Unsupported revamp operation")
