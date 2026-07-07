import json
from typing import Any

from sqlalchemy.orm import Session

from app.modules.usage.models import UsageEvent


def write_usage_event(
    db: Session,
    *,
    tenant_id: str,
    event_type: str,
    unit: str = "count",
    quantity: float = 1.0,
    project_id: str | None = None,
    meeting_id: str | None = None,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> UsageEvent:
    event = UsageEvent(
        tenant_id=tenant_id,
        project_id=project_id,
        meeting_id=meeting_id,
        user_id=user_id,
        event_type=event_type,
        unit=unit,
        quantity=quantity,
        details=json.dumps(details or {}, ensure_ascii=False),
    )
    db.add(event)
    return event
