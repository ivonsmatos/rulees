from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentRunResponse(BaseModel):
    schema_version: str = "1.0"
    run_id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    agent_name: str
    agent_role: str
    status: str
    confidence_score: float | None = None
    input_reference: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    warnings: list[Any] = Field(default_factory=list)
    errors: list[Any] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class TranscriptAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)


class TranscriptAnalysisResponse(BaseModel):
    engine: str
    normalized_text: str
    is_rule_candidate: bool
    quality_details: dict[str, Any] = Field(default_factory=dict)
    is_question_candidate: bool
    is_decision_candidate: bool
