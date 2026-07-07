import json
from difflib import ndiff

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import feature_disabled, not_found
from app.core.settings import get_settings
from app.core.signed_storage import create_signed_storage_token, verify_signed_storage_token, write_private_file
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.ai_agents.service import write_agent_run
from app.modules.billing.service import ensure_billing_limit
from app.modules.decisions.models import Decision
from app.modules.documents.models import Document, DocumentExportJob, DocumentSection, DocumentTemplate, DocumentTemplateSection, DocumentVersion
from app.modules.documents.excel import build_document_xlsx
from app.modules.documents.pdf import build_simple_pdf
from app.modules.documents.schemas import (
    DocumentResponse,
    DocumentUpdate,
    DocumentExportJobCreate,
    DocumentExportJobResponse,
    DocumentSectionCreate,
    DocumentSectionResponse,
    DocumentSectionUpdate,
    DocumentTemplateSectionResponse,
    DocumentTemplateCreate,
    DocumentTemplateResponse,
    DocumentTemplateUpdate,
    DocumentVersionCreate,
    DocumentVersionResponse,
    ApplyTemplateRequest,
    SectionReorderRequest,
    SignedExportUrlResponse,
    VersionDiffResponse,
)
from app.modules.documents.service import (
    build_confluence_payload,
    build_jira_payload,
    create_document_sections,
    create_document_version,
    render_markdown_export,
    render_document_content,
)
from app.modules.meetings.models import Meeting, TranscriptChunk
from app.modules.permissions.service import require_permission
from app.modules.questions.models import OpenQuestion
from app.modules.rules_ledger.models import BusinessRule
from app.modules.usage.service import write_usage_event

router = APIRouter()

settings = get_settings()


def _get_meeting(db: Session, context: RequestContext, meeting_id: str) -> Meeting:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.tenant_id != context.tenant_id:
        raise not_found("Meeting not found")
    return meeting


def _get_document(db: Session, context: RequestContext, document_id: str) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.tenant_id != context.tenant_id:
        raise not_found("Document not found")
    return document


def _document_markdown(db: Session, document: Document) -> str:
    return render_markdown_export(document, _document_sections(db, document))


def _document_sections(db: Session, document: Document) -> list[DocumentSection]:
    return list(
        db.scalars(
            select(DocumentSection)
            .where(DocumentSection.tenant_id == document.tenant_id, DocumentSection.document_id == document.id)
            .order_by(DocumentSection.sort_order.asc())
        )
    )


def _diff_lines(left: str, right: str) -> list[dict]:
    mapped = []
    for line in ndiff(left.splitlines(), right.splitlines()):
        marker = line[:2]
        if marker == "  ":
            kind = "context"
        elif marker == "- ":
            kind = "removed"
        elif marker == "+ ":
            kind = "added"
        else:
            continue
        mapped.append({"kind": kind, "text": line[2:]})
    return mapped[:500]


