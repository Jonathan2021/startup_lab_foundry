"""Transactional use cases for the first Foundry venture workflow."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

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
    DecisionKind,
    DecisionStatus,
    Evidence,
    EvidenceKind,
    Experiment,
    ExperimentAssumption,
    IdentityMixin,
    Portfolio,
    Venture,
    VentureStage,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    Workspace,
    WorkspaceKind,
    new_id,
)
from startup_foundry.errors import (
    ConflictError,
    ReferenceError,
    ValidationError,
    VentureNotFoundError,
)
from startup_foundry.repository import SessionFactory, UnitOfWork

JsonObject = dict[str, object]


def required_text(name: str, value: str) -> str:
    """Return trimmed required text or raise before persistence is opened."""

    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{name} is required and cannot be blank")
    return cleaned


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class FoundryApplication:
    """Application boundary; every public method owns one unit of work."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _session(unit_of_work: UnitOfWork) -> Session:
        if unit_of_work.session is None:
            raise RuntimeError("UnitOfWork did not create a session")
        return unit_of_work.session

    @staticmethod
    def _venture(session: Session, venture_id: str) -> tuple[Venture, Workspace]:
        venture = session.get(Venture, venture_id)
        if venture is None:
            raise VentureNotFoundError(venture_id)
        workspace = session.get(Workspace, venture.workspace_id)
        if workspace is None:
            raise ReferenceError(
                f"Venture {venture_id!r} has no associated workspace"
            )
        return venture, workspace

    @staticmethod
    def _same_workspace(
        *, expected: str, actual: str, description: str
    ) -> None:
        if expected != actual:
            raise ReferenceError(f"{description} must belong to the same venture")

    def create_venture(
        self,
        *,
        venture_id: str,
        name: str,
        objective: str,
        stage: VentureStage,
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            if session.get(Venture, venture_id) is not None:
                raise ConflictError(f"Venture {venture_id!r} already exists")

            portfolio = session.scalar(
                select(Portfolio).where(Portfolio.key == "default")
            )
            if portfolio is None:
                portfolio = Portfolio(
                    id="portfolio-default", key="default", name="Foundry ventures"
                )
                session.add(portfolio)
                session.flush()

            workspace = Workspace(
                id=new_id(),
                portfolio_id=portfolio.id,
                key=venture_id,
                title=name,
                description=objective,
                kind=WorkspaceKind.VENTURE,
            )
            venture = Venture(
                id=venture_id,
                workspace_id=workspace.id,
                objective=objective,
                stage=stage,
            )
            session.add(workspace)
            session.flush()
            session.add(venture)
            session.flush()
            return self._venture_json(venture, workspace)

    def show_venture(self, venture_id: str) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            venture, workspace = self._venture(session, venture_id)

            assumptions = list(
                session.scalars(
                    select(Assumption)
                    .where(Assumption.workspace_id == workspace.id)
                    .order_by(Assumption.created_at, Assumption.id)
                )
            )
            evidence = list(
                session.scalars(
                    select(Evidence)
                    .where(Evidence.workspace_id == workspace.id)
                    .order_by(Evidence.created_at, Evidence.id)
                )
            )
            assessments = list(
                session.scalars(
                    select(AssumptionAssessment)
                    .join(Assumption)
                    .where(Assumption.workspace_id == workspace.id)
                    .order_by(
                        AssumptionAssessment.created_at, AssumptionAssessment.id
                    )
                )
            )
            decisions = list(
                session.scalars(
                    select(Decision)
                    .where(Decision.workspace_id == workspace.id)
                    .order_by(Decision.created_at, Decision.id)
                )
            )
            work_items = list(
                session.scalars(
                    select(WorkItem)
                    .where(WorkItem.workspace_id == workspace.id)
                    .order_by(WorkItem.created_at, WorkItem.id)
                )
            )
            artifacts = list(
                session.scalars(
                    select(Artifact)
                    .where(Artifact.workspace_id == workspace.id)
                    .order_by(Artifact.created_at, Artifact.id)
                )
            )
            return {
                "venture": self._venture_json(venture, workspace),
                "assumptions": [self._assumption_json(item) for item in assumptions],
                "evidence": [self._evidence_json(item) for item in evidence],
                "assumption_assessments": [
                    self._assessment_json(session, item) for item in assessments
                ],
                "decisions": [
                    self._decision_json(session, item) for item in decisions
                ],
                "work_items": [self._work_item_json(item) for item in work_items],
                "artifacts": [self._artifact_json(item) for item in artifacts],
            }

    def add_assumption(
        self,
        *,
        assumption_id: str,
        venture_id: str,
        statement: str,
        kind: AssumptionKind,
        importance: int,
        uncertainty: int,
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            _, workspace = self._venture(session, venture_id)
            self._ensure_new(session, Assumption, assumption_id)
            assumption = Assumption(
                id=assumption_id,
                workspace_id=workspace.id,
                statement=statement,
                kind=kind,
                importance=importance,
                uncertainty=uncertainty,
            )
            session.add(assumption)
            session.flush()
            return self._assumption_json(assumption)

    def assess_assumption(
        self,
        *,
        assessment_id: str,
        assumption_id: str,
        evidence_ids: list[str],
        outcome: AssessmentOutcome,
        confidence: ConfidenceLevel,
        rationale: str,
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            self._ensure_new(session, AssumptionAssessment, assessment_id)
            assumption = session.get(Assumption, assumption_id)
            if assumption is None:
                raise ReferenceError(f"Assumption {assumption_id!r} was not found")
            linked_evidence: list[Evidence] = []
            for evidence_id in evidence_ids:
                item = session.get(Evidence, evidence_id)
                if item is None:
                    raise ReferenceError(f"Evidence {evidence_id!r} was not found")
                self._same_workspace(
                    expected=assumption.workspace_id,
                    actual=item.workspace_id,
                    description=f"Evidence {evidence_id!r}",
                )
                linked_evidence.append(item)

            assessment = AssumptionAssessment(
                id=assessment_id,
                assumption_id=assumption.id,
                outcome=outcome,
                confidence=confidence,
                rationale=rationale,
            )
            session.add(assessment)
            session.flush()
            session.add_all(
                AssessmentEvidence(
                    assessment_id=assessment.id, evidence_id=item.id
                )
                for item in linked_evidence
            )
            session.flush()
            return self._assessment_json(session, assessment)

    def add_evidence(
        self,
        *,
        evidence_id: str,
        venture_id: str,
        origin_work_item_id: str | None,
        kind: EvidenceKind,
        confidence: ConfidenceLevel,
        summary: str,
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            _, workspace = self._venture(session, venture_id)
            self._ensure_new(session, Evidence, evidence_id)
            if origin_work_item_id is not None:
                work_item = session.get(WorkItem, origin_work_item_id)
                if work_item is None:
                    raise ReferenceError(
                        f"WorkItem {origin_work_item_id!r} was not found"
                    )
                self._same_workspace(
                    expected=workspace.id,
                    actual=work_item.workspace_id,
                    description=f"WorkItem {origin_work_item_id!r}",
                )
            evidence = Evidence(
                id=evidence_id,
                workspace_id=workspace.id,
                origin_work_item_id=origin_work_item_id,
                kind=kind,
                confidence=confidence,
                summary=summary,
            )
            session.add(evidence)
            session.flush()
            return self._evidence_json(evidence)

    def add_decision(
        self,
        *,
        decision_id: str,
        venture_id: str,
        kind: DecisionKind,
        summary: str,
        rationale: str,
        assessment_ids: list[str],
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            _, workspace = self._venture(session, venture_id)
            self._ensure_new(session, Decision, decision_id)
            assessments: list[AssumptionAssessment] = []
            for assessment_id in assessment_ids:
                assessment = session.get(AssumptionAssessment, assessment_id)
                if assessment is None:
                    raise ReferenceError(
                        f"AssumptionAssessment {assessment_id!r} was not found"
                    )
                assumption = session.get(Assumption, assessment.assumption_id)
                if assumption is None:
                    raise ReferenceError(
                        f"Assessment {assessment_id!r} has no assumption"
                    )
                self._same_workspace(
                    expected=workspace.id,
                    actual=assumption.workspace_id,
                    description=f"Assessment {assessment_id!r}",
                )
                assessments.append(assessment)

            decision = Decision(
                id=decision_id,
                workspace_id=workspace.id,
                kind=kind,
                status=DecisionStatus.ACCEPTED,
                summary=summary,
                rationale=rationale,
            )
            session.add(decision)
            session.flush()
            session.add_all(
                DecisionAssessment(
                    decision_id=decision.id, assessment_id=item.id
                )
                for item in assessments
            )
            session.flush()
            return self._decision_json(session, decision)

    def add_work_item(
        self,
        *,
        work_item_id: str,
        venture_id: str,
        title: str,
        kind: WorkItemKind,
        decision_id: str | None,
        acceptance_criteria: str | None,
        method: str | None,
        success_criteria: str | None,
        failure_criteria: str | None,
        assumption_ids: list[str],
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            _, workspace = self._venture(session, venture_id)
            self._ensure_new(session, WorkItem, work_item_id)
            if decision_id is not None:
                decision = session.get(Decision, decision_id)
                if decision is None:
                    raise ReferenceError(f"Decision {decision_id!r} was not found")
                self._same_workspace(
                    expected=workspace.id,
                    actual=decision.workspace_id,
                    description=f"Decision {decision_id!r}",
                )

            assumptions: list[Assumption] = []
            for assumption_id in assumption_ids:
                assumption = session.get(Assumption, assumption_id)
                if assumption is None:
                    raise ReferenceError(
                        f"Assumption {assumption_id!r} was not found"
                    )
                self._same_workspace(
                    expected=workspace.id,
                    actual=assumption.workspace_id,
                    description=f"Assumption {assumption_id!r}",
                )
                assumptions.append(assumption)

            work_item = WorkItem(
                id=work_item_id,
                workspace_id=workspace.id,
                decision_id=decision_id,
                title=title,
                kind=kind,
                status=WorkItemStatus.TODO,
                acceptance_criteria=acceptance_criteria,
            )
            session.add(work_item)
            session.flush()

            if kind is WorkItemKind.EXPERIMENT:
                if (
                    method is None
                    or success_criteria is None
                    or failure_criteria is None
                ):
                    raise ValidationError(
                        "experiment work requires method, success criteria, and "
                        "failure criteria"
                    )
                if not assumptions:
                    raise ValidationError(
                        "experiment work requires at least one assumption"
                    )
                experiment = Experiment(
                    id=new_id(),
                    work_item_id=work_item.id,
                    method=method,
                    success_criteria=success_criteria,
                    failure_criteria=failure_criteria,
                )
                session.add(experiment)
                session.flush()
                session.add_all(
                    ExperimentAssumption(
                        experiment_id=experiment.id,
                        assumption_id=assumption.id,
                        is_primary=index == 0,
                    )
                    for index, assumption in enumerate(assumptions)
                )
                session.flush()
            elif kind is WorkItemKind.EXECUTION and acceptance_criteria is None:
                raise ValidationError(
                    "execution work requires acceptance criteria"
                )

            return self._work_item_json(work_item)

    def set_work_item_status(
        self, work_item_id: str, status: WorkItemStatus
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            work_item = session.get(WorkItem, work_item_id)
            if work_item is None:
                raise ReferenceError(f"WorkItem {work_item_id!r} was not found")
            work_item.status = status
            session.flush()
            return self._work_item_json(work_item)

    def add_artifact(
        self,
        *,
        artifact_id: str,
        venture_id: str,
        work_item_id: str | None,
        kind: ArtifactKind,
        name: str,
        location: str,
    ) -> JsonObject:
        with UnitOfWork(self._session_factory) as unit_of_work:
            session = self._session(unit_of_work)
            _, workspace = self._venture(session, venture_id)
            self._ensure_new(session, Artifact, artifact_id)
            if work_item_id is not None:
                work_item = session.get(WorkItem, work_item_id)
                if work_item is None:
                    raise ReferenceError(f"WorkItem {work_item_id!r} was not found")
                self._same_workspace(
                    expected=workspace.id,
                    actual=work_item.workspace_id,
                    description=f"WorkItem {work_item_id!r}",
                )
            artifact = Artifact(
                id=artifact_id,
                workspace_id=workspace.id,
                work_item_id=work_item_id,
                kind=kind,
                name=name,
                location=location,
            )
            session.add(artifact)
            session.flush()
            return self._artifact_json(artifact)

    @staticmethod
    def _ensure_new(
        session: Session, model: type[IdentityMixin], entity_id: str
    ) -> None:
        if session.get(model, entity_id) is not None:
            raise ConflictError(f"{model.__name__} {entity_id!r} already exists")

    @staticmethod
    def _venture_json(venture: Venture, workspace: Workspace) -> JsonObject:
        return {
            "id": venture.id,
            "name": workspace.title,
            "objective": venture.objective,
            "stage": venture.stage.value,
            "created_at": _timestamp(venture.created_at),
        }

    @staticmethod
    def _assumption_json(assumption: Assumption) -> JsonObject:
        return {
            "id": assumption.id,
            "statement": assumption.statement,
            "kind": assumption.kind.value,
            "status": assumption.status.value,
            "importance": assumption.importance,
            "uncertainty": assumption.uncertainty,
            "created_at": _timestamp(assumption.created_at),
        }

    @staticmethod
    def _evidence_json(evidence: Evidence) -> JsonObject:
        return {
            "id": evidence.id,
            "origin_work_item_id": evidence.origin_work_item_id,
            "kind": evidence.kind.value,
            "summary": evidence.summary,
            "confidence": evidence.confidence.value,
            "captured_at": _timestamp(evidence.captured_at),
        }

    @staticmethod
    def _assessment_json(
        session: Session, assessment: AssumptionAssessment
    ) -> JsonObject:
        evidence_ids = list(
            session.scalars(
                select(AssessmentEvidence.evidence_id)
                .where(AssessmentEvidence.assessment_id == assessment.id)
                .order_by(AssessmentEvidence.evidence_id)
            )
        )
        return {
            "id": assessment.id,
            "assumption_id": assessment.assumption_id,
            "evidence_ids": evidence_ids,
            "outcome": assessment.outcome.value,
            "confidence": assessment.confidence.value,
            "rationale": assessment.rationale,
            "assessed_at": _timestamp(assessment.assessed_at),
        }

    @staticmethod
    def _decision_json(session: Session, decision: Decision) -> JsonObject:
        assessment_ids = list(
            session.scalars(
                select(DecisionAssessment.assessment_id)
                .where(DecisionAssessment.decision_id == decision.id)
                .order_by(DecisionAssessment.assessment_id)
            )
        )
        return {
            "id": decision.id,
            "assessment_ids": assessment_ids,
            "kind": decision.kind.value,
            "status": decision.status.value,
            "summary": decision.summary,
            "rationale": decision.rationale,
            "decided_at": _timestamp(decision.decided_at),
        }

    @staticmethod
    def _work_item_json(work_item: WorkItem) -> JsonObject:
        return {
            "id": work_item.id,
            "decision_id": work_item.decision_id,
            "title": work_item.title,
            "kind": work_item.kind.value,
            "status": work_item.status.value,
            "acceptance_criteria": work_item.acceptance_criteria,
            "created_at": _timestamp(work_item.created_at),
        }

    @staticmethod
    def _artifact_json(artifact: Artifact) -> JsonObject:
        return {
            "id": artifact.id,
            "work_item_id": artifact.work_item_id,
            "kind": artifact.kind.value,
            "name": artifact.name,
            "location": artifact.location,
            "created_at": _timestamp(artifact.created_at),
        }
