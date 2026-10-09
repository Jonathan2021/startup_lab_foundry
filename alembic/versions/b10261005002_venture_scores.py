"""Additive schema-only venture scores; bootstrap is explicit."""

from alembic import op
import sqlalchemy as sa

revision = "b10261005002"
down_revision = "b10261005001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "venture_assessments",
        sa.Column("venture_id", sa.String(length=36), nullable=False),
        sa.Column("scorecard_id", sa.String(length=36), nullable=False),
        sa.Column("baseline_card_id", sa.String(length=36), nullable=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("source_assessment_id", sa.String(length=36), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column(
            "confidence",
            sa.Enum(
                "low",
                "medium",
                "high",
                name="venture_assessment_confidence",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("author", sa.String(length=200), nullable=False),
        sa.Column("context_json", sa.JSON(), nullable=False),
        sa.Column("context_digest", sa.String(length=64), nullable=False),
        sa.Column("request_key", sa.String(length=160), nullable=False),
        sa.Column("payload_digest", sa.String(length=64), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "kind IN ('source_baseline','reviewed')",
            name=op.f("ck_venture_assessments_venture_assessment_kind"),
        ),
        sa.CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)",
            name=op.f("ck_venture_assessments_venture_score_range"),
        ),
        sa.CheckConstraint(
            "sequence >= 1",
            name=op.f("ck_venture_assessments_venture_sequence_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["baseline_card_id"],
            ["scorecards.id"],
            name=op.f("fk_venture_assessments_baseline_card_id_scorecards"),
        ),
        sa.ForeignKeyConstraint(
            ["scorecard_id"],
            ["scorecards.id"],
            name=op.f("fk_venture_assessments_scorecard_id_scorecards"),
        ),
        sa.ForeignKeyConstraint(
            ["source_assessment_id"],
            ["idea_assessments.id"],
            name=op.f("fk_venture_assessments_source_assessment_id_idea_assessments"),
        ),
        sa.ForeignKeyConstraint(
            ["venture_id"],
            ["ventures.id"],
            name=op.f("fk_venture_assessments_venture_id_ventures"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_venture_assessments")),
        sa.UniqueConstraint(
            "venture_id", "baseline_card_id", name="venture_baseline_card"
        ),
        sa.UniqueConstraint(
            "venture_id", "request_key", name="venture_assessment_request"
        ),
        sa.UniqueConstraint(
            "venture_id", "scorecard_id", "sequence", name="venture_assessment_sequence"
        ),
    )
    op.create_index(
        op.f("ix_venture_assessments_scorecard_id"),
        "venture_assessments",
        ["scorecard_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_venture_assessments_venture_id"),
        "venture_assessments",
        ["venture_id"],
        unique=False,
    )
    op.create_table(
        "venture_criterion_scores",
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("criterion_id", sa.String(length=36), nullable=False),
        sa.Column("raw_score", sa.Float(), nullable=False),
        sa.Column("normalized_score", sa.Float(), nullable=True),
        sa.Column("weighted_contribution", sa.Float(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["venture_assessments.id"],
            name=op.f("fk_venture_criterion_scores_assessment_id_venture_assessments"),
        ),
        sa.ForeignKeyConstraint(
            ["criterion_id"],
            ["scoring_criteria.id"],
            name=op.f("fk_venture_criterion_scores_criterion_id_scoring_criteria"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_venture_criterion_scores")),
        sa.UniqueConstraint(
            "assessment_id", "criterion_id", name="venture_criterion_unique"
        ),
    )
    op.create_index(
        op.f("ix_venture_criterion_scores_assessment_id"),
        "venture_criterion_scores",
        ["assessment_id"],
        unique=False,
    )
    op.create_table(
        "venture_criterion_score_evidence",
        sa.Column("criterion_score_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["criterion_score_id"],
            ["venture_criterion_scores.id"],
            name=op.f(
                "fk_venture_criterion_score_evidence_criterion_score_id_venture_criterion_scores"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id"],
            ["evidence.id"],
            name=op.f("fk_venture_criterion_score_evidence_evidence_id_evidence"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_venture_criterion_score_evidence")),
        sa.UniqueConstraint(
            "criterion_score_id",
            "evidence_id",
            name="venture_criterion_evidence_unique",
        ),
    )


def downgrade() -> None:
    op.drop_table("venture_criterion_score_evidence")
    op.drop_index(
        op.f("ix_venture_criterion_scores_assessment_id"),
        table_name="venture_criterion_scores",
    )
    op.drop_table("venture_criterion_scores")
    op.drop_index(
        op.f("ix_venture_assessments_venture_id"), table_name="venture_assessments"
    )
    op.drop_index(
        op.f("ix_venture_assessments_scorecard_id"), table_name="venture_assessments"
    )
    op.drop_table("venture_assessments")
