"""Narrow manual initial review; persistent local work without a scheduler."""

from pathlib import Path
from typing import Any, Literal

from pydantic import Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    Artifact,
    Decision,
    DecisionEvidence,
    DecisionKind,
    DecisionStatus,
    Disposition,
    Evidence,
    HumanRequestDependency,
    HumanRequestTarget,
    Idea,
    IdeaAssessment,
    IdeaRevision,
    InvestigationStage,
    ProductMaturity,
    Venture,
    WorkItem,
    WorkItemStatus,
    WorkspaceReview,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.human_inputs import (
    ClaimInput,
    Contract,
    HumanInputService,
    ReleaseInput,
    RequestInput,
)
from startup_foundry.portfolio import stable_id
from startup_foundry.repository import SessionFactory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import REVIEWED, AssessmentInput, ScoringService, digest
from startup_foundry.snapshots import audit, snapshot, transaction
from startup_foundry.venture_scoring import (
    VentureAssessmentInput,
    VentureScoringService,
)

JSON = dict[str, Any]
Subject = Literal["idea", "venture"]


class IntakeRequest(Contract):
    expected_revision_id: str | None
    actor: str = Field(min_length=1, max_length=200)


class IntakeCompletion(Contract):
    schema_version: Literal[2] = 2
    work_id: str
    expected_version: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=200)
    request_key: str = Field(min_length=1, max_length=160)
    research_summary: str = Field(min_length=1, max_length=20000)
    research_source: str = Field(min_length=1, max_length=10000)
    research_limits: str = Field(min_length=1, max_length=10000)
    scores: dict[str, Any]
    score_rationale: str = Field(min_length=1, max_length=20000)
    unknown_reason: str = Field(min_length=1, max_length=10000)
    expected_sequence: int = Field(ge=0)
    expected_review_revision: int = Field(ge=0)
    next_action: str = Field(min_length=1, max_length=10000)
    outcome: Literal["continue", "narrow", "hold", "stop"] = "continue"
    revisit_trigger: str | None = Field(default=None, min_length=1, max_length=10000)
    narrowed_scope: str | None = Field(default=None, min_length=1, max_length=10000)
    next_work_title: str | None = Field(default=None, min_length=1, max_length=300)
    next_owner: Literal["agent", "you"] | None = None
    question_id: str | None = Field(default=None, pattern=r"^R[0-9]{3,6}$")
    question: str | None = Field(default=None, min_length=1, max_length=20000)

    @model_validator(mode="after")
    def validate_outcome(self) -> "IntakeCompletion":
        if self.outcome in {"continue", "narrow"} and (
            not self.next_work_title or not self.next_owner
        ):
            raise ValueError("Continue/narrow requires bounded next work and owner")
        if self.outcome == "stop" and (self.next_work_title or self.next_owner):
            raise ValueError("Stop finishes intake without scheduling continuation")
        if self.outcome == "hold" and not (self.revisit_trigger or "").strip():
            raise ValueError("Hold requires a revisit trigger")
        if self.outcome == "hold" and self.next_owner == "agent":
            raise ValueError("Hold cannot schedule ready agent work")
        if bool(self.next_work_title) != bool(self.next_owner):
            raise ValueError("Next work title and owner must be supplied together")
        if self.outcome == "narrow" and not (self.narrowed_scope or "").strip():
            raise ValueError("Narrow requires the explicit proposed scope")
        if self.next_owner != "you" and (self.question_id or self.question):
            raise ValueError("Human questions require human next work")
        return self


