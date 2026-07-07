from datetime import datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, Field


class SsoConfigCreate(BaseModel):
    provider_name: str = Field(default="SAML IdP", max_length=160)
    entity_id: str = Field(..., description="IdP EntityID URI")
    sso_url: AnyHttpUrl = Field(..., description="IdP SSO URL (POST ou Redirect binding)")
    slo_url: AnyHttpUrl | None = None
    x509_cert: str = Field(..., description="Certificado X.509 do IdP em PEM (sem headers -----)")
    attribute_map: dict[str, str] = Field(
        default={"email": "email", "name": "name"},
        description="Mapeamento de atributos SAML → campos Rulees",
    )
    sp_entity_id: str = Field(default="", description="Entity ID do SP (deixar vazio = auto)")


class SsoConfigUpdate(BaseModel):
    provider_name: str | None = None
    sso_url: AnyHttpUrl | None = None
    slo_url: AnyHttpUrl | None = None
    x509_cert: str | None = None
    attribute_map: dict[str, str] | None = None
    is_active: bool | None = None


class SsoConfigResponse(BaseModel):
    id: str
    tenant_id: str
    provider_name: str
    entity_id: str
    sso_url: str
    slo_url: str | None
    sp_entity_id: str
    attribute_map: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SsoLoginInitResponse(BaseModel):
    redirect_url: str
    relay_state: str


class SsoCallbackRequest(BaseModel):
    SAMLResponse: str
    RelayState: str | None = None
