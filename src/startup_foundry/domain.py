"""Relational domain model for the Agentic Startup Foundry.

The model deliberately separates mutable coordination state from semantic
history.  Ideas have revisions, portfolios have ranking snapshots, assumptions
have assessments, and decisions are superseded rather than overwritten.  The
application layer is responsible for append-only policy and cross-aggregate
invariants; database constraints protect the local invariants that can be
expressed portably in SQLite and PostgreSQL.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, TypeVar
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


def new_id() -> str:
    """Return a storage-portable UUID identifier."""

    return str(uuid4())


def utc_now() -> datetime:
    """Return an aware UTC timestamp for Python-side defaults."""

    return datetime.now(UTC)


EnumT = TypeVar("EnumT", bound=StrEnum)


def enum_type(enum_class: type[EnumT], name: str) -> SqlEnum:
    """Build a portable enum that stores stable values, not Python names."""

    return SqlEnum(
        enum_class,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base shared by the Foundry persistence adapters."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class IdentityMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class VersionedMixin:
    """Optimistic locking for mutable aggregates; not an audit history."""

    version_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    @declared_attr.directive
    def __mapper_args__(cls) -> dict[str, Any]:
        return {"version_id_col": cls.version_id}


class WorkspaceKind(StrEnum):
    IDEA = "idea"
    VENTURE = "venture"
    FOUNDRY_CAPABILITY = "foundry_capability"


class RecordStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class IdeaOrigin(StrEnum):
    ORIGINAL_SOURCE = "original_source"
    GENERATED_DERIVED = "generated_derived"
    GENERATED_NEW = "generated_new"
    USER_ADDED = "user_added"


class IdeaRelationKind(StrEnum):
    DERIVED_FROM = "derived_from"
    COMBINED_WITH = "combined_with"
    DUPLICATES = "duplicates"
    PIVOTS_FROM = "pivots_from"


class SourceKind(StrEnum):
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    WEBPAGE = "webpage"
    INTERVIEW = "interview"
    DATASET = "dataset"
    OBSERVATION = "observation"
    REPORT = "report"
    OTHER = "other"


class IdeaSourceRole(StrEnum):
    INSPIRATION = "inspiration"
    MARKET_REFERENCE = "market_reference"
    VALIDATION = "validation"


class MarketActorRelation(StrEnum):
    COMPETITOR = "competitor"
    ALTERNATIVE = "alternative"
    PARTNER = "partner"
    BENCHMARK = "benchmark"


class ScorecardStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class ScoreDirection(StrEnum):
    POSITIVE = "positive"
    PENALTY = "penalty"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VentureStage(StrEnum):
    DISCOVERY = "discovery"
    VALIDATION = "validation"
    BUILD = "build"
    PILOT = "pilot"
    BETA = "beta"
    OPERATING = "operating"
    PAUSED = "paused"
    ARCHIVED = "archived"


class AssumptionKind(StrEnum):
    DESIRABILITY = "desirability"
    VIABILITY = "viability"
    FEASIBILITY = "feasibility"
    USABILITY = "usability"
    GROWTH = "growth"
    ETHICS = "ethics"


class AssumptionStatus(StrEnum):
    OPEN = "open"
    TESTING = "testing"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    SUPERSEDED = "superseded"
    ACCEPTED_RISK = "accepted_risk"


class AssumptionRelationKind(StrEnum):
    DERIVED_FROM = "derived_from"
    REFINES = "refines"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"


class WorkItemKind(StrEnum):
    INVESTIGATION = "investigation"
    EXPERIMENT = "experiment"
    EXECUTION = "execution"


class WorkItemStatus(StrEnum):
    TODO = "todo"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class ExperimentStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


class EvidenceKind(StrEnum):
    OBSERVATION = "observation"
    INTERVIEW = "interview"
    EXPERIMENT_RESULT = "experiment_result"
    ANALYTICS = "analytics"
    DOCUMENT = "document"
    MARKET_RESEARCH = "market_research"
    EXTERNAL_OUTCOME = "external_outcome"
    ARTIFACT_REVIEW = "artifact_review"


class ArtifactKind(StrEnum):
    DOCUMENT = "document"
    DATASET = "dataset"
    REPORT = "report"
    PROTOTYPE = "prototype"
    CODE = "code"
    MODEL = "model"
    CONFIGURATION = "configuration"
    PROMPT = "prompt"
    EVALUATION = "evaluation"
    RELEASE = "release"
    OTHER = "other"


class ArtifactRelationKind(StrEnum):
    DERIVED_FROM = "derived_from"
    SUPERSEDES = "supersedes"
    INPUT_TO = "input_to"
    OUTPUT_OF = "output_of"


class AssessmentOutcome(StrEnum):
    SUPPORTED = "supported"
    WEAKENED = "weakened"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


class DecisionKind(StrEnum):
    CONTINUE = "continue"
    PIVOT = "pivot"
    NARROW = "narrow"
    STOP = "stop"
    BUILD = "build"
    DEFER = "defer"
    ACCEPT_RISK = "accept_risk"
    PROMOTE = "promote"
    ROLLBACK = "rollback"


class DecisionStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    SUPERSEDED = "superseded"
    REVERSED = "reversed"


class FrictionSeverity(StrEnum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    BLOCKER = "blocker"


class FrictionStatus(StrEnum):
    OPEN = "open"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class CapabilityStatus(StrEnum):
    OBSERVED = "observed"
    SHAPING = "shaping"
    PILOTING = "piloting"
    ADOPTED = "adopted"
    REJECTED = "rejected"
    RETIRED = "retired"


class CapabilityUseOutcome(StrEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    INCONCLUSIVE = "inconclusive"


class AgentDefinitionStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class AgentRunStatus(StrEnum):
    REQUESTED = "requested"
    WAITING_APPROVAL = "waiting_approval"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionRisk(StrEnum):
    INTERNAL = "internal"
    REVERSIBLE_EXTERNAL = "reversible_external"
    EXTERNAL_COMMUNICATION = "external_communication"
    FINANCIAL = "financial"
    DESTRUCTIVE = "destructive"


class ExternalActionStatus(StrEnum):
    PROPOSED = "proposed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ActionAttemptStatus(StrEnum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class Portfolio(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "portfolios"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    base_currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)


class Workspace(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    """A context that can run the same learning and execution loops."""

    __tablename__ = "workspaces"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "key", name="workspace_portfolio_key"),
    )

    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    kind: Mapped[WorkspaceKind] = mapped_column(
        enum_type(WorkspaceKind, "workspace_kind"), nullable=False
    )
    status: Mapped[RecordStatus] = mapped_column(
        enum_type(RecordStatus, "workspace_status"),
        default=RecordStatus.ACTIVE,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)


class ReferenceSource(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "reference_sources"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "locator", name="source_portfolio_locator"),
    )

    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False, index=True
    )
    kind: Mapped[SourceKind] = mapped_column(
        enum_type(SourceKind, "source_kind"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    locator: Mapped[str] = mapped_column(Text, nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(240))
    published_at: Mapped[date | None] = mapped_column(Date)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content_digest: Mapped[str | None] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text)


class Idea(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "ideas"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, unique=True
    )
    origin: Mapped[IdeaOrigin] = mapped_column(
        enum_type(IdeaOrigin, "idea_origin"), nullable=False
    )
    external_key: Mapped[str | None] = mapped_column(String(100), index=True)
    current_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "idea_revisions.id",
            name="fk_ideas_current_revision",
            use_alter=True,
            deferrable=True,
            initially="DEFERRED",
        )
    )
    status: Mapped[RecordStatus] = mapped_column(
        enum_type(RecordStatus, "idea_status"),
        default=RecordStatus.ACTIVE,
        nullable=False,
    )


class IdeaRevision(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "idea_revisions"
    __table_args__ = (
        UniqueConstraint("idea_id", "revision_number", name="idea_revision_number"),
        CheckConstraint("revision_number >= 1", name="revision_number_positive"),
    )

    idea_id: Mapped[str] = mapped_column(
        ForeignKey("ideas.id"), nullable=False, index=True
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str | None] = mapped_column(String(160))
    venture_type: Mapped[str | None] = mapped_column(String(160))
    cluster: Mapped[str | None] = mapped_column(String(160))
    original_text: Mapped[str | None] = mapped_column(Text)
    cleaned_description: Mapped[str] = mapped_column(Text, nullable=False)
    narrowing_or_pivot: Mapped[str | None] = mapped_column(Text)
    target_customer: Mapped[str | None] = mapped_column(Text)
    business_model: Mapped[str | None] = mapped_column(Text)
    focused_mvp_scope: Mapped[str | None] = mapped_column(Text)
    estimated_mvp_weeks: Mapped[float | None] = mapped_column(Float)
    key_validation_test: Mapped[str | None] = mapped_column(Text)
    change_reason: Mapped[str | None] = mapped_column(Text)
    authored_by: Mapped[str | None] = mapped_column(String(200))


class IdeaRelation(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "idea_relations"
    __table_args__ = (
        UniqueConstraint(
            "source_idea_id", "target_idea_id", "kind", name="idea_relation_unique"
        ),
        CheckConstraint(
            "source_idea_id <> target_idea_id", name="idea_relation_not_self"
        ),
    )

    source_idea_id: Mapped[str] = mapped_column(
        ForeignKey("ideas.id"), nullable=False, index=True
    )
    target_idea_id: Mapped[str] = mapped_column(
        ForeignKey("ideas.id"), nullable=False, index=True
    )
    kind: Mapped[IdeaRelationKind] = mapped_column(
        enum_type(IdeaRelationKind, "idea_relation_kind"), nullable=False
    )
    rationale: Mapped[str | None] = mapped_column(Text)


class IdeaSource(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "idea_sources"
    __table_args__ = (
        UniqueConstraint("idea_id", "source_id", "role", name="idea_source_unique"),
    )

    idea_id: Mapped[str] = mapped_column(
        ForeignKey("ideas.id"), nullable=False, index=True
    )
    source_id: Mapped[str] = mapped_column(
        ForeignKey("reference_sources.id"), nullable=False, index=True
    )
    role: Mapped[IdeaSourceRole] = mapped_column(
        enum_type(IdeaSourceRole, "idea_source_role"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text)


class MarketActor(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "market_actors"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "name", name="market_actor_portfolio_name"),
    )

    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    website: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)


class IdeaMarketActor(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "idea_market_actors"
    __table_args__ = (
        UniqueConstraint(
            "idea_revision_id", "market_actor_id", "relation", name="idea_actor_unique"
        ),
    )

    idea_revision_id: Mapped[str] = mapped_column(
        ForeignKey("idea_revisions.id"), nullable=False, index=True
    )
    market_actor_id: Mapped[str] = mapped_column(
        ForeignKey("market_actors.id"), nullable=False, index=True
    )
    relation: Mapped[MarketActorRelation] = mapped_column(
        enum_type(MarketActorRelation, "market_actor_relation"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)


class Scorecard(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "scorecards"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "name", "version", name="scorecard_version"),
        CheckConstraint("version >= 1", name="scorecard_version_positive"),
    )

    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ScorecardStatus] = mapped_column(
        enum_type(ScorecardStatus, "scorecard_status"),
        default=ScorecardStatus.DRAFT,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    formula_description: Mapped[str | None] = mapped_column(Text)


class ScoringCriterion(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "scoring_criteria"
    __table_args__ = (
        UniqueConstraint("scorecard_id", "key", name="criterion_scorecard_key"),
        CheckConstraint("weight >= 0 AND weight <= 1", name="criterion_weight_range"),
        CheckConstraint("scale_min < scale_max", name="criterion_scale_order"),
    )

    scorecard_id: Mapped[str] = mapped_column(
        ForeignKey("scorecards.id"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    direction: Mapped[ScoreDirection] = mapped_column(
        enum_type(ScoreDirection, "score_direction"), nullable=False
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    scale_min: Mapped[int] = mapped_column(Integer, nullable=False)
    scale_max: Mapped[int] = mapped_column(Integer, nullable=False)
    guidance: Mapped[str | None] = mapped_column(Text)


class IdeaAssessment(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "idea_assessments"
    __table_args__ = (
        UniqueConstraint(
            "idea_revision_id",
            "scorecard_id",
            "assessment_number",
            name="assessment_revision_scorecard_number",
        ),
        CheckConstraint("assessment_number >= 1", name="assessment_number_positive"),
        CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)",
            name="assessment_score_range",
        ),
    )

    idea_revision_id: Mapped[str] = mapped_column(
        ForeignKey("idea_revisions.id"), nullable=False, index=True
    )
    scorecard_id: Mapped[str] = mapped_column(
        ForeignKey("scorecards.id"), nullable=False, index=True
    )
    assessment_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        enum_type(ConfidenceLevel, "idea_assessment_confidence"), nullable=False
    )
    overall_score: Mapped[float | None] = mapped_column(Float)
    grade: Mapped[str | None] = mapped_column(String(20))
    recommendation: Mapped[str | None] = mapped_column(Text)
    pros: Mapped[str | None] = mapped_column(Text)
    cons: Mapped[str | None] = mapped_column(Text)
    revenue_year_1: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    revenue_year_3: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    rationale: Mapped[str | None] = mapped_column(Text)
    assessed_by: Mapped[str | None] = mapped_column(String(200))


class CriterionScore(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "criterion_scores"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id", "criterion_id", name="criterion_score_unique"
        ),
    )

    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("idea_assessments.id"), nullable=False, index=True
    )
    criterion_id: Mapped[str] = mapped_column(
        ForeignKey("scoring_criteria.id"), nullable=False, index=True
    )
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    normalized_score: Mapped[float | None] = mapped_column(Float)
    weighted_contribution: Mapped[float | None] = mapped_column(Float)
    rationale: Mapped[str | None] = mapped_column(Text)


class CriterionScoreEvidence(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "criterion_score_evidence"
    __table_args__ = (
        UniqueConstraint(
            "criterion_score_id", "evidence_id", name="criterion_evidence_unique"
        ),
    )

    criterion_score_id: Mapped[str] = mapped_column(
        ForeignKey("criterion_scores.id"), nullable=False, index=True
    )
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id"), nullable=False, index=True
    )
    note: Mapped[str | None] = mapped_column(Text)


class RankingSnapshot(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "ranking_snapshots"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "label", name="ranking_portfolio_label"),
    )

    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False, index=True
    )
    scorecard_id: Mapped[str] = mapped_column(
        ForeignKey("scorecards.id"), nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    generated_by: Mapped[str | None] = mapped_column(String(200))
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class RankingEntry(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "ranking_entries"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "rank", name="ranking_rank_unique"),
        UniqueConstraint("snapshot_id", "idea_id", name="ranking_idea_unique"),
        CheckConstraint("rank >= 1", name="ranking_rank_positive"),
    )

    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("ranking_snapshots.id"), nullable=False, index=True
    )
    idea_id: Mapped[str] = mapped_column(
        ForeignKey("ideas.id"), nullable=False, index=True
    )
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("idea_assessments.id"), nullable=False, index=True
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)


class Venture(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "ventures"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, unique=True
    )
    source_idea_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("idea_revisions.id"), index=True
    )
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    stage: Mapped[VentureStage] = mapped_column(
        enum_type(VentureStage, "venture_stage"), nullable=False
    )
    current_focus: Mapped[str | None] = mapped_column(Text)
    budget_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    budget_currency: Mapped[str] = mapped_column(
        String(3), default="EUR", nullable=False
    )


class Assumption(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "assumptions"
    __table_args__ = (
        CheckConstraint("importance >= 1 AND importance <= 5", name="importance_range"),
        CheckConstraint(
            "uncertainty >= 1 AND uncertainty <= 5", name="uncertainty_range"
        ),
    )

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[AssumptionKind] = mapped_column(
        enum_type(AssumptionKind, "assumption_kind"), nullable=False
    )
    status: Mapped[AssumptionStatus] = mapped_column(
        enum_type(AssumptionStatus, "assumption_status"),
        default=AssumptionStatus.OPEN,
        nullable=False,
    )
    importance: Mapped[int] = mapped_column(Integer, nullable=False)
    uncertainty: Mapped[int] = mapped_column(Integer, nullable=False)
    origin_evidence_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidence.id"), index=True
    )
    created_by: Mapped[str | None] = mapped_column(String(200))


class AssumptionRelation(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "assumption_relations"
    __table_args__ = (
        UniqueConstraint(
            "source_assumption_id",
            "target_assumption_id",
            "kind",
            name="assumption_relation_unique",
        ),
        CheckConstraint(
            "source_assumption_id <> target_assumption_id",
            name="assumption_relation_not_self",
        ),
    )

    source_assumption_id: Mapped[str] = mapped_column(
        ForeignKey("assumptions.id"), nullable=False, index=True
    )
    target_assumption_id: Mapped[str] = mapped_column(
        ForeignKey("assumptions.id"), nullable=False, index=True
    )
    kind: Mapped[AssumptionRelationKind] = mapped_column(
        enum_type(AssumptionRelationKind, "assumption_relation_kind"), nullable=False
    )
    rationale: Mapped[str | None] = mapped_column(Text)


class WorkItem(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "work_items"
    __table_args__ = (
        CheckConstraint(
            "budget_limit IS NULL OR budget_limit >= 0",
            name="work_item_budget_nonnegative",
        ),
    )

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    decision_id: Mapped[str | None] = mapped_column(
        ForeignKey("decisions.id"), index=True
    )
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_items.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    question: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[WorkItemKind] = mapped_column(
        enum_type(WorkItemKind, "work_item_kind"), nullable=False
    )
    status: Mapped[WorkItemStatus] = mapped_column(
        enum_type(WorkItemStatus, "work_item_status"), nullable=False
    )
    desired_outcome: Mapped[str | None] = mapped_column(Text)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None] = mapped_column(String(200))
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    budget_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    budget_currency: Mapped[str] = mapped_column(
        String(3), default="EUR", nullable=False
    )
    blocked_reason: Mapped[str | None] = mapped_column(Text)


class Experiment(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "experiments"

    work_item_id: Mapped[str] = mapped_column(
        ForeignKey("work_items.id"), nullable=False, unique=True
    )
    status: Mapped[ExperimentStatus] = mapped_column(
        enum_type(ExperimentStatus, "experiment_status"),
        default=ExperimentStatus.PLANNED,
        nullable=False,
    )
    method: Mapped[str] = mapped_column(Text, nullable=False)
    success_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    failure_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    result_summary: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ExperimentAssumption(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "experiment_assumptions"
    __table_args__ = (
        UniqueConstraint(
            "experiment_id", "assumption_id", name="experiment_assumption_unique"
        ),
    )

    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id"), nullable=False, index=True
    )
    assumption_id: Mapped[str] = mapped_column(
        ForeignKey("assumptions.id"), nullable=False, index=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Evidence(IdentityMixin, TimestampMixin, Base):
    """Append-only fact or observation; interpretation lives in assessments."""

    __tablename__ = "evidence"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    origin_work_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_items.id"), index=True
    )
    kind: Mapped[EvidenceKind] = mapped_column(
        enum_type(EvidenceKind, "evidence_kind"), nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        enum_type(ConfidenceLevel, "evidence_confidence"), nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    captured_by: Mapped[str | None] = mapped_column(String(200))


class EvidenceSource(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "evidence_sources"
    __table_args__ = (
        UniqueConstraint("evidence_id", "source_id", name="evidence_source_unique"),
    )

    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id"), nullable=False, index=True
    )
    source_id: Mapped[str] = mapped_column(
        ForeignKey("reference_sources.id"), nullable=False, index=True
    )
    excerpt: Mapped[str | None] = mapped_column(Text)
    source_location: Mapped[str | None] = mapped_column(String(500))


class Artifact(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "artifacts"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_items.id"), index=True
    )
    agent_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_runs.id"), index=True
    )
    kind: Mapped[ArtifactKind] = mapped_column(
        enum_type(ArtifactKind, "artifact_kind"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[str | None] = mapped_column(String(200))
    content_digest: Mapped[str | None] = mapped_column(String(128))
    semantic_version: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )


class ArtifactRelation(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "artifact_relations"
    __table_args__ = (
        UniqueConstraint(
            "source_artifact_id",
            "target_artifact_id",
            "kind",
            name="artifact_relation_unique",
        ),
        CheckConstraint(
            "source_artifact_id <> target_artifact_id",
            name="artifact_relation_not_self",
        ),
    )

    source_artifact_id: Mapped[str] = mapped_column(
        ForeignKey("artifacts.id"), nullable=False, index=True
    )
    target_artifact_id: Mapped[str] = mapped_column(
        ForeignKey("artifacts.id"), nullable=False, index=True
    )
    kind: Mapped[ArtifactRelationKind] = mapped_column(
        enum_type(ArtifactRelationKind, "artifact_relation_kind"), nullable=False
    )
    rationale: Mapped[str | None] = mapped_column(Text)


class EvidenceArtifact(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "evidence_artifacts"
    __table_args__ = (
        UniqueConstraint("evidence_id", "artifact_id", name="evidence_artifact_unique"),
    )

    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id"), nullable=False, index=True
    )
    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("artifacts.id"), nullable=False, index=True
    )
    role: Mapped[str | None] = mapped_column(String(100))


class AssumptionAssessment(IdentityMixin, TimestampMixin, Base):
    """Append-only interpretation of an assumption at a point in time."""

    __tablename__ = "assumption_assessments"

    assumption_id: Mapped[str] = mapped_column(
        ForeignKey("assumptions.id"), nullable=False, index=True
    )
    outcome: Mapped[AssessmentOutcome] = mapped_column(
        enum_type(AssessmentOutcome, "assessment_outcome"), nullable=False
    )
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        enum_type(ConfidenceLevel, "assumption_assessment_confidence"), nullable=False
    )
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    assessed_by: Mapped[str | None] = mapped_column(String(200))
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class AssessmentEvidence(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "assessment_evidence"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id", "evidence_id", name="assessment_evidence_unique"
        ),
    )

    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assumption_assessments.id"), nullable=False, index=True
    )
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id"), nullable=False, index=True
    )
    weight: Mapped[float | None] = mapped_column(Float)
    note: Mapped[str | None] = mapped_column(Text)


class Decision(IdentityMixin, TimestampMixin, Base):
    """Append-only commitment; later changes point at the superseded decision."""

    __tablename__ = "decisions"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    supersedes_decision_id: Mapped[str | None] = mapped_column(
        ForeignKey("decisions.id"), index=True
    )
    kind: Mapped[DecisionKind] = mapped_column(
        enum_type(DecisionKind, "decision_kind"), nullable=False
    )
    status: Mapped[DecisionStatus] = mapped_column(
        enum_type(DecisionStatus, "decision_status"), nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    decided_by: Mapped[str | None] = mapped_column(String(200))
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class DecisionEvidence(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "decision_evidence"
    __table_args__ = (
        UniqueConstraint("decision_id", "evidence_id", name="decision_evidence_unique"),
    )

    decision_id: Mapped[str] = mapped_column(
        ForeignKey("decisions.id"), nullable=False, index=True
    )
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id"), nullable=False, index=True
    )
    note: Mapped[str | None] = mapped_column(Text)


class DecisionAssessment(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "decision_assessments"
    __table_args__ = (
        UniqueConstraint(
            "decision_id", "assessment_id", name="decision_assessment_unique"
        ),
    )

    decision_id: Mapped[str] = mapped_column(
        ForeignKey("decisions.id"), nullable=False, index=True
    )
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assumption_assessments.id"), nullable=False, index=True
    )
    note: Mapped[str | None] = mapped_column(Text)


class FrictionOccurrence(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "friction_occurrences"
    __table_args__ = (
        CheckConstraint(
            "time_cost_minutes IS NULL OR time_cost_minutes >= 0",
            name="friction_time_nonnegative",
        ),
        CheckConstraint(
            "money_cost IS NULL OR money_cost >= 0", name="friction_cost_nonnegative"
        ),
        Index("ix_friction_recurrence_key", "recurrence_key"),
    )

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_items.id"), index=True
    )
    agent_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_runs.id"), index=True
    )
    recurrence_key: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[FrictionSeverity] = mapped_column(
        enum_type(FrictionSeverity, "friction_severity"), nullable=False
    )
    status: Mapped[FrictionStatus] = mapped_column(
        enum_type(FrictionStatus, "friction_status"),
        default=FrictionStatus.OPEN,
        nullable=False,
    )
    impact: Mapped[str | None] = mapped_column(Text)
    workaround: Mapped[str | None] = mapped_column(Text)
    time_cost_minutes: Mapped[int | None] = mapped_column(Integer)
    money_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    cost_currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class CapabilityCandidate(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "capability_candidates"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, unique=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    minimal_scope: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[CapabilityStatus] = mapped_column(
        enum_type(CapabilityStatus, "capability_status"), nullable=False
    )
    owner: Mapped[str | None] = mapped_column(String(200))


class FrictionCapability(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "friction_capabilities"
    __table_args__ = (
        UniqueConstraint(
            "friction_id", "capability_id", name="friction_capability_unique"
        ),
        CheckConstraint(
            "match_strength >= 1 AND match_strength <= 5", name="match_range"
        ),
    )

    friction_id: Mapped[str] = mapped_column(
        ForeignKey("friction_occurrences.id"), nullable=False, index=True
    )
    capability_id: Mapped[str] = mapped_column(
        ForeignKey("capability_candidates.id"), nullable=False, index=True
    )
    match_strength: Mapped[int] = mapped_column(Integer, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)


class CapabilityUse(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "capability_uses"
    __table_args__ = (
        CheckConstraint(
            "time_saved_minutes IS NULL OR time_saved_minutes >= 0",
            name="capability_time_saved_nonnegative",
        ),
    )

    capability_id: Mapped[str] = mapped_column(
        ForeignKey("capability_candidates.id"), nullable=False, index=True
    )
    venture_id: Mapped[str] = mapped_column(
        ForeignKey("ventures.id"), nullable=False, index=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_items.id"), index=True
    )
    evidence_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidence.id"), index=True
    )
    outcome: Mapped[CapabilityUseOutcome] = mapped_column(
        enum_type(CapabilityUseOutcome, "capability_use_outcome"), nullable=False
    )
    time_saved_minutes: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class AgentDefinition(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "agent_definitions"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "key", name="agent_portfolio_key"),
    )

    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AgentDefinitionStatus] = mapped_column(
        enum_type(AgentDefinitionStatus, "agent_definition_status"),
        default=AgentDefinitionStatus.ACTIVE,
        nullable=False,
    )


class AgentVersion(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "agent_versions"
    __table_args__ = (
        UniqueConstraint("agent_definition_id", "version", name="agent_version_unique"),
    )

    agent_definition_id: Mapped[str] = mapped_column(
        ForeignKey("agent_definitions.id"), nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(160), nullable=False)
    toolset_version: Mapped[str] = mapped_column(String(160), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(160), nullable=False)
    code_version: Mapped[str | None] = mapped_column(String(160))
    provider_config: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    runtime_config: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )


class AgentRun(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "agent_runs"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_items.id"), index=True
    )
    agent_version_id: Mapped[str] = mapped_column(
        ForeignKey("agent_versions.id"), nullable=False, index=True
    )
    status: Mapped[AgentRunStatus] = mapped_column(
        enum_type(AgentRunStatus, "agent_run_status"), nullable=False
    )
    provider: Mapped[str | None] = mapped_column(String(120))
    model: Mapped[str | None] = mapped_column(String(160))
    runtime_config: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    correlation_id: Mapped[str | None] = mapped_column(String(160), index=True)
    evalops_trace_id: Mapped[str | None] = mapped_column(String(160), index=True)
    input_digest: Mapped[str | None] = mapped_column(String(128))
    output_digest: Mapped[str | None] = mapped_column(String(128))
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    cost_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_summary: Mapped[str | None] = mapped_column(Text)


class ExternalAction(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "external_actions"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="external_action_idempotency"),
        CheckConstraint(
            "estimated_cost IS NULL OR estimated_cost >= 0",
            name="action_cost_nonnegative",
        ),
    )

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), nullable=False, index=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_items.id"), index=True
    )
    agent_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_runs.id"), index=True
    )
    action_type: Mapped[str] = mapped_column(String(160), nullable=False)
    adapter: Mapped[str] = mapped_column(String(160), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    payload_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(240), nullable=False)
    risk: Mapped[ActionRisk] = mapped_column(
        enum_type(ActionRisk, "action_risk"), nullable=False
    )
    approval_required: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    status: Mapped[ExternalActionStatus] = mapped_column(
        enum_type(ExternalActionStatus, "external_action_status"), nullable=False
    )
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    cost_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    not_before: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ApprovalRequest(IdentityMixin, TimestampMixin, VersionedMixin, Base):
    __tablename__ = "approval_requests"

    external_action_id: Mapped[str] = mapped_column(
        ForeignKey("external_actions.id"), nullable=False, unique=True
    )
    status: Mapped[ApprovalStatus] = mapped_column(
        enum_type(ApprovalStatus, "approval_status"), nullable=False
    )
    requested_by: Mapped[str] = mapped_column(String(200), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    decided_by: Mapped[str | None] = mapped_column(String(200))
    decision_notes: Mapped[str | None] = mapped_column(Text)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ActionAttempt(IdentityMixin, TimestampMixin, Base):
    __tablename__ = "action_attempts"
    __table_args__ = (
        UniqueConstraint(
            "external_action_id", "attempt_number", name="action_attempt_number"
        ),
        CheckConstraint("attempt_number >= 1", name="action_attempt_positive"),
    )

    external_action_id: Mapped[str] = mapped_column(
        ForeignKey("external_actions.id"), nullable=False, index=True
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ActionAttemptStatus] = mapped_column(
        enum_type(ActionAttemptStatus, "action_attempt_status"), nullable=False
    )
    provider_reference: Mapped[str | None] = mapped_column(String(300))
    receipt: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error_summary: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditEvent(IdentityMixin, Base):
    """Append-only technical trace for state transitions and actor attribution."""

    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_workspace_time", "workspace_id", "occurred_at"),
    )

    workspace_id: Mapped[str | None] = mapped_column(
        ForeignKey("workspaces.id"), index=True
    )
    entity_type: Mapped[str] = mapped_column(String(160), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False)
    actor: Mapped[str] = mapped_column(String(200), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(160), index=True)
    causation_id: Mapped[str | None] = mapped_column(String(160))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
