from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.permissions.service import require_permission
from app.modules.usage.models import UsageEvent
from app.modules.usage.schemas import UsageEventResponse, UsageSummaryItem

router = APIRouter()


@router.get("/usage/events", response_model=list[UsageEventResponse])
def list_usage_events(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[UsageEvent]:
    require_permission(context, "usage.view")
    return list(
        db.scalars(
            select(UsageEvent)
            .where(UsageEvent.tenant_id == context.tenant_id)
            .order_by(UsageEvent.created_at.desc())
            .limit(limit)
        )
    )


@router.get("/usage/summary", response_model=list[UsageSummaryItem])
def usage_summary(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[UsageSummaryItem]:
    require_permission(context, "usage.view")
    rows = db.execute(
        select(UsageEvent.event_type, UsageEvent.unit, func.sum(UsageEvent.quantity))
        .where(UsageEvent.tenant_id == context.tenant_id)
        .group_by(UsageEvent.event_type, UsageEvent.unit)
        .order_by(UsageEvent.event_type.asc())
    ).all()
    return [
        UsageSummaryItem(event_type=event_type, unit=unit, quantity=float(quantity or 0))
        for event_type, unit, quantity in rows
    ]