@router.post("/meetings/{meeting_id}/documents/generate", response_model=DocumentResponse)
def generate_document(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Document:
    require_permission(context, "document.generate")
    if not get_settings().document_generation_enabled:
        raise feature_disabled("Geração de documentos está temporariamente desativada.")
    meeting = _get_meeting(db, context, meeting_id)
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="document_generated")
    transcript = list(
        db.scalars(
            select(TranscriptChunk)
            .where(TranscriptChunk.tenant_id == context.tenant_id, TranscriptChunk.meeting_id == meeting.id)
            .order_by(TranscriptChunk.created_at.asc())
        )
    )
    approved_rules = list(
        db.scalars(
            select(BusinessRule)
            .where(
                BusinessRule.tenant_id == context.tenant_id,
                BusinessRule.meeting_id == meeting.id,
                BusinessRule.status == "approved",
            )
            .order_by(BusinessRule.created_at.asc())
        )
    )
    draft_rules = list(
        db.scalars(
            select(BusinessRule)
            .where(
                BusinessRule.tenant_id == context.tenant_id,
                BusinessRule.meeting_id == meeting.id,
                BusinessRule.status != "rejected",
            )
            .order_by(BusinessRule.created_at.asc())
        )
    )
    rule_lines = approved_rules or draft_rules
    questions = list(
        db.scalars(
            select(OpenQuestion)
            .where(OpenQuestion.tenant_id == context.tenant_id, OpenQuestion.meeting_id == meeting.id)
            .order_by(OpenQuestion.created_at.asc())
        )
    )
    decisions = list(
        db.scalars(
            select(Decision)
            .where(Decision.tenant_id == context.tenant_id, Decision.meeting_id == meeting.id)
            .order_by(Decision.created_at.asc())
        )
    )
    title = f"Documento funcional - {meeting.title}"
    sections = [
        {
            "section_key": "summary",
            "title": "Resumo",
            "body": meeting.objective or "Documento gerado a partir da reuniao.",
        },
        {
            "section_key": "rules",
            "title": "Regras",
            "body": "\n".join(
                [f"- {rule.code}: {rule.rule_text} ({rule.status})" for rule in rule_lines]
                or ["- Nenhuma regra registrada."]
            ),
        },
        {
            "section_key": "evidence",
            "title": "Evidencias",
            "body": "\n".join(
                [f"- {chunk.normalized_text}" for chunk in transcript]
                or ["- Nenhuma transcricao registrada."]
            ),
        },
        {
            "section_key": "questions",
            "title": "Duvidas abertas",
            "body": "\n".join(
                [f"- {question.question_text} ({question.priority})" for question in questions]
                or ["- Nenhuma duvida aberta registrada."]
            ),
        },
        {
            "section_key": "decisions",
            "title": "Decisoes detectadas",
            "body": "\n".join(
                [f"- {decision.decision_text} ({decision.status})" for decision in decisions]
                or ["- Nenhuma decisao detectada."]
            ),
        },
    ]
    document = Document(
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        title=title,
        content=render_document_content(title, sections),
        status="ready",
    )
    db.add(document)
    db.flush()
    requirements_run = write_agent_run(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        agent_name="Requirements",
        agent_role="requirements_analyst",
        input_reference={
            "source_type": "meeting",
            "source_ids": [meeting.id],
        },
        output={
            "requirements": [
                {
                    "source": rule.code,
                    "text": rule.rule_text,
                    "status": rule.status,
                }
                for rule in rule_lines
            ],
            "source_references": [
                {"source_type": "business_rule", "source_id": rule.id}
                for rule in rule_lines
            ],
        },
        confidence_score=0.72,
    )
    tech_writer_run = write_agent_run(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        agent_name="Tech Writer",
        agent_role="technical_writer",
        input_reference={
            "source_type": "requirements_agent_run",
            "source_ids": [requirements_run.run_id],
        },
        output={
            "document_id": document.id,
            "sections": [{"section_key": section["section_key"], "title": section["title"]} for section in sections],
        },
        confidence_score=0.78,
    )
    write_agent_run(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        agent_name="Traceability",
        agent_role="traceability_mapper",
        input_reference={
            "source_type": "document",
            "source_ids": [document.id],
        },
        output={
            "links": [
                {
                    "from_type": "business_rule",
                    "from_id": rule.id,
                    "to_type": "document",
                    "to_id": document.id,
                }
                for rule in rule_lines
            ]
        },
        confidence_score=0.76,
    )
    write_agent_run(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        agent_name="Compliance",
        agent_role="compliance_checker",
        input_reference={
            "source_type": "document",
            "source_ids": [document.id],
        },
        output={
            "checks": [
                {"name": "has_summary", "passed": bool(sections[0]["body"])},
                {"name": "has_evidence_section", "passed": True},
                {"name": "has_human_review_status", "passed": all(rule.status for rule in rule_lines)},
            ],
            "warnings": [] if rule_lines else [{"code": "NO_RULES", "message": "Documento gerado sem regras aprovadas"}],
        },
        confidence_score=0.7,
        metadata={"depends_on_run_id": tech_writer_run.run_id},
    )
    create_document_sections(
        db,
        tenant_id=context.tenant_id,
        document_id=document.id,
        sections=sections,
    )
    create_document_version(
        db,
        document,
        created_by=context.user_id,
        change_reason="Documento gerado automaticamente",
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.generate",
        resource_type="document",
        resource_id=document.id,
        details={"meeting_id": meeting.id},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="document_generated",
        details={"document_id": document.id},
    )
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[Document]:
    require_permission(context, "document.view")
    return list(
        db.scalars(
            select(Document)
            .where(Document.tenant_id == context.tenant_id)
            .order_by(Document.created_at.desc())
        )
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Document:
    require_permission(context, "document.view")
    document = db.get(Document, document_id)
    if document is None or document.tenant_id != context.tenant_id:
        raise not_found("Document not found")
    return document


@router.get("/documents/{document_id}/sections", response_model=list[DocumentSectionResponse])
def list_document_sections(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[DocumentSection]:
    require_permission(context, "document.section.view")
    document = db.get(Document, document_id)
    if document is None or document.tenant_id != context.tenant_id:
        raise not_found("Document not found")
    return list(
        db.scalars(
            select(DocumentSection)
            .where(
                DocumentSection.tenant_id == context.tenant_id,
                DocumentSection.document_id == document.id,
            )
            .order_by(DocumentSection.sort_order.asc())
        )
    )


@router.get("/documents/{document_id}/versions", response_model=list[DocumentVersionResponse])
def list_document_versions(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[DocumentVersion]:
    require_permission(context, "document.version.view")
    document = db.get(Document, document_id)
    if document is None or document.tenant_id != context.tenant_id:
        raise not_found("Document not found")
    return list(
        db.scalars(
            select(DocumentVersion)
            .where(
                DocumentVersion.tenant_id == context.tenant_id,
                DocumentVersion.document_id == document.id,
            )
            .order_by(DocumentVersion.version_number.desc())
        )
    )


@router.post("/documents/{document_id}/versions", response_model=DocumentResponse)
def create_document_revision(
    document_id: str,
    payload: DocumentVersionCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Document:
    require_permission(context, "document.version.create")
    document = db.get(Document, document_id)
    if document is None or document.tenant_id != context.tenant_id:
        raise not_found("Document not found")
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="document_version_created")
    document.title = payload.title.strip() if payload.title else document.title
    document.content = payload.content.strip()
    document.status = "draft"
    version = create_document_version(
        db,
        document,
        created_by=context.user_id,
        change_reason=payload.change_reason,
    )
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.version.create",
        resource_type="document",
        resource_id=document.id,
        details={"version_number": version.version_number},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=document.project_id,
        meeting_id=document.meeting_id,
        user_id=context.user_id,
        event_type="document_version_created",
        details={"document_id": document.id, "version_number": version.version_number},
    )
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents/{document_id}/export/markdown")
def export_markdown(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Response:
    require_permission(context, "document.export")
    if not get_settings().export_enabled:
        raise feature_disabled("Exportação está temporariamente desativada.")
    document = _get_document(db, context, document_id)
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="markdown_exported")
    markdown = _document_markdown(db, document)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.export.markdown",
        resource_type="document",
        resource_id=document.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=document.project_id,
        meeting_id=document.meeting_id,
        user_id=context.user_id,
        event_type="markdown_exported",
        details={"document_id": document.id},
    )
    db.commit()
    return Response(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{document.id}.md"'},
    )


@router.get("/documents/{document_id}/export/excel")
def export_excel(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Response:
    require_permission(context, "document.export")
    if not get_settings().export_enabled:
        raise feature_disabled("Exportação está temporariamente desativada.")
    document = _get_document(db, context, document_id)
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="excel_exported")
    content = build_document_xlsx(document, _document_sections(db, document))
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.export.excel",
        resource_type="document",
        resource_id=document.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=document.project_id,
        meeting_id=document.meeting_id,
        user_id=context.user_id,
        event_type="excel_exported",
        details={"document_id": document.id},
    )
    db.commit()
    return Response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{document.id}.xlsx"'},
    )


