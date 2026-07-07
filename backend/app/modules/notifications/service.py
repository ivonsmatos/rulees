from sqlalchemy.orm import Session

from app.modules.notifications.models import Notification


def create_notification(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    title: str,
    body: str = "",
    resource_type: str | None = None,
    resource_id: str | None = None,
) -> Notification:
    notification = Notification(
        tenant_id=tenant_id,
        user_id=user_id,
        title=title,
        body=body,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    db.add(notification)
    return notification
