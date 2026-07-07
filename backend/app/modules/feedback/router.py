from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.feedback.models import BetaFeedback
from app.modules.feedback.schemas import BetaFeedbackCreate, BetaFeedbackResponse
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project

router = APIRouter()


@router.post("/feedback/beta", response_model=BetaFeedbackResponse)
def create_beta_feedback(
    payload: BetaFeedbackCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BetaFeedback:
    require_permission(context, "feedback.create")
    if payload.project_id:
        project = db.get(Project, payload.project_id)
        if project is None or project.tenant_id != context.tenant_id:
            raise not_found("Project not found")
    feedback = BetaFeedback(
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        project_id=payload.project_id,
        rating=payload.rating,
        category=payload.category.strip() or "general",
        comment=payload.comment.strip(),
    )
    db.add(feedback)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="feedback.beta.create",
        resource_type="beta_feedback",
        resource_id=feedback.id,
        details={"rating": payload.rating, "category": feedback.category},
    )
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/feedback/beta", response_model=list[BetaFeedbackResponse])
def list_beta_feedback(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[BetaFeedback]:
    require_permission(context, "feedback.view")
    return list(
        db.scalars(
            select(BetaFeedback)
            .where(BetaFeedback.tenant_id == context.tenant_id)
            .order_by(BetaFeedback.created_at.desc())
            .limit(limit)
        )
    )
