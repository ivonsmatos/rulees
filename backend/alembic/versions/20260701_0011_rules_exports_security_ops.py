"""add rule lifecycle and document export jobs

Revision ID: 20260701_0011
Revises: 20260701_0010
Create Date: 2026-07-01 01:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0011"
down_revision: str | None = "20260701_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("business_rules", sa.Column("quality_details", sa.Text(), nullable=False, server_default="{}"))
    op.add_column("business_rules", sa.Column("replaced_by_rule_id", sa.String(length=36), nullable=True))
    op.add_column("business_rules", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("business_rules", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_business_rules_replaced_by_rule_id"), "business_rules", ["replaced_by_rule_id"])

    op.create_table(
        "rule_lifecycle_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("rule_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=True),
        sa.Column("details", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rule_lifecycle_events_created_at"), "rule_lifecycle_events", ["created_at"])
    op.create_index(op.f("ix_rule_lifecycle_events_event_type"), "rule_lifecycle_events", ["event_type"])
    op.create_index(op.f("ix_rule_lifecycle_events_meeting_id"), "rule_lifecycle_events", ["meeting_id"])
    op.create_index(op.f("ix_rule_lifecycle_events_project_id"), "rule_lifecycle_events", ["project_id"])
    op.create_index(op.f("ix_rule_lifecycle_events_rule_id"), "rule_lifecycle_events", ["rule_id"])
    op.create_index(op.f("ix_rule_lifecycle_events_tenant_id"), "rule_lifecycle_events", ["tenant_id"])
    op.create_index(op.f("ix_rule_lifecycle_events_user_id"), "rule_lifecycle_events", ["user_id"])

    op.create_table(
        "document_export_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("format", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("result_url", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_export_jobs_created_at"), "document_export_jobs", ["created_at"])
    op.create_index(op.f("ix_document_export_jobs_created_by"), "document_export_jobs", ["created_by"])
    op.create_index(op.f("ix_document_export_jobs_document_id"), "document_export_jobs", ["document_id"])
    op.create_index(op.f("ix_document_export_jobs_format"), "document_export_jobs", ["format"])
    op.create_index(op.f("ix_document_export_jobs_meeting_id"), "document_export_jobs", ["meeting_id"])
    op.create_index(op.f("ix_document_export_jobs_project_id"), "document_export_jobs", ["project_id"])
    op.create_index(op.f("ix_document_export_jobs_status"), "document_export_jobs", ["status"])
    op.create_index(op.f("ix_document_export_jobs_tenant_id"), "document_export_jobs", ["tenant_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_document_export_jobs_tenant_id"), table_name="document_export_jobs")
    op.drop_index(op.f("ix_document_export_jobs_status"), table_name="document_export_jobs")
    op.drop_index(op.f("ix_document_export_jobs_project_id"), table_name="document_export_jobs")
    op.drop_index(op.f("ix_document_export_jobs_meeting_id"), table_name="document_export_jobs")
    op.drop_index(op.f("ix_document_export_jobs_format"), table_name="document_export_jobs")
    op.drop_index(op.f("ix_document_export_jobs_document_id"), table_name="document_export_jobs")
    op.drop_index(op.f("ix_document_export_jobs_created_by"), table_name="document_export_jobs")
    op.drop_index(op.f("ix_document_export_jobs_created_at"), table_name="document_export_jobs")
    op.drop_table("document_export_jobs")

    op.drop_index(op.f("ix_rule_lifecycle_events_user_id"), table_name="rule_lifecycle_events")
    op.drop_index(op.f("ix_rule_lifecycle_events_tenant_id"), table_name="rule_lifecycle_events")
    op.drop_index(op.f("ix_rule_lifecycle_events_rule_id"), table_name="rule_lifecycle_events")
    op.drop_index(op.f("ix_rule_lifecycle_events_project_id"), table_name="rule_lifecycle_events")
    op.drop_index(op.f("ix_rule_lifecycle_events_meeting_id"), table_name="rule_lifecycle_events")
    op.drop_index(op.f("ix_rule_lifecycle_events_event_type"), table_name="rule_lifecycle_events")
    op.drop_index(op.f("ix_rule_lifecycle_events_created_at"), table_name="rule_lifecycle_events")
    op.drop_table("rule_lifecycle_events")

    op.drop_index(op.f("ix_business_rules_replaced_by_rule_id"), table_name="business_rules")
    op.drop_column("business_rules", "archived_at")
    op.drop_column("business_rules", "revoked_at")
    op.drop_column("business_rules", "replaced_by_rule_id")
    op.drop_column("business_rules", "quality_details")
