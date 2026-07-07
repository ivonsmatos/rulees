from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str = Field(default="", max_length=2000)


class ProjectUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str = Field(default="", max_length=2000)


class ProjectResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str
    status: str
    created_at: datetime
    archived_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ProjectGlossaryTermCreate(BaseModel):
    term: str = Field(min_length=2, max_length=160)
    definition: str = Field(default="", max_length=2000)
    aliases: list[str] = Field(default_factory=list, max_length=12)


class ProjectGlossaryTermUpdate(BaseModel):
    term: str = Field(min_length=2, max_length=160)
    definition: str = Field(default="", max_length=2000)
    aliases: list[str] = Field(default_factory=list, max_length=12)


class ProjectGlossaryTermResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    term: str
    definition: str
    aliases: list[str]
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectTemplateGlossaryTerm(BaseModel):
    term: str
    definition: str
    aliases: list[str] = Field(default_factory=list)


class ProjectTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str = Field(default="", max_length=2000)
    default_objective: str = Field(default="", max_length=2000)
    default_glossary_terms: list[ProjectGlossaryTermCreate] = Field(default_factory=list, max_length=20)


class ProjectFromTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=2000)


class ProjectTemplateResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str
    default_objective: str
    default_glossary_terms: list[ProjectTemplateGlossaryTerm]
    created_by: str
    created_at: datetime


class ProjectMemberCreate(BaseModel):
    user_id: str = Field(min_length=36, max_length=36)
    role: str = Field(default="member", pattern="^(manager|member|viewer)$")


class ProjectMemberResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    user_id: str
    role: str
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectGapSummaryResponse(BaseModel):
    project_id: str
    meetings_total: int
    meetings_without_transcript: int
    rules_pending_review: int
    rules_conflicted: int
    open_questions: int
    documents_total: int
    readiness_score: int
    gaps: list[str]
