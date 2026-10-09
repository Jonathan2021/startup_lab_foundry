"""Retain check date and source references on idea market-actor links.

Revision ID: b10261009001
Revises: b10261006003
Create Date: 2026-10-09

Additive only: existing links keep a null check date and no source references.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b10261009001"
down_revision: str | Sequence[str] | None = "b10261006003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "idea_market_actors", sa.Column("checked_on", sa.Date(), nullable=True)
    )
    op.add_column(
        "idea_market_actors", sa.Column("source_ids", sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("idea_market_actors", "source_ids")
    op.drop_column("idea_market_actors", "checked_on")
