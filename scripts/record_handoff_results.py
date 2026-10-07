"""Append this bounded handoff's findings, reviews and targeted judgments."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from startup_foundry.config import load_settings
from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    AssessmentEvidence,
    AssessmentOutcome,
    Assumption,
    AssumptionAssessment,
    AssumptionKind,
    ConfidenceLevel,
    Decision,
    DecisionAssessment,
    DecisionEvidence,
    DecisionKind,
    DecisionStatus,
    Evidence,
    EvidenceArtifact,
    EvidenceKind,
    EvidenceSource,
    Experiment,
    ExperimentAssumption,
    ExperimentStatus,
    Idea,
    Venture,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    WorkspaceReview,
)
from startup_foundry.portfolio import PortfolioService, stable_id
from startup_foundry.repository import (
    SessionFactory,
    UnitOfWork,
    create_db_engine,
    create_session_factory,
)
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import AssessmentInput, ScoringService, digest

FINDINGS = [
    (
        "ROUTE",
        "ROUTE.md",
        ["N008", "D001"],
        "v-route-repair",
        "weakened",
        (
            "Exported geometry explains at least 44.5 of the reported 89 "
            "extra ETA minutes."
        ),
        (
            "Both tracks are close; 68° is 3.326 km shorter. Implied "
            "mean speeds differ. No timestamps, so ETA accuracy is "
            "unmeasured."
        ),
        "pursue",
        "comparison",
        "concept",
        (
            "Specify riding budget and must-keep areas, then compare "
            "scenic-route planning."
        ),
        "human_input",
    ),
    (
        "COOPAIN",
        "COOPAIN.md",
        ["P046"],
        "v-coopain",
        "inconclusive",
        (
            "An employer will use/pay for a niche candidate-free "
            "introduction beyond existing referral operations."
        ),
        (
            "Prototype code and disposable mock fixtures exist; separate "
            "environment lacks pytest. Employer payer, contracts, "
            "ownership and adoption unknown."
        ),
        "hold",
        "business_validation",
        "prototype",
        (
            "Review one employer/referrer workflow; resolve ownership "
            "and label compatibility placeholder before users."
        ),
        "human_input",
    ),
    (
        "SPORTS",
        "SPORTS.md",
        ["P023", "P103"],
        "v-sports-ranking",
        "inconclusive",
        (
            "Friends repeatedly prefer a session/ranking helper over "
            "current free incumbents."
        ),
        (
            "User interest is reported in the handoff. Rankat documents "
            "relevant ranking/team tournaments. Rankade indexed "
            "faction/approval docs are relevant; direct access failed. "
            "No group session was run."
        ),
        "pursue",
        "comparison",
        "concept",
        (
            "Specify the actual sport/group, then compare ranking and "
            "rotating-team tasks in one session."
        ),
        "human_input",
    ),
    (
        "PHYSICAL",
        "PHYSICAL.md",
        ["N001", "G014", "P007"],
        "v-physical",
        "inconclusive",
        (
            "Public procedural datasets can replace competent "
            "correctness labels for the reported renovation tasks."
        ),
        (
            "Cooking/toy-assembly error labels exist; none inspected "
            "establishes renovation correctness or hidden defects. No "
            "benchmark or safety claim."
        ),
        "hold",
        "comparison",
        "concept",
        (
            "Obtain one repeatable observable low-risk task and "
            "competent labels, or retain field-data hold."
        ),
        "external_access",
    ),
    (
        "RECEIPT",
        "RECEIPT.md",
        ["N003", "D003", "G005", "P106"],
        "v-receipt",
        "inconclusive",
        (
            "A receiving practitioner uses a scoped work-sample receipt "
            "in an actual decision."
        ),
        (
            "Fictional sample and four unsent bilingual drafts prepared; "
            "existing Open Badges already has criteria/evidence. No "
            "issuer/receiver adoption."
        ),
        "hold",
        "problem_validation",
        "concept",
        (
            "Choose one receiving practitioner; review the fictional "
            "sample and record a real decision-use response."
        ),
        "human_input",
    ),
]


def record(factory: SessionFactory, project: Path) -> dict[str, object]:
    directory = project / "docs/inquiry/handoff-2026-10-04"
    portfolio = PortfolioService(factory)
    sources_by_idea: dict[str, list[str]] = {}
    for source in json.loads((directory / "sources.json").read_text()):
        ideas = source.pop("idea_ids")
        result = portfolio.record_source(source, idea_ids=ideas)
        for idea in ideas:
            sources_by_idea.setdefault(idea, []).append(result["id"])
    receipts = []
    idea_evidence: dict[str, str] = {}
    for (
        key,
        filename,
        ideas,
        venture_id,
        outcome,
        question,
        observation,
        disposition,
        stage,
        maturity,
        next_action,
        blocker,
    ) in FINDINGS:
        report = (directory / filename).read_text()
        report_digest = digest(report)
        with UnitOfWork(factory) as unit:
            s = unit.session
            assert s is not None
            venture = s.get(Venture, venture_id)
            assert venture is not None
            workspaces = [(venture.workspace_id, ideas[0])]
            for idea_id in ideas:
                idea = s.get(Idea, idea_id)
                assert idea is not None
                workspaces.append((idea.workspace_id, idea_id))
            if key == "SPORTS":
                extra = s.get(Venture, "v-sports-session")
                assert extra is not None
                workspaces.append((extra.workspace_id, "P103"))
            for workspace, idea_id in workspaces:
                identity = stable_id(
                    "handoff:" + key + ":" + workspace + ":" + report_digest
                )
                evidence_id = stable_id(identity + ":evidence")
                owning_idea = s.get(Idea, idea_id)
                if owning_idea and owning_idea.workspace_id == workspace:
                    idea_evidence[idea_id] = evidence_id
                if s.get(Artifact, identity):
                    # Complete links for an interrupted earlier registration, without
                    # replacing its observations or review history.
                    decision_id = stable_id(identity + ":decision")
                    assessment_id = stable_id(identity + ":assessment")
                    if (
                        s.scalar(
                            select(DecisionAssessment).where(
                                DecisionAssessment.decision_id == decision_id,
                                DecisionAssessment.assessment_id == assessment_id,
                            )
                        )
                        is None
                    ):
                        s.add(
                            DecisionAssessment(
                                decision_id=decision_id, assessment_id=assessment_id
                            )
                        )
                    if (
                        s.scalar(
                            select(DecisionEvidence).where(
                                DecisionEvidence.decision_id == decision_id,
                                DecisionEvidence.evidence_id == evidence_id,
                            )
                        )
                        is None
                    ):
                        s.add(
                            DecisionEvidence(
                                decision_id=decision_id, evidence_id=evidence_id
                            )
                        )
                    receipts.append(
                        {
                            "finding": key,
                            "workspace": workspace,
                            "evidence_id": evidence_id,
                            "unchanged": True,
                        }
                    )
                    continue
                artifact = Artifact(
                    id=identity,
                    workspace_id=workspace,
                    kind=ArtifactKind.REPORT,
                    name=key + " handoff investigation r1",
                    location=str((directory / filename).resolve()),
                    content_digest=__import__("hashlib")
                    .sha256((directory / filename).read_bytes())
                    .hexdigest(),
                    semantic_version="r1",
                    metadata_json={
                        "run_id": key + "-20261004-001",
                        "record_revision": 1,
                        "protocol_location": str((directory / "PROTOCOL.md").resolve()),
                        "protocol_sha256": __import__("hashlib")
                        .sha256((directory / "PROTOCOL.md").read_bytes())
                        .hexdigest(),
                        "source_ids": sources_by_idea.get(idea_id, []),
                        "scope": (
                            "bounded local/docs/reported investigation; limitations in "
                            "report"
                        ),
                    },
                )
                s.add(artifact)
                s.flush()
                work = WorkItem(
                    id=stable_id(identity + ":experiment-work"),
                    workspace_id=workspace,
                    title=key + " bounded investigation",
                    kind=WorkItemKind.EXPERIMENT,
                    status=WorkItemStatus.DONE,
                    owner="agent",
                    question=question,
                    description=(
                        "Frozen file protocol before execution; canonical records "
                        "appended after observed run. Environment/access failures "
                        "are findings, not passes."
                    ),
                    acceptance_criteria=(
                        "One reproducible finding or diagnosed access/domain "
                        "blocker; preserve uncertainty."
                    ),
                )
                s.add(work)
                s.flush()
                experiment = Experiment(
                    id=stable_id(identity + ":experiment"),
                    work_item_id=work.id,
                    status=ExperimentStatus.COMPLETE,
                    method="Protocol r1; see linked artifact. " + key + "-20261004-001",
                    success_criteria=(
                        "Bounded evidence supports the named question in its actual "
                        "scope."
                    ),
                    failure_criteria=(
                        "Frozen protocol falsifier, or explicit inconclusive "
                        "access/data/setup outcome."
                    ),
                    result_summary=observation,
                )
                s.add(experiment)
                s.flush()
                assumption = Assumption(
                    id=stable_id(identity + ":assumption"),
                    workspace_id=workspace,
                    statement=question,
                    kind=AssumptionKind.FEASIBILITY
                    if key in {"ROUTE", "PHYSICAL"}
                    else AssumptionKind.DESIRABILITY,
                    importance=3,
                    uncertainty=4,
                )
                s.add(assumption)
                s.flush()
                s.add(
                    ExperimentAssumption(
                        experiment_id=experiment.id,
                        assumption_id=assumption.id,
                        is_primary=True,
                    )
                )
                evidence = Evidence(
                    id=evidence_id,
                    workspace_id=workspace,
                    origin_work_item_id=work.id,
                    kind=EvidenceKind.EXPERIMENT_RESULT
                    if key == "ROUTE"
                    else EvidenceKind.DOCUMENT,
                    summary=observation,
                    details="See "
                    + filename
                    + (
                        " for observed/code/doc/user-reported/synthetic attribution "
                        "and limits."
                    ),
                    confidence=ConfidenceLevel.MEDIUM
                    if key == "ROUTE"
                    else ConfidenceLevel.LOW,
                    captured_by="agent:handoff-20261004",
                )
                s.add(evidence)
                s.flush()
                s.add(
                    EvidenceArtifact(
                        evidence_id=evidence.id,
                        artifact_id=artifact.id,
                        role="canonical result",
                    )
                )
                for source_id in sources_by_idea.get(idea_id, []):
                    s.add(
                        EvidenceSource(
                            evidence_id=evidence.id,
                            source_id=source_id,
                            source_location=filename,
                        )
                    )
                assessment = AssumptionAssessment(
                    id=stable_id(identity + ":assessment"),
                    assumption_id=assumption.id,
                    outcome=AssessmentOutcome(outcome),
                    confidence=ConfidenceLevel.MEDIUM
                    if key == "ROUTE"
                    else ConfidenceLevel.LOW,
                    rationale=observation,
                    assessed_by="agent:handoff-20261004",
                )
                s.add(assessment)
                s.flush()
                s.add(
                    AssessmentEvidence(
                        assessment_id=assessment.id, evidence_id=evidence.id
                    )
                )
                decision = Decision(
                    id=stable_id(identity + ":decision"),
                    workspace_id=workspace,
                    kind=DecisionKind.CONTINUE
                    if disposition == "pursue"
                    else DecisionKind.DEFER,
                    status=DecisionStatus.ACCEPTED,
                    summary=next_action,
                    rationale=observation,
                    decided_by="agent:authorized-portfolio-discovery",
                )
                s.add(decision)
                s.flush()
                s.add(
                    DecisionAssessment(
                        decision_id=decision.id, assessment_id=assessment.id
                    )
                )
                s.add(
                    DecisionEvidence(decision_id=decision.id, evidence_id=evidence.id)
                )
                next_work = WorkItem(
                    id=stable_id(identity + ":next-work"),
                    workspace_id=workspace,
                    title=next_action[:300],
                    question=next_action,
                    description=(
                        "Exact remaining gate in requests/2026-10-04-followups.md; "
                        "prior supplied answers preserved."
                    ),
                    kind=WorkItemKind.INVESTIGATION,
                    status=WorkItemStatus.BLOCKED,
                    owner="human",
                    blocked_reason=blocker,
                    acceptance_criteria=next_action,
                )
                s.add(next_work)
                s.flush()
                latest = s.scalar(
                    select(WorkspaceReview)
                    .where(WorkspaceReview.workspace_id == workspace)
                    .order_by(WorkspaceReview.revision.desc())
                )
                review = ReviewService._append(
                    s,
                    ReviewInput.model_validate(
                        {
                            "workspace_id": workspace,
                            "expected_revision": latest.revision if latest else 0,
                            "investigation_stage": stage,
                            "product_maturity": maturity,
                            "disposition": disposition,
                            "next_action": next_action,
                            "next_work_item_id": next_work.id,
                            "reason": observation,
                            "author": "agent:handoff-20261004",
                            "source_artifact_id": artifact.id,
                            "decision_id": decision.id,
                        }
                    ),
                )
                receipts.append(
                    {
                        "finding": key,
                        "workspace": workspace,
                        "artifact_id": artifact.id,
                        "evidence_id": evidence.id,
                        "assessment_id": assessment.id,
                        "decision_id": decision.id,
                        "review_id": review.id,
                        "unchanged": False,
                    }
                )
    # Useful Foundry operation has a separate, ready agent-owned next action.
    with UnitOfWork(factory) as unit:
        s = unit.session
        assert s is not None
        venture = s.get(Venture, "v-foundry")
        assert venture is not None
        identity = "handoff-foundry-operation-r1"
        if s.get(Artifact, identity) is None:
            art = Artifact(
                id=identity,
                workspace_id=venture.workspace_id,
                kind=ArtifactKind.REPORT,
                name="Handoff operation checkpoint",
                location=str((directory / "REPORT.md").resolve()),
                metadata_json={
                    "scope": "Internal tool; no commercial validation",
                    "features": [
                        "scoring",
                        "portfolio reviews",
                        "existing project intake",
                        "manual outreach",
                        "help",
                    ],
                    "visual_browser_check": "Unavailable: no enabled browser",
                },
            )
            s.add(art)
            s.flush()
            work = WorkItem(
                id="handoff-foundry-next-r1",
                workspace_id=venture.workspace_id,
                title=(
                    "Collect first operation feedback and run visual QA when "
                    "browser is available"
                ),
                kind=WorkItemKind.INVESTIGATION,
                status=WorkItemStatus.READY,
                owner="agent",
                acceptance_criteria=(
                    "One observed workflow issue or confirmation; no fabricated "
                    "time-saving claim"
                ),
            )
            s.add(work)
            s.flush()
            latest = s.scalar(
                select(WorkspaceReview)
                .where(WorkspaceReview.workspace_id == venture.workspace_id)
                .order_by(WorkspaceReview.revision.desc())
            )
            ReviewService._append(
                s,
                ReviewInput.model_validate(
                    {
                        "workspace_id": venture.workspace_id,
                        "expected_revision": latest.revision if latest else 0,
                        "investigation_stage": "solution_validation",
                        "product_maturity": "prototype",
                        "disposition": "internal_only",
                        "next_action": work.title,
                        "next_work_item_id": work.id,
                        "reason": (
                            "Implemented local handoff features; HTTP checks pass; "
                            "visual/browser and real operator feedback still needed."
                        ),
                        "author": "agent:handoff-20261004",
                        "source_artifact_id": art.id,
                    }
                ),
            )
    scores = ScoringService(factory)
    score_receipts = []
    for idea_id in ["P023", "P103", "P046", "N008", "D001"]:
        history = scores.show(idea_id)["history"]
        with factory() as lookup:
            idea = lookup.get(Idea, idea_id)
            assert idea is not None
            receipt_id = stable_id("targeted-assessment-r1:" + idea.current_revision_id)
            if lookup.get(Artifact, receipt_id):
                continue
        original = next(
            (a for a in history if a["scorecard_id"] == "portfolio-original-v1"), None
        )
        values = {c["key"]: c["raw"] for c in original["criteria"]} if original else {}
        reasons = (
            {
                key: "Explicitly carried from original assessment "
                + original["id"]
                + "; provisional source judgment, not independently revalidated."
                for key in values
            }
            if original
            else {}
        )
        if idea_id in ["P023", "P103"]:
            old = values["founder_fit"]
            values["founder_fit"] = min(10, old + 1)
            reasons["founder_fit"] = (
                f"{old} → {values['founder_fit']}: handoff reports founder interest "
                "and possible friends access; this changes personal fit only, "
                "not independent demand."
            )
        elif idea_id == "P046":
            old = values["mvp_speed"]
            values["mvp_speed"] = min(10, old + 1)
            reasons["mvp_speed"] = (
                f"{old} → {values['mvp_speed']}: inspected existing prototype "
                "reduces starting engineering effort. Runtime blocked; "
                "payer/legal/network judgments carried, not cleared."
            )
        else:
            values = {"founder_fit": 9, "mvp_speed": 8 if idea_id == "D001" else 5}
            reasons = {
                "founder_fit": (
                    "User has supplied a real ride and detailed "
                    "pain/preferences; first-party founder fit, not market "
                    "demand."
                ),
                "mvp_speed": "GPX diagnostic is locally reproducible"
                if idea_id == "D001"
                else (
                    "Scenic planning/editing remains larger than transfer "
                    "analysis; provisional effort judgment only."
                ),
            }
        payload = AssessmentInput(
            idea_id=idea_id,
            scores=values,
            criterion_rationales=reasons,
            evidence_ids={
                key: [idea_evidence[idea_id]]
                for key in (
                    "founder_fit"
                    if idea_id in ["P023", "P103", "N008", "D001"]
                    else "mvp_speed",
                )
            },
            rationale=(
                "Targeted handoff r1; changed factors explained "
                "individually. Unchanged workbook judgments explicitly "
                "carried where present; no adoption/payment validation. "
                "Source reports retain uncertainty."
            ),
            author="agent:handoff-20261004",
            confidence=ConfidenceLevel.LOW,
            recommendation=(
                "Bounded next test or specific hold; no commercial build commitment"
            ),
        )
        with UnitOfWork(factory) as unit:
            s = unit.session
            assert s is not None
            ScoringService._default_card(s, payload.scorecard_id)
            assessment = ScoringService._append(s, payload)
            s.flush()
            result = ScoringService._assessment(s, assessment)
            idea = s.get(Idea, idea_id)
            assert idea is not None
            s.add(
                Artifact(
                    id=receipt_id,
                    workspace_id=idea.workspace_id,
                    kind=ArtifactKind.REPORT,
                    name="Targeted assessment provenance",
                    location="db:idea_assessments/" + result["id"],
                    metadata_json={
                        "assessment_id": result["id"],
                        "original_assessment_id": original["id"] if original else None,
                        "payload": payload.model_dump(mode="json"),
                    },
                )
            )
        score_receipts.append(
            {
                "idea_id": idea_id,
                "assessment_id": result["id"],
                "total": result["total"],
                "coverage": result["coverage"],
            }
        )
    return {"records": receipts, "targeted_scores": score_receipts}


if __name__ == "__main__":
    engine = create_db_engine(load_settings().database_url)
    try:
        print(
            json.dumps(
                record(
                    create_session_factory(engine), Path(__file__).resolve().parents[1]
                ),
                indent=2,
            )
        )
    finally:
        engine.dispose()
