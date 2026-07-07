from datetime import datetime
import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RuleResponse(BaseModel):
    id: str
    code: str
    tenant_id: str
    project_id: str
    meeting_id: str
    rule_text: str
    condition_text: str | None
    result_text: str | None
    status: str
    version_number: int
    confidence_score: float
    quality_score: int
    quality_details: dict = Field(default_factory=dict)
    source_chunk_ids: list[str] = Field(default_factory=list)
    replaced_by_rule_id: str | None = None
    approved_by: str | None
    approved_at: datetime | None
    revoked_at: datetime | None = None
    archived_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("quality_details", mode="before")
    @classmethod
    def parse_quality_details(cls, value: object) -> dict:
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value:
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}

    @field_validator("source_chunk_ids", mode="before")
    @classmethod
    def parse_source_chunk_ids(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str) and value:
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return []
            return [str(item) for item in parsed] if isinstance(parsed, list) else []
        return []


class RuleVersionCreate(BaseModel):
    rule_text: str = Field(min_length=5, max_length=2000)
    condition_text: str | None = Field(default=None, max_length=2000)
    result_text: str | None = Field(default=None, max_length=2000)
    change_reason: str = Field(default="Revisao manual", max_length=500)


class RuleReplaceCreate(RuleVersionCreate):
    pass


class RuleLifecycleAction(BaseModel):
    reason: str = Field(default="", max_length=500)


class RuleVersionResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    rule_id: str
    version_number: int
    status: str
    rule_text: str
    condition_text: str | None
    result_text: str | None
    source_chunk_ids: str
    change_reason: str
    created_by: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleLifecycleEventResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    rule_id: str
    user_id: str | None
    event_type: str
    from_status: str | None
    to_status: str | None
    details: dict
    created_at: datetime

    @field_validator("details", mode="before")
    @classmethod
    def parse_details(cls, value: object) -> dict:
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value:
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}


class RuleVersionDiffLine(BaseModel):
    kind: str
    text: str


class RuleVersionDiffResponse(BaseModel):
    resource_type: str
    resource_id: str
    from_version: int
    to_version: int
    lines: list[RuleVersionDiffLine]
