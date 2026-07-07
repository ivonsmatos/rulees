from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.analytics.schemas import AnalyticsSummaryResponse
from app.modules.comments.models import Comment
from app.modules.documents.models import Document
from app.modules.meetings.models import Meeting
from app.modules.notifications.models import Notification
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project
from app.modules.questions.models import OpenQuestion
from app.modules.rules_ledger.models import BusinessRule

router = APIRouter()


def _count(db: Session, query) -> int:
    return int(db.scalar(query) or 0)


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> AnalyticsSummaryResponse:
    require_permission(context, "analytics.view")
    projects_total = _count(db, select(func.count(Project.id)).where(Project.tenant_id == context.tenant_id))
    meetings_total = _count(db, select(func.count(Meeting.id)).where(Meeting.tenant_id == context.tenant_id))
    rules_total = _count(db, select(func.count(BusinessRule.id)).where(BusinessRule.tenant_id == context.tenant_id))
    approved_rules = _count(
        db,
        select(func.count(BusinessRule.id)).where(
            BusinessRule.tenant_id == context.tenant_id,
            BusinessRule.status == "approved",
        ),
    )
    documents_total = _count(db, select(func.count(Document.id)).where(Document.tenant_id == context.tenant_id))
    open_questions = _count(
        db,
        select(func.count(OpenQuestion.id)).where(
            OpenQuestion.tenant_id == context.tenant_id,
            OpenQuestion.status == "open",
        ),
    )
    comments_total = _count(db, select(func.count(Comment.id)).where(Comment.tenant_id == context.tenant_id))
    notifications_unread = _count(
        db,
        select(func.count(Notification.id)).where(
            Notification.tenant_id == context.tenant_id,
            Notification.user_id == context.user_id,
            Notification.read_at.is_(None),
        ),
    )
    penalty = open_questions * 5 + max(rules_total - approved_rules, 0) * 4
    readiness_score = max(0, min(100, 75 + approved_rules * 3 + documents_total * 5 - penalty))
    return AnalyticsSummaryResponse(
        projects_total=projects_total,
        meetings_total=meetings_total,
        rules_total=rules_total,
        approved_rules=approved_rules,
        documents_total=documents_total,
        open_questions=open_questions,
        comments_total=comments_total,
        notifications_unread=notifications_unread,
        readiness_score=readiness_score,
    )
