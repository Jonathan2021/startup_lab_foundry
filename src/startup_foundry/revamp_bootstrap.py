"""Explicit repeat-safe campaign registration/intake; never a migration side effect."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

from startup_foundry.domain import (
    Artifact,
    Disposition,
    HumanRequest,
    Idea,
    ProductMaturity,
    Venture,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    WorkspaceReview,
)
from startup_foundry.errors import ReferenceError, ValidationError
from startup_foundry.human_inputs import (
    ClaimInput,
    DependencyInput,
    HumanInputService,
    RequestInput,
    ReviewResult,
    TargetChange,
)
from startup_foundry.portfolio import stable_id
from startup_foundry.proposals import (
    FusionInput,
    ProposalService,
    ScopeItem,
    WorkTreatment,
)
from startup_foundry.repository import SessionFactory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import digest
from startup_foundry.snapshots import audit, snapshot, transaction
from startup_foundry.venture_scoring import VentureScoringService
from startup_foundry.workspace_modules import ConfigInput, WorkspaceModuleService

JSON = dict[str, Any]
OWNERS = {
    "R001": "v-route-repair",
    "R002": "v-physical",
    "R003": "v-receipt",
    "R004": "v-foundry",
    "R005": "v-route-repair",
    "R006": "v-sports-session",
    "R007": "v-coopain",
    "R008": "v-physical",
    "R009": "v-receipt",
}
IDEAS = {
    "R001": ["N008", "D001"],
    "R002": ["N001", "G014", "P007"],
    "R003": ["N003", "G005", "P106", "D003"],
    "R004": ["D002"],
    "R005": ["N008", "D001"],
    "R006": ["P023", "P103"],
    "R007": ["P046"],
    "R008": ["N001", "G014", "P007"],
    "R009": ["N003", "G005", "P106", "D003"],
}


def bootstrap(
    factory: SessionFactory, directory: Path, *, review_latest: bool = False
) -> JSON:
    inputs = HumanInputService(factory, directory)
    registered = []
    for request_id, owner in OWNERS.items():
        file = "INBOX.md" if request_id < "R005" else "2026-10-04-followups.md"
        content, _ = inputs.read_source(file)
        parsed = inputs.section(content, request_id)
        title = parsed["section"].splitlines()[0].split("—", 1)[-1].strip()
        with factory() as session:
            v = session.get(Venture, owner)
            if not v:
                raise ReferenceError("Campaign owner missing: " + owner)
            targets = [v.workspace_id]
            for i in IDEAS[request_id]:
                idea = session.get(Idea, i)
                if idea:
                    targets.append(idea.workspace_id)
            if request_id == "R006":
                other = session.get(Venture, "v-sports-ranking")
                if other:
                    targets.append(other.workspace_id)
        inputs.register(
            RequestInput(
                id=request_id,
                workspace_id=v.workspace_id,
                target_workspace_ids=targets,
                title=title,
                question=parsed["section"]
                .split("Response:", 1)[0]
                .split("My answer:", 1)[0],
                file_path=file,
                actor="agent:workspace-revamp",
            )
        )
        registered.append(request_id)
        if request_id < "R005":
            with transaction(factory) as session:
                item = session.get(HumanRequest, request_id)
                assert item
                if item.response_artifact_id:
                    continue
                legacy = session.scalar(
                    select(Artifact)
                    .where(Artifact.name == request_id + " answer receipt")
                    .order_by(Artifact.created_at.desc())
                    .limit(1)
                )
                if not legacy:
                    raise ReferenceError("Expected historical receipt " + request_id)
                work_id = stable_id(
                    "inbox-question:" + request_id + ":" + item.workspace_id
                )
                answer = snapshot(
                    session,
                    item.workspace_id,
                    "human-response/v1",
                    {
                        "request_id": request_id,
                        "definition_revision": 1,
                        "definition_artifact_id": item.definition_artifact_id,
                        "sequence": 1,
                        "text": parsed["text"],
                        "author": "operator (historical file)",
                        "source": "file",
                        "received_at": legacy.created_at.isoformat(),
                        "previous_response_id": None,
                        "submission_key": "legacy:" + legacy.id,
                        "submission_digest": digest(parsed["text"]),
                        "work_id": work_id,
                        "legacy_receipt_id": legacy.id,
                        "legacy_section_digest": legacy.content_digest,
                        "file_path": file,
                        "answer_hash": parsed["answer_hash"],
                    },
                    key=request_id + ":legacy:" + legacy.id,
                )
                review = snapshot(
                    session,
                    item.workspace_id,
                    "human-response-review/v1",
                    {
                        "request_id": request_id,
                        "response_id": answer.id,
                        "work_id": work_id,
                        "actor": "legacy-intake (retained)",
                        "interpretation": (
                            "Historical reviewed answer; original receipt retained"
                        ),
                        "outcome": "no_change",
                        "rationale": "Link historical review; no repeated campaign",
                        "remaining_unknowns": [],
                        "changes": [],
                        "score_explanation": "Historical source estimates retained",
                        "reviewed_at": legacy.created_at.isoformat(),
                        "legacy_receipt_id": legacy.id,
                    },
                    key=request_id + ":legacy-review",
                )
                item.response_artifact_id = answer.id
                item.review_artifact_id = review.id
                item.status = "resolved"
                item.source_diagnostics = {
                    "last_file_answer_hash": parsed["answer_hash"]
                }
    synced = inputs.sync(inputs.preview())
    reviewed = []
    if review_latest:
        _, file_hash = inputs.read_source("2026-10-04-followups.md")
        if (
            file_hash
            != "8705a386ac0e8588cfd8d70e397c509ef56391ce6a85f1e8f1d94a4ef0411d7b"
        ):
            raise ValidationError(
                "Follow-up answers changed from documented handoff; review "
                "current exact text manually"
            )
        for request in ["R005", "R006", "R007", "R008", "R009"]:
            detail = inputs.show(request)
            if detail["status"] in {"resolved", "deferred"}:
                continue
            changes = []
            with factory() as session:
                for target in detail["targets"]:
                    w = target["workspace_id"]
                    current = session.scalar(
                        select(WorkspaceReview)
                        .where(WorkspaceReview.workspace_id == w)
                        .order_by(WorkspaceReview.revision.desc())
                        .limit(1)
                    )
                    close = []
                    if request in {"R005", "R006"}:
                        close = [
                            task.id
                            for task in session.scalars(
                                select(WorkItem).where(
                                    WorkItem.workspace_id == w,
                                    WorkItem.status == WorkItemStatus.BLOCKED,
                                    WorkItem.blocked_reason == "human_input",
                                )
                            )
                            if (
                                (
                                    "riding budget"
                                    if request == "R005"
                                    else "actual sport/group"
                                )
                                in task.title
                            )
                        ]
                    actions = {
                        "R005": (
                            "Prepare three editable route-planning alternatives; riding"
                            " target 4–5 hours, breaks separate. Routing basis remains "
                            "unknown."
                        ),
                        "R006": (
                            "Review the pending volleyball-first fusion proposal, then "
                            "prepare the bounded trial sheet; actual attendance/formats"
                            " and consent remain unknown."
                        ),
                        "R007": (
                            "Prepare private tester walkthrough and ownership "
                            "checklist. Runtime tests, placeholder labeling, rights and"
                            " employer payer remain unresolved."
                        ),
                        "R008": (
                            "Deferred by you; reopen only when construction contact "
                            "feedback is supplied."
                        ),
                        "R009": (
                            "Deferred by you; reopen when a receiving practitioner is "
                            "identified."
                        ),
                    }
                    owner = w == detail["workspace_id"]
                    title = (
                        {
                            "R005": (
                                "Prepare frozen three-option route comparison brief"
                            ),
                            "R006": (
                                "Prepare volleyball fusion proposal and trial sheet"
                            ),
                            "R007": (
                                "Prepare Coopain tester walkthrough and "
                                "ownership checklist"
                            ),
                        }.get(request)
                        if owner
                        else None
                    )
                    changes.append(
                        TargetChange(
                            workspace_id=w,
                            expected_revision=current.revision if current else 0,
                            product_maturity=current.product_maturity
                            if current
                            else ProductMaturity.CONCEPT,
                            disposition=Disposition.HOLD
                            if request in {"R008", "R009"}
                            else Disposition.PURSUE,
                            next_action=actions[request],
                            next_work_title=title,
                            close_input_work_ids=close,
                        )
                    )
            for change in changes:
                for work_id in change.close_input_work_ids:
                    inputs.link_dependency(
                        request,
                        DependencyInput(
                            expected_version=inputs.show(request)["version"],
                            workspace_id=change.workspace_id,
                            work_id=work_id,
                            actor="agent:workspace-revamp",
                            reason="Exact documented campaign input dependency",
                        ),
                    )
            claim = inputs.claim(
                request,
                ClaimInput(
                    expected_version=inputs.show(request)["version"],
                    actor="agent:workspace-revamp",
                ),
            )
            known = {
                "R005": (
                    "Broad markers plus quicker/scenic/balanced editable "
                    "alternatives address planning effort; 4–5 h is target "
                    "riding time, not hard deadline."
                ),
                "R006": (
                    "Outdoor volleyball, WhatsApp and "
                    "balancing/pool/progression jobs support a combined "
                    "investigation; planned outing is not observed attendance."
                ),
                "R007": (
                    "Referral-bonus reports give access opportunity, not buyer "
                    "validation. No real tests, scheduling pause, rights "
                    "unagreed. Shared discussion body not reviewed."
                ),
                "R008": (
                    "User explicitly holds this track pending construction feedback."
                ),
                "R009": (
                    "User explicitly holds this track pending a receiving practitioner."
                ),
            }
            unknown = {
                "R005": [
                    "Routing basis and exact ETA",
                    "Hard deadline only if needed by concrete alternative",
                ],
                "R006": [
                    "Normal attendance/frequency",
                    "Organizer role and team formats",
                    "Participant consent",
                    "Whether planned outing occurred",
                ],
                "R007": [
                    "Runtime verification",
                    "Ownership/license",
                    "Employer buyer and repeat workflow",
                ],
                "R008": ["Competent feedback / task labels"],
                "R009": ["Named receiving practitioner and real decision use"],
            }
            reviewed.append(
                inputs.complete(
                    request,
                    ReviewResult(
                        work_id=claim["work_id"],
                        response_id=claim["response_id"],
                        actor="agent:workspace-revamp",
                        interpretation=known[request],
                        outcome="deferred"
                        if request in {"R008", "R009"}
                        else "sufficient",
                        rationale=(
                            "Latest supplied answer interpreted under the 2026-10-04 "
                            "revamp handoff; validation remains separate."
                        ),
                        remaining_unknowns=unknown[request],
                        changes=changes,
                    ),
                )
            )
    scores = VentureScoringService(factory).bootstrap()
    modules = WorkspaceModuleService(factory)
    config = modules.show("v-coopain")["config"]
    if config["revision"] == 0:
        modules.configure(
            "v-coopain",
            ConfigInput(
                expected_revision=0,
                actor="agent:workspace-revamp",
                modules=["software", "outreach"],
            ),
        )
    return {
        "registered": registered,
        "sync": synced,
        "reviewed": reviewed,
        "scores": scores,
    }


def seed_sports(factory: SessionFactory, root: Path) -> JSON:
    spec = root / "docs/plans/2026-10-04-venture-workspace-revamp/03-FUSION.md"
    text = spec.read_text()
    scope = []
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| Capability"):
            continue
        columns = [v.strip() for v in line.strip("|").split("|")]
        if len(columns) != 3:
            continue
        capability, provenance, reason = columns
        treatment = (
            "excluded"
            if "excluded" in reason.lower()
            else "deferred"
            if "deferred" in reason.lower() or "future" in reason.lower()
            else "combined"
            if "Fused" in reason
            else "added"
            if "Necessary" in provenance
            else "retained"
        )
        scope.append(
            {
                "capability": capability,
                "provenance": provenance,
                "reason": reason,
                "treatment": treatment,
            }
        )
    with factory() as session:
        works = list(
            session.scalars(
                select(WorkItem).where(
                    WorkItem.workspace_id.in_(
                        select(Venture.workspace_id).where(
                            Venture.id.in_(["v-sports-session", "v-sports-ranking"])
                        )
                    ),
                    WorkItem.title
                    == "Prepare volleyball fusion proposal and trial sheet",
                    WorkItem.status == WorkItemStatus.READY,
                )
            )
        )
        treatments = [
            {
                "work_id": w.id,
                "treatment": "supersede",
                "reason": (
                    "Coalesce into one trial preparation task only on exact acceptance"
                ),
            }
            for w in works
        ]
    return ProposalService(factory).create(
        FusionInput(
            name="Volleyball Sessions and Fair Tournaments",
            description="For friends"
            + text.split("For friends", 1)[1].split("\n\nRecommendation:", 1)[0],
            customer="Friends and informal outdoor volleyball organizers",
            next_work_title=(
                "Prepare one balanced-session and tournament-pool trial comparison"
            ),
            source_idea_ids=["P023", "P103"],
            source_venture_ids=["v-sports-ranking", "v-sports-session"],
            result_venture_id="v-volley-sessions",
            request_key="sports-volleyball-r006-v1",
            rationale=(
                "Recommend one volleyball investigation with balanced "
                "sessions and ranking/tournament seeding sharing "
                "participants, matches and distribution; this is design "
                "inference, not demand validation."
            ),
            scope=[ScopeItem.model_validate(s) for s in scope],
            alternatives=[
                (
                    "One volleyball venture, two jobs: shared data and one "
                    "group comparison, with scope restraint."
                ),
                (
                    "Keep two ventures: independent future buyers, but "
                    "duplicate current discovery/data entry."
                ),
                "Share research only: low commitment, management boundary unresolved.",
                (
                    "Adopt existing tools and stop new product work if real "
                    "task trials meet the combined job."
                ),
            ],
            work_treatments=[WorkTreatment.model_validate(t) for t in treatments],
            evidence_links=[
                "request:R006",
                "docs/inquiry/handoff-2026-10-04/SPORTS.md",
                "docs/inquiry/revamp-2026-10-05/VOLLEYBALL.md",
            ],
        )
    )


def retain_briefs(factory: SessionFactory, root: Path) -> JSON:
    output = []
    with transaction(factory) as session:
        for venture, file, request in [
            ("v-route-repair", "ROUTE.md", "R005"),
            ("v-sports-session", "VOLLEYBALL.md", "R006"),
            ("v-coopain", "COOPAIN.md", "R007"),
        ]:
            v = session.get(Venture, venture)
            assert v
            text = (root / "docs/inquiry/revamp-2026-10-05" / file).read_text()
            artifact = snapshot(
                session,
                v.workspace_id,
                "venture-followup-brief/v1",
                {
                    "venture_id": v.id,
                    "request_id": request,
                    "text": text,
                    "source": "docs/inquiry/revamp-2026-10-05/" + file,
                    "actor": "agent:workspace-revamp",
                    "status": "prepared; trial not run",
                },
                key=request + ":r1",
            )
            output.append(artifact.id)
            task_titles = {
                "R005": ("Prepare frozen three-option route comparison brief"),
                "R006": ("Prepare volleyball fusion proposal and trial sheet"),
                "R007": ("Prepare Coopain tester walkthrough and ownership checklist"),
            }
            for work in session.scalars(
                select(WorkItem).where(
                    WorkItem.workspace_id == v.workspace_id,
                    WorkItem.title == task_titles[request],
                    WorkItem.status == WorkItemStatus.READY,
                )
            ):
                work.status = WorkItemStatus.DONE
                audit(
                    session,
                    v.workspace_id,
                    work.id,
                    "brief_preparation_completed",
                    "agent:workspace-revamp",
                    {
                        "artifact_id": artifact.id,
                        "limits": ("Preparation only; no actual trial or user test"),
                    },
                )
                current = session.scalar(
                    select(WorkspaceReview)
                    .where(WorkspaceReview.workspace_id == v.workspace_id)
                    .order_by(WorkspaceReview.revision.desc())
                    .limit(1)
                )
                assert current
                next_titles = {
                    "R005": (
                        "Compare route-planning alternatives using "
                        "an explicit routing basis"
                    ),
                    "R007": (
                        "Verify Coopain runtime and label the "
                        "compatibility placeholder before private "
                        "testing"
                    ),
                }
                next_work = None
                if request in next_titles:
                    next_work = WorkItem(
                        workspace_id=v.workspace_id,
                        title=next_titles[request],
                        kind=WorkItemKind.INVESTIGATION,
                        status=WorkItemStatus.READY,
                        owner="agent",
                        acceptance_criteria=(
                            "Record routing/runtime basis and "
                            "uncertainty; no external uploads, "
                            "invitations or publication"
                        ),
                    )
                    session.add(next_work)
                    session.flush()
                ReviewService._append(
                    session,
                    ReviewInput(
                        workspace_id=v.workspace_id,
                        expected_revision=current.revision,
                        investigation_stage=current.investigation_stage,
                        product_maturity=current.product_maturity,
                        disposition=current.disposition,
                        next_action=next_titles.get(
                            request,
                            (
                                "Review the pending volleyball-first fusion"
                                " proposal; trial attendance and consent "
                                "remain future gates"
                            ),
                        ),
                        next_work_item_id=next_work.id if next_work else None,
                        reason=(
                            "Follow-up brief prepared; actual trial "
                            "outcomes remain unknown."
                        ),
                        author="agent:workspace-revamp",
                        source_artifact_id=artifact.id,
                    ),
                )
    return {"brief_ids": output}
