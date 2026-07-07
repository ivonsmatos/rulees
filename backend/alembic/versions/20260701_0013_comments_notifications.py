"""add comments and notifications

Revision ID: 20260701_0013
Revises: 20260701_0012
Create Date: 2026-07-01 02:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0013"
down_revision: str | None = "20260701_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("author_id", sa.String(length=36), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_author_id"), "comments", ["author_id"])
    op.create_index(op.f("ix_comments_created_at"), "comments", ["created_at"])
    op.create_index(op.f("ix_comments_project_id"), "comments", ["project_id"])
    op.create_index(op.f("ix_comments_resource_id"), "comments", ["resource_id"])
    op.create_index(op.f("ix_comments_resource_type"), "comments", ["resource_type"])
    op.create_index(op.f("ix_comments_status"), "comments", ["status"])
    op.create_index(op.f("ix_comments_tenant_id"), "comments", ["tenant_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=True),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_created_at"), "notifications", ["created_at"])
    op.create_index(op.f("ix_notifications_resource_id"), "notifications", ["resource_id"])
    op.create_index(op.f("ix_notifications_resource_type"), "notifications", ["resource_type"])
    op.create_index(op.f("ix_notifications_tenant_id"), "notifications", ["tenant_id"])
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_tenant_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_resource_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_resource_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_comments_tenant_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_status"), table_name="comments")
    op.drop_index(op.f("ix_comments_resource_type"), table_name="comments")
    op.drop_index(op.f("ix_comments_resource_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_project_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_created_at"), table_name="comments")
    op.drop_index(op.f("ix_comments_author_id"), table_name="comments")
    op.drop_table("comments")
