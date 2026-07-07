"""add document sections and versions

Revision ID: 20260630_0005
Revises: 20260630_0004
Create Date: 2026-06-30 00:05:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0005"
down_revision: str | None = "20260630_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_sections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("section_key", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_sections_created_at"), "document_sections", ["created_at"])
    op.create_index(op.f("ix_document_sections_document_id"), "document_sections", ["document_id"])
    op.create_index(op.f("ix_document_sections_section_key"), "document_sections", ["section_key"])
    op.create_index(op.f("ix_document_sections_tenant_id"), "document_sections", ["tenant_id"])

    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("change_reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_versions_created_at"), "document_versions", ["created_at"])
    op.create_index(op.f("ix_document_versions_created_by"), "document_versions", ["created_by"])
    op.create_index(op.f("ix_document_versions_document_id"), "document_versions", ["document_id"])
    op.create_index(op.f("ix_document_versions_meeting_id"), "document_versions", ["meeting_id"])
    op.create_index(op.f("ix_document_versions_project_id"), "document_versions", ["project_id"])
    op.create_index(op.f("ix_document_versions_status"), "document_versions", ["status"])
    op.create_index(op.f("ix_document_versions_tenant_id"), "document_versions", ["tenant_id"])
    op.create_index(op.f("ix_document_versions_version_number"), "document_versions", ["version_number"])


def downgrade() -> None:
    op.drop_index(op.f("ix_document_versions_version_number"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_tenant_id"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_status"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_project_id"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_meeting_id"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_document_id"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_created_by"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_created_at"), table_name="document_versions")
    op.drop_table("document_versions")

    op.drop_index(op.f("ix_document_sections_tenant_id"), table_name="document_sections")
    op.drop_index(op.f("ix_document_sections_section_key"), table_name="document_sections")
    op.drop_index(op.f("ix_document_sections_document_id"), table_name="document_sections")
    op.drop_index(op.f("ix_document_sections_created_at"), table_name="document_sections")
    op.drop_table("document_sections")
