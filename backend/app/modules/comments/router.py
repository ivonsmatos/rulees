from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import TenantMember
from app.modules.comments.models import Comment
from app.modules.comments.schemas import CommentCreate, CommentResponse
from app.modules.notifications.service import create_notification
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project

router = APIRouter()


@router.post("/comments", response_model=CommentResponse)
def create_comment(
    payload: CommentCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Comment:
    require_permission(context, "comment.create")
    if payload.project_id:
        project = db.get(Project, payload.project_id)
        if project is None or project.tenant_id != context.tenant_id:
            raise not_found("Project not found")
    comment = Comment(
        tenant_id=context.tenant_id,
        project_id=payload.project_id,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        author_id=context.user_id,
        body=payload.body.strip(),
    )
    db.add(comment)
    recipients = list(
        db.scalars(
            select(TenantMember).where(
                TenantMember.tenant_id == context.tenant_id,
                TenantMember.user_id != context.user_id,
            )
        )
    )
    for recipient in recipients:
        create_notification(
            db,
            tenant_id=context.tenant_id,
            user_id=recipient.user_id,
            title="Novo comentario",
            body=payload.body.strip()[:240],
            resource_type=payload.resource_type,
            resource_id=payload.resource_id,
        )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="comment.create",
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
    )
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/comments", response_model=list[CommentResponse])
def list_comments(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    resource_type: str = Query(max_length=80),
    resource_id: str = Query(max_length=36),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[Comment]:
    require_permission(context, "comment.view")
    return list(
        db.scalars(
            select(Comment)
            .where(
                Comment.tenant_id == context.tenant_id,
                Comment.resource_type == resource_type,
                Comment.resource_id == resource_id,
            )
            .order_by(Comment.created_at.desc())
            .limit(limit)
        )
    )
