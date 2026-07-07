from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import NotificationResponse
from app.modules.permissions.service import require_permission

router = APIRouter()


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[Notification]:
    require_permission(context, "notification.view")
    query = select(Notification).where(
        Notification.tenant_id == context.tenant_id,
        Notification.user_id == context.user_id,
    )
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    return list(db.scalars(query.order_by(Notification.created_at.desc()).limit(limit)))


@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Notification:
    require_permission(context, "notification.view")
    notification = db.get(Notification, notification_id)
    if notification is None or notification.tenant_id != context.tenant_id or notification.user_id != context.user_id:
        raise not_found("Notification not found")
    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return notification
