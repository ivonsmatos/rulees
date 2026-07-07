from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CustomerKey(Base):
    """
    Chave de criptografia gerenciada pelo cliente (BYOK).

    Padrão de envelope encryption:
    - O cliente fornece uma KEK (Key Encryption Key) via KMS (ex: AWS KMS ARN).
    - O Rulees gera um DEK (Data Encryption Key) por tenant.
    - O DEK é cifrado com a KEK e armazenado aqui.
    - Dados sensíveis são cifrados com o DEK em memória.
    """

    __tablename__ = "customer_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    kms_provider: Mapped[str] = mapped_column(String(40), default="local")  # aws|gcp|azure|local
    kms_key_arn: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    encrypted_dek: Mapped[str] = mapped_column(Text)  # DEK cifrado com KEK (base64)
    key_label: Mapped[str] = mapped_column(String(160), default="primary")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
