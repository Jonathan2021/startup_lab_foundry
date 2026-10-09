"""Additive schema-only human requests; bootstrap is explicit."""

from alembic import op
import sqlalchemy as sa

revision = "b10261005001"
down_revision = "9af261004001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "human_requests",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("definition_revision", sa.Integer(), nullable=False),
        sa.Column("definition_artifact_id", sa.String(length=36), nullable=False),
        sa.Column("response_artifact_id", sa.String(length=36), nullable=True),
        sa.Column("review_artifact_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("file_path", sa.String(length=300), nullable=True),
        sa.Column("source_diagnostics", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "status IN ('waiting_for_answer','ready_for_review','reviewing','needs_clarification','resolved','deferred')",
            name=op.f("ck_human_requests_request_status"),
        ),
        sa.ForeignKeyConstraint(
            ["definition_artifact_id"],
            ["artifacts.id"],
            name=op.f("fk_human_requests_definition_artifact_id_artifacts"),
        ),
        sa.ForeignKeyConstraint(
            ["response_artifact_id"],
            ["artifacts.id"],
            name=op.f("fk_human_requests_response_artifact_id_artifacts"),
        ),
        sa.ForeignKeyConstraint(
            ["review_artifact_id"],
            ["artifacts.id"],
            name=op.f("fk_human_requests_review_artifact_id_artifacts"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_human_requests_workspace_id_workspaces"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_human_requests")),
    )
    op.create_index(
        op.f("ix_human_requests_status"), "human_requests", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_human_requests_workspace_id"),
        "human_requests",
        ["workspace_id"],
        unique=False,
    )
    op.create_table(
        "human_request_targets",
        sa.Column("request_id", sa.String(length=36), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("work_item_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["human_requests.id"],
            name=op.f("fk_human_request_targets_request_id_human_requests"),
        ),
        sa.ForeignKeyConstraint(
            ["work_item_id"],
            ["work_items.id"],
            name=op.f("fk_human_request_targets_work_item_id_work_items"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_human_request_targets_workspace_id_workspaces"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_human_request_targets")),
        sa.UniqueConstraint("request_id", "workspace_id", name="request_target_unique"),
    )
    op.create_index(
        op.f("ix_human_request_targets_request_id"),
        "human_request_targets",
        ["request_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_human_request_targets_workspace_id"),
        "human_request_targets",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_human_request_targets_workspace_id"),
        table_name="human_request_targets",
    )
    op.drop_index(
        op.f("ix_human_request_targets_request_id"), table_name="human_request_targets"
    )
    op.drop_table("human_request_targets")
    op.drop_index(op.f("ix_human_requests_workspace_id"), table_name="human_requests")
    op.drop_index(op.f("ix_human_requests_status"), table_name="human_requests")
    op.drop_table("human_requests")
