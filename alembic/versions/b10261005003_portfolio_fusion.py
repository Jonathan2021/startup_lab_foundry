"""Additive schema-only portfolio fusion; bootstrap is explicit."""

from alembic import op
import sqlalchemy as sa

revision = "b10261005003"
down_revision = "b10261005002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portfolio_proposals",
        sa.Column("portfolio_id", sa.String(length=36), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("revision_artifact_id", sa.String(length=36), nullable=False),
        sa.Column("resolution_artifact_id", sa.String(length=36), nullable=True),
        sa.Column("request_key", sa.String(length=160), nullable=False),
        sa.Column("state", sa.String(length=30), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "kind = 'fusion'", name=op.f("ck_portfolio_proposals_proposal_kind")
        ),
        sa.CheckConstraint(
            "state IN ('proposed','rejected','applied','reversed','superseded')",
            name=op.f("ck_portfolio_proposals_proposal_state"),
        ),
        sa.ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
            name=op.f("fk_portfolio_proposals_portfolio_id_portfolios"),
        ),
        sa.ForeignKeyConstraint(
            ["resolution_artifact_id"],
            ["artifacts.id"],
            name=op.f("fk_portfolio_proposals_resolution_artifact_id_artifacts"),
        ),
        sa.ForeignKeyConstraint(
            ["revision_artifact_id"],
            ["artifacts.id"],
            name=op.f("fk_portfolio_proposals_revision_artifact_id_artifacts"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_portfolio_proposals_workspace_id_workspaces"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_portfolio_proposals")),
        sa.UniqueConstraint("portfolio_id", "request_key", name="proposal_request_key"),
    )
    op.create_index(
        op.f("ix_portfolio_proposals_state"),
        "portfolio_proposals",
        ["state"],
        unique=False,
    )
    op.create_table(
        "proposal_participants",
        sa.Column("proposal_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("idea_id", sa.String(length=36), nullable=True),
        sa.Column("venture_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "role IN ('source','result')",
            name=op.f("ck_proposal_participants_participant_role"),
        ),
        sa.CheckConstraint(
            "(idea_id IS NULL) <> (venture_id IS NULL)",
            name=op.f("ck_proposal_participants_participant_one_entity"),
        ),
        sa.ForeignKeyConstraint(
            ["idea_id"],
            ["ideas.id"],
            name=op.f("fk_proposal_participants_idea_id_ideas"),
        ),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["portfolio_proposals.id"],
            name=op.f("fk_proposal_participants_proposal_id_portfolio_proposals"),
        ),
        sa.ForeignKeyConstraint(
            ["venture_id"],
            ["ventures.id"],
            name=op.f("fk_proposal_participants_venture_id_ventures"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_proposal_participants")),
        sa.UniqueConstraint(
            "proposal_id", "role", "idea_id", name="proposal_idea_unique"
        ),
        sa.UniqueConstraint(
            "proposal_id", "role", "venture_id", name="proposal_venture_unique"
        ),
    )
    op.create_index(
        op.f("ix_proposal_participants_proposal_id"),
        "proposal_participants",
        ["proposal_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_proposal_participants_proposal_id"), table_name="proposal_participants"
    )
    op.drop_table("proposal_participants")
    op.drop_index(
        op.f("ix_portfolio_proposals_state"), table_name="portfolio_proposals"
    )
    op.drop_table("portfolio_proposals")
