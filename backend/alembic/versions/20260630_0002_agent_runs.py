"""add agent runs

Revision ID: 20260630_0002
Revises: 20260630_0001
Create Date: 2026-06-30 00:02:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0002"
down_revision: str | None = "20260630_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=80), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("agent_name", sa.String(length=80), nullable=False),
        sa.Column("agent_role", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("model_name", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("input_reference", sa.Text(), nullable=False),
        sa.Column("output", sa.Text(), nullable=False),
        sa.Column("warnings", sa.Text(), nullable=False),
        sa.Column("errors", sa.Text(), nullable=False),
        sa.Column("run_metadata", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_runs_agent_name"), "agent_runs", ["agent_name"])
    op.create_index(op.f("ix_agent_runs_agent_role"), "agent_runs", ["agent_role"])
    op.create_index(op.f("ix_agent_runs_created_at"), "agent_runs", ["created_at"])
    op.create_index(op.f("ix_agent_runs_meeting_id"), "agent_runs", ["meeting_id"])
    op.create_index(op.f("ix_agent_runs_project_id"), "agent_runs", ["project_id"])
    op.create_index(op.f("ix_agent_runs_run_id"), "agent_runs", ["run_id"], unique=True)
    op.create_index(op.f("ix_agent_runs_status"), "agent_runs", ["status"])
    op.create_index(op.f("ix_agent_runs_tenant_id"), "agent_runs", ["tenant_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_runs_tenant_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_status"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_run_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_project_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_meeting_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_created_at"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_agent_role"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_agent_name"), table_name="agent_runs")
    op.drop_table("agent_runs")
