from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.documents.models import Document
from app.modules.meetings.models import Meeting, TranscriptChunk
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project
from app.modules.rules_ledger.models import BusinessRule
from app.modules.search.schemas import GlobalSearchResult

router = APIRouter()


def _match(value: str, query: str) -> bool:
    return query.lower() in value.lower()


def _snippet(value: str, query: str, limit: int = 180) -> str:
    lowered = value.lower()
    index = lowered.find(query.lower())
    if index < 0:
        return value[:limit]
    start = max(index - 45, 0)
    return value[start : start + limit]


@router.get("/search/global", response_model=list[GlobalSearchResult])
def global_search(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    query: str = Query(min_length=2, max_length=120),
    limit: int = Query(default=20, ge=1, le=50),
) -> list[GlobalSearchResult]:
    require_permission(context, "search.global")
    results: list[GlobalSearchResult] = []
    projects = db.scalars(select(Project).where(Project.tenant_id == context.tenant_id).order_by(Project.created_at.desc())).all()
    for project in projects:
        if _match(project.name + " " + project.description, query):
            results.append(
                GlobalSearchResult(
                    source_type="project",
                    source_id=project.id,
                    project_id=project.id,
                    title=project.name,
                    snippet=_snippet(project.description or project.name, query),
                    created_at=project.created_at,
                )
            )
    meetings = db.scalars(select(Meeting).where(Meeting.tenant_id == context.tenant_id).order_by(Meeting.created_at.desc())).all()
    for meeting in meetings:
        if _match(meeting.title + " " + meeting.objective, query):
            results.append(
                GlobalSearchResult(
                    source_type="meeting",
                    source_id=meeting.id,
                    project_id=meeting.project_id,
                    title=meeting.title,
                    snippet=_snippet(meeting.objective or meeting.title, query),
                    created_at=meeting.created_at,
                )
            )
    documents = db.scalars(select(Document).where(Document.tenant_id == context.tenant_id).order_by(Document.created_at.desc())).all()
    for document in documents:
        if _match(document.title + " " + document.content, query):
            results.append(
                GlobalSearchResult(
                    source_type="document",
                    source_id=document.id,
                    project_id=document.project_id,
                    title=document.title,
                    snippet=_snippet(document.content, query),
                    created_at=document.created_at,
                )
            )
    rules = db.scalars(select(BusinessRule).where(BusinessRule.tenant_id == context.tenant_id).order_by(BusinessRule.created_at.desc())).all()
    for rule in rules:
        if _match(rule.code + " " + rule.rule_text, query):
            results.append(
                GlobalSearchResult(
                    source_type="business_rule",
                    source_id=rule.id,
                    project_id=rule.project_id,
                    title=rule.code,
                    snippet=_snippet(rule.rule_text, query),
                    created_at=rule.created_at,
                )
            )
    chunks = db.scalars(
        select(TranscriptChunk).where(TranscriptChunk.tenant_id == context.tenant_id).order_by(TranscriptChunk.created_at.desc())
    ).all()
    for chunk in chunks:
        if _match(chunk.normalized_text, query):
            results.append(
                GlobalSearchResult(
                    source_type="transcript_chunk",
                    source_id=chunk.id,
                    project_id=chunk.project_id,
                    title=chunk.speaker_label or "Transcricao",
                    snippet=_snippet(chunk.normalized_text, query),
                    created_at=chunk.created_at,
                )
            )
    return sorted(results, key=lambda item: item.created_at, reverse=True)[:limit]
