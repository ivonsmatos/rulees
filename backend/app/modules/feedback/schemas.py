from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BetaFeedbackCreate(BaseModel):
    project_id: str | None = Field(default=None, max_length=36)
    rating: int = Field(ge=1, le=5)
    category: str = Field(default="general", max_length=80)
    comment: str = Field(default="", max_length=2000)


class BetaFeedbackResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    project_id: str | None
    rating: int
    category: str
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
