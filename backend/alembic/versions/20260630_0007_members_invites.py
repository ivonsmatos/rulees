"""add tenant invites and project members

Revision ID: 20260630_0007
Revises: 20260630_0006
Create Date: 2026-06-30 00:07:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0007"
down_revision: str | None = "20260630_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenant_invites",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("invited_by", sa.String(length=36), nullable=False),
        sa.Column("accepted_by", sa.String(length=36), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_tenant_invites"),
    )
    op.create_index(op.f("ix_tenant_invites_accepted_by"), "tenant_invites", ["accepted_by"])
    op.create_index(op.f("ix_tenant_invites_created_at"), "tenant_invites", ["created_at"])
    op.create_index(op.f("ix_tenant_invites_email"), "tenant_invites", ["email"])
    op.create_index(op.f("ix_tenant_invites_invited_by"), "tenant_invites", ["invited_by"])
    op.create_index(op.f("ix_tenant_invites_status"), "tenant_invites", ["status"])
    op.create_index(op.f("ix_tenant_invites_tenant_id"), "tenant_invites", ["tenant_id"])

    op.create_table(
        "project_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_members"),
    )
    op.create_index(op.f("ix_project_members_created_at"), "project_members", ["created_at"])
    op.create_index(op.f("ix_project_members_project_id"), "project_members", ["project_id"])
    op.create_index(op.f("ix_project_members_role"), "project_members", ["role"])
    op.create_index(op.f("ix_project_members_tenant_id"), "project_members", ["tenant_id"])
    op.create_index(op.f("ix_project_members_user_id"), "project_members", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_project_members_user_id"), table_name="project_members")
    op.drop_index(op.f("ix_project_members_tenant_id"), table_name="project_members")
    op.drop_index(op.f("ix_project_members_role"), table_name="project_members")
    op.drop_index(op.f("ix_project_members_project_id"), table_name="project_members")
    op.drop_index(op.f("ix_project_members_created_at"), table_name="project_members")
    op.drop_table("project_members")

    op.drop_index(op.f("ix_tenant_invites_tenant_id"), table_name="tenant_invites")
    op.drop_index(op.f("ix_tenant_invites_status"), table_name="tenant_invites")
    op.drop_index(op.f("ix_tenant_invites_invited_by"), table_name="tenant_invites")
    op.drop_index(op.f("ix_tenant_invites_email"), table_name="tenant_invites")
    op.drop_index(op.f("ix_tenant_invites_created_at"), table_name="tenant_invites")
    op.drop_index(op.f("ix_tenant_invites_accepted_by"), table_name="tenant_invites")
    op.drop_table("tenant_invites")
