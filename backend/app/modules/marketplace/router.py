"""Marketplace router — plugins e integrações disponíveis para tenants."""

import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import conflict, not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.marketplace.models import MarketplacePlugin, TenantPlugin
from app.modules.marketplace.schemas import (
    PluginInstallRequest,
    PluginResponse,
    PluginUpdateRequest,
    TenantPluginResponse,
)
from app.modules.permissions.service import require_permission

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


def _plugin_response(p: MarketplacePlugin) -> PluginResponse:
    try:
        schema = json.loads(p.config_schema)
    except Exception:
        schema = {}
    return PluginResponse(
        id=p.id,
        slug=p.slug,
        name=p.name,
        description=p.description,
        category=p.category,
        is_official=p.is_official,
        version=p.version,
        config_schema=schema,
    )


def _tenant_plugin_response(tp: TenantPlugin) -> TenantPluginResponse:
    try:
        cfg = json.loads(tp.config_json)
    except Exception:
        cfg = {}
    return TenantPluginResponse(
        id=tp.id,
        plugin_id=tp.plugin_id,
        plugin_slug=tp.plugin_slug,
        config=cfg,
        is_enabled=tp.is_enabled,
        installed_by=tp.installed_by,
        installed_at=tp.installed_at,
    )


# ── Catálogo ──────────────────────────────────────────────────────────────────

@router.get("/plugins", response_model=list[PluginResponse])
def list_plugins(
    category: str | None = None,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list:
    require_permission(context, "marketplace.view")
    q = select(MarketplacePlugin).where(MarketplacePlugin.is_active == True)  # noqa: E712
    if category:
        q = q.where(MarketplacePlugin.category == category)
    plugins = list(db.scalars(q.order_by(MarketplacePlugin.name)))
    return [_plugin_response(p) for p in plugins]


@router.get("/plugins/{slug}", response_model=PluginResponse)
def get_plugin(
    slug: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> PluginResponse:
    require_permission(context, "marketplace.view")
    plugin = db.scalar(
        select(MarketplacePlugin).where(
            MarketplacePlugin.slug == slug,
            MarketplacePlugin.is_active == True,  # noqa: E712
        )
    )
    if plugin is None:
        raise not_found("Plugin não encontrado")
    return _plugin_response(plugin)


# ── Instalações do tenant ─────────────────────────────────────────────────────

@router.get("/installed", response_model=list[TenantPluginResponse])
def list_installed(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list:
    require_permission(context, "marketplace.view")
    items = list(db.scalars(
        select(TenantPlugin).where(TenantPlugin.tenant_id == context.tenant_id)
        .order_by(TenantPlugin.installed_at.desc())
    ))
    return [_tenant_plugin_response(tp) for tp in items]


@router.post("/install/{slug}", response_model=TenantPluginResponse, status_code=201)
def install_plugin(
    slug: str,
    payload: PluginInstallRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> TenantPluginResponse:
    require_permission(context, "marketplace.install")
    plugin = db.scalar(
        select(MarketplacePlugin).where(
            MarketplacePlugin.slug == slug,
            MarketplacePlugin.is_active == True,  # noqa: E712
        )
    )
    if plugin is None:
        raise not_found("Plugin não encontrado")
    existing = db.scalar(
        select(TenantPlugin).where(
            TenantPlugin.tenant_id == context.tenant_id,
            TenantPlugin.plugin_id == plugin.id,
        )
    )
    if existing:
        raise conflict("Plugin já instalado neste tenant")
    tp = TenantPlugin(
        tenant_id=context.tenant_id,
        plugin_id=plugin.id,
        plugin_slug=slug,
        config_json=json.dumps(payload.config),
        installed_by=context.user_id,
    )
    db.add(tp)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="marketplace.plugin.installed",
        resource_type="tenant_plugin",
        details={"slug": slug},
    )
    db.commit()
    db.refresh(tp)
    return _tenant_plugin_response(tp)


@router.patch("/installed/{installation_id}", response_model=TenantPluginResponse)
def update_installation(
    installation_id: str,
    payload: PluginUpdateRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> TenantPluginResponse:
    require_permission(context, "marketplace.install")
    tp = db.scalar(
        select(TenantPlugin).where(
            TenantPlugin.id == installation_id,
            TenantPlugin.tenant_id == context.tenant_id,
        )
    )
    if tp is None:
        raise not_found("Instalação não encontrada")
    if payload.config is not None:
        tp.config_json = json.dumps(payload.config)
    if payload.is_enabled is not None:
        tp.is_enabled = payload.is_enabled
    db.add(tp)
    db.commit()
    db.refresh(tp)
    return _tenant_plugin_response(tp)


@router.delete("/installed/{installation_id}", status_code=204)
def uninstall_plugin(
    installation_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> None:
    require_permission(context, "marketplace.install")
    tp = db.scalar(
        select(TenantPlugin).where(
            TenantPlugin.id == installation_id,
            TenantPlugin.tenant_id == context.tenant_id,
        )
    )
    if tp is None:
        raise not_found("Instalação não encontrada")
    slug = tp.plugin_slug
    db.delete(tp)
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="marketplace.plugin.uninstalled",
        resource_type="tenant_plugin",
        details={"slug": slug},
    )
    db.commit()
