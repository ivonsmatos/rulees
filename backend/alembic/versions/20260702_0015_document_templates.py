"""document_templates and document_template_sections

Revision ID: 20260702_0015
Revises: 20260702_0014
Create Date: 2026-07-02 01:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260702_0015"
down_revision: str | None = "20260702_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_templates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.String(80), nullable=False, server_default="general", index=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "document_template_sections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("template_id", sa.String(36), nullable=False, index=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("section_key", sa.String(80), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("body_template", sa.Text(), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("required", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Seed: template padrão "Documento Funcional"
    op.execute("""
        INSERT INTO document_templates
            (id, tenant_id, name, description, category, is_default, created_by, created_at, updated_at)
        VALUES
            ('dt-system-001', '__system__', 'Documento Funcional Padrão',
             'Template padrão com seções de resumo, regras, questões e decisões.',
             'general', TRUE, '__system__', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """)
    op.execute("""
        INSERT INTO document_template_sections
            (id, template_id, tenant_id, section_key, title, body_template, sort_order, required, created_at)
        VALUES
            ('dts-001', 'dt-system-001', '__system__', 'summary', 'Resumo Executivo',
             '## Objetivo da Reunião\n\n{{summary}}\n', 0, TRUE, CURRENT_TIMESTAMP),
            ('dts-002', 'dt-system-001', '__system__', 'rules', 'Regras de Negócio',
             '## Regras Aprovadas\n\n{{rules}}\n', 1, TRUE, CURRENT_TIMESTAMP),
            ('dts-003', 'dt-system-001', '__system__', 'decisions', 'Decisões',
             '## Decisões Registradas\n\n{{decisions}}\n', 2, FALSE, CURRENT_TIMESTAMP),
            ('dts-004', 'dt-system-001', '__system__', 'questions', 'Questões Abertas',
             '## Dúvidas e Lacunas\n\n{{questions}}\n', 3, FALSE, CURRENT_TIMESTAMP),
            ('dts-005', 'dt-system-001', '__system__', 'glossary', 'Glossário',
             '## Glossário do Projeto\n\n{{glossary}}\n', 4, FALSE, CURRENT_TIMESTAMP)
    """)


def downgrade() -> None:
    op.drop_table("document_template_sections")
    op.drop_table("document_templates")
