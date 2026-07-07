from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeetingCreate(BaseModel):
    title: str = Field(min_length=2, max_length=220)
    objective: str = Field(default="", max_length=2000)


class MeetingTemplateResponse(BaseModel):
    key: str
    title: str
    objective: str
    agenda: list[str]


class MeetingFromTemplateCreate(BaseModel):
    template_key: str = Field(min_length=2, max_length=80)
    title: str | None = Field(default=None, max_length=220)


class MeetingResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    title: str
    objective: str
    status: str
    created_at: datetime
    started_at: datetime | None = None
    ended_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConsentCreate(BaseModel):
    text_version: str = Field(default="v1", max_length=40)
    accepted_scope: dict[str, bool] = Field(
        default_factory=lambda: {"audio": True, "transcription": True, "ai_analysis": True}
    )


class ConsentRevokeCreate(BaseModel):
    reason: str = Field(default="", max_length=500)


class ConsentResponse(BaseModel):
    id: str
    meeting_id: str
    user_id: str
    text_version: str
    accepted_at: datetime
    revoked_at: datetime | None = None
    revoked_by: str | None = None
    revoke_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MeetingParticipantCreate(BaseModel):
    user_id: str = Field(min_length=36, max_length=36)
    role: str = Field(default="participant", pattern="^(owner|facilitator|participant|observer)$")
    consent_required: bool = True


class MeetingParticipantResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    user_id: str
    role: str
    consent_required: bool
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingLifecycleEventResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    user_id: str
    event_type: str
    from_status: str | None
    to_status: str | None
    details: dict
    created_at: datetime


class TranscriptChunkResponse(BaseModel):
    id: str
    meeting_id: str
    raw_text: str
    normalized_text: str
    is_final: bool
    start_time: float | None
    end_time: float | None
    speaker_label: str | None = None
    language: str | None = None
    confidence_score: float | None = None
    sequence: int | None = None
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingStateResponse(BaseModel):
    meeting: MeetingResponse
    has_consent: bool
    consent: ConsentResponse | None = None
    participants: list[MeetingParticipantResponse] = Field(default_factory=list)
    lifecycle_events: list[MeetingLifecycleEventResponse] = Field(default_factory=list)
    transcript: list[TranscriptChunkResponse]
    rules: list[dict]
    questions: list[dict]
    decisions: list[dict]


class MeetingSummaryResponse(BaseModel):
    meeting_id: str
    title: str
    status: str
    transcript_chunks: int
    rules_total: int
    rules_approved: int
    open_questions: int
    decisions_total: int
    summary: str
    next_steps: list[str]
