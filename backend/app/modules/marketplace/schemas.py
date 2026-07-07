from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PluginResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    category: str
    is_official: bool
    version: str
    config_schema: dict[str, Any]

    model_config = {"from_attributes": True}


class TenantPluginResponse(BaseModel):
    id: str
    plugin_id: str
    plugin_slug: str
    config: dict[str, Any]
    is_enabled: bool
    installed_by: str
    installed_at: datetime

    model_config = {"from_attributes": True}


class PluginInstallRequest(BaseModel):
    config: dict[str, Any] = Field(default={})


class PluginUpdateRequest(BaseModel):
    config: dict[str, Any] | None = None
    is_enabled: bool | None = None
