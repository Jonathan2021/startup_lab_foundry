"""Add the deferred current-idea-revision foreign key.

Revision ID: 42d765ac6946
Revises: 149fc56b9af9
Create Date: 2026-08-14

"""

from collections.abc import Sequence

from alembic import op

revision: str = "42d765ac6946"
down_revision: str | Sequence[str] | None = "149fc56b9af9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Bring the database constraint in line with the domain metadata."""

    with op.batch_alter_table("ideas") as batch_op:
        batch_op.create_foreign_key(
            "fk_ideas_current_revision",
            "idea_revisions",
            ["current_revision_id"],
            ["id"],
            deferrable=True,
            initially="DEFERRED",
        )


def downgrade() -> None:
    """Remove the deferred current-idea-revision foreign key."""

    with op.batch_alter_table("ideas") as batch_op:
        batch_op.drop_constraint(
            "fk_ideas_current_revision",
            type_="foreignkey",
        )
