"""Optional unique venture alias for slug-style lookups.

Revision ID: b10261009002
Revises: b10261009001
Create Date: 2026-10-09

Additive only: existing ventures keep a null alias; no identity is rewritten.
A unique index (not a table constraint) avoids a SQLite table rebuild.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b10261009002"
down_revision: str | Sequence[str] | None = "b10261009001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("ventures", sa.Column("alias", sa.String(length=64), nullable=True))
    op.create_index("venture_alias_unique", "ventures", ["alias"], unique=True)


def downgrade() -> None:
    op.drop_index("venture_alias_unique", table_name="ventures")
    op.drop_column("ventures", "alias")
