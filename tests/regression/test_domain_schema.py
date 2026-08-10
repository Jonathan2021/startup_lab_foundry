"""Regression checks for the agent-owned Foundry domain schema."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    ActionRisk,
    AgentDefinition,
    AgentRun,
    AgentRunStatus,
    AgentVersion,
    ApprovalRequest,
    ApprovalStatus,
    Artifact,
    ArtifactKind,
    AssessmentEvidence,
    AssessmentOutcome,
    Assumption,
    AssumptionAssessment,
    AssumptionKind,
    Base,
    CapabilityCandidate,
    CapabilityStatus,
    ConfidenceLevel,
    CriterionScore,
    Decision,
    DecisionAssessment,
    DecisionKind,
    DecisionStatus,
    Evidence,
    EvidenceKind,
    Experiment,
    ExperimentAssumption,
    ExternalAction,
    ExternalActionStatus,
    FrictionCapability,
    FrictionOccurrence,
    FrictionSeverity,
    Idea,
    IdeaAssessment,
    IdeaOrigin,
    IdeaRevision,
    Portfolio,
    Scorecard,
    ScoreDirection,
    ScoringCriterion,
    Venture,
    VentureStage,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    Workspace,
    WorkspaceKind,
    new_id,
)

EXPECTED_TABLES = {
    "action_attempts",
    "agent_definitions",
    "agent_runs",
    "agent_versions",
    "approval_requests",
    "artifact_relations",
    "artifacts",
    "assessment_evidence",
    "assumption_assessments",
    "assumption_relations",
    "assumptions",
    "audit_events",
    "capability_candidates",
    "capability_uses",
    "criterion_score_evidence",
    "criterion_scores",
    "decision_assessments",
    "decision_evidence",
    "decisions",
    "evidence",
    "evidence_artifacts",
    "evidence_sources",
    "experiments",
    "experiment_assumptions",
    "external_actions",
    "friction_capabilities",
    "friction_occurrences",
    "ideas",
    "idea_assessments",
    "idea_market_actors",
    "idea_relations",
    "idea_revisions",
    "idea_sources",
    "market_actors",
    "portfolios",
    "ranking_entries",
    "ranking_snapshots",
    "reference_sources",
    "scorecards",
    "scoring_criteria",
    "ventures",
    "work_items",
    "workspaces",
}


def sqlite_engine():  # type: ignore[no-untyped-def]
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_schema_creates_and_dbml_covers_every_table() -> None:
    engine = sqlite_engine()
    assert set(Base.metadata.tables) == EXPECTED_TABLES

    dbml_path = Path(__file__).resolve().parents[2] / "docs/foundry-domain.dbml"
    dbml_tables = set(
        re.findall(r"^Table\s+([a-z_]+)\s*\{", dbml_path.read_text(), re.MULTILINE)
    )
    assert dbml_tables == EXPECTED_TABLES

    Base.metadata.drop_all(engine)


def test_schema_supports_idea_learning_execution_and_capability_loops() -> None:
    engine = sqlite_engine()
    with Session(engine) as session:
        portfolio = Portfolio(id=new_id(), key="startup-ideas", name="Startup ideas")
        idea_workspace = Workspace(
            id=new_id(),
            portfolio_id=portfolio.id,
            key="idea-evalops",
            title="Evaluation Dataset Builder",
            kind=WorkspaceKind.IDEA,
        )
        venture_workspace = Workspace(
            id=new_id(),
            portfolio_id=portfolio.id,
            key="venture-evalops",
            title="Agent EvalOps",
            kind=WorkspaceKind.VENTURE,
        )
        capability_workspace = Workspace(
            id=new_id(),
            portfolio_id=portfolio.id,
            key="capability-approvals",
            title="Approval-controlled external actions",
            kind=WorkspaceKind.FOUNDRY_CAPABILITY,
        )
        idea = Idea(
            id=new_id(),
            workspace_id=idea_workspace.id,
            origin=IdeaOrigin.GENERATED_DERIVED,
        )
        revision = IdeaRevision(
            id=new_id(),
            idea_id=idea.id,
            revision_number=1,
            title="Evaluation Dataset Builder for AI Teams",
            cleaned_description="Turn reviewed failures into reusable evaluation data.",
            target_customer="AI teams with human review queues",
            focused_mvp_scope="Import feedback and compare two releases.",
        )
        idea.current_revision_id = revision.id
        scorecard = Scorecard(
            id=new_id(),
            portfolio_id=portfolio.id,
            name="Risk-adjusted opportunity",
            version=1,
        )
        founder_fit = ScoringCriterion(
            id=new_id(),
            scorecard_id=scorecard.id,
            key="founder_fit",
            name="Founder fit",
            direction=ScoreDirection.POSITIVE,
            weight=0.15,
            scale_min=1,
            scale_max=10,
        )
        idea_assessment = IdeaAssessment(
            id=new_id(),
            idea_revision_id=revision.id,
            scorecard_id=scorecard.id,
            confidence=ConfidenceLevel.HIGH,
            overall_score=76,
            grade="A",
            recommendation="Build a focused MVP",
        )
        criterion_score = CriterionScore(
            id=new_id(),
            assessment_id=idea_assessment.id,
            criterion_id=founder_fit.id,
            raw_score=10,
            normalized_score=10,
            weighted_contribution=1.5,
        )
        venture = Venture(
            id=new_id(),
            workspace_id=venture_workspace.id,
            source_idea_revision_id=revision.id,
            objective="Turn corrections into reusable release evidence.",
            stage=VentureStage.DISCOVERY,
        )
        assumption = Assumption(
            id=new_id(),
            workspace_id=venture_workspace.id,
            statement=(
                "Teams repeat failures because corrections are not regression cases."
            ),
            kind=AssumptionKind.DESIRABILITY,
            importance=5,
            uncertainty=4,
        )
        experiment_task = WorkItem(
            id=new_id(),
            workspace_id=venture_workspace.id,
            title="Inspect design-partner correction workflows",
            kind=WorkItemKind.EXPERIMENT,
            status=WorkItemStatus.TODO,
            desired_outcome="Determine whether corrected failures recur.",
        )
        experiment = Experiment(
            id=new_id(),
            work_item_id=experiment_task.id,
            method="Inspect anonymized correction logs from two teams.",
            success_criteria="At least one repeated corrected failure per team.",
            failure_criteria="No repeated failure and durable cases already exist.",
        )
        experiment_assumption = ExperimentAssumption(
            experiment_id=experiment.id,
            assumption_id=assumption.id,
            is_primary=True,
        )
        evidence = Evidence(
            id=new_id(),
            workspace_id=venture_workspace.id,
            origin_work_item_id=experiment_task.id,
            kind=EvidenceKind.EXPERIMENT_RESULT,
            summary="Both teams found previously corrected failures that recurred.",
            confidence=ConfidenceLevel.HIGH,
        )
        assessment = AssumptionAssessment(
            id=new_id(),
            assumption_id=assumption.id,
            outcome=AssessmentOutcome.SUPPORTED,
            confidence=ConfidenceLevel.MEDIUM,
            rationale="The observation supports the pain but the sample is small.",
        )
        assessment_evidence = AssessmentEvidence(
            assessment_id=assessment.id,
            evidence_id=evidence.id,
        )
        decision = Decision(
            id=new_id(),
            workspace_id=venture_workspace.id,
            kind=DecisionKind.NARROW,
            status=DecisionStatus.ACCEPTED,
            summary="Own the failure-to-evaluation loop.",
            rationale="Observed corrections are not retained as release tests.",
        )
        decision_assessment = DecisionAssessment(
            decision_id=decision.id,
            assessment_id=assessment.id,
        )
        execution_task = WorkItem(
            id=new_id(),
            workspace_id=venture_workspace.id,
            decision_id=decision.id,
            title="Build the trace-to-case workflow",
            kind=WorkItemKind.EXECUTION,
            status=WorkItemStatus.TODO,
            acceptance_criteria="One reviewed failure becomes a versioned case.",
        )
        artifact = Artifact(
            id=new_id(),
            workspace_id=venture_workspace.id,
            work_item_id=execution_task.id,
            kind=ArtifactKind.DOCUMENT,
            name="Trace contract",
            location="agentevalops/docs/trace-contract.md",
        )
        friction = FrictionOccurrence(
            id=new_id(),
            workspace_id=venture_workspace.id,
            work_item_id=execution_task.id,
            recurrence_key="external-action-approval-state",
            summary="Approval state is split across notes and agent output.",
            severity=FrictionSeverity.MAJOR,
            workaround="Track the exact payload manually.",
        )
        capability = CapabilityCandidate(
            id=new_id(),
            workspace_id=capability_workspace.id,
            title="Approval-controlled external actions",
            problem_statement="Ventures cannot safely resume exact approved actions.",
            minimal_scope="Exact payload, decision, expiry, and idempotency key.",
            status=CapabilityStatus.OBSERVED,
        )
        friction_capability = FrictionCapability(
            friction_id=friction.id,
            capability_id=capability.id,
            match_strength=5,
            rationale="The capability directly removes the observed blockage.",
        )
        agent = AgentDefinition(
            id=new_id(),
            portfolio_id=portfolio.id,
            key="competitor-research",
            name="Competitor research",
            purpose="Produce sourced competitor reports.",
        )
        agent_version = AgentVersion(
            id=new_id(),
            agent_definition_id=agent.id,
            version="1",
            prompt_version="prompt-1",
            toolset_version="tools-1",
            policy_version="policy-1",
        )
        agent_run = AgentRun(
            id=new_id(),
            workspace_id=venture_workspace.id,
            work_item_id=execution_task.id,
            agent_version_id=agent_version.id,
            status=AgentRunStatus.REQUESTED,
        )
        action = ExternalAction(
            id=new_id(),
            workspace_id=venture_workspace.id,
            work_item_id=execution_task.id,
            agent_run_id=agent_run.id,
            action_type="send_email",
            adapter="email",
            payload={
                "draft_id": "draft-1",
                "recipient": "design-partner@example.invalid",
            },
            payload_digest="sha256:example",
            idempotency_key="venture-evalops:send-email:draft-1",
            risk=ActionRisk.EXTERNAL_COMMUNICATION,
            approval_required=True,
            status=ExternalActionStatus.AWAITING_APPROVAL,
        )
        approval = ApprovalRequest(
            id=new_id(),
            external_action_id=action.id,
            status=ApprovalStatus.PENDING,
            requested_by="agent:competitor-research",
            reason="External communication requires exact-payload approval.",
        )

        session.add_all(
            [
                portfolio,
                idea_workspace,
                venture_workspace,
                capability_workspace,
                idea,
                revision,
                scorecard,
                founder_fit,
                idea_assessment,
                criterion_score,
                venture,
                assumption,
                experiment_task,
                experiment,
                experiment_assumption,
                evidence,
                assessment,
                assessment_evidence,
                decision,
                decision_assessment,
                execution_task,
                artifact,
                friction,
                capability,
                friction_capability,
                agent,
                agent_version,
                agent_run,
                action,
                approval,
            ]
        )
        session.commit()

        assert session.scalar(select(IdeaAssessment.overall_score)) == 76
        assert (
            session.scalar(select(AssumptionAssessment.outcome))
            is AssessmentOutcome.SUPPORTED
        )
        assert (
            session.scalar(select(ExternalAction.status))
            is ExternalActionStatus.AWAITING_APPROVAL
        )

        venture.stage = VentureStage.VALIDATION
        session.commit()
        assert venture.version_id == 2


def test_database_constraints_reject_invalid_assumption_risk_values() -> None:
    engine = sqlite_engine()
    with Session(engine) as session:
        portfolio = Portfolio(id=new_id(), key="portfolio", name="Portfolio")
        workspace = Workspace(
            id=new_id(),
            portfolio_id=portfolio.id,
            key="venture",
            title="Venture",
            kind=WorkspaceKind.VENTURE,
        )
        invalid = Assumption(
            id=new_id(),
            workspace_id=workspace.id,
            statement="Importance must remain on the documented scale.",
            kind=AssumptionKind.VIABILITY,
            importance=6,
            uncertainty=3,
        )
        session.add_all([portfolio, workspace, invalid])
        with pytest.raises(IntegrityError):
            session.commit()
