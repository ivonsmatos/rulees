from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.permissions.service import require_permission
from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogResponse, AuditRetentionResponse

router = APIRouter()
settings = get_settings()


@router.get("/audit/logs", response_model=list[AuditLogResponse])
def list_audit_logs(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    action: str | None = Query(default=None, max_length=120),
    resource_type: str | None = Query(default=None, max_length=80),
) -> list[AuditLog]:
    require_permission(context, "audit.view")
    query = select(AuditLog).where(AuditLog.tenant_id == context.tenant_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    return list(
        db.scalars(
            query
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
    )


@router.post("/audit/retention/run", response_model=AuditRetentionResponse)
def run_audit_retention(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    retention_days: int = Query(default=settings.audit_retention_days, ge=1, le=3650),
) -> AuditRetentionResponse:
    require_permission(context, "audit.retention.manage")
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    result = db.execute(
        delete(AuditLog).where(
            AuditLog.tenant_id == context.tenant_id,
            AuditLog.created_at < cutoff,
        )
    )
    db.commit()
    return AuditRetentionResponse(
        retention_days=retention_days,
        deleted_logs=int(result.rowcount or 0),
        cutoff=cutoff,
    )