class ManualIntakeService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    @staticmethod
    def _subject(session: Session, kind: Subject, identity: str) -> JSON:
        entity = (
            session.get(Idea, identity)
            if kind == "idea"
            else session.get(Venture, identity)
        )
        if not entity:
            raise ReferenceError("Intake subject missing")
        revision_id = (
            entity.current_revision_id
            if isinstance(entity, Idea)
            else entity.source_idea_revision_id
        )
        revision = session.get(IdeaRevision, revision_id) if revision_id else None
        return {
            "subject": kind,
            "subject_id": identity,
            "workspace_id": entity.workspace_id,
            "idea_id": revision.idea_id if revision else None,
            "idea_revision_id": revision_id,
            "venture_id": identity if kind == "venture" else None,
            "known_input": {
                "description": revision.cleaned_description
                if isinstance(entity, Idea) and revision
                else entity.objective
                if isinstance(entity, Venture)
                else "",
                "customer": revision.target_customer if revision else None,
                "business_model": revision.business_model if revision else None,
                "proposed_test": revision.key_validation_test if revision else None,
            },
        }

    @classmethod
    def queue(
        cls, session: Session, kind: Subject, identity: str, actor: str
    ) -> WorkItem:
        context = cls._subject(session, kind, identity)
        key = identity + ":" + str(context["idea_revision_id"])
        work_id = stable_id("manual-intake:" + kind + ":" + key)
        existing = session.get(WorkItem, work_id)
        if existing:
            return existing
        if session.scalar(
            select(WorkspaceReview.id).where(
                WorkspaceReview.workspace_id == context["workspace_id"]
            )
        ):
            raise ConflictError(
                "Initial review already recorded; use the current next work"
            )
        work = WorkItem(
            id=work_id,
            workspace_id=context["workspace_id"],
            title="Initial manual review of " + identity,
            kind="investigation",
            status=WorkItemStatus.READY,
            owner="agent",
            description=(
                "Investigate the stated hypothesis and existing alternatives. "
                "Retain sources, limits, partial scores and the next bounded "
                "action; no external action."
            ),
            acceptance_criteria=(
                "Attributed research, justified known factors, explicit unknowns, "
                "review and concrete next owner/action. Queue does not start a worker."
            ),
        )
        session.add(work)
        session.flush()
        snapshot(
            session,
            work.workspace_id,
            "manual-intake/v1",
            {
                **context,
                "work_id": work.id,
                "actor": actor,
                "completion_requirements": work.acceptance_criteria,
            },
            key=key,
            work_id=work.id,
        )
        audit(
            session,
            work.workspace_id,
            work.id,
            "manual_intake_queued",
            actor,
            {"subject": kind, "subject_id": identity},
        )
        return work

    @staticmethod
    def _work_json(work: WorkItem) -> JSON:
        return {
            "id": work.id,
            "workspace_id": work.workspace_id,
            "title": work.title,
            "owner": work.owner,
            "status": work.status.value,
            "version": work.version_id,
            "description": work.description,
            "acceptance_criteria": work.acceptance_criteria,
        }

    def request(self, kind: Subject, identity: str, payload: IntakeRequest) -> JSON:
        with transaction(self.factory) as session:
            context = self._subject(session, kind, identity)
            if context["idea_revision_id"] != payload.expected_revision_id:
                raise ConflictError(
                    "Subject revision changed; refresh before requesting intake"
                )
            linked = self._handoff(session, kind, identity)
            if linked and linked.get("linked_intake"):
                return {**linked["work"], "linked_intake": linked["linked_intake"]}
            return self._work_json(self.queue(session, kind, identity, payload.actor))

    @classmethod
    def promotion(cls, session: Session, idea: Idea, venture: Venture) -> JSON:
        """Keep one overlapping investigation; preserve source ownership/history."""
        source = cls._handoff(session, "idea", idea.id)
        source_work = session.get(WorkItem, source["work_id"]) if source else None
        exact = bool(
            source and source["idea_revision_id"] == venture.source_idea_revision_id
        )
        reuse = (
            exact
            and source_work
            and source_work.status
            in {
                WorkItemStatus.IN_PROGRESS,
                WorkItemStatus.DONE,
            }
        )
        next_work = (
            None
            if reuse
            else cls.queue(session, "venture", venture.id, "local operator")
        )
        policy = "linked_existing" if reuse else "new_intake"
        if exact and source_work and source_work.status == WorkItemStatus.READY:
            source_work.status = WorkItemStatus.CANCELLED
            policy = "superseded_unstarted"
        data = {
            "idea_id": idea.id,
            "venture_id": venture.id,
            "policy": policy,
            "source_work_id": source_work.id if source_work and exact else None,
            "venture_work_id": next_work.id if next_work else None,
            "reason": "Same source scope; original research and history are retained",
        }
        for workspace in [idea.workspace_id, venture.workspace_id]:
            snapshot(session, workspace, "promotion-intake/v1", data, key=venture.id)
            audit(
                session,
                workspace,
                venture.id,
                "intake_promotion_linked",
                "local operator",
                data,
            )
        return data

    @classmethod
    def _handoff(cls, session: Session, kind: Subject, identity: str) -> JSON | None:
        context = cls._subject(session, kind, identity)
        artifact = session.scalar(
            select(Artifact)
            .where(
                Artifact.workspace_id == context["workspace_id"],
                Artifact.name == "manual-intake/v1",
            )
            .order_by(Artifact.created_at.desc(), Artifact.id)
            .limit(1)
        )
        promotion = session.scalar(
            select(Artifact)
            .where(
                Artifact.workspace_id == context["workspace_id"],
                Artifact.name == "promotion-intake/v1",
            )
            .order_by(Artifact.created_at.desc(), Artifact.id)
            .limit(1)
        )
        if not artifact:
            if kind == "venture" and promotion:
                linked = cls._handoff(
                    session, "idea", promotion.metadata_json["idea_id"]
                )
                if linked:
                    return {**linked, "linked_intake": promotion.metadata_json}
            return None
        data = artifact.metadata_json
        work = session.get(WorkItem, data["work_id"])
        assert work
        return {
            **data,
            "promotion": promotion.metadata_json if promotion else None,
            "artifact_id": artifact.id,
            "work": cls._work_json(work),
            "worker_running": False,
            "revision_stale": context["idea_revision_id"] != data["idea_revision_id"],
            "scope_stale": context["known_input"] != data["known_input"],
            "expected_sequence": VentureScoringService.latest(
                session, identity, REVIEWED
            )
            if kind == "venture"
            else session.scalar(
                select(IdeaAssessment.assessment_number)
                .where(
                    IdeaAssessment.idea_revision_id == context["idea_revision_id"],
                    IdeaAssessment.scorecard_id == REVIEWED,
                )
                .order_by(IdeaAssessment.assessment_number.desc())
                .limit(1)
            )
            or 0,
            "expected_review_revision": session.scalar(
                select(WorkspaceReview.revision)
                .where(WorkspaceReview.workspace_id == context["workspace_id"])
                .order_by(WorkspaceReview.revision.desc())
                .limit(1)
            )
            or 0,
        }

    def handoff(self, kind: Subject, identity: str) -> JSON | None:
        with self.factory() as session:
            return self._handoff(session, kind, identity)

    def claim(self, kind: Subject, identity: str, payload: ClaimInput) -> JSON:
        with transaction(self.factory) as session:
            handoff = self._handoff(session, kind, identity)
            if handoff and handoff.get("linked_intake"):
                raise ConflictError(
                    "Intake is retained in the source idea; claim it there"
                )
            if not handoff or handoff["revision_stale"] or handoff["scope_stale"]:
                raise ConflictError(
                    "No current intake; request the exact current revision"
                )
            work = session.get(WorkItem, handoff["work_id"])
            assert work
            from startup_foundry.decision_maps import require_execution_eligible

            require_execution_eligible(session, work)
            if (
                work.version_id != payload.expected_version
                or work.status != WorkItemStatus.READY
            ):
                raise ConflictError("Intake changed or already claimed")
            work.status = WorkItemStatus.IN_PROGRESS
            work.owner = payload.actor
            audit(
                session,
                work.workspace_id,
                work.id,
                "manual_intake_claimed",
                payload.actor,
                {},
            )
            session.flush()
            return self._work_json(work)

    def release(self, kind: Subject, identity: str, payload: ReleaseInput) -> JSON:
        with transaction(self.factory) as session:
            handoff = self._handoff(session, kind, identity)
            if handoff and handoff.get("linked_intake"):
                raise ConflictError("Release the linked intake in its source idea")
            if not handoff or handoff["work_id"] != payload.work_id:
                raise ReferenceError("Release belongs to a different intake")
            work = session.get(WorkItem, payload.work_id)
            assert work
            if (
                work.version_id != payload.expected_version
                or work.owner != payload.actor
                or work.status != WorkItemStatus.IN_PROGRESS
            ):
                raise ConflictError("Only this intake claimant can release work")
            work.status = WorkItemStatus.READY
            work.owner = "agent"
            audit(
                session,
                work.workspace_id,
                work.id,
                "manual_intake_requeued",
                payload.actor,
                {"reason": payload.reason},
            )
            session.flush()
            return self._work_json(work)

    def complete(self, kind: Subject, identity: str, payload: IntakeCompletion) -> JSON:
        with transaction(self.factory) as session:
            handoff = self._handoff(session, kind, identity)
            if handoff and handoff.get("linked_intake"):
                raise ConflictError("Complete the linked intake in its source idea")
            if not handoff or handoff["work_id"] != payload.work_id:
                raise ReferenceError("Completion belongs to a different intake")
            receipt_id = stable_id(
                "manual-intake-completion/v1:"
                + handoff["workspace_id"]
                + ":"
                + payload.work_id
            )
            old = session.get(Artifact, receipt_id)
            if old:
                original_input = payload.model_dump(mode="json")
                if "input_schema" not in old.metadata_json:
                    if (
                        payload.outcome != "continue"
                        or payload.narrowed_scope
                        or payload.revisit_trigger
                    ):
                        raise ConflictError(
                            "Historical completion has a different outcome"
                        )
                    for key in [
                        "schema_version",
                        "outcome",
                        "revisit_trigger",
                        "narrowed_scope",
                    ]:
                        original_input.pop(key)
                if old.metadata_json["payload_digest"] != digest(original_input):
                    raise ConflictError(
                        "Intake already completed with different content"
                    )
                return old.metadata_json
            work = session.get(WorkItem, payload.work_id)
            assert work
            if (
                handoff["revision_stale"]
                or handoff["scope_stale"]
                or work.version_id != payload.expected_version
                or work.status != WorkItemStatus.IN_PROGRESS
                or work.owner != payload.actor
            ):
                raise ConflictError(
                    "Only the claimant of this current intake can complete it"
                )
            if any(
                not value.strip()
                for value in [
                    payload.research_summary,
                    payload.research_source,
                    payload.research_limits,
                    payload.score_rationale,
                    payload.unknown_reason,
                    payload.next_action,
                ]
            ):
                raise ValidationError(
                    "Research, limits, unknowns and next action must be nonblank"
                )
            if payload.next_owner == "you" and (
                not payload.question_id or not payload.question
            ):
                raise ValidationError(
                    "Human next work needs a narrowly scoped question and request ID"
                )
            if payload.next_owner == "agent" and (
                payload.question_id or payload.question
            ):
                raise ValidationError("Human request belongs to human next work")
            evidence = Evidence(
                workspace_id=work.workspace_id,
                origin_work_item_id=work.id,
                kind="market_research",
                confidence="low",
                summary=payload.research_summary,
                details="Source: "
                + payload.research_source
                + "\nLimits: "
                + payload.research_limits,
                captured_by=payload.actor,
            )
            session.add(evidence)
            session.flush()
            rationale = (
                payload.score_rationale + "\nUnknown factors: " + payload.unknown_reason
            )
            next_work = (
                WorkItem(
                    workspace_id=work.workspace_id,
                    title=payload.next_work_title,
                    description=payload.next_action,
                    acceptance_criteria=payload.next_action,
                    kind="investigation",
                    owner=payload.next_owner,
                    status=WorkItemStatus.BLOCKED
                    if payload.next_owner == "you"
                    else WorkItemStatus.READY,
                    blocked_reason="human_input"
                    if payload.next_owner == "you"
                    else None,
                )
                if payload.next_work_title
                else None
            )
            if next_work:
                session.add(next_work)
                session.flush()
            if payload.next_owner == "you":
                assert next_work is not None and payload.next_work_title is not None
                inputs = HumanInputService(self.factory, Path("."))
                inputs._register(
                    session,
                    RequestInput(
                        id=payload.question_id or "",
                        workspace_id=work.workspace_id,
                        target_workspace_ids=[work.workspace_id],
                        title=payload.next_work_title,
                        question=payload.question or "",
                        actor=payload.actor,
                    ),
                )
                target = session.scalar(
                    select(HumanRequestTarget).where(
                        HumanRequestTarget.request_id == payload.question_id,
                        HumanRequestTarget.workspace_id == work.workspace_id,
                    )
                )
                assert target
                session.add(
                    HumanRequestDependency(
                        target_id=target.id, work_item_id=next_work.id, other_causes=[]
                    )
                )
            research = snapshot(
                session,
                work.workspace_id,
                "manual-intake-research/v1",
                {
                    "evidence_id": evidence.id,
                    "unknown_reason": payload.unknown_reason,
                    "actor": payload.actor,
                    "source": payload.research_source,
                },
                work_id=work.id,
            )
            current = session.scalar(
                select(WorkspaceReview)
                .where(WorkspaceReview.workspace_id == work.workspace_id)
                .order_by(WorkspaceReview.revision.desc())
                .limit(1)
            )
            venture = session.get(Venture, identity) if kind == "venture" else None
            initial_maturity = (
                ProductMaturity.OPERATING
                if venture and venture.stage.value == "operating"
                else ProductMaturity.CONCEPT
            )
            next_action = payload.next_action
            if payload.revisit_trigger:
                next_action += "\nRevisit when: " + payload.revisit_trigger
            if payload.narrowed_scope:
                rationale += "\nProposed narrowed scope: " + payload.narrowed_scope
            decision = Decision(
                workspace_id=work.workspace_id,
                kind={
                    "stop": DecisionKind.STOP,
                    "hold": DecisionKind.DEFER,
                    "narrow": DecisionKind.NARROW,
                }.get(payload.outcome, DecisionKind.CONTINUE),
                status=DecisionStatus.ACCEPTED,
                summary=payload.outcome.capitalize() + ": " + payload.next_action,
                rationale=rationale + "\nLimits: " + payload.research_limits,
                decided_by=payload.actor,
            )
            session.add(decision)
            session.flush()
            session.add(
                DecisionEvidence(decision_id=decision.id, evidence_id=evidence.id)
            )
            review = ReviewService._append(
                session,
                ReviewInput(
                    workspace_id=work.workspace_id,
                    expected_revision=payload.expected_review_revision,
                    investigation_stage=current.investigation_stage
                    if current
                    else InvestigationStage.TRIAGE,
                    product_maturity=current.product_maturity
                    if current
                    else initial_maturity,
                    disposition={
                        "stop": Disposition.DROPPED,
                        "hold": Disposition.HOLD,
                    }.get(payload.outcome, Disposition.PURSUE),
                    next_action=next_action,
                    next_work_item_id=next_work.id if next_work else None,
                    reason=rationale,
                    author=payload.actor,
                    source_artifact_id=research.id,
                    decision_id=decision.id,
                ),
            )
            refs = {
                key: [evidence.id]
                for key, value in payload.scores.items()
                if value is not None
            }
            if kind == "venture":
                assessment = VentureScoringService(self.factory)._assess(
                    session,
                    VentureAssessmentInput(
                        venture_id=identity,
                        expected_sequence=payload.expected_sequence,
                        request_key="intake:" + payload.work_id,
                        scores=payload.scores,
                        rationale=rationale,
                        author=payload.actor,
                        evidence_ids=refs,
                    ),
                )
            else:
                current_sequence = (
                    session.scalar(
                        select(IdeaAssessment.assessment_number)
                        .where(
                            IdeaAssessment.idea_revision_id
                            == handoff["idea_revision_id"],
                            IdeaAssessment.scorecard_id == REVIEWED,
                        )
                        .order_by(IdeaAssessment.assessment_number.desc())
                        .limit(1)
                    )
                    or 0
                )
                if current_sequence != payload.expected_sequence:
                    raise ConflictError(
                        "Idea assessment changed; refresh intake context"
                    )
                ScoringService._default_card(session, REVIEWED)
                a = ScoringService._append(
                    session,
                    AssessmentInput(
                        idea_id=identity,
                        revision_id=handoff["idea_revision_id"],
                        scores=payload.scores,
                        rationale=rationale,
                        author=payload.actor,
                        evidence_ids=refs,
                    ),
                )
                assessment = ScoringService._assessment(session, a)
            result = {
                "input_schema": 2,
                "outcome": payload.outcome,
                "payload_digest": digest(payload.model_dump(mode="json")),
                "work_id": work.id,
                "assessment": assessment,
                "evidence_id": evidence.id,
                "review_id": review.id,
                "next_work_id": next_work.id if next_work else None,
                "next_owner": payload.next_owner,
                "question_id": payload.question_id,
            }
            snapshot(
                session,
                work.workspace_id,
                "manual-intake-completion/v1",
                result,
                key=work.id,
                work_id=work.id,
            )
            work.status = WorkItemStatus.DONE
            audit(
                session,
                work.workspace_id,
                work.id,
                "manual_intake_completed",
                payload.actor,
                {"review_id": review.id, "assessment_id": assessment["id"]},
            )
            return result
