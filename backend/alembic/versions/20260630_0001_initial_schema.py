"""initial schema

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30 00:01:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_slug"), "tenants", ["slug"], unique=True)

    op.create_table(
        "tenant_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_tenant_members"),
    )
    op.create_index(op.f("ix_tenant_members_tenant_id"), "tenant_members", ["tenant_id"])
    op.create_index(op.f("ix_tenant_members_user_id"), "tenant_members", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"])
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"])
    op.create_index(op.f("ix_audit_logs_tenant_id"), "audit_logs", ["tenant_id"])
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"])

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_status"), "projects", ["status"])
    op.create_index(op.f("ix_projects_tenant_id"), "projects", ["tenant_id"])

    op.create_table(
        "meetings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meetings_project_id"), "meetings", ["project_id"])
    op.create_index(op.f("ix_meetings_status"), "meetings", ["status"])
    op.create_index(op.f("ix_meetings_tenant_id"), "meetings", ["tenant_id"])

    op.create_table(
        "consent_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("text_version", sa.String(length=40), nullable=False),
        sa.Column("accepted_scope", sa.Text(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_consent_records_meeting_id"), "consent_records", ["meeting_id"])
    op.create_index(op.f("ix_consent_records_tenant_id"), "consent_records", ["tenant_id"])
    op.create_index(op.f("ix_consent_records_user_id"), "consent_records", ["user_id"])

    op.create_table(
        "transcript_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False),
        sa.Column("start_time", sa.Float(), nullable=True),
        sa.Column("end_time", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transcript_chunks_created_at"), "transcript_chunks", ["created_at"])
    op.create_index(op.f("ix_transcript_chunks_meeting_id"), "transcript_chunks", ["meeting_id"])
    op.create_index(op.f("ix_transcript_chunks_project_id"), "transcript_chunks", ["project_id"])
    op.create_index(op.f("ix_transcript_chunks_tenant_id"), "transcript_chunks", ["tenant_id"])

    op.create_table(
        "business_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("rule_text", sa.Text(), nullable=False),
        sa.Column("condition_text", sa.Text(), nullable=True),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("quality_score", sa.Integer(), nullable=False),
        sa.Column("source_chunk_ids", sa.Text(), nullable=False),
        sa.Column("approved_by", sa.String(length=36), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_business_rules_code"), "business_rules", ["code"])
    op.create_index(op.f("ix_business_rules_created_at"), "business_rules", ["created_at"])
    op.create_index(op.f("ix_business_rules_meeting_id"), "business_rules", ["meeting_id"])
    op.create_index(op.f("ix_business_rules_project_id"), "business_rules", ["project_id"])
    op.create_index(op.f("ix_business_rules_status"), "business_rules", ["status"])
    op.create_index(op.f("ix_business_rules_tenant_id"), "business_rules", ["tenant_id"])

    op.create_table(
        "open_questions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("gap_type", sa.String(length=80), nullable=False),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("source_chunk_ids", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_open_questions_created_at"), "open_questions", ["created_at"])
    op.create_index(op.f("ix_open_questions_meeting_id"), "open_questions", ["meeting_id"])
    op.create_index(op.f("ix_open_questions_project_id"), "open_questions", ["project_id"])
    op.create_index(op.f("ix_open_questions_status"), "open_questions", ["status"])
    op.create_index(op.f("ix_open_questions_tenant_id"), "open_questions", ["tenant_id"])

    op.create_table(
        "decisions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("decision_text", sa.Text(), nullable=False),
        sa.Column("decision_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("responsible_area", sa.String(length=120), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("source_chunk_ids", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decisions_created_at"), "decisions", ["created_at"])
    op.create_index(op.f("ix_decisions_meeting_id"), "decisions", ["meeting_id"])
    op.create_index(op.f("ix_decisions_project_id"), "decisions", ["project_id"])
    op.create_index(op.f("ix_decisions_status"), "decisions", ["status"])
    op.create_index(op.f("ix_decisions_tenant_id"), "decisions", ["tenant_id"])

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_created_at"), "documents", ["created_at"])
    op.create_index(op.f("ix_documents_meeting_id"), "documents", ["meeting_id"])
    op.create_index(op.f("ix_documents_project_id"), "documents", ["project_id"])
    op.create_index(op.f("ix_documents_tenant_id"), "documents", ["tenant_id"])

    op.create_table(
        "usage_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("meeting_id", sa.String(length=36), nullable=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usage_events_created_at"), "usage_events", ["created_at"])
    op.create_index(op.f("ix_usage_events_event_type"), "usage_events", ["event_type"])
    op.create_index(op.f("ix_usage_events_meeting_id"), "usage_events", ["meeting_id"])
    op.create_index(op.f("ix_usage_events_project_id"), "usage_events", ["project_id"])
    op.create_index(op.f("ix_usage_events_tenant_id"), "usage_events", ["tenant_id"])
    op.create_index(op.f("ix_usage_events_user_id"), "usage_events", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_usage_events_user_id"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_tenant_id"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_project_id"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_meeting_id"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_event_type"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_created_at"), table_name="usage_events")
    op.drop_table("usage_events")

    op.drop_index(op.f("ix_documents_tenant_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_project_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_meeting_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_created_at"), table_name="documents")
    op.drop_table("documents")

    op.drop_index(op.f("ix_decisions_tenant_id"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_status"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_project_id"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_meeting_id"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_created_at"), table_name="decisions")
    op.drop_table("decisions")

    op.drop_index(op.f("ix_open_questions_tenant_id"), table_name="open_questions")
    op.drop_index(op.f("ix_open_questions_status"), table_name="open_questions")
    op.drop_index(op.f("ix_open_questions_project_id"), table_name="open_questions")
    op.drop_index(op.f("ix_open_questions_meeting_id"), table_name="open_questions")
    op.drop_index(op.f("ix_open_questions_created_at"), table_name="open_questions")
    op.drop_table("open_questions")

    op.drop_index(op.f("ix_business_rules_tenant_id"), table_name="business_rules")
    op.drop_index(op.f("ix_business_rules_status"), table_name="business_rules")
    op.drop_index(op.f("ix_business_rules_project_id"), table_name="business_rules")
    op.drop_index(op.f("ix_business_rules_meeting_id"), table_name="business_rules")
    op.drop_index(op.f("ix_business_rules_created_at"), table_name="business_rules")
    op.drop_index(op.f("ix_business_rules_code"), table_name="business_rules")
    op.drop_table("business_rules")

    op.drop_index(op.f("ix_transcript_chunks_tenant_id"), table_name="transcript_chunks")
    op.drop_index(op.f("ix_transcript_chunks_project_id"), table_name="transcript_chunks")
    op.drop_index(op.f("ix_transcript_chunks_meeting_id"), table_name="transcript_chunks")
    op.drop_index(op.f("ix_transcript_chunks_created_at"), table_name="transcript_chunks")
    op.drop_table("transcript_chunks")

    op.drop_index(op.f("ix_consent_records_user_id"), table_name="consent_records")
    op.drop_index(op.f("ix_consent_records_tenant_id"), table_name="consent_records")
    op.drop_index(op.f("ix_consent_records_meeting_id"), table_name="consent_records")
    op.drop_table("consent_records")

    op.drop_index(op.f("ix_meetings_tenant_id"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_status"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_project_id"), table_name="meetings")
    op.drop_table("meetings")

    op.drop_index(op.f("ix_projects_tenant_id"), table_name="projects")
    op.drop_index(op.f("ix_projects_status"), table_name="projects")
    op.drop_table("projects")

    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_tenant_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_tenant_members_user_id"), table_name="tenant_members")
    op.drop_index(op.f("ix_tenant_members_tenant_id"), table_name="tenant_members")
    op.drop_table("tenant_members")

    op.drop_index(op.f("ix_tenants_slug"), table_name="tenants")
    op.drop_table("tenants")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
