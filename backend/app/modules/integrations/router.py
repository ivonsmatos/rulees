"""
Integrations router — Jira, Confluence, Azure DevOps.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import bad_request, not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.documents.models import Document
from app.modules.documents.service import build_confluence_payload, build_jira_payload, render_markdown_export
from app.modules.integrations import service
from app.modules.integrations.schemas import (
    DispatchRequest,
    DispatchResponse,
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
    TestConnectionResponse,
)
from app.modules.permissions.service import require_permission

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("", response_model=IntegrationResponse, status_code=201)
def create_integration(
    payload: IntegrationCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> IntegrationResponse:
    require_permission(context, "integration.manage")
    obj = service.create_integration(
        db,
        tenant_id=context.tenant_id,
        provider=payload.provider,
        label=payload.label,
        config=payload.config,
        created_by=context.user_id,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="integration.created",
        resource_type="integration",
        resource_id=obj.id,
        details={"provider": payload.provider, "label": payload.label},
    )
    db.commit()
    db.refresh(obj)
    return IntegrationResponse.model_validate(obj)


@router.get("", response_model=list[IntegrationResponse])
def list_integrations(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list:
    require_permission(context, "integration.view")
    return [
        IntegrationResponse.model_validate(i)
        for i in service.list_integrations(db, tenant_id=context.tenant_id)
    ]


@router.put("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: str,
    payload: IntegrationUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> IntegrationResponse:
    require_permission(context, "integration.manage")
    obj = service.get_integration(db, tenant_id=context.tenant_id, integration_id=integration_id)
    if obj is None:
        raise not_found("Integração não encontrada")
    obj = service.update_integration(
        db, obj,
        label=payload.label,
        config=payload.config,
        is_active=payload.is_active,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="integration.updated",
        resource_type="integration",
        resource_id=integration_id,
    )
    db.commit()
    db.refresh(obj)
    return IntegrationResponse.model_validate(obj)


@router.delete("/{integration_id}", status_code=204)
def delete_integration(
    integration_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> None:
    require_permission(context, "integration.manage")
    obj = service.get_integration(db, tenant_id=context.tenant_id, integration_id=integration_id)
    if obj is None:
        raise not_found("Integração não encontrada")
    service.delete_integration(db, obj)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="integration.deleted",
        resource_type="integration",
        resource_id=integration_id,
    )
    db.commit()


@router.post("/{integration_id}/test", response_model=TestConnectionResponse)
def test_connection(
    integration_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> TestConnectionResponse:
    require_permission(context, "integration.manage")
    obj = service.get_integration(db, tenant_id=context.tenant_id, integration_id=integration_id)
    if obj is None:
        raise not_found("Integração não encontrada")
    result = service.test_connection(obj)
    return TestConnectionResponse(**result)


@router.post("/dispatch/{document_id}", response_model=DispatchResponse)
def dispatch_document(
    document_id: str,
    payload: DispatchRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DispatchResponse:
    require_permission(context, "document.export")
    doc: Document | None = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == context.tenant_id,
    ).first()
    if doc is None:
        raise not_found("Documento não encontrado")
    integration = service.get_integration(
        db, tenant_id=context.tenant_id, integration_id=payload.integration_id
    )
    if integration is None:
        raise not_found("Integração não encontrada")
    if not integration.is_active:
        raise bad_request("Integração desativada")

    from app.modules.documents.models import DocumentSection
    sections = db.query(DocumentSection).filter(
        DocumentSection.document_id == document_id,
    ).order_by(DocumentSection.sort_order).all()
    markdown = render_markdown_export(doc, list(sections))

    if integration.provider == "jira":
        export_payload = build_jira_payload(doc, markdown)
    elif integration.provider == "confluence":
        export_payload = build_confluence_payload(doc, markdown)
    else:
        export_payload = {"summary": doc.title, "description": markdown}

    dispatch = service.dispatch_document(
        db,
        integration=integration,
        document_id=document_id,
        payload=export_payload,
        dispatched_by=context.user_id,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="document.dispatched",
        resource_type="document",
        resource_id=document_id,
        details={"provider": integration.provider, "status": dispatch.status},
    )
    db.commit()
    db.refresh(dispatch)
    return DispatchResponse.model_validate(dispatch)
