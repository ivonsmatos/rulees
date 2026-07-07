from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    question_text: str
    reason: str
    gap_type: str
    priority: str
    status: str
    confidence_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
