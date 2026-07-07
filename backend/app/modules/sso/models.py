from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SsoConfig(Base):
    """Configuração de IdP SAML 2.0 por tenant."""

    __tablename__ = "sso_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    provider_name: Mapped[str] = mapped_column(String(160), default="SAML IdP")
    entity_id: Mapped[str] = mapped_column(String(1024))    # IdP EntityID
    sso_url: Mapped[str] = mapped_column(String(1024))      # IdP SSO URL
    slo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)  # SLO opcional
    x509_cert: Mapped[str] = mapped_column(Text)            # Certificado IdP (PEM, sem headers)
    attribute_map: Mapped[str] = mapped_column(Text, default="{}")  # JSON: SAML attr → user field
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sp_entity_id: Mapped[str] = mapped_column(String(1024), default="")  # nosso SP EntityID
    created_by: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class SsoSession(Base):
    """Sessão temporária durante o fluxo SSO (RelayState/AuthnRequest)."""

    __tablename__ = "sso_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)
    relay_state: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    redirect_url: Mapped[str] = mapped_column(String(1024), default="/")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
