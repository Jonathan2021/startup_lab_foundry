"""Versioned, evidence-linked judgments; never inferred success probabilities."""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    ConfidenceLevel,
    CriterionScore,
    CriterionScoreEvidence,
    Evidence,
    Idea,
    IdeaAssessment,
    IdeaRevision,
    RankingEntry,
    RankingSnapshot,
    ReferenceSource,
    Scorecard,
    ScorecardStatus,
    ScoreDirection,
    ScoringCriterion,
    SourceKind,
    Workspace,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.portfolio import PortfolioService, stable_id
from startup_foundry.repository import SessionFactory, UnitOfWork
from startup_foundry.score_presentation import ScoreSummary

JSON = dict[str, Any]
ORIGINAL = "portfolio-original-v1"
REVIEWED = "portfolio-reviewed-v1"
FORMULA = "workbook-AK2-penalty-minus-one-half-away-v1"
FACTORS = (
    ("revenue", "Revenue potential", "positive", "0.22"),
    ("profitability", "Profitability ease", "positive", "0.18"),
    ("mvp_speed", "MVP speed", "positive", "0.12"),
    ("founder_fit", "Founder fit", "positive", "0.15"),
    ("go_to_market", "Go-to-market ease", "positive", "0.10"),
    ("moat", "Moat / defensibility", "positive", "0.08"),
    ("problem", "Problem intensity", "positive", "0.10"),
    ("retention", "Retention potential", "positive", "0.05"),
    ("legal_risk", "Legal / ethical risk", "penalty", "0.10"),
    ("capital", "Capital intensity", "penalty", "0.06"),
    ("network", "Network dependency", "penalty", "0.05"),
    ("competition", "Competition intensity", "penalty", "0.04"),
)


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def scorecard_for_view(score_view: str) -> str:
    """Resolve a list/detail `score_view` (built-in name or card ID) to a card ID."""
    return {"original": ORIGINAL, "reviewed": REVIEWED}.get(score_view, score_view)


def number(value: Any) -> Decimal:
    try:
        if isinstance(value, bool):
            raise InvalidOperation
        result = Decimal(str(value))
        if not result.is_finite() or not 1 <= result <= 10:
            raise InvalidOperation
        return result
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(
            "Criterion scores must be finite numbers from 1 to 10; use null for unknown"
        ) from exc


class CriterionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=1, max_length=240)
    direction: ScoreDirection
    weight: Decimal = Field(ge=0, le=1, allow_inf_nan=False)
    scale_min: int = Field(default=1, ge=1, le=1)
    scale_max: int = Field(default=10, ge=10, le=10)


class ScorecardInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=36)
    name: str = Field(min_length=1, max_length=240)
    version: int = Field(ge=1)
    rationale: str = Field(min_length=1, max_length=10000)
    criteria: list[CriterionInput] = Field(min_length=1, max_length=30)


class AssessmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    idea_id: str = Field(min_length=1, max_length=36)
    revision_id: str | None = None
    scorecard_id: str = REVIEWED
    scores: dict[str, Any]
    rationale: str = Field(min_length=1, max_length=20000)
    author: str = Field(min_length=1, max_length=200)
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    criterion_rationales: dict[str, str] = Field(default_factory=dict)
    evidence_ids: dict[str, list[str]] = Field(default_factory=dict)
    recommendation: str | None = None
    category: str | None = None
    expected_sequence: int | None = Field(default=None, ge=0)


def default_criteria() -> list[CriterionInput]:
    return [
        CriterionInput(key=k, name=n, direction=ScoreDirection(d), weight=Decimal(w))
        for k, n, d, w in FACTORS
    ]


