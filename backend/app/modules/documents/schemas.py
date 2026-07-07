from datetime import datetime
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str
    title: str
    status: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentSectionResponse(BaseModel):
    id: str
    document_id: str
    section_key: str
    title: str
    body: str
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentVersionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=220)
    content: str = Field(min_length=10, max_length=20000)
    change_reason: str = Field(default="Revisao manual do documento", max_length=500)


class DocumentVersionResponse(BaseModel):
    id: str
    document_id: str
    version_number: int
    title: str
    status: str
    content: str
    change_reason: str
    created_by: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentExportJobCreate(BaseModel):
    format: Literal["pdf", "markdown", "excel", "jira", "confluence"]


class DocumentExportJobResponse(BaseModel):
    id: str
    document_id: str
    format: str
    status: str
    payload: dict = Field(default_factory=dict)
    result_url: str | None = None
    created_by: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("payload", mode="before")
    @classmethod
    def parse_payload(cls, value: object) -> dict:
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value:
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}


class SignedExportUrlResponse(BaseModel):
    url: str
    expires_in_seconds: int


class VersionDiffLine(BaseModel):
    kind: str
    text: str


class VersionDiffResponse(BaseModel):
    resource_type: str
    resource_id: str
    from_version: int
    to_version: int
    lines: list[VersionDiffLine]


# ── Editor completo — seções ──────────────────────────────────────────────────

class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=220)
    status: str | None = Field(default=None, max_length=40)


class DocumentSectionCreate(BaseModel):
    section_key: str = Field(..., min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")
    title: str = Field(..., min_length=1, max_length=180)
    body: str = Field(default="")
    sort_order: int = Field(default=0, ge=0)


class DocumentSectionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    body: str | None = None
    sort_order: int | None = Field(default=None, ge=0)


class SectionReorderItem(BaseModel):
    id: str
    sort_order: int = Field(..., ge=0)


class SectionReorderRequest(BaseModel):
    sections: list[SectionReorderItem] = Field(..., min_length=1)


# ── Document Templates ────────────────────────────────────────────────────────

class DocumentTemplateSectionCreate(BaseModel):
    section_key: str = Field(..., min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")
    title: str = Field(..., min_length=1, max_length=180)
    body_template: str = Field(
        default="",
        description=(
            "Corpo com variáveis: {{rules}}, {{summary}}, {{decisions}}, "
            "{{questions}}, {{glossary}}, {{custom:nome}}"
        ),
    )
    sort_order: int = Field(default=0, ge=0)
    required: bool = False


class DocumentTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=180)
    description: str = Field(default="")
    category: str = Field(default="general", max_length=80)
    is_default: bool = False
    sections: list[DocumentTemplateSectionCreate] = Field(default=[])


class DocumentTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = None
    category: str | None = Field(default=None, max_length=80)
    is_default: bool | None = None
    sections: list[DocumentTemplateSectionCreate] | None = None


class DocumentTemplateSectionResponse(BaseModel):
    id: str
    section_key: str
    title: str
    body_template: str
    sort_order: int
    required: bool

    model_config = ConfigDict(from_attributes=True)


class DocumentTemplateResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str
    category: str
    is_default: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    sections: list[DocumentTemplateSectionResponse] = Field(default=[])

    model_config = ConfigDict(from_attributes=True)


class ApplyTemplateRequest(BaseModel):
    replace_existing: bool = Field(
        default=False,
        description="Se True, substitui todas as seções existentes. Se False, apenas adiciona seções ausentes.",
    )
    variables: dict[str, str] = Field(
        default={},
        description="Variáveis extras para interpolação: {'custom:nome': 'valor'}",
    )
