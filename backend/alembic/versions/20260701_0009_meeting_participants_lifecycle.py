"""add meeting participants lifecycle and consent revocation

Revision ID: 20260701_0009
Revises: 20260630_0008
Create Date: 2026-07-01 00:09:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0009"
down_revision: str | None = "20260630_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("consent_records", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("consent_records", sa.Column("revoked_by", sa.String(length=36), nullable=True))
    op.add_column("consent_records", sa.Column("revoke_reason", sa.Text(), nullable=True))
    op.create_index(op.f("ix_consent_records_revoked_by"), "consent_records", ["revoked_by"])

    op.create_table(
        "meeting_participants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("consent_required", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meeting_participants_created_at"), "meeting_participants", ["created_at"])
    op.create_index(op.f("ix_meeting_participants_meeting_id"), "meeting_participants", ["meeting_id"])
    op.create_index(op.f("ix_meeting_participants_project_id"), "meeting_participants", ["project_id"])
    op.create_index(op.f("ix_meeting_participants_role"), "meeting_participants", ["role"])
    op.create_index(op.f("ix_meeting_participants_tenant_id"), "meeting_participants", ["tenant_id"])
    op.create_index(op.f("ix_meeting_participants_user_id"), "meeting_participants", ["user_id"])

    op.create_table(
        "meeting_lifecycle_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=True),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meeting_lifecycle_events_created_at"), "meeting_lifecycle_events", ["created_at"])
    op.create_index(op.f("ix_meeting_lifecycle_events_event_type"), "meeting_lifecycle_events", ["event_type"])
    op.create_index(op.f("ix_meeting_lifecycle_events_meeting_id"), "meeting_lifecycle_events", ["meeting_id"])
    op.create_index(op.f("ix_meeting_lifecycle_events_project_id"), "meeting_lifecycle_events", ["project_id"])
    op.create_index(op.f("ix_meeting_lifecycle_events_tenant_id"), "meeting_lifecycle_events", ["tenant_id"])
    op.create_index(op.f("ix_meeting_lifecycle_events_user_id"), "meeting_lifecycle_events", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_meeting_lifecycle_events_user_id"), table_name="meeting_lifecycle_events")
    op.drop_index(op.f("ix_meeting_lifecycle_events_tenant_id"), table_name="meeting_lifecycle_events")
    op.drop_index(op.f("ix_meeting_lifecycle_events_project_id"), table_name="meeting_lifecycle_events")
    op.drop_index(op.f("ix_meeting_lifecycle_events_meeting_id"), table_name="meeting_lifecycle_events")
    op.drop_index(op.f("ix_meeting_lifecycle_events_event_type"), table_name="meeting_lifecycle_events")
    op.drop_index(op.f("ix_meeting_lifecycle_events_created_at"), table_name="meeting_lifecycle_events")
    op.drop_table("meeting_lifecycle_events")

    op.drop_index(op.f("ix_meeting_participants_user_id"), table_name="meeting_participants")
    op.drop_index(op.f("ix_meeting_participants_tenant_id"), table_name="meeting_participants")
    op.drop_index(op.f("ix_meeting_participants_role"), table_name="meeting_participants")
    op.drop_index(op.f("ix_meeting_participants_project_id"), table_name="meeting_participants")
    op.drop_index(op.f("ix_meeting_participants_meeting_id"), table_name="meeting_participants")
    op.drop_index(op.f("ix_meeting_participants_created_at"), table_name="meeting_participants")
    op.drop_table("meeting_participants")

    op.drop_index(op.f("ix_consent_records_revoked_by"), table_name="consent_records")
    op.drop_column("consent_records", "revoke_reason")
    op.drop_column("consent_records", "revoked_by")
    op.drop_column("consent_records", "revoked_at")
