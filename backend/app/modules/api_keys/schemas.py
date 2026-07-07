from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ScopeT = Literal["read", "write", "scim", "webhooks"]


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    scopes: list[ScopeT] = Field(default=["read"])
    expires_at: datetime | None = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreated(ApiKeyResponse):
    """Retornado apenas uma vez após criação — contém a chave completa."""
    raw_key: str


class ApiKeyRevoke(BaseModel):
    reason: str | None = None
