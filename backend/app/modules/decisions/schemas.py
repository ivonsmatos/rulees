from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DecisionResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    decision_text: str
    decision_type: str
    status: str
    responsible_area: str | None
    confidence_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
