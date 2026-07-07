"""add billing profiles

Revision ID: 20260630_0006
Revises: 20260630_0005
Create Date: 2026-06-30 00:06:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0006"
down_revision: str | None = "20260630_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenant_billing_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("plan_name", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenant_billing_profiles_created_at"), "tenant_billing_profiles", ["created_at"])
    op.create_index(op.f("ix_tenant_billing_profiles_plan_name"), "tenant_billing_profiles", ["plan_name"])
    op.create_index(op.f("ix_tenant_billing_profiles_status"), "tenant_billing_profiles", ["status"])
    op.create_index(op.f("ix_tenant_billing_profiles_tenant_id"), "tenant_billing_profiles", ["tenant_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_tenant_billing_profiles_tenant_id"), table_name="tenant_billing_profiles")
    op.drop_index(op.f("ix_tenant_billing_profiles_status"), table_name="tenant_billing_profiles")
    op.drop_index(op.f("ix_tenant_billing_profiles_plan_name"), table_name="tenant_billing_profiles")
    op.drop_index(op.f("ix_tenant_billing_profiles_created_at"), table_name="tenant_billing_profiles")
    op.drop_table("tenant_billing_profiles")
