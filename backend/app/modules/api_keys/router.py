"""
API Keys router.

Permite que admins de tenant criem/listem/revoguem API keys para integração externa.
Auth: JWT normal (não API Key) para gerenciar as chaves.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.api_keys import service
from app.modules.api_keys.schemas import ApiKeyCreate, ApiKeyCreated, ApiKeyResponse
from app.modules.audit.service import write_audit_log
from app.modules.permissions.service import require_permission

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreated, status_code=201)
def create_api_key(
    payload: ApiKeyCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    require_permission(context, "api_key.create")
    key, raw_key = service.generate_api_key(
        db,
        tenant_id=context.tenant_id,
        name=payload.name,
        scopes=list(payload.scopes),
        expires_at=payload.expires_at,
        created_by=context.user_id,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="api_key.created",
        resource_type="api_key",
        resource_id=key.id,
        details={"name": payload.name, "scopes": list(payload.scopes)},
    )
    db.commit()
    db.refresh(key)
    return {
        **ApiKeyResponse.model_validate(key).model_dump(),
        "scopes": service.get_scopes(key),
        "raw_key": raw_key,
    }


@router.get("", response_model=list[ApiKeyResponse])
def list_api_keys(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list:
    require_permission(context, "api_key.view")
    keys = service.list_api_keys(db, tenant_id=context.tenant_id)
    result = []
    for k in keys:
        data = ApiKeyResponse.model_validate(k).model_dump()
        data["scopes"] = service.get_scopes(k)
        result.append(data)
    return result


@router.delete("/{key_id}", status_code=204)
def revoke_api_key(
    key_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> None:
    require_permission(context, "api_key.revoke")
    key = service.revoke_api_key(db, tenant_id=context.tenant_id, key_id=key_id)
    if key is None:
        raise not_found("API key não encontrada")
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="api_key.revoked",
        resource_type="api_key",
        resource_id=key_id,
    )
    db.commit()
