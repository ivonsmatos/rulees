from datetime import datetime
from typing import Any, Literal

from pydantic import AnyHttpUrl, BaseModel, Field


ProviderT = Literal["jira", "confluence", "azure_devops"]


# ── Configs específicas por provider ──────────────────────────────────────────

class JiraConfig(BaseModel):
    base_url: AnyHttpUrl
    project_key: str
    email: str
    api_token: str = Field(..., repr=False)
    issue_type: str = "Story"


class ConfluenceConfig(BaseModel):
    base_url: AnyHttpUrl
    space_key: str
    email: str
    api_token: str = Field(..., repr=False)
    parent_page_id: str | None = None


class AzureDevOpsConfig(BaseModel):
    org_url: AnyHttpUrl
    project: str
    work_item_type: str = "User Story"
    personal_access_token: str = Field(..., repr=False)


# ── Requests / Responses ──────────────────────────────────────────────────────

class IntegrationCreate(BaseModel):
    provider: ProviderT
    label: str = Field(..., min_length=1, max_length=160)
    config: dict[str, Any]


class IntegrationUpdate(BaseModel):
    label: str | None = None
    config: dict[str, Any] | None = None
    is_active: bool | None = None


class IntegrationResponse(BaseModel):
    id: str
    provider: str
    label: str
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DispatchRequest(BaseModel):
    integration_id: str


class DispatchResponse(BaseModel):
    id: str
    status: str
    external_id: str | None
    external_url: str | None
    error_message: str | None
    dispatched_at: datetime

    model_config = {"from_attributes": True}


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
