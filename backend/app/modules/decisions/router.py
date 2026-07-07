from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.decisions.models import Decision
from app.modules.decisions.schemas import DecisionResponse
from app.modules.meetings.models import Meeting
from app.modules.permissions.service import require_permission

router = APIRouter()


@router.get("/meetings/{meeting_id}/decisions", response_model=list[DecisionResponse])
def list_decisions(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[Decision]:
    require_permission(context, "decision.view")
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.tenant_id != context.tenant_id:
        raise not_found("Meeting not found")
    return list(
        db.scalars(
            select(Decision)
            .where(Decision.tenant_id == context.tenant_id, Decision.meeting_id == meeting_id)
            .order_by(Decision.created_at.desc())
        )
    )
