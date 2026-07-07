from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)
    project_id: Mapped[str] = mapped_column(String(36), index=True)
    meeting_id: Mapped[str] = mapped_column(String(36), index=True)
    decision_text: Mapped[str] = mapped_column(Text)
    decision_type: Mapped[str] = mapped_column(String(80), default="business_decision")
    status: Mapped[str] = mapped_column(String(40), default="detected", index=True)
    responsible_area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.78)
    source_chunk_ids: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
