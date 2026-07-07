from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    details: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditRetentionResponse(BaseModel):
    retention_days: int
    deleted_logs: int
    cutoff: datetime
