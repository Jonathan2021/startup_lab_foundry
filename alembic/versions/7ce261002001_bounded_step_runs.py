"""Add durable bounded-step runs without altering existing venture records."""
from alembic import op
import sqlalchemy as sa

revision = '7ce261002001'
down_revision = '42d765ac6946'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'step_runs',
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('work_item_id', sa.String(36), nullable=False),
        sa.Column('request_key', sa.String(160), nullable=False),
        sa.Column('kind', sa.String(80), nullable=False),
        sa.Column('runner', sa.String(120), nullable=False),
        sa.Column('runner_version', sa.String(100), nullable=False),
        sa.Column('status', sa.Enum('running', 'succeeded', 'blocked', 'failed',
                                   name='step_status', native_enum=False,
                                   create_constraint=True), nullable=False),
        sa.Column('input_json', sa.JSON(), nullable=False),
        sa.Column('input_digest', sa.String(64), nullable=False),
        sa.Column('output_json', sa.JSON(), nullable=False),
        sa.Column('error_summary', sa.Text()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'],
                                name='fk_step_runs_workspace_id_workspaces'),
        sa.ForeignKeyConstraint(['work_item_id'], ['work_items.id'],
                                name='fk_step_runs_work_item_id_work_items'),
        sa.PrimaryKeyConstraint('id', name='pk_step_runs'),
        sa.UniqueConstraint('request_key', name='uq_step_runs_request_key'),
        sa.UniqueConstraint('work_item_id', name='uq_step_runs_work_item_id'),
    )
    op.create_index('ix_step_runs_workspace_id', 'step_runs', ['workspace_id'])


def downgrade() -> None:
    op.drop_index('ix_step_runs_workspace_id', table_name='step_runs')
    op.drop_table('step_runs')
