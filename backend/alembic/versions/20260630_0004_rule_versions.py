"""add rule versions

Revision ID: 20260630_0004
Revises: 20260630_0003
Create Date: 2026-06-30 00:04:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0004"
down_revision: str | None = "20260630_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rule_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("rule_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("rule_text", sa.Text(), nullable=False),
        sa.Column("condition_text", sa.Text(), nullable=True),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("source_chunk_ids", sa.Text(), nullable=False),
        sa.Column("change_reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rule_versions_created_at"), "rule_versions", ["created_at"])
    op.create_index(op.f("ix_rule_versions_created_by"), "rule_versions", ["created_by"])
    op.create_index(op.f("ix_rule_versions_meeting_id"), "rule_versions", ["meeting_id"])
    op.create_index(op.f("ix_rule_versions_project_id"), "rule_versions", ["project_id"])
    op.create_index(op.f("ix_rule_versions_rule_id"), "rule_versions", ["rule_id"])
    op.create_index(op.f("ix_rule_versions_status"), "rule_versions", ["status"])
    op.create_index(op.f("ix_rule_versions_tenant_id"), "rule_versions", ["tenant_id"])
    op.create_index(op.f("ix_rule_versions_version_number"), "rule_versions", ["version_number"])


def downgrade() -> None:
    op.drop_index(op.f("ix_rule_versions_version_number"), table_name="rule_versions")
    op.drop_index(op.f("ix_rule_versions_tenant_id"), table_name="rule_versions")
    op.drop_index(op.f("ix_rule_versions_status"), table_name="rule_versions")
    op.drop_index(op.f("ix_rule_versions_rule_id"), table_name="rule_versions")
    op.drop_index(op.f("ix_rule_versions_project_id"), table_name="rule_versions")
    op.drop_index(op.f("ix_rule_versions_meeting_id"), table_name="rule_versions")
    op.drop_index(op.f("ix_rule_versions_created_by"), table_name="rule_versions")
    op.drop_index(op.f("ix_rule_versions_created_at"), table_name="rule_versions")
    op.drop_table("rule_versions")
