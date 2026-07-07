"""add semantic embeddings

Revision ID: 20260630_0003
Revises: 20260630_0002
Create Date: 2026-06-30 00:03:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0003"
down_revision: str | None = "20260630_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "semantic_embeddings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=True),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.String(length=80), nullable=False),
        sa.Column("embedding_dim", sa.Integer(), nullable=False),
        sa.Column("embedding_vector", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "source_type",
            "source_id",
            name="uq_semantic_embeddings_source",
        ),
    )
    op.create_index(op.f("ix_semantic_embeddings_content_hash"), "semantic_embeddings", ["content_hash"])
    op.create_index(op.f("ix_semantic_embeddings_created_at"), "semantic_embeddings", ["created_at"])
    op.create_index(op.f("ix_semantic_embeddings_meeting_id"), "semantic_embeddings", ["meeting_id"])
    op.create_index(op.f("ix_semantic_embeddings_project_id"), "semantic_embeddings", ["project_id"])
    op.create_index(op.f("ix_semantic_embeddings_source_id"), "semantic_embeddings", ["source_id"])
    op.create_index(op.f("ix_semantic_embeddings_source_type"), "semantic_embeddings", ["source_type"])
    op.create_index(op.f("ix_semantic_embeddings_tenant_id"), "semantic_embeddings", ["tenant_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_semantic_embeddings_tenant_id"), table_name="semantic_embeddings")
    op.drop_index(op.f("ix_semantic_embeddings_source_type"), table_name="semantic_embeddings")
    op.drop_index(op.f("ix_semantic_embeddings_source_id"), table_name="semantic_embeddings")
    op.drop_index(op.f("ix_semantic_embeddings_project_id"), table_name="semantic_embeddings")
    op.drop_index(op.f("ix_semantic_embeddings_meeting_id"), table_name="semantic_embeddings")
    op.drop_index(op.f("ix_semantic_embeddings_created_at"), table_name="semantic_embeddings")
    op.drop_index(op.f("ix_semantic_embeddings_content_hash"), table_name="semantic_embeddings")
    op.drop_table("semantic_embeddings")
