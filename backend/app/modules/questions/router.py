from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.meetings.models import Meeting
from app.modules.permissions.service import require_permission
from app.modules.questions.models import OpenQuestion
from app.modules.questions.schemas import QuestionResponse

router = APIRouter()


@router.get("/meetings/{meeting_id}/questions", response_model=list[QuestionResponse])
def list_questions(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[OpenQuestion]:
    require_permission(context, "question.view")
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.tenant_id != context.tenant_id:
        raise not_found("Meeting not found")
    return list(
        db.scalars(
            select(OpenQuestion)
            .where(OpenQuestion.tenant_id == context.tenant_id, OpenQuestion.meeting_id == meeting_id)
            .order_by(OpenQuestion.created_at.desc())
        )
    )
