from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


KmsProviderT = Literal["local", "aws", "gcp", "azure"]


class CustomerKeyCreate(BaseModel):
    kms_provider: KmsProviderT = "local"
    kms_key_arn: str | None = Field(
        default=None,
        description="ARN/Resource ID da KEK no KMS (obrigatório para providers externos)",
    )
    key_label: str = "primary"
    master_key_b64: str | None = Field(
        default=None,
        description="KEK local em base64 (somente para kms_provider=local, testes/demo)",
        repr=False,
    )


class CustomerKeyResponse(BaseModel):
    id: str
    tenant_id: str
    kms_provider: str
    kms_key_arn: str | None
    key_label: str
    is_active: bool
    created_at: datetime
    rotated_at: datetime | None

    model_config = {"from_attributes": True}


class EncryptRequest(BaseModel):
    plaintext: str = Field(..., description="Texto a cifrar (UTF-8)")


class EncryptResponse(BaseModel):
    ciphertext_b64: str


class DecryptRequest(BaseModel):
    ciphertext_b64: str


class DecryptResponse(BaseModel):
    plaintext: str
