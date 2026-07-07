"""add transcription metadata

Revision ID: 20260701_0010
Revises: 20260701_0009
Create Date: 2026-07-01 00:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0010"
down_revision: str | None = "20260701_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("transcript_chunks", sa.Column("speaker_label", sa.String(length=80), nullable=True))
    op.add_column("transcript_chunks", sa.Column("language", sa.String(length=20), nullable=True))
    op.add_column("transcript_chunks", sa.Column("confidence_score", sa.Float(), nullable=True))
    op.add_column("transcript_chunks", sa.Column("sequence", sa.Integer(), nullable=True))
    op.add_column("transcript_chunks", sa.Column("provider_metadata", sa.Text(), nullable=False, server_default="{}"))
    op.create_index(op.f("ix_transcript_chunks_sequence"), "transcript_chunks", ["sequence"])
    op.create_index(op.f("ix_transcript_chunks_speaker_label"), "transcript_chunks", ["speaker_label"])


def downgrade() -> None:
    op.drop_index(op.f("ix_transcript_chunks_speaker_label"), table_name="transcript_chunks")
    op.drop_index(op.f("ix_transcript_chunks_sequence"), table_name="transcript_chunks")
    op.drop_column("transcript_chunks", "provider_metadata")
    op.drop_column("transcript_chunks", "sequence")
    op.drop_column("transcript_chunks", "confidence_score")
    op.drop_column("transcript_chunks", "language")
    op.drop_column("transcript_chunks", "speaker_label")