@router.get("/documents/{document_id}/export/{format}/signed-url", response_model=SignedExportUrlResponse)
def signed_export_url(
    document_id: str,
    format: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> SignedExportUrlResponse:
    require_permission(context, "document.export")
    document = _get_document(db, context, document_id)
    if format == "pdf":
        content = build_simple_pdf(document.title, document.content)
        media_type = "application/pdf"
        filename = f"{document.id}.pdf"
    elif format == "markdown":
        content = _document_markdown(db, document).encode("utf-8")
        media_type = "text/markdown; charset=utf-8"
        filename = f"{document.id}.md"
    elif format == "excel":
        content = build_document_xlsx(document, _document_sections(db, document))
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{document.id}.xlsx"
    else:
        raise not_found("Export format not found")
    relative_path = f"tenants/{context.tenant_id}/exports/{filename}"
    write_private_file(settings, tenant_id=context.tenant_id, filename=f"exports/{filename}", content=content)
    token = create_signed_storage_token(
        settings,
        tenant_id=context.tenant_id,
        path=relative_path,
        media_type=media_type,
        filename=filename,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action=f"document.export.{format}.signed_url",
        resource_type="document",
        resource_id=document.id,
    )
    db.commit()
    return SignedExportUrlResponse(url=f"/api/storage/signed/{token}", expires_in_seconds=settings.signed_url_expire_seconds)


@router.get("/storage/signed/{token}")
def download_signed_storage(token: str) -> Response:
    try:
        payload = verify_signed_storage_token(settings, token)
    except ValueError as exc:
        raise not_found(str(exc)) from exc
    path = payload["resolved_path"]
    content = open(path, "rb").read()
    return Response(
        content,
        media_type=payload["media_type"],
        headers={"Content-Disposition": f'attachment; filename="{payload["filename"]}"'},
    )


@router.get("/documents/{document_id}/versions/diff", response_model=VersionDiffResponse)
def document_version_diff(
    document_id: str,
    from_version: int,
    to_version: int,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> VersionDiffResponse:
    require_permission(context, "document.version.view")
    document = _get_document(db, context, document_id)
    versions = list(
        db.scalars(
            select(DocumentVersion).where(
                DocumentVersion.tenant_id == context.tenant_id,
                DocumentVersion.document_id == document.id,
                DocumentVersion.version_number.in_([from_version, to_version]),
            )
        )
    )
    by_number = {version.version_number: version for version in versions}
    if from_version not in by_number or to_version not in by_number:
        raise not_found("Version not found")
    return VersionDiffResponse(
        resource_type="document",
        resource_id=document.id,
        from_version=from_version,
        to_version=to_version,
        lines=_diff_lines(by_number[from_version].content, by_number[to_version].content),
    )


@router.get("/documents/{document_id}/export-jobs", response_model=list[DocumentExportJobResponse])
def list_export_jobs(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[DocumentExportJob]:
    require_permission(context, "document.export")
    document = _get_document(db, context, document_id)
    return list(
        db.scalars(
            select(DocumentExportJob)
            .where(
                DocumentExportJob.tenant_id == context.tenant_id,
                DocumentExportJob.document_id == document.id,
            )
            .order_by(DocumentExportJob.created_at.desc())
        )
    )


@router.post("/documents/{document_id}/export-jobs", response_model=DocumentExportJobResponse)
def create_export_job(
    document_id: str,
    payload: DocumentExportJobCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DocumentExportJob:
    require_permission(context, "document.export")
    document = _get_document(db, context, document_id)
    event_type = f"{payload.format}_exported" if payload.format in {"pdf", "markdown", "excel"} else "export_job_created"
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type=event_type)
    markdown = _document_markdown(db, document)
    payload_data: dict
    result_url: str | None = None
    if payload.format == "jira":
        payload_data = build_jira_payload(document, markdown)
    elif payload.format == "confluence":
        payload_data = build_confluence_payload(document, markdown)
    else:
        payload_data = {"document_id": document.id, "download_format": payload.format}
        result_url = f"/api/documents/{document.id}/export/{payload.format}"

    job = DocumentExportJob(
        tenant_id=context.tenant_id,
        project_id=document.project_id,
        meeting_id=document.meeting_id,
        document_id=document.id,
        format=payload.format,
        status="completed",
        payload=json.dumps(payload_data, ensure_ascii=False),
        result_url=result_url,
        created_by=context.user_id,
    )
    db.add(job)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action=f"document.export_job.{payload.format}",
        resource_type="document",
        resource_id=document.id,
        details={"job_format": payload.format},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=document.project_id,
        meeting_id=document.meeting_id,
        user_id=context.user_id,
        event_type=event_type,
        details={"document_id": document.id, "job_format": payload.format},
    )
    document.status = "exported"
    db.commit()
    db.refresh(job)
    return job


@router.get("/documents/{document_id}/export/pdf")
def export_pdf(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Response:
    require_permission(context, "document.export")
    document = _get_document(db, context, document_id)
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="pdf_exported")
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.export.pdf",
        resource_type="document",
        resource_id=document.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=document.project_id,
        meeting_id=document.meeting_id,
        user_id=context.user_id,
        event_type="pdf_exported",
        details={"document_id": document.id},
    )
    document.status = "exported"
    db.commit()
    return Response(
        build_simple_pdf(document.title, document.content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{document.id}.pdf"'},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EDITOR COMPLETO DE DOCUMENTO
# ═══════════════════════════════════════════════════════════════════════════════

@router.patch("/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    payload: DocumentUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Document:
    """Edita título e/ou status do documento."""
    require_permission(context, "document.version.create")
    document = _get_document(db, context, document_id)
    changed = False
    if payload.title is not None:
        document.title = payload.title.strip()
        changed = True
    if payload.status is not None:
        document.status = payload.status
        changed = True
    if changed:
        write_audit_log(
            db,
            tenant_id=context.tenant_id,
            user_id=context.user_id,
            action="document.updated",
            resource_type="document",
            resource_id=document.id,
            details={"title": payload.title, "status": payload.status},
        )
        db.commit()
        db.refresh(document)
    return document


@router.post("/documents/{document_id}/sections", response_model=DocumentSectionResponse, status_code=201)
def add_section(
    document_id: str,
    payload: DocumentSectionCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DocumentSection:
    """Adiciona uma nova seção ao documento."""
    require_permission(context, "document.version.create")
    document = _get_document(db, context, document_id)
    # evita section_key duplicada no mesmo documento
    existing = db.scalar(
        select(DocumentSection).where(
            DocumentSection.document_id == document.id,
            DocumentSection.section_key == payload.section_key,
        )
    )
    if existing:
        from app.core.errors import conflict
        raise conflict(f"section_key '{payload.section_key}' já existe neste documento")
    section = DocumentSection(
        tenant_id=context.tenant_id,
        document_id=document.id,
        section_key=payload.section_key,
        title=payload.title,
        body=payload.body,
        sort_order=payload.sort_order,
    )
    db.add(section)
    _sync_document_content(db, document)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.section.added",
        resource_type="document",
        resource_id=document.id,
        details={"section_key": payload.section_key},
    )
    db.commit()
    db.refresh(section)
    return section


@router.patch("/documents/{document_id}/sections/{section_id}", response_model=DocumentSectionResponse)
def update_section(
    document_id: str,
    section_id: str,
    payload: DocumentSectionUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DocumentSection:
    """Edita título, corpo e/ou ordem de uma seção."""
    require_permission(context, "document.version.create")
    document = _get_document(db, context, document_id)
    section = db.scalar(
        select(DocumentSection).where(
            DocumentSection.id == section_id,
            DocumentSection.document_id == document.id,
            DocumentSection.tenant_id == context.tenant_id,
        )
    )
    if section is None:
        raise not_found("Seção não encontrada")
    if payload.title is not None:
        section.title = payload.title
    if payload.body is not None:
        section.body = payload.body
    if payload.sort_order is not None:
        section.sort_order = payload.sort_order
    db.add(section)
    _sync_document_content(db, document)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.section.updated",
        resource_type="document",
        resource_id=document.id,
        details={"section_id": section_id},
    )
    db.commit()
    db.refresh(section)
    return section


@router.delete("/documents/{document_id}/sections/{section_id}", status_code=204)
def delete_section(
    document_id: str,
    section_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> None:
    """Remove uma seção do documento."""
    require_permission(context, "document.version.create")
    document = _get_document(db, context, document_id)
    section = db.scalar(
        select(DocumentSection).where(
            DocumentSection.id == section_id,
            DocumentSection.document_id == document.id,
            DocumentSection.tenant_id == context.tenant_id,
        )
    )
    if section is None:
        raise not_found("Seção não encontrada")
    db.delete(section)
    db.flush()
    _sync_document_content(db, document)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.section.deleted",
        resource_type="document",
        resource_id=document.id,
        details={"section_id": section_id},
    )
    db.commit()


@router.put("/documents/{document_id}/sections/reorder", response_model=list[DocumentSectionResponse])
def reorder_sections(
    document_id: str,
    payload: SectionReorderRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[DocumentSection]:
    """Reordena seções em lote. Body: {sections: [{id, sort_order}, ...]}"""
    require_permission(context, "document.version.create")
    document = _get_document(db, context, document_id)
    order_map = {item.id: item.sort_order for item in payload.sections}
    sections = list(db.scalars(
        select(DocumentSection).where(
            DocumentSection.document_id == document.id,
            DocumentSection.tenant_id == context.tenant_id,
        )
    ))
    for sec in sections:
        if sec.id in order_map:
            sec.sort_order = order_map[sec.id]
            db.add(sec)
    db.flush()
    _sync_document_content(db, document)
    db.commit()
    return sorted(sections, key=lambda s: s.sort_order)


def _sync_document_content(db, document: Document) -> None:
    """Re-renderiza document.content a partir das seções atuais (mantém consistência)."""
    sections = list(db.scalars(
        select(DocumentSection)
        .where(DocumentSection.document_id == document.id)
        .order_by(DocumentSection.sort_order.asc())
    ))
    document.content = render_document_content(
        document.title,
        [{"title": s.title, "body": s.body} for s in sections],
    )
    db.add(document)


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES FUNCIONAIS DE DOCUMENTO
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/document-templates", response_model=DocumentTemplateResponse, status_code=201)
def create_document_template(
    payload: DocumentTemplateCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DocumentTemplateResponse:
    require_permission(context, "document.generate")
    if payload.is_default:
        # remove flag default dos outros templates da categoria
        db.execute(
            select(DocumentTemplate).where(
                DocumentTemplate.tenant_id == context.tenant_id,
                DocumentTemplate.category == payload.category,
                DocumentTemplate.is_default == True,  # noqa: E712
            )
        )
        for existing in db.scalars(
            select(DocumentTemplate).where(
                DocumentTemplate.tenant_id == context.tenant_id,
                DocumentTemplate.category == payload.category,
                DocumentTemplate.is_default == True,  # noqa: E712
            )
        ):
            existing.is_default = False
            db.add(existing)

    tmpl = DocumentTemplate(
        tenant_id=context.tenant_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        is_default=payload.is_default,
        created_by=context.user_id,
    )
    db.add(tmpl)
    db.flush()

    sections = _upsert_template_sections(db, tmpl, payload.sections)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document_template.created",
        resource_type="document_template",
        resource_id=tmpl.id,
        details={"name": payload.name, "sections": len(sections)},
    )
    db.commit()
    db.refresh(tmpl)
    return _template_response(db, tmpl)


@router.get("/document-templates", response_model=list[DocumentTemplateResponse])
def list_document_templates(
    category: str | None = None,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list:
    require_permission(context, "document.view")
    q = select(DocumentTemplate).where(
        DocumentTemplate.tenant_id == context.tenant_id,
        DocumentTemplate.archived_at.is_(None),
    )
    if category:
        q = q.where(DocumentTemplate.category == category)
    templates = list(db.scalars(q.order_by(DocumentTemplate.name.asc())))
    return [_template_response(db, t) for t in templates]


@router.get("/document-templates/{template_id}", response_model=DocumentTemplateResponse)
def get_document_template(
    template_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DocumentTemplateResponse:
    require_permission(context, "document.view")
    tmpl = _get_template(db, context, template_id)
    return _template_response(db, tmpl)


@router.put("/document-templates/{template_id}", response_model=DocumentTemplateResponse)
def update_document_template(
    template_id: str,
    payload: DocumentTemplateUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DocumentTemplateResponse:
    require_permission(context, "document.generate")
    from datetime import datetime, timezone as _tz
    tmpl = _get_template(db, context, template_id)
    if payload.name is not None:
        tmpl.name = payload.name
    if payload.description is not None:
        tmpl.description = payload.description
    if payload.category is not None:
        tmpl.category = payload.category
    if payload.is_default is not None:
        tmpl.is_default = payload.is_default
    tmpl.updated_at = datetime.now(_tz.utc)
    db.add(tmpl)
    if payload.sections is not None:
        # substitui todas as seções
        db.query(DocumentTemplateSection).filter(
            DocumentTemplateSection.template_id == tmpl.id
        ).delete()
        db.flush()
        _upsert_template_sections(db, tmpl, payload.sections)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document_template.updated",
        resource_type="document_template",
        resource_id=tmpl.id,
    )
    db.commit()
    db.refresh(tmpl)
    return _template_response(db, tmpl)


@router.delete("/document-templates/{template_id}", status_code=204)
def archive_document_template(
    template_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> None:
    require_permission(context, "document.generate")
    from datetime import datetime, timezone as _tz
    tmpl = _get_template(db, context, template_id)
    tmpl.archived_at = datetime.now(_tz.utc)
    db.add(tmpl)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document_template.archived",
        resource_type="document_template",
        resource_id=tmpl.id,
    )
    db.commit()


@router.post("/documents/{document_id}/apply-template/{template_id}", response_model=list[DocumentSectionResponse])
def apply_template_to_document(
    document_id: str,
    template_id: str,
    payload: ApplyTemplateRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[DocumentSection]:
    """
    Aplica um template ao documento, interpolando variáveis:
    - {{rules}}      → regras aprovadas da reunião
    - {{summary}}    → objetivo da reunião
    - {{decisions}}  → decisões detectadas
    - {{questions}}  → questões abertas
    - {{glossary}}   → termos do glossário do projeto
    - {{custom:x}}   → valor de payload.variables["custom:x"]
    """
    require_permission(context, "document.version.create")
    document = _get_document(db, context, document_id)
    tmpl = _get_template(db, context, template_id)

    # resolve variáveis do contexto da reunião
    variables = _resolve_template_variables(db, document, context, payload.variables)

    tmpl_sections = list(db.scalars(
        select(DocumentTemplateSection)
        .where(DocumentTemplateSection.template_id == tmpl.id)
        .order_by(DocumentTemplateSection.sort_order.asc())
    ))

    if payload.replace_existing:
        db.query(DocumentSection).filter(
            DocumentSection.document_id == document.id
        ).delete()
        db.flush()

    # busca seções já existentes (para modo merge)
    existing_keys = {
        s.section_key
        for s in db.scalars(
            select(DocumentSection).where(DocumentSection.document_id == document.id)
        )
    } if not payload.replace_existing else set()

    new_sections: list[DocumentSection] = []
    for tmpl_sec in tmpl_sections:
        if tmpl_sec.section_key in existing_keys:
            continue  # não sobrescreve seção existente em modo merge
        body = _interpolate(tmpl_sec.body_template, variables)
        sec = DocumentSection(
            tenant_id=context.tenant_id,
            document_id=document.id,
            section_key=tmpl_sec.section_key,
            title=tmpl_sec.title,
            body=body,
            sort_order=tmpl_sec.sort_order,
        )
        db.add(sec)
        new_sections.append(sec)

    db.flush()
    _sync_document_content(db, document)
    create_document_version(
        db,
        document,
        created_by=context.user_id,
        change_reason=f"Template '{tmpl.name}' aplicado",
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.template.applied",
        resource_type="document",
        resource_id=document.id,
        details={"template_id": template_id, "template_name": tmpl.name, "sections_added": len(new_sections)},
    )
    db.commit()
    # retorna todas as seções do documento após aplicação
    return list(db.scalars(
        select(DocumentSection)
        .where(DocumentSection.document_id == document.id)
        .order_by(DocumentSection.sort_order.asc())
    ))


# ── Helpers de template ───────────────────────────────────────────────────────

def _get_template(db, context, template_id: str) -> DocumentTemplate:
    tmpl = db.scalar(
        select(DocumentTemplate).where(
            DocumentTemplate.id == template_id,
            DocumentTemplate.tenant_id == context.tenant_id,
            DocumentTemplate.archived_at.is_(None),
        )
    )
    if tmpl is None:
        raise not_found("Template não encontrado")
    return tmpl


def _upsert_template_sections(
    db, tmpl: DocumentTemplate, sections_payload
) -> list[DocumentTemplateSection]:
    created = []
    for i, sec in enumerate(sections_payload):
        obj = DocumentTemplateSection(
            template_id=tmpl.id,
            tenant_id=tmpl.tenant_id,
            section_key=sec.section_key,
            title=sec.title,
            body_template=sec.body_template,
            sort_order=sec.sort_order if sec.sort_order else i,
            required=sec.required,
        )
        db.add(obj)
        created.append(obj)
    db.flush()
    return created


def _template_response(db, tmpl: DocumentTemplate) -> DocumentTemplateResponse:
    sections = list(db.scalars(
        select(DocumentTemplateSection)
        .where(DocumentTemplateSection.template_id == tmpl.id)
        .order_by(DocumentTemplateSection.sort_order.asc())
    ))
    return DocumentTemplateResponse(
        id=tmpl.id,
        tenant_id=tmpl.tenant_id,
        name=tmpl.name,
        description=tmpl.description,
        category=tmpl.category,
        is_default=tmpl.is_default,
        created_by=tmpl.created_by,
        created_at=tmpl.created_at,
        updated_at=tmpl.updated_at,
        sections=[DocumentTemplateSectionResponse.model_validate(s) for s in sections],
    )


def _resolve_template_variables(
    db, document: Document, context, extra: dict[str, str]
) -> dict[str, str]:
    """Constrói dicionário de variáveis para interpolação do template."""
    from app.modules.meetings.models import Meeting
    from app.modules.rules_ledger.models import BusinessRule
    from app.modules.questions.models import OpenQuestion
    from app.modules.decisions.models import Decision
    from app.modules.projects.models import ProjectGlossaryTerm

    variables: dict[str, str] = {}

    meeting = db.get(Meeting, document.meeting_id)
    if meeting:
        variables["summary"] = meeting.objective or ""

    rules = list(db.scalars(
        select(BusinessRule).where(
            BusinessRule.meeting_id == document.meeting_id,
            BusinessRule.tenant_id == context.tenant_id,
            BusinessRule.status == "approved",
        ).order_by(BusinessRule.created_at.asc())
    ))
    variables["rules"] = "\n".join(
        f"- **{r.code}**: {r.rule_text} _(aprovada)_" for r in rules
    ) or "_Nenhuma regra aprovada._"

    questions = list(db.scalars(
        select(OpenQuestion).where(
            OpenQuestion.meeting_id == document.meeting_id,
            OpenQuestion.tenant_id == context.tenant_id,
        ).order_by(OpenQuestion.created_at.asc())
    ))
    variables["questions"] = "\n".join(
        f"- [{q.priority.upper()}] {q.question_text}" for q in questions
    ) or "_Nenhuma questão aberta._"

    decisions = list(db.scalars(
        select(Decision).where(
            Decision.meeting_id == document.meeting_id,
            Decision.tenant_id == context.tenant_id,
        ).order_by(Decision.created_at.asc())
    ))
    variables["decisions"] = "\n".join(
        f"- {d.decision_text}" for d in decisions
    ) or "_Nenhuma decisão registrada._"

    glossary = list(db.scalars(
        select(ProjectGlossaryTerm).where(
            ProjectGlossaryTerm.project_id == document.project_id,
            ProjectGlossaryTerm.tenant_id == context.tenant_id,
        ).order_by(ProjectGlossaryTerm.term.asc())
    ))
    variables["glossary"] = "\n".join(
        f"- **{g.term}**: {g.definition}" for g in glossary
    ) or "_Glossário vazio._"

    # variáveis extras (custom:xxx)
    variables.update(extra)
    return variables


def _interpolate(template_body: str, variables: dict[str, str]) -> str:
    """Substitui {{var}} e {{custom:nome}} pelos valores do dicionário."""
    import re
    def replacer(match: re.Match) -> str:
        key = match.group(1).strip()
        return variables.get(key, match.group(0))
    return re.sub(r"\{\{([^}]+)\}\}", replacer, template_body)
