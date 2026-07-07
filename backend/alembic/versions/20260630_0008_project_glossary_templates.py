"""add project glossary and templates

Revision ID: 20260630_0008
Revises: 20260630_0007
Create Date: 2026-06-30 00:08:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0008"
down_revision: str | None = "20260630_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_templates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("default_objective", sa.Text(), nullable=False),
        sa.Column("default_glossary_terms", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_project_templates"),
    )
    op.create_index(op.f("ix_project_templates_created_at"), "project_templates", ["created_at"])
    op.create_index(op.f("ix_project_templates_tenant_id"), "project_templates", ["tenant_id"])

    op.create_table(
        "project_glossary_terms",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("term", sa.String(length=160), nullable=False),
        sa.Column("definition", sa.Text(), nullable=False),
        sa.Column("aliases", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "term", name="uq_project_glossary_terms"),
    )
    op.create_index(op.f("ix_project_glossary_terms_created_at"), "project_glossary_terms", ["created_at"])
    op.create_index(op.f("ix_project_glossary_terms_project_id"), "project_glossary_terms", ["project_id"])
    op.create_index(op.f("ix_project_glossary_terms_tenant_id"), "project_glossary_terms", ["tenant_id"])
    op.create_index(op.f("ix_project_glossary_terms_term"), "project_glossary_terms", ["term"])


def downgrade() -> None:
    op.drop_index(op.f("ix_project_glossary_terms_term"), table_name="project_glossary_terms")
    op.drop_index(op.f("ix_project_glossary_terms_tenant_id"), table_name="project_glossary_terms")
    op.drop_index(op.f("ix_project_glossary_terms_project_id"), table_name="project_glossary_terms")
    op.drop_index(op.f("ix_project_glossary_terms_created_at"), table_name="project_glossary_terms")
    op.drop_table("project_glossary_terms")

    op.drop_index(op.f("ix_project_templates_tenant_id"), table_name="project_templates")
    op.drop_index(op.f("ix_project_templates_created_at"), table_name="project_templates")
    op.drop_table("project_templates")
