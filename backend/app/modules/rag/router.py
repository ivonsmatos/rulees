from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project
from app.modules.rag.models import SemanticEmbedding
from app.modules.rag.schemas import RagSearchResponse, SemanticEmbeddingResponse
from app.modules.rag.service import rag_match_to_dict, retrieve_similar

router = APIRouter()


def _get_tenant_project(db: Session, context: RequestContext, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != context.tenant_id:
        raise not_found("Project not found")
    return project


@router.get("/projects/{project_id}/rag/search", response_model=list[RagSearchResponse])
def search_project_memory(
    project_id: str,
    query: str = Query(min_length=2, max_length=2000),
    limit: int = Query(default=8, ge=1, le=20),
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    require_permission(context, "rag.view")
    _get_tenant_project(db, context, project_id)
    matches = retrieve_similar(
        db,
        tenant_id=context.tenant_id,
        project_id=project_id,
        query=query,
        limit=limit,
    )
    return [rag_match_to_dict(match) for match in matches]


@router.get("/projects/{project_id}/rag/embeddings", response_model=list[SemanticEmbeddingResponse])
def list_project_embeddings(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[SemanticEmbedding]:
    require_permission(context, "rag.view")
    _get_tenant_project(db, context, project_id)
    return list(
        db.scalars(
            select(SemanticEmbedding)
            .where(
                SemanticEmbedding.tenant_id == context.tenant_id,
                SemanticEmbedding.project_id == project_id,
            )
            .order_by(SemanticEmbedding.created_at.desc())
        )
    )
