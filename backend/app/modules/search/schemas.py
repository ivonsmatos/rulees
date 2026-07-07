from datetime import datetime

from pydantic import BaseModel


class GlobalSearchResult(BaseModel):
    source_type: str
    source_id: str
    project_id: str | None = None
    title: str
    snippet: str
    created_at: datetime
