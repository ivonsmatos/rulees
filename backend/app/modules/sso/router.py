"""
SSO/SAML router.

Endpoints públicos (sem JWT):
  GET  /sso/{tenant_slug}/metadata  → SP metadata XML
  GET  /sso/{tenant_slug}/login     → inicia fluxo SSO
  POST /sso/callback                → consome SAMLResponse, emite JWT Rulees

Endpoints protegidos (admin):
  POST /sso/config   → configura IdP
  GET  /sso/config   → lê config atual
  PUT  /sso/config   → atualiza
"""

import json

from fastapi import APIRouter, Depends, Form
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, not_found
from app.core.security import create_access_token
from app.core.settings import get_settings
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import Tenant, TenantMember, User
from app.modules.permissions.service import require_permission
from app.modules.sso import service
from app.modules.sso.schemas import (
    SsoConfigCreate,
    SsoConfigResponse,
    SsoLoginInitResponse,
)

router = APIRouter(prefix="/sso", tags=["sso"])
settings = get_settings()


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.post("/config", response_model=SsoConfigResponse, status_code=201)
def upsert_sso_config(
    payload: SsoConfigCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> SsoConfigResponse:
    require_permission(context, "sso.manage")
    sp_entity = payload.sp_entity_id or f"rulees:{context.tenant_id}"
    cfg = service.create_sso_config(
        db,
        tenant_id=context.tenant_id,
        created_by=context.user_id,
        provider_name=payload.provider_name,
        entity_id=str(payload.entity_id),
        sso_url=str(payload.sso_url),
        slo_url=str(payload.slo_url) if payload.slo_url else None,
        x509_cert=payload.x509_cert,
        attribute_map=payload.attribute_map,
        sp_entity_id=sp_entity,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="sso.config.upserted",
        resource_type="sso_config",
        resource_id=cfg.id,
        details={"provider": payload.provider_name},
    )
    db.commit()
    db.refresh(cfg)
    return _to_response(cfg)


@router.get("/config", response_model=SsoConfigResponse)
def get_sso_config(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> SsoConfigResponse:
    require_permission(context, "sso.manage")
    cfg = service.get_sso_config(db, tenant_id=context.tenant_id)
    if cfg is None:
        raise not_found("Configuração SSO não encontrada")
    return _to_response(cfg)


# ── Public SP endpoints ───────────────────────────────────────────────────────

@router.get("/{tenant_slug}/metadata")
def sp_metadata(tenant_slug: str, db: Session = Depends(get_db)) -> Response:
    tenant: Tenant | None = db.scalar(select(Tenant).where(Tenant.slug == tenant_slug))
    if tenant is None:
        raise not_found("Tenant não encontrado")
    cfg = service.get_sso_config(db, tenant_id=tenant.id)
    if cfg is None:
        raise not_found("SSO não configurado para este tenant")
    base_url = settings.frontend_origin.replace(":5173", ":8001")  # backend URL
    sp_entity = cfg.sp_entity_id or f"rulees:{tenant.id}"
    xml = service.build_sp_metadata(tenant.id, sp_entity, base_url)
    return Response(content=xml, media_type="application/xml")


@router.get("/{tenant_slug}/login", response_model=SsoLoginInitResponse)
def sso_login(
    tenant_slug: str,
    redirect_url: str = "/",
    db: Session = Depends(get_db),
) -> SsoLoginInitResponse:
    tenant: Tenant | None = db.scalar(select(Tenant).where(Tenant.slug == tenant_slug))
    if tenant is None:
        raise not_found("Tenant não encontrado")
    cfg = service.get_sso_config(db, tenant_id=tenant.id)
    if cfg is None:
        raise not_found("SSO não configurado para este tenant")
    result = service.initiate_sso_login(db, config=cfg, redirect_url=redirect_url)
    db.commit()
    return SsoLoginInitResponse(**result)


@router.post("/callback")
def sso_callback(
    SAMLResponse: str = Form(...),
    RelayState: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> dict:
    """
    Consome SAMLResponse do IdP.
    Cria User + TenantMember se não existir (JIT provisioning).
    Retorna access_token JWT Rulees.
    """
    try:
        attrs = service.process_saml_response(
            db,
            saml_response_b64=SAMLResponse,
            relay_state=RelayState,
        )
    except ValueError as exc:
        raise bad_request(str(exc)) from exc

    email: str = attrs["email"]
    name: str = attrs.get("name", email)
    tenant_id: str = attrs["tenant_id"]

    # JIT: cria user se não existir
    user: User | None = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(
            name=name,
            email=email,
            password_hash="sso_no_password",
        )
        db.add(user)
        db.flush()

    # Garante membership no tenant
    member: TenantMember | None = db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == user.id,
        )
    )
    if member is None:
        member = TenantMember(
            tenant_id=tenant_id,
            user_id=user.id,
            role="member",
        )
        db.add(member)
        db.flush()

    write_audit_log(
        db,
        tenant_id=tenant_id,
        user_id=user.id,
        action="sso.login",
        resource_type="user",
        resource_id=user.id,
        details={"email": email, "jit_provisioned": member is None},
    )
    db.commit()

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "tenant_id": tenant_id}


def _to_response(cfg) -> SsoConfigResponse:
    try:
        attr_map = json.loads(cfg.attribute_map)
    except Exception:
        attr_map = {}
    return SsoConfigResponse(
        id=cfg.id,
        tenant_id=cfg.tenant_id,
        provider_name=cfg.provider_name,
        entity_id=cfg.entity_id,
        sso_url=cfg.sso_url,
        slo_url=cfg.slo_url,
        sp_entity_id=cfg.sp_entity_id,
        attribute_map=attr_map,
        is_active=cfg.is_active,
        created_at=cfg.created_at,
        updated_at=cfg.updated_at,
    )
