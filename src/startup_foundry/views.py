"""Shared SQL portfolio query for CLI, HTML and JSON; no page-local sorting."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import String, case, cast, func, or_, select

from startup_foundry.domain import (
    Artifact,
    CriterionScore,
    Disposition,
    Idea,
    IdeaAssessment,
    IdeaRevision,
    IdeaSource,
    InvestigationStage,
    PortfolioProposal,
    ProductMaturity,
    ProposalParticipant,
    ScoringCriterion,
    Venture,
    VentureAssessment,
    VentureCriterionScore,
    VentureStage,
    WorkItem,
    Workspace,
    WorkspaceReview,
)
from startup_foundry.errors import ValidationError
from startup_foundry.repository import SessionFactory
from startup_foundry.scoring import FACTORS, ORIGINAL, REVIEWED, scorecard_for_view

JSON = dict[str, Any]


class PortfolioQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    q: str = Field(default="", max_length=500)
    disposition: Disposition | None = None
    investigation_stage: InvestigationStage | None = None
    product_maturity: ProductMaturity | None = None
    blocker: (
        Literal[
            "human_input",
            "external_access",
            "setup",
            "other",
            "not_scheduled",
            "ready",
            "in_progress",
        ]
        | None
    ) = None
    stage: VentureStage | None = None
    # Ideas linked to one retained source (a discovery cohort).
    source_id: str | None = Field(default=None, min_length=1, max_length=36)
    continued: Literal["all", "exclude"] = "all"
    score_view: str = Field(default="reviewed", min_length=1, max_length=36)
    criterion: str = Field(
        default="priority", min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_]*$"
    )
    min_score: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    sort: Literal["score", "priority", "stage", "recent", "name", "id"] = "score"
    direction: Literal["asc", "desc"] = "desc"
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def consistent(self) -> PortfolioQuery:
        if self.card_id in {ORIGINAL, REVIEWED} and self.criterion not in {
            "priority",
            *[key for key, _, _, _ in FACTORS],
        }:
            raise ValueError("Unknown criterion for the built-in scorecard")
        if (
            self.criterion != "priority"
            and self.min_score is not None
            and self.min_score > 10
        ):
            raise ValueError("Criterion minimum is at most 10")
        return self

    @property
    def card_id(self) -> str:
        return scorecard_for_view(self.score_view)


class PortfolioViewService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    def list(self, subject: Literal["idea", "venture"], query: PortfolioQuery) -> JSON:
        model = Idea if subject == "idea" else Venture
        latest_review = select(
            WorkspaceReview.id,
            func.row_number()
            .over(
                partition_by=WorkspaceReview.workspace_id,
                order_by=WorkspaceReview.revision.desc(),
            )
            .label("position"),
        ).subquery()
        review = (
            select(WorkspaceReview)
            .join(latest_review, latest_review.c.id == WorkspaceReview.id)
            .where(latest_review.c.position == 1)
            .subquery()
        )
        score_model = IdeaAssessment if subject == "idea" else VentureAssessment
        factor_model = CriterionScore if subject == "idea" else VentureCriterionScore
        subject_column = (
            IdeaAssessment.idea_revision_id
            if subject == "idea"
            else VentureAssessment.venture_id
        )
        sequence_column = (
            IdeaAssessment.assessment_number
            if subject == "idea"
            else VentureAssessment.sequence
        )
        latest_score = (
            select(
                score_model.id,
                func.row_number()
                .over(
                    partition_by=subject_column,
                    order_by=(
                        [
                            case(
                                (VentureAssessment.kind == "reviewed", 1), else_=0
                            ).desc(),
                            sequence_column.desc(),
                        ]
                        if subject == "venture"
                        else sequence_column.desc()
                    ),
                )
                .label("position"),
            )
            .where(score_model.scorecard_id == query.card_id)
            .subquery()
        )
        assessment = (
            select(score_model)
            .join(latest_score, latest_score.c.id == score_model.id)
            .where(latest_score.c.position == 1)
            .subquery()
        )
        factors = (
            select(
                factor_model.assessment_id,
                func.count().label("coverage"),
                *[
                    func.max(
                        case(
                            (ScoringCriterion.key == key, factor_model.raw_score),
                            else_=None,
                        )
                    ).label(key)
                    for key in {"founder_fit", "mvp_speed", query.criterion}
                    - {"priority"}
                ],
            )
            .join(ScoringCriterion)
            .group_by(factor_model.assessment_id)
            .subquery()
        )
        blocker = case(
            (
                WorkItem.status == "blocked",
                case(
                    (
                        WorkItem.blocked_reason.in_(
                            ["human_input", "external_access", "setup"]
                        ),
                        WorkItem.blocked_reason,
                    ),
                    else_="other",
                ),
            ),
            else_=None,
        )
        work_state = func.coalesce(cast(WorkItem.status, String), "not_scheduled")
        score = (
            assessment.c.overall_score
            if query.criterion == "priority"
            else factors.c[query.criterion]
        )
        title = IdeaRevision.title if subject == "idea" else Workspace.title
        intake_ranked = (
            select(
                Artifact.workspace_id,
                Artifact.work_item_id,
                func.row_number()
                .over(
                    partition_by=Artifact.workspace_id,
                    order_by=(Artifact.created_at.desc(), Artifact.id),
                )
                .label("position"),
            )
            .where(Artifact.name == "manual-intake/v1")
            .subquery()
        )
        intake = select(intake_ranked).where(intake_ranked.c.position == 1).subquery()
        description = (
            IdeaRevision.cleaned_description if subject == "idea" else Venture.objective
        )
        statement = (
            select(
                model.id.label("id"),
                model.workspace_id,
                title.label("title"),
                description.label("description"),
                Workspace.updated_at,
                review.c.revision.label("review_revision"),
                review.c.investigation_stage,
                review.c.product_maturity,
                review.c.disposition,
                review.c.reason,
                review.c.author,
                review.c.reviewed_at,
                func.coalesce(review.c.next_action, WorkItem.title).label(
                    "next_action"
                ),
                WorkItem.owner.label("next_owner"),
                blocker.label("blocker"),
                work_state.label("work_state"),
                assessment.c.overall_score.label("priority"),
                assessment.c.confidence,
                assessment.c.id.label("assessment_id"),
                (
                    assessment.c.kind if subject == "venture" else cast(None, String)
                ).label("assessment_kind"),
                factors.c.founder_fit,
                factors.c.mvp_speed,
                func.coalesce(factors.c.coverage, 0).label("coverage"),
                score.label("selected_score"),
                IdeaRevision.target_customer.label("customer"),
                (Idea.origin if subject == "idea" else Venture.stage).label(
                    "origin" if subject == "idea" else "stage"
                ),
            )
            .join(Workspace, model.workspace_id == Workspace.id)
            .outerjoin(
                IdeaRevision,
                (
                    Idea.current_revision_id
                    if subject == "idea"
                    else Venture.source_idea_revision_id
                )
                == IdeaRevision.id,
            )
            .outerjoin(review, review.c.workspace_id == Workspace.id)
            .outerjoin(intake, intake.c.workspace_id == Workspace.id)
            .outerjoin(
                WorkItem,
                WorkItem.id
                == case(
                    (review.c.id.is_(None), intake.c.work_item_id),
                    else_=review.c.next_work_item_id,
                ),
            )
            .outerjoin(
                assessment,
                (assessment.c.idea_revision_id == IdeaRevision.id)
                if subject == "idea"
                else (assessment.c.venture_id == Venture.id),
            )
            .outerjoin(factors, factors.c.assessment_id == assessment.c.id)
        )
        if query.continued == "exclude":
            continued_source = (
                select(ProposalParticipant.id)
                .join(PortfolioProposal)
                .where(
                    PortfolioProposal.state == "applied",
                    ProposalParticipant.role == "source",
                    (ProposalParticipant.idea_id == model.id)
                    if subject == "idea"
                    else (ProposalParticipant.venture_id == model.id),
                )
                .exists()
            )
            statement = statement.where(~continued_source)
        if query.q:
            statement = statement.where(
                or_(
                    model.id.icontains(query.q, autoescape=True),
                    title.icontains(query.q, autoescape=True),
                    description.icontains(query.q, autoescape=True),
                )
            )
        for name in ["disposition", "investigation_stage", "product_maturity"]:
            value = getattr(query, name)
            if value is not None:
                expression = func.coalesce(
                    cast(review.c[name], String),
                    "unknown"
                    if name == "product_maturity"
                    else "intake"
                    if name == "investigation_stage"
                    else "not_reviewed",
                )
                statement = statement.where(expression == value)
        if query.blocker:
            blocker_expression = (
                work_state
                if query.blocker in {"not_scheduled", "ready", "in_progress"}
                else blocker
            )
            statement = statement.where(blocker_expression == query.blocker)
        if query.source_id is not None:
            if subject != "idea":
                raise ValidationError("source_id filters ideas, not ventures")
            statement = statement.where(
                model.id.in_(
                    select(IdeaSource.idea_id).where(
                        IdeaSource.source_id == query.source_id
                    )
                )
            )
        if subject == "venture" and query.stage:
            statement = statement.where(Venture.stage == query.stage)
        if query.min_score is not None:
            statement = statement.where(score >= query.min_score)
        activity = case(
            (review.c.reviewed_at > Workspace.updated_at, review.c.reviewed_at),
            else_=Workspace.updated_at,
        )
        activity = case(
            (assessment.c.created_at > activity, assessment.c.created_at),
            else_=activity,
        )
        activity = case(
            (WorkItem.updated_at > activity, WorkItem.updated_at), else_=activity
        )
        sort = {
            "score": score,
            "priority": assessment.c.overall_score,
            "stage": case(
                *[
                    (review.c.investigation_stage == stage.value, i)
                    for i, stage in enumerate(InvestigationStage)
                ],
                else_=None,
            ),
            "recent": activity,
            "name": title,
            "id": model.id,
        }[query.sort]
        with self.factory() as session:
            from startup_foundry.scoring import ScoringService

            selected_card = ScoringService.read_card(session, query.card_id)
            if query.criterion != "priority" and query.criterion not in {
                c["key"] for c in selected_card["criteria"]
            }:
                raise ValidationError("Criterion does not belong to selected scorecard")
            required = (
                session.scalar(
                    select(func.count())
                    .select_from(ScoringCriterion)
                    .where(ScoringCriterion.scorecard_id == query.card_id)
                )
                or 12
            )
            filtered = statement.subquery()
            total, unscored = session.execute(
                select(
                    func.count(),
                    func.sum(case((filtered.c.priority.is_(None), 1), else_=0)),
                ).select_from(filtered)
            ).one()
            result = (
                session.execute(
                    statement.order_by(
                        sort.is_(None),
                        sort.desc() if query.direction == "desc" else sort.asc(),
                        model.id.asc(),
                    )
                    .limit(query.limit)
                    .offset(query.offset)
                )
                .mappings()
                .all()
            )
            items = []
            for row in result:
                item = dict(row)
                for key in [
                    "disposition",
                    "investigation_stage",
                    "product_maturity",
                    "confidence",
                    "origin",
                    "stage",
                    "work_state",
                ]:
                    if key in item and hasattr(item[key], "value"):
                        item[key] = item[key].value
                for key in ["updated_at", "reviewed_at"]:
                    if item.get(key):
                        item[key] = item[key].isoformat()
                item["name"] = item["title"]
                item["scorecard_id"] = query.card_id
                item["score_label"] = (
                    "Imported/unreviewed reported confidence"
                    if query.card_id == ORIGINAL
                    else "Reviewed judgment"
                )
                if (
                    subject == "venture"
                    and item["assessment_kind"] == "source_baseline"
                ):
                    item["score_label"] = (
                        "Original idea estimate"
                        if query.card_id == ORIGINAL
                        else "Starting estimate from source idea"
                    )
                elif subject == "venture":
                    item["score_label"] = (
                        "Reviewed venture judgment"
                        if item["assessment_id"]
                        else "Not yet scored"
                    )
                item["product_maturity"] = item["product_maturity"] or "unknown"
                item["investigation_stage"] = item["investigation_stage"] or "intake"
                item["disposition"] = item["disposition"] or "not_reviewed"
                item["next_action"] = (
                    item["next_action"] or "Review and schedule the next bounded task."
                )
                items.append(item)
            if subject == "idea" and items:
                ids = [i["id"] for i in items]
                linked = session.execute(
                    select(IdeaRevision.idea_id, Venture.id, Venture.stage)
                    .join(Venture, Venture.source_idea_revision_id == IdeaRevision.id)
                    .where(IdeaRevision.idea_id.in_(ids))
                    .order_by(Venture.id)
                ).all()
                for item in items:
                    item["ventures"] = [
                        {"id": v, "stage": stage.value}
                        for idea, v, stage in linked
                        if idea == item["id"]
                    ]
            return {
                "criteria": selected_card["criteria"],
                "items": items,
                "total": total,
                "unscored": unscored or 0,
                "limit": query.limit,
                "offset": query.offset,
                "query": query.model_dump(mode="json"),
                "scorecard_id": query.card_id,
                "criterion": query.criterion,
                "required_factors": required,
            }
