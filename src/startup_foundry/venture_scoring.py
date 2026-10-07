"""Independent venture assessments reusing the existing Decimal scorecard rubric."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    ConfidenceLevel,
    CriterionScore,
    Decision,
    Evidence,
    IdeaAssessment,
    IdeaRevision,
    Venture,
    VentureAssessment,
    VentureCriterionScore,
    VentureCriterionScoreEvidence,
    WorkspaceReview,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.repository import SessionFactory
from startup_foundry.score_presentation import ScoreSummary
from startup_foundry.scoring import (
    ORIGINAL,
    REVIEWED,
    CriterionInput,
    ScoringService,
    calculate,
    digest,
    score_components,
)
from startup_foundry.snapshots import transaction

JSON = dict[str, Any]


class VentureAssessmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    venture_id: str = Field(min_length=1, max_length=36)
    scorecard_id: str = REVIEWED
    expected_sequence: int = Field(ge=0)
    request_key: str = Field(min_length=1, max_length=160)
    scores: dict[str, Any]
    rationale: str = Field(min_length=1, max_length=20000)
    author: str = Field(min_length=1, max_length=200)
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    criterion_rationales: dict[str, str] = Field(default_factory=dict)
    evidence_ids: dict[str, list[str]] = Field(default_factory=dict)


class VentureScoringService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    @staticmethod
    def context(session: Session, v: Venture) -> JSON:
        review = session.scalar(
            select(WorkspaceReview)
            .where(WorkspaceReview.workspace_id == v.workspace_id)
            .order_by(WorkspaceReview.revision.desc())
            .limit(1)
        )
        # IDs plus immutable semantic content make evidence provenance reproducible.
        evidence = [
            {"id": e.id, "summary": e.summary, "details": e.details}
            for e in session.scalars(
                select(Evidence)
                .where(Evidence.workspace_id == v.workspace_id)
                .order_by(Evidence.id)
            )
        ]
        decisions = [
            {"id": d.id, "rationale": d.rationale}
            for d in session.scalars(
                select(Decision)
                .where(Decision.workspace_id == v.workspace_id)
                .order_by(Decision.id)
            )
        ]
        return {
            "objective": v.objective,
            "source_idea_revision_id": v.source_idea_revision_id,
            "review_id": review.id if review else None,
            "evidence": evidence,
            "decisions": decisions,
        }

    @staticmethod
    def latest(session: Session, venture: str, card: str) -> int:
        return (
            session.scalar(
                select(func.max(VentureAssessment.sequence)).where(
                    VentureAssessment.venture_id == venture,
                    VentureAssessment.scorecard_id == card,
                )
            )
            or 0
        )

    def assess(self, payload: VentureAssessmentInput) -> JSON:
        with transaction(self.factory) as session:
            return self._assess(session, payload)

    def _assess(self, session: Session, payload: VentureAssessmentInput) -> JSON:
        if payload.scorecard_id == ORIGINAL:
            raise ValidationError("Original card is baseline-import only")
        if not payload.author.strip() or not payload.rationale.strip():
            raise ValidationError("Author and rationale must be nonblank")
        v = session.get(Venture, payload.venture_id)
        if not v:
            raise ReferenceError("Venture missing")
        fingerprint = digest(payload.model_dump(mode="json"))
        existing = session.scalar(
            select(VentureAssessment).where(
                VentureAssessment.venture_id == v.id,
                VentureAssessment.request_key == payload.request_key,
            )
        )
        if existing:
            if existing.payload_digest != fingerprint:
                raise ConflictError("Request key reused with different assessment")
            return self._json(session, existing)
        if payload.scorecard_id == REVIEWED:
            ScoringService._default_card(session, REVIEWED)
        criteria = ScoringService._criteria(session, payload.scorecard_id)
        allowed = {c.key for c in criteria}
        if (set(payload.criterion_rationales) | set(payload.evidence_ids)) - allowed:
            raise ValidationError("Unknown scorecard criteria")
        specs = [
            CriterionInput(
                key=c.key,
                name=c.name,
                direction=c.direction,
                weight=Decimal(str(c.weight)),
            )
            for c in criteria
        ]
        total = calculate(payload.scores, specs)
        latest = self.latest(session, v.id, payload.scorecard_id)
        if latest != payload.expected_sequence:
            raise ConflictError("Assessment changed; reload latest sequence")
        for key, ids in payload.evidence_ids.items():
            if payload.scores.get(key) is None:
                raise ValidationError("Evidence needs a known factor")
            for identity in ids:
                e = session.get(Evidence, identity)
                if not e or e.workspace_id != v.workspace_id:
                    raise ReferenceError("Evidence must belong to assessed venture")
        context = self.context(session, v)
        a = VentureAssessment(
            venture_id=v.id,
            scorecard_id=payload.scorecard_id,
            sequence=latest + 1,
            kind="reviewed",
            overall_score=total,
            confidence=payload.confidence,
            rationale=payload.rationale,
            author=payload.author,
            context_json=context,
            context_digest=digest(context),
            request_key=payload.request_key,
            payload_digest=fingerprint,
        )
        session.add(a)
        session.flush()
        for c in criteria:
            if payload.scores.get(c.key) is None:
                continue
            raw, normalized, contribution = score_components(
                payload.scores[c.key], c.direction, c.weight
            )
            score = VentureCriterionScore(
                assessment_id=a.id,
                criterion_id=c.id,
                raw_score=float(raw),
                normalized_score=float(normalized),
                weighted_contribution=contribution,
                rationale=payload.criterion_rationales.get(c.key, payload.rationale),
            )
            session.add(score)
            session.flush()
            for identity in set(payload.evidence_ids.get(c.key, [])):
                session.add(
                    VentureCriterionScoreEvidence(
                        criterion_score_id=score.id, evidence_id=identity
                    )
                )
        session.flush()
        return self._json(session, a)

    def bootstrap(self) -> JSON:
        with transaction(self.factory) as session:
            imported = sum(
                self.bootstrap_venture(session, v)
                for v in session.scalars(
                    select(Venture).where(Venture.source_idea_revision_id.is_not(None))
                )
            )
            return {"imported": imported}

    def bootstrap_venture(self, session: Session, v: Venture) -> int:
        """Copy only this venture's pinned source within the caller's transaction."""
        imported = 0
        cards = list(
            session.scalars(
                select(IdeaAssessment.scorecard_id)
                .where(IdeaAssessment.idea_revision_id == v.source_idea_revision_id)
                .distinct()
                .order_by(IdeaAssessment.scorecard_id)
            )
        )
        for card in cards:
            if session.scalar(
                select(VentureAssessment.id).where(
                    VentureAssessment.venture_id == v.id,
                    VentureAssessment.baseline_card_id == card,
                )
            ):
                continue
            source = session.scalar(
                select(IdeaAssessment)
                .where(
                    IdeaAssessment.idea_revision_id == v.source_idea_revision_id,
                    IdeaAssessment.scorecard_id == card,
                )
                .order_by(IdeaAssessment.assessment_number.desc())
                .limit(1)
            )
            if not source:
                continue
            context = self.context(session, v)
            a = VentureAssessment(
                venture_id=v.id,
                scorecard_id=card,
                baseline_card_id=card,
                sequence=self.latest(session, v.id, card) + 1,
                kind="source_baseline",
                source_assessment_id=source.id,
                overall_score=source.overall_score,
                confidence=source.confidence,
                rationale=source.rationale or "Source estimate",
                author="source-baseline-import-v1",
                context_json=context,
                context_digest=digest(context),
                request_key="baseline:" + card,
                payload_digest=digest({"source": source.id}),
            )
            session.add(a)
            session.flush()
            for row in session.scalars(
                select(CriterionScore).where(CriterionScore.assessment_id == source.id)
            ):
                session.add(
                    VentureCriterionScore(
                        assessment_id=a.id,
                        criterion_id=row.criterion_id,
                        raw_score=row.raw_score,
                        normalized_score=row.normalized_score,
                        weighted_contribution=row.weighted_contribution,
                        rationale=row.rationale or "Copied source rationale",
                    )
                )
            imported += 1
        return imported

    @staticmethod
    def _json(session: Session, a: VentureAssessment) -> JSON:
        from startup_foundry.domain import ScoringCriterion

        pairs = session.execute(
            select(VentureCriterionScore, ScoringCriterion)
            .join(ScoringCriterion)
            .where(VentureCriterionScore.assessment_id == a.id)
            .order_by(ScoringCriterion.key)
        ).all()
        required = session.scalar(
            select(func.count())
            .select_from(ScoringCriterion)
            .where(ScoringCriterion.scorecard_id == a.scorecard_id)
        )
        v = session.get(Venture, a.venture_id)
        assert v
        context = VentureScoringService.context(session, v)
        scope = {k: context[k] for k in ["objective", "source_idea_revision_id"]}
        old_scope = {k: a.context_json[k] for k in scope}
        source = (
            session.get(IdeaAssessment, a.source_assessment_id)
            if a.source_assessment_id
            else None
        )
        result: JSON = {
            "id": a.id,
            "venture_id": a.venture_id,
            "scorecard_id": a.scorecard_id,
            "sequence": a.sequence,
            "kind": a.kind,
            "source_assessment_id": a.source_assessment_id,
            "original_assessor": source.assessed_by if source else None,
            "total": a.overall_score,
            "confidence": a.confidence.value,
            "coverage": len(pairs),
            "required": required,
            "label": (
                "Original idea estimate"
                if a.scorecard_id == ORIGINAL
                else "Starting estimate from source idea"
            )
            if a.kind == "source_baseline"
            else "Reviewed venture judgment",
            "rationale": a.rationale,
            "author": a.author,
            "created_at": a.created_at.isoformat(),
            "context": a.context_json,
            "scope_stale": scope != old_scope,
            "reassessment_suggested": context != a.context_json,
            "criteria": [
                {
                    "key": c.key,
                    "name": c.name,
                    "raw": s.raw_score,
                    "direction": c.direction.value,
                    "weight": c.weight,
                    "contribution": s.weighted_contribution,
                    "rationale": s.rationale,
                    "evidence_ids": list(
                        session.scalars(
                            select(VentureCriterionScoreEvidence.evidence_id).where(
                                VentureCriterionScoreEvidence.criterion_score_id == s.id
                            )
                        )
                    ),
                }
                for s, c in pairs
            ],
        }
        result.update(ScoreSummary.model_validate(result).model_dump())
        return result

    def show(self, identity: str, card: str = REVIEWED) -> JSON:
        with self.factory() as session:
            ScoringService.read_card(session, card)
            v = session.get(Venture, identity)
            if not v:
                raise ReferenceError("Venture missing")
            history = [
                self._json(session, a)
                for a in session.scalars(
                    select(VentureAssessment)
                    .where(VentureAssessment.venture_id == identity)
                    .order_by(
                        VentureAssessment.created_at.desc(),
                        VentureAssessment.sequence.desc(),
                    )
                )
            ]
            primary = next(
                (
                    a
                    for a in history
                    if a["scorecard_id"] == card and a["kind"] == "reviewed"
                ),
                None,
            ) or next((a for a in history if a["scorecard_id"] == card), None)
            fallback = (
                next((a for a in history if a["scorecard_id"] == ORIGINAL), None)
                if card == REVIEWED and not primary
                else None
            )
            current = primary or fallback
            for i, a in enumerate(history):
                prev = next(
                    (
                        b
                        for b in history[i + 1 :]
                        if b["scorecard_id"] == a["scorecard_id"]
                    ),
                    None,
                )
                compatible = prev and all(
                    prev["context"][k] == a["context"][k]
                    for k in ["objective", "source_idea_revision_id"]
                )
                a["comparison"] = (
                    "Not directly comparable"
                    if prev and not compatible
                    else "Compared to copied source baseline"
                    if prev and prev["kind"] == "source_baseline"
                    else "Same scope and scorecard"
                    if prev
                    else "First assessment"
                )
                a["delta"] = (
                    a["total"] - prev["total"]
                    if compatible
                    and prev is not None
                    and a["total"] is not None
                    and prev["total"] is not None
                    else None
                )
            source_revision = (
                session.get(IdeaRevision, v.source_idea_revision_id)
                if v.source_idea_revision_id
                else None
            )
            return {
                "history": history,
                "current": current,
                "primary": primary,
                "fallback": fallback,
                "card_id": card,
                "expected_sequence": self.latest(session, identity, card),
                "source_idea_id": source_revision.idea_id if source_revision else None,
            }
