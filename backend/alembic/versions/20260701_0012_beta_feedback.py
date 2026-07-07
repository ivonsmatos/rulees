"""add beta feedback

Revision ID: 20260701_0012
Revises: 20260701_0011
Create Date: 2026-07-01 01:40:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0012"
down_revision: str | None = "20260701_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "beta_feedback",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_beta_feedback_category"), "beta_feedback", ["category"])
    op.create_index(op.f("ix_beta_feedback_created_at"), "beta_feedback", ["created_at"])
    op.create_index(op.f("ix_beta_feedback_project_id"), "beta_feedback", ["project_id"])
    op.create_index(op.f("ix_beta_feedback_tenant_id"), "beta_feedback", ["tenant_id"])
    op.create_index(op.f("ix_beta_feedback_user_id"), "beta_feedback", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_beta_feedback_user_id"), table_name="beta_feedback")
    op.drop_index(op.f("ix_beta_feedback_tenant_id"), table_name="beta_feedback")
    op.drop_index(op.f("ix_beta_feedback_project_id"), table_name="beta_feedback")
    op.drop_index(op.f("ix_beta_feedback_created_at"), table_name="beta_feedback")
    op.drop_index(op.f("ix_beta_feedback_category"), table_name="beta_feedback")
    op.drop_table("beta_feedback")
