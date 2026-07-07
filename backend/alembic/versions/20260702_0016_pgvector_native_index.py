"""add native pgvector column and index for semantic_embeddings

Only applied on PostgreSQL (production/staging). No-op on SQLite (tests),
which keeps using the JSON text fallback column `embedding_vector`.

Revision ID: 20260702_0016
Revises: 20260702_0015
Create Date: 2026-07-02 02:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260702_0016"
down_revision: str | None = "20260702_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Dimensão fixa do índice nativo — deve casar com NATIVE_INDEX_DIMENSION em
# app/modules/rag/service.py (embedding determinístico padrão = 64).
NATIVE_DIM = 64


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(f"ALTER TABLE semantic_embeddings ADD COLUMN IF NOT EXISTS embedding_native vector({NATIVE_DIM})")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_semantic_embeddings_native "
        "ON semantic_embeddings USING ivfflat (embedding_native vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("DROP INDEX IF EXISTS ix_semantic_embeddings_native")
    op.execute("ALTER TABLE semantic_embeddings DROP COLUMN IF EXISTS embedding_native")
