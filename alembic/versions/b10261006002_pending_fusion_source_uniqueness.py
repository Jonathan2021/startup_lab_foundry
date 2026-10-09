"""Pending fusion source uniqueness

Revision ID: b10261006002
Revises: b10261006001
Create Date: 2026-10-06 14:58:38.499204

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b10261006002"
down_revision: str | Sequence[str] | None = "b10261006001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A unique index enforces the same invariant without rebuilding a SQLite
    # table that already has participant foreign keys.
    op.add_column(
        "portfolio_proposals",
        sa.Column("pending_source_key", sa.String(64), nullable=True),
    )
    op.create_index(
        "pending_fusion_sources",
        "portfolio_proposals",
        ["portfolio_id", "pending_source_key"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("pending_fusion_sources", table_name="portfolio_proposals")
    op.drop_column("portfolio_proposals", "pending_source_key")
