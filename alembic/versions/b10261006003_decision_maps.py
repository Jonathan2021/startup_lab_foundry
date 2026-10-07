"""Add one versioned decision-map head per workspace; retain existing records."""

import sqlalchemy as sa
from alembic import op

revision = "b10261006003"
down_revision = "b10261006002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decision_maps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), nullable=False),
        sa.Column("current_revision_artifact_id", sa.String(36), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["current_revision_artifact_id"], ["artifacts.id"]),
        sa.UniqueConstraint("workspace_id"),
    )


def downgrade() -> None:
    op.drop_table("decision_maps")
