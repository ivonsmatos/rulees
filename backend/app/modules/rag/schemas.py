from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RagSearchResponse(BaseModel):
    source_type: str
    source_id: str
    meeting_id: str | None
    content: str
    similarity_score: float
    created_at: datetime


class SemanticEmbeddingResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    meeting_id: str | None
    source_type: str
    source_id: str
    content_hash: str
    content: str
    embedding_model: str
    embedding_dim: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RagSearchQuery(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    limit: int = Field(default=8, ge=1, le=20)
