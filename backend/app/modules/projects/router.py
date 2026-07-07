import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict, not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import TenantMember
from app.modules.documents.models import Document
from app.modules.meetings.models import Meeting, TranscriptChunk
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project, ProjectGlossaryTerm, ProjectMember, ProjectTemplate
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectFromTemplateCreate,
    ProjectGapSummaryResponse,
    ProjectGlossaryTermCreate,
    ProjectGlossaryTermResponse,
    ProjectGlossaryTermUpdate,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectTemplateCreate,
    ProjectTemplateGlossaryTerm,
    ProjectTemplateResponse,
    ProjectUpdate,
)
from app.modules.questions.models import OpenQuestion
from app.modules.rules_ledger.models import BusinessRule
from app.modules.usage.service import write_usage_event

router = APIRouter()


def _get_project_or_404(db: Session, context: RequestContext, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != context.tenant_id:
        raise not_found("Project not found")
    return project


def _clean_aliases(aliases: list[str]) -> list[str]:
    cleaned: list[str] = []
    for alias in aliases:
        value = alias.strip()
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned[:12]


def _glossary_response(term: ProjectGlossaryTerm) -> ProjectGlossaryTermResponse:
    return ProjectGlossaryTermResponse(
        id=term.id,
        tenant_id=term.tenant_id,
        project_id=term.project_id,
        term=term.term,
        definition=term.definition,
        aliases=json.loads(term.aliases or "[]"),
        created_by=term.created_by,
        created_at=term.created_at,
    )


def _template_terms_from_json(value: str) -> list[ProjectTemplateGlossaryTerm]:
    raw_terms = json.loads(value or "[]")
    terms: list[ProjectTemplateGlossaryTerm] = []
    for item in raw_terms:
        terms.append(
            ProjectTemplateGlossaryTerm(
                term=str(item.get("term", "")),
                definition=str(item.get("definition", "")),
                aliases=[str(alias) for alias in item.get("aliases", [])],
            )
        )
    return terms


def _template_response(template: ProjectTemplate) -> ProjectTemplateResponse:
    return ProjectTemplateResponse(
        id=template.id,
        tenant_id=template.tenant_id,
        name=template.name,
        description=template.description,
        default_objective=template.default_objective,
        default_glossary_terms=_template_terms_from_json(template.default_glossary_terms),
        created_by=template.created_by,
        created_at=template.created_at,
    )


def _template_terms_to_json(terms: list[ProjectGlossaryTermCreate]) -> str:
    return json.dumps(
        [
            {
                "term": term.term.strip(),
                "definition": term.definition.strip(),
                "aliases": _clean_aliases(term.aliases),
            }
            for term in terms
        ]
    )


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[Project]:
    require_permission(context, "project.view")
    return list(
        db.scalars(
            select(Project)
            .where(Project.tenant_id == context.tenant_id)
            .order_by(Project.created_at.desc())
        )
    )


@router.post("", response_model=ProjectResponse)
def create_project(
    payload: ProjectCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Project:
    require_permission(context, "project.create")
    project = Project(
        tenant_id=context.tenant_id,
        name=payload.name.strip(),
        description=payload.description.strip(),
        created_by=context.user_id,
    )
    db.add(project)
    db.flush()
    db.add(
        ProjectMember(
            tenant_id=context.tenant_id,
            project_id=project.id,
            user_id=context.user_id,
            role="manager",
            created_by=context.user_id,
        )
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="project.create",
        resource_type="project",
        resource_id=project.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=project.id,
        user_id=context.user_id,
        event_type="project_created",
        details={"project_name": project.name},
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/templates", response_model=list[ProjectTemplateResponse])
def list_project_templates(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[ProjectTemplateResponse]:
    require_permission(context, "project.template.view")
    templates = list(
        db.scalars(
            select(ProjectTemplate)
            .where(ProjectTemplate.tenant_id == context.tenant_id)
            .order_by(ProjectTemplate.created_at.desc())
        )
    )
    return [_template_response(template) for template in templates]


@router.post("/templates", response_model=ProjectTemplateResponse)
def create_project_template(
    payload: ProjectTemplateCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ProjectTemplateResponse:
    require_permission(context, "project.template.create")
    name = payload.name.strip()
    existing = db.scalar(
        select(ProjectTemplate).where(
            ProjectTemplate.tenant_id == context.tenant_id,
            ProjectTemplate.name == name,
        )
    )
    if existing:
        raise conflict("Project template already exists")
    template = ProjectTemplate(
        tenant_id=context.tenant_id,
        name=name,
        description=payload.description.strip(),
        default_objective=payload.default_objective.strip(),
        default_glossary_terms=_template_terms_to_json(payload.default_glossary_terms),
        created_by=context.user_id,
    )
    db.add(template)
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="project.template.create",
        resource_type="project_template",
        resource_id=template.id,
    )
    db.commit()
    db.refresh(template)
    return _template_response(template)


@router.post("/templates/{template_id}/projects", response_model=ProjectResponse)
def create_project_from_template(
    template_id: str,
    payload: ProjectFromTemplateCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Project:
    require_permission(context, "project.create")
    require_permission(context, "project.template.use")
    template = db.get(ProjectTemplate, template_id)
    if template is None or template.tenant_id != context.tenant_id:
        raise not_found("Project template not found")
    project = Project(
        tenant_id=context.tenant_id,
        name=payload.name.strip(),
        description=(payload.description if payload.description is not None else template.description).strip(),
        created_by=context.user_id,
    )
    db.add(project)
    db.flush()
    db.add(
        ProjectMember(
            tenant_id=context.tenant_id,
            project_id=project.id,
            user_id=context.user_id,
            role="manager",
            created_by=context.user_id,
        )
    )
    for term in _template_terms_from_json(template.default_glossary_terms):
        db.add(
            ProjectGlossaryTerm(
                tenant_id=context.tenant_id,
                project_id=project.id,
                term=term.term.strip(),
                definition=term.definition.strip(),
                aliases=json.dumps(_clean_aliases(term.aliases)),
                created_by=context.user_id,
            )
        )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="project.template.use",
        resource_type="project_template",
        resource_id=template.id,
        details={"project_id": project.id},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=project.id,
        user_id=context.user_id,
        event_type="project_created",
        details={"project_name": project.name, "template_id": template.id},
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Project:
    require_permission(context, "project.view")
    return _get_project_or_404(db, context, project_id)


@router.get("/{project_id}/gaps/summary", response_model=ProjectGapSummaryResponse)
def project_gap_summary(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ProjectGapSummaryResponse:
    require_permission(context, "project.view")
    _get_project_or_404(db, context, project_id)
    meetings = list(
        db.scalars(
            select(Meeting).where(
                Meeting.tenant_id == context.tenant_id,
                Meeting.project_id == project_id,
            )
        )
    )
    meetings_without_transcript = 0
    for meeting in meetings:
        chunk_count = db.scalar(
            select(func.count(TranscriptChunk.id)).where(
                TranscriptChunk.tenant_id == context.tenant_id,
                TranscriptChunk.meeting_id == meeting.id,
            )
        )
        if not chunk_count:
            meetings_without_transcript += 1
    rules_pending_review = db.scalar(
        select(func.count(BusinessRule.id)).where(
            BusinessRule.tenant_id == context.tenant_id,
            BusinessRule.project_id == project_id,
            BusinessRule.status == "needs_review",
        )
    ) or 0
    rules_conflicted = db.scalar(
        select(func.count(BusinessRule.id)).where(
            BusinessRule.tenant_id == context.tenant_id,
            BusinessRule.project_id == project_id,
            BusinessRule.status == "conflict_detected",
        )
    ) or 0
    open_questions = db.scalar(
        select(func.count(OpenQuestion.id)).where(
            OpenQuestion.tenant_id == context.tenant_id,
            OpenQuestion.project_id == project_id,
            OpenQuestion.status == "open",
        )
    ) or 0
    documents_total = db.scalar(
        select(func.count(Document.id)).where(
            Document.tenant_id == context.tenant_id,
            Document.project_id == project_id,
        )
    ) or 0
    gaps: list[str] = []
    if meetings_without_transcript:
        gaps.append(f"{meetings_without_transcript} reunioes sem transcricao.")
    if rules_pending_review:
        gaps.append(f"{rules_pending_review} regras aguardando revisao.")
    if rules_conflicted:
        gaps.append(f"{rules_conflicted} conflitos de regra pendentes.")
    if open_questions:
        gaps.append(f"{open_questions} duvidas abertas.")
    if meetings and not documents_total:
        gaps.append("Nenhum documento funcional gerado para o projeto.")
    readiness_score = max(
        0,
        100
        - meetings_without_transcript * 12
        - int(rules_pending_review) * 10
        - int(rules_conflicted) * 18
        - int(open_questions) * 8
        - (15 if meetings and not documents_total else 0),
    )
    return ProjectGapSummaryResponse(
        project_id=project_id,
        meetings_total=len(meetings),
        meetings_without_transcript=meetings_without_transcript,
        rules_pending_review=int(rules_pending_review),
        rules_conflicted=int(rules_conflicted),
        open_questions=int(open_questions),
        documents_total=int(documents_total),
        readiness_score=readiness_score,
        gaps=gaps,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Project:
    require_permission(context, "project.update")
    project = _get_project_or_404(db, context, project_id)
    if project.status == "archived":
        raise bad_request("Archived projects cannot be edited")
    project.name = payload.name.strip()
    project.description = payload.description.strip()
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="project.update",
        resource_type="project",
        resource_id=project.id,
    )
    db.commit()
    db.refresh(project)
    return project


@router.post("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Project:
    require_permission(context, "project.archive")
    project = _get_project_or_404(db, context, project_id)
    if project.status != "archived":
        project.status = "archived"
        project.archived_at = datetime.now(timezone.utc)
        db.flush()
        write_audit_log(
            db,
            tenant_id=context.tenant_id,
            user_id=context.user_id,
            action="project.archive",
            resource_type="project",
            resource_id=project.id,
        )
        db.commit()
        db.refresh(project)
    return project


@router.get("/{project_id}/glossary", response_model=list[ProjectGlossaryTermResponse])
def list_project_glossary(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[ProjectGlossaryTermResponse]:
    require_permission(context, "project.glossary.view")
    _get_project_or_404(db, context, project_id)
    terms = list(
        db.scalars(
            select(ProjectGlossaryTerm)
            .where(ProjectGlossaryTerm.tenant_id == context.tenant_id, ProjectGlossaryTerm.project_id == project_id)
            .order_by(ProjectGlossaryTerm.term.asc())
        )
    )
    return [_glossary_response(term) for term in terms]


@router.post("/{project_id}/glossary", response_model=ProjectGlossaryTermResponse)
def create_project_glossary_term(
    project_id: str,
    payload: ProjectGlossaryTermCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ProjectGlossaryTermResponse:
    require_permission(context, "project.glossary.manage")
    project = _get_project_or_404(db, context, project_id)
    if project.status == "archived":
        raise bad_request("Archived projects cannot receive glossary terms")
    term_name = payload.term.strip()
    existing = db.scalar(
        select(ProjectGlossaryTerm).where(
            ProjectGlossaryTerm.project_id == project.id,
            ProjectGlossaryTerm.term == term_name,
        )
    )
    if existing:
        raise conflict("Glossary term already exists")
    term = ProjectGlossaryTerm(
        tenant_id=context.tenant_id,
        project_id=project.id,
        term=term_name,
        definition=payload.definition.strip(),
        aliases=json.dumps(_clean_aliases(payload.aliases)),
        created_by=context.user_id,
    )
    db.add(term)
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="project.glossary.create",
        resource_type="project_glossary_term",
        resource_id=term.id,
    )
    db.commit()
    db.refresh(term)
    return _glossary_response(term)


@router.patch("/{project_id}/glossary/{term_id}", response_model=ProjectGlossaryTermResponse)
def update_project_glossary_term(
    project_id: str,
    term_id: str,
    payload: ProjectGlossaryTermUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ProjectGlossaryTermResponse:
    require_permission(context, "project.glossary.manage")
    project = _get_project_or_404(db, context, project_id)
    if project.status == "archived":
        raise bad_request("Archived projects cannot be edited")
    term = db.get(ProjectGlossaryTerm, term_id)
    if term is None or term.project_id != project.id or term.tenant_id != context.tenant_id:
        raise not_found("Glossary term not found")
    term.term = payload.term.strip()
    term.definition = payload.definition.strip()
    term.aliases = json.dumps(_clean_aliases(payload.aliases))
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="project.glossary.update",
        resource_type="project_glossary_term",
        resource_id=term.id,
    )
    db.commit()
    db.refresh(term)
    return _glossary_response(term)


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def list_project_members(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[ProjectMember]:
    require_permission(context, "project.member.view")
    _get_project_or_404(db, context, project_id)
    return list(
        db.scalars(
            select(ProjectMember)
            .where(ProjectMember.tenant_id == context.tenant_id, ProjectMember.project_id == project_id)
            .order_by(ProjectMember.created_at.asc())
        )
    )


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
def add_project_member(
    project_id: str,
    payload: ProjectMemberCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ProjectMember:
    require_permission(context, "project.member.manage")
    project = _get_project_or_404(db, context, project_id)
    tenant_member = db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == context.tenant_id,
            TenantMember.user_id == payload.user_id,
        )
    )
    if tenant_member is None:
        raise bad_request("User must be a tenant member before joining a project")
    project_member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == payload.user_id,
        )
    )
    if project_member is None:
        project_member = ProjectMember(
            tenant_id=context.tenant_id,
            project_id=project.id,
            user_id=payload.user_id,
            role=payload.role,
            created_by=context.user_id,
        )
        db.add(project_member)
    else:
        project_member.role = payload.role
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="project.member.manage",
        resource_type="project",
        resource_id=project.id,
        details={"member_user_id": payload.user_id, "role": payload.role},
    )
    db.commit()
    db.refresh(project_member)
    return project_member
