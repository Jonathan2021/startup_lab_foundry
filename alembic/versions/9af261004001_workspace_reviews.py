"""Append-only workspace reviews; no campaign data or lifecycle rewrites."""
from alembic import op
import sqlalchemy as sa

revision = '9af261004001'
down_revision = '7ce261002001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'workspace_reviews',
        sa.Column('id',sa.String(36),nullable=False),
        sa.Column('workspace_id',sa.String(36),nullable=False),
        sa.Column('revision',sa.Integer(),nullable=False),
        sa.Column('investigation_stage',sa.Enum('intake','triage','comparison',
            'problem_validation','solution_validation','business_validation',
            name='investigation_stage',native_enum=False,create_constraint=True),nullable=False),
        sa.Column('product_maturity',sa.Enum('unknown','concept','prototype','mvp','pilot','operating',
            name='product_maturity',native_enum=False,create_constraint=True),nullable=False),
        sa.Column('disposition',sa.Enum('pursue','hold','dropped','internal_only','use_existing',
            name='review_disposition',native_enum=False,create_constraint=True),nullable=False),
        sa.Column('next_action',sa.Text(),nullable=False),
        sa.Column('next_work_item_id',sa.String(36)),
        sa.Column('reason',sa.Text(),nullable=False),
        sa.Column('author',sa.String(200),nullable=False),
        sa.Column('reviewed_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('source_artifact_id',sa.String(36)),
        sa.Column('decision_id',sa.String(36)),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'],['workspaces.id']),
        sa.ForeignKeyConstraint(['next_work_item_id'],['work_items.id']),
        sa.ForeignKeyConstraint(['source_artifact_id'],['artifacts.id']),
        sa.ForeignKeyConstraint(['decision_id'],['decisions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id','revision',name='workspace_review_revision'),
        sa.CheckConstraint('revision >= 1',name='review_revision_positive'),
    )
    op.create_index('ix_workspace_reviews_workspace_id','workspace_reviews',['workspace_id'])


def downgrade() -> None:
    op.drop_index('ix_workspace_reviews_workspace_id',table_name='workspace_reviews')
    op.drop_table('workspace_reviews')
