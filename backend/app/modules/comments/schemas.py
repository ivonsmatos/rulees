from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    project_id: str | None = Field(default=None, max_length=36)
    resource_type: str = Field(min_length=2, max_length=80)
    resource_id: str = Field(min_length=2, max_length=36)
    body: str = Field(min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str | None
    resource_type: str
    resource_id: str
    author_id: str
    body: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