def calculate(
    scores: dict[str, Any], criteria: list[CriterionInput] | None = None
) -> int | None:
    factors = criteria or default_criteria()
    allowed = {c.key for c in factors}
    if set(scores) - allowed:
        raise ValidationError(
            "Unknown criteria: " + ", ".join(sorted(set(scores) - allowed))
        )
    values = {k: number(v) for k, v in scores.items() if v is not None}
    if set(values) != allowed:
        return None
    total = Decimal(0)
    for c in factors:
        raw = values[c.key]
        total += c.weight * (
            raw if c.direction == ScoreDirection.POSITIVE else -(raw - 1)
        )
    return max(
        0, min(100, int((10 * total).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
    )


def score_components(
    value: Any, direction: ScoreDirection, weight: float
) -> tuple[float, float, float]:
    raw = number(value)
    normalized = (raw if direction == ScoreDirection.POSITIVE else raw - 1) / 10
    contribution = (
        100
        * Decimal(str(weight))
        * normalized
        * (1 if direction == ScoreDirection.POSITIVE else -1)
    )
    return float(raw), float(normalized), float(contribution)


def grade(total: int | None, category: str | None = None) -> str | None:
    if category == "Reject: deceptive / harmful":
        return "X"
    return (
        None
        if total is None
        else "A"
        if total >= 70
        else "B"
        if total >= 58
        else "C"
        if total >= 45
        else "D"
    )


class ScoringService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    @staticmethod
    def _card(session: Session, payload: ScorecardInput) -> Scorecard:
        keys = [c.key for c in payload.criteria]
        if len(keys) != len(set(keys)) or not payload.rationale.strip():
            raise ValidationError(
                "Scorecard needs unique criterion keys and a rationale"
            )
        encoded = payload.model_dump(mode="json")
        existing = session.get(Scorecard, payload.id)
        if existing:
            if existing.description != canonical(encoded):
                raise ConflictError("Scorecard is immutable; import a new ID/version")
            return existing
        portfolio = PortfolioService._portfolio(session)
        card = Scorecard(
            id=payload.id,
            portfolio_id=portfolio.id,
            name=payload.name,
            version=payload.version,
            status=ScorecardStatus.ACTIVE,
            description=canonical(encoded),
            formula_description=FORMULA,
        )
        session.add(card)
        session.flush()
        for c in payload.criteria:
            session.add(
                ScoringCriterion(
                    id=stable_id(payload.id + ":" + c.key),
                    scorecard_id=card.id,
                    key=c.key,
                    name=c.name,
                    direction=c.direction,
                    weight=float(c.weight),
                    scale_min=c.scale_min,
                    scale_max=c.scale_max,
                )
            )
        session.flush()
        return card

    def import_scorecard(self, payload: ScorecardInput) -> JSON:
        with UnitOfWork(self.factory) as unit:
            assert unit.session is not None
            card = self._card(unit.session, payload)
            return {"id": card.id, "name": card.name, "version": card.version}

    @staticmethod
    def _default_card(session: Session, identity: str) -> Scorecard:
        return ScoringService._card(
            session,
            ScorecardInput(
                id=identity,
                name=identity,
                version=1,
                rationale="Original workbook, imported/unreviewed"
                if identity == ORIGINAL
                else (
                    "Reviewed judgments using unchanged workbook weights; "
                    "unknown factors remain missing"
                ),
                criteria=default_criteria(),
            ),
        )

    @staticmethod
    def _criteria(session: Session, card_id: str) -> list[ScoringCriterion]:
        if session.get(Scorecard, card_id) is None:
            raise ReferenceError("Scorecard does not exist")
        return list(
            session.scalars(
                select(ScoringCriterion)
                .where(ScoringCriterion.scorecard_id == card_id)
                .order_by(ScoringCriterion.key)
            )
        )

    @staticmethod
    def read_card(session: Session, identity: str) -> JSON:
        """Known empty built-ins have a rubric without creating records on GET."""
        card = session.get(Scorecard, identity)
        if not card:
            if identity not in {ORIGINAL, REVIEWED}:
                raise ReferenceError("Scorecard does not exist")
            return {
                "id": identity,
                "name": identity,
                "criteria": [c.model_dump(mode="json") for c in default_criteria()],
            }
        return {
            "id": card.id,
            "name": card.name,
            "criteria": [
                {
                    "key": c.key,
                    "name": c.name,
                    "direction": c.direction.value,
                    "weight": c.weight,
                    "scale_min": c.scale_min,
                    "scale_max": c.scale_max,
                }
                for c in ScoringService._criteria(session, identity)
            ],
        }

    @staticmethod
    def _append(session: Session, payload: AssessmentInput) -> IdeaAssessment:
        idea = session.get(Idea, payload.idea_id)
        if idea is None:
            raise ReferenceError("Idea does not exist")
        revision = session.get(
            IdeaRevision, payload.revision_id or idea.current_revision_id
        )
        if revision is None or revision.idea_id != idea.id:
            raise ReferenceError("Revision does not belong to this idea")
        criteria = ScoringService._criteria(session, payload.scorecard_id)
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
        keys = {c.key for c in criteria}
        if (set(payload.criterion_rationales) | set(payload.evidence_ids)) - keys:
            raise ValidationError("Rationale/evidence references unknown criteria")
        for key, identities in payload.evidence_ids.items():
            if payload.scores.get(key) is None:
                raise ValidationError("Evidence cannot attach to a missing score")
            for identity in identities:
                evidence = session.get(Evidence, identity)
                if evidence is None or evidence.workspace_id != idea.workspace_id:
                    raise ReferenceError(
                        "Score evidence must belong to the idea workspace; "
                        "link source provenance explicitly"
                    )
        sequence = (
            session.scalar(
                select(func.max(IdeaAssessment.assessment_number)).where(
                    IdeaAssessment.idea_revision_id == revision.id,
                    IdeaAssessment.scorecard_id == payload.scorecard_id,
                )
            )
            or 0
        ) + 1
        if (
            payload.expected_sequence is not None
            and payload.expected_sequence != sequence - 1
        ):
            raise ConflictError("Idea assessment changed; reload latest sequence")
        assessment = IdeaAssessment(
            idea_revision_id=revision.id,
            scorecard_id=payload.scorecard_id,
            assessment_number=sequence,
            confidence=payload.confidence,
            overall_score=total,
            grade=grade(total, payload.category or revision.category),
            rationale=payload.rationale,
            assessed_by=payload.author,
            recommendation=payload.recommendation,
        )
        session.add(assessment)
        session.flush()
        for c in criteria:
            value = payload.scores.get(c.key)
            if value is None:
                continue
            raw, normalized, contribution = score_components(
                value, c.direction, c.weight
            )
            score = CriterionScore(
                assessment_id=assessment.id,
                criterion_id=c.id,
                raw_score=float(raw),
                normalized_score=float(normalized),
                weighted_contribution=float(contribution),
                rationale=payload.criterion_rationales.get(c.key, payload.rationale),
            )
            session.add(score)
            session.flush()
            for identity in set(payload.evidence_ids.get(c.key, [])):
                session.add(
                    CriterionScoreEvidence(
                        criterion_score_id=score.id, evidence_id=identity
                    )
                )
        return assessment

    def assess(self, payload: AssessmentInput) -> JSON:
        if payload.scorecard_id == ORIGINAL:
            raise ValidationError(
                "Original workbook assessments are immutable; use a reviewed scorecard"
            )
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            if payload.scorecard_id == REVIEWED:
                self._default_card(session, REVIEWED)
            assessment = self._append(session, payload)
            session.flush()
            return self._assessment(session, assessment)

    def import_original(self, directory: Path) -> JSON:
        path = directory / "startup_ideas.csv"
        try:
            data = path.read_bytes()
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                if not reader.fieldnames or len(set(reader.fieldnames)) != len(
                    reader.fieldnames
                ):
                    raise ValidationError("Missing or duplicate CSV headers")
                rows = list(reader)
        except (OSError, UnicodeError, csv.Error) as exc:
            raise ValidationError("Cannot read startup_ideas.csv") from exc
        required = {
            "Idea ID",
            "Priority score",
            "Grade",
            *[h for _, h, _, _ in FACTORS],
        }
        if (
            not rows
            or not required <= set(rows[0])
            or any(None in r or None in r.values() for r in rows)
        ):
            raise ValidationError("CSV is empty, malformed, or missing scoring fields")
        identities = [r["Idea ID"] for r in rows]
        if len(identities) != len(set(identities)):
            raise ValidationError("Duplicate CSV idea IDs")
        for row in rows:
            total = calculate({k: row[h] for k, h, _, _ in FACTORS})
            if (
                str(total) != row["Priority score"]
                or grade(total, row.get("Category")) != row["Grade"]
            ):
                raise ValidationError("Workbook parity conflict for " + row["Idea ID"])
        source_digest = hashlib.sha256(data).hexdigest()
        imported = 0
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            self._default_card(session, ORIGINAL)
            source = session.scalar(
                select(ReferenceSource)
                .where(ReferenceSource.content_digest == source_digest)
                .order_by(ReferenceSource.id)
            )
            if source is None:
                source = ReferenceSource(
                    id=stable_id("score-source:" + source_digest),
                    portfolio_id=PortfolioService._portfolio(session).id,
                    kind=SourceKind.SPREADSHEET,
                    title="Original workbook CSV scores",
                    locator=str(path.resolve()),
                    content_digest=source_digest,
                    notes=(
                        "Imported source judgments, "
                        "not independently validated forecasts."
                    ),
                )
                session.add(source)
                session.flush()
            for row in rows:
                idea = session.get(Idea, row["Idea ID"])
                if idea is None:
                    raise ReferenceError("Import ideas first: " + row["Idea ID"])
                artifact_id = stable_id(
                    "original-score:" + str(idea.current_revision_id)
                )
                # The original row belongs to whichever revision first received
                # it; a later idea revision never re-imports the workbook score.
                existing = next(
                    (
                        artifact
                        for revision_id in session.scalars(
                            select(IdeaRevision.id)
                            .where(IdeaRevision.idea_id == idea.id)
                            .order_by(IdeaRevision.revision_number)
                        )
                        if (
                            artifact := session.get(
                                Artifact, stable_id("original-score:" + revision_id)
                            )
                        )
                    ),
                    None,
                )
                row_digest = digest(row)
                if existing:
                    if existing.metadata_json["row_sha256"] != row_digest:
                        raise ConflictError(
                            "Changed original row needs an explicit revision: "
                            + idea.id
                        )
                    continue
                assessment = self._append(
                    session,
                    AssessmentInput(
                        idea_id=idea.id,
                        scorecard_id=ORIGINAL,
                        scores={k: row[h] for k, h, _, _ in FACTORS},
                        confidence=ConfidenceLevel(
                            row["Assessment confidence"].lower()
                        ),
                        rationale="Imported/unreviewed source judgment; "
                        + row.get("Market sanity-check note", ""),
                        author="workbook-import-v1",
                        recommendation=row.get("Recommendation"),
                    ),
                )
                assessment.pros = row.get("Pros / what could work")
                assessment.cons = row.get("Cons / limitations")
                session.add(
                    Artifact(
                        id=artifact_id,
                        workspace_id=idea.workspace_id,
                        kind=ArtifactKind.DOCUMENT,
                        name="Original workbook scoring provenance",
                        location="db:idea_assessments/" + assessment.id,
                        content_digest=row_digest,
                        metadata_json={
                            "assessment_id": assessment.id,
                            "row_sha256": row_digest,
                            "source_id": source.id,
                            "csv_sha256": source_digest,
                            "idea_id": idea.id,
                            "formula": FORMULA,
                            "source_rank": row["Rank"],
                            "monthly_revenue_low": row.get(
                                "Mature monthly revenue - low"
                            ),
                            "monthly_revenue_high": row.get(
                                "Mature monthly revenue - high"
                            ),
                            "source_row": row,
                            "limits": (
                                "Reported confidence; mature monthly ranges "
                                "are unvalidated, not forecasts."
                            ),
                        },
                    )
                )
                imported += 1
            # A relocation is availability, not a new source.
            availability = stable_id(
                "source-availability:" + source_digest + ":" + str(path.resolve())
            )
            if session.get(Artifact, availability) is None:
                workspace = session.get(Idea, identities[0])
                assert workspace is not None
                session.add(
                    Artifact(
                        id=availability,
                        workspace_id=workspace.workspace_id,
                        kind=ArtifactKind.DOCUMENT,
                        name="Source availability",
                        location=str(path.resolve()),
                        content_digest=source_digest,
                        metadata_json={
                            "source_id": source.id,
                            "availability_only": True,
                        },
                    )
                )
        return {
            "imported": imported,
            "unchanged": len(rows) - imported,
            "csv_sha256": source_digest,
            "scorecard_id": ORIGINAL,
        }

    @staticmethod
    def _assessment(session: Session, a: IdeaAssessment) -> JSON:
        scores = session.execute(
            select(CriterionScore, ScoringCriterion)
            .join(ScoringCriterion)
            .where(CriterionScore.assessment_id == a.id)
            .order_by(ScoringCriterion.key)
        ).all()
        provenance = session.scalar(
            select(Artifact).where(
                Artifact.name == "Original workbook scoring provenance",
                Artifact.location == "db:idea_assessments/" + a.id,
            )
        )
        criteria_count = session.scalar(
            select(func.count())
            .select_from(ScoringCriterion)
            .where(ScoringCriterion.scorecard_id == a.scorecard_id)
        )
        revision = session.get(IdeaRevision, a.idea_revision_id)
        result: JSON = {
            "id": a.id,
            "revision_id": a.idea_revision_id,
            "revision_number": revision.revision_number if revision else None,
            "scorecard_id": a.scorecard_id,
            "number": a.assessment_number,
            "total": a.overall_score,
            "grade": a.grade,
            "confidence": a.confidence.value,
            "coverage": len(scores),
            "required": criteria_count,
            "label": "Imported/unreviewed reported confidence"
            if a.scorecard_id == ORIGINAL
            else "Reviewed judgment",
            "rationale": a.rationale,
            "author": a.assessed_by,
            "created_at": a.created_at.isoformat(),
            "recommendation": a.recommendation,
            "pros": a.pros,
            "cons": a.cons,
            "source": provenance.metadata_json if provenance else None,
            "criteria": [
                {
                    "key": c.key,
                    "name": c.name,
                    "direction": c.direction.value,
                    "weight": c.weight,
                    "raw": s.raw_score,
                    "contribution": s.weighted_contribution,
                    "rationale": s.rationale,
                    "evidence_ids": list(
                        session.scalars(
                            select(CriterionScoreEvidence.evidence_id).where(
                                CriterionScoreEvidence.criterion_score_id == s.id
                            )
                        )
                    ),
                }
                for s, c in scores
            ],
        }
        result.update(ScoreSummary.model_validate(result).model_dump())
        return result

    def show(self, idea_id: str) -> JSON:
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            idea = session.get(Idea, idea_id)
            if idea is None:
                raise ReferenceError("Idea does not exist")
            assessments = session.scalars(
                select(IdeaAssessment)
                .join(IdeaRevision)
                .where(IdeaRevision.idea_id == idea_id)
                .order_by(IdeaAssessment.created_at.desc(), IdeaAssessment.id)
            )
            history = [self._assessment(session, a) for a in assessments]
            for item in history:
                # Assessments stay attached to the revision they judged.
                item["current_revision"] = (
                    item["revision_id"] == idea.current_revision_id
                )
            return {
                "idea_id": idea_id,
                "current_revision_id": idea.current_revision_id,
                "history": history,
            }

    def list_scorecards(self) -> JSON:
        with self.factory() as session:
            return {
                "items": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "version": c.version,
                        "description": c.description,
                    }
                    for c in session.scalars(select(Scorecard).order_by(Scorecard.id))
                ]
            }

    def sensitivity(self, idea_id: str, scorecard_id: str = ORIGINAL) -> JSON:
        history = [
            a
            for a in self.show(idea_id)["history"]
            if a["scorecard_id"] == scorecard_id
        ]
        if not history:
            raise ReferenceError("No assessment for this scorecard")
        a = history[0]
        values = {c["key"]: c["raw"] for c in a["criteria"]}
        with self.factory() as session:
            criteria = [
                CriterionInput(
                    key=c.key,
                    name=c.name,
                    direction=c.direction,
                    weight=Decimal(str(c.weight)),
                )
                for c in self._criteria(session, scorecard_id)
            ]
        output = []
        for c in criteria:
            if c.key not in values:
                continue
            for delta in (-1, 1):
                value = values[c.key] + delta
                if 1 <= value <= 10:
                    output.append(
                        {
                            "criterion": c.key,
                            "delta": delta,
                            "total": calculate({**values, c.key: value}, criteria),
                        }
                    )
        return {
            "assessment_id": a["id"],
            "scorecard_id": scorecard_id,
            "base": a["total"],
            "changes": output,
            "limits": "Sensitivity, not success probability",
        }

    def rank(self, scorecard_id: str, label: str) -> JSON:
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            card = session.get(Scorecard, scorecard_id)
            if card is None:
                raise ReferenceError("Scorecard does not exist")
            if session.scalar(
                select(RankingSnapshot).where(
                    RankingSnapshot.portfolio_id == card.portfolio_id,
                    RankingSnapshot.label == label,
                )
            ):
                raise ConflictError(
                    "Ranking label already exists; snapshots are immutable"
                )
            latest = (
                select(
                    IdeaAssessment.id,
                    func.row_number()
                    .over(
                        partition_by=IdeaAssessment.idea_revision_id,
                        order_by=IdeaAssessment.assessment_number.desc(),
                    )
                    .label("position"),
                )
                .where(IdeaAssessment.scorecard_id == scorecard_id)
                .subquery()
            )
            rows = session.execute(
                select(Idea, IdeaAssessment)
                .join(
                    IdeaAssessment,
                    IdeaAssessment.idea_revision_id == Idea.current_revision_id,
                )
                .join(latest, latest.c.id == IdeaAssessment.id)
                .where(
                    latest.c.position == 1, IdeaAssessment.overall_score.is_not(None)
                )
                .order_by(IdeaAssessment.overall_score.desc(), Idea.id)
            ).all()
            all_ideas = list(
                session.scalars(
                    select(Idea)
                    .join(Workspace)
                    .where(Workspace.portfolio_id == card.portfolio_id)
                    .order_by(Idea.id)
                )
            )
            all_count = len(all_ideas)
            snapshot = RankingSnapshot(
                portfolio_id=card.portfolio_id,
                scorecard_id=card.id,
                label=label,
                description=f"{len(rows)} comparable totals; missing totals excluded",
                generated_by="scoring-service-v1",
            )
            session.add(snapshot)
            session.flush()
            ranked_entries = []
            for rank, (idea, a) in enumerate(rows, 1):
                session.add(
                    RankingEntry(
                        snapshot_id=snapshot.id,
                        idea_id=idea.id,
                        assessment_id=a.id,
                        rank=rank,
                        score=a.overall_score,
                    )
                )
                ranked_entries.append(
                    {
                        "rank": rank,
                        "idea_id": idea.id,
                        "score": a.overall_score,
                        "assessment_id": a.id,
                    }
                )
            ranked_ids = {idea.id for idea, _ in rows}
            return {
                "id": snapshot.id,
                "ranked": len(rows),
                "excluded": all_count - len(rows),
                "ranked_entries": ranked_entries,
                "excluded_entries": self._exclusions(
                    session,
                    scorecard_id,
                    [idea for idea in all_ideas if idea.id not in ranked_ids],
                ),
            }

    @staticmethod
    def _exclusions(
        session: Session, scorecard_id: str, ideas: list[Idea]
    ) -> list[JSON]:
        """Explain each unranked idea; nothing is inferred for a missing total."""
        excluded = []
        for idea in ideas:
            latest = session.scalar(
                select(IdeaAssessment)
                .where(
                    IdeaAssessment.idea_revision_id == idea.current_revision_id,
                    IdeaAssessment.scorecard_id == scorecard_id,
                )
                .order_by(IdeaAssessment.assessment_number.desc())
                .limit(1)
            )
            if latest is not None:
                reason = "partial_total"
                assessment_id: str | None = latest.id
            else:
                earlier = session.scalar(
                    select(IdeaAssessment.id)
                    .join(
                        IdeaRevision,
                        IdeaRevision.id == IdeaAssessment.idea_revision_id,
                    )
                    .where(
                        IdeaRevision.idea_id == idea.id,
                        IdeaAssessment.scorecard_id == scorecard_id,
                    )
                    .order_by(IdeaAssessment.created_at.desc())
                    .limit(1)
                )
                reason = (
                    "assessed_on_earlier_revision_only"
                    if earlier
                    else "not_assessed_on_scorecard"
                )
                assessment_id = earlier
            excluded.append(
                {"idea_id": idea.id, "reason": reason, "assessment_id": assessment_id}
            )
        return excluded
