from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UsageEventResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str | None
    meeting_id: str | None
    user_id: str | None
    event_type: str
    unit: str
    quantity: float
    details: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsageSummaryItem(BaseModel):
    event_type: str
    unit: str
    quantity: float
