"""BYOK router — configuração e uso de chave do cliente."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import bad_request, not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.byok import service
from app.modules.byok.schemas import (
    CustomerKeyCreate,
    CustomerKeyResponse,
    DecryptRequest,
    DecryptResponse,
    EncryptRequest,
    EncryptResponse,
)
from app.modules.permissions.service import require_permission

router = APIRouter(prefix="/byok", tags=["byok"])


@router.post("", response_model=CustomerKeyResponse, status_code=201)
def provision_key(
    payload: CustomerKeyCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> CustomerKeyResponse:
    require_permission(context, "byok.manage")
    try:
        ck = service.provision_customer_key(
            db,
            tenant_id=context.tenant_id,
            created_by=context.user_id,
            kms_provider=payload.kms_provider,
            kms_key_arn=payload.kms_key_arn,
            key_label=payload.key_label,
            master_key_b64=payload.master_key_b64,
        )
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="byok.provisioned",
        resource_type="customer_key",
        resource_id=ck.id,
        details={"kms_provider": payload.kms_provider},
    )
    db.commit()
    db.refresh(ck)
    return CustomerKeyResponse.model_validate(ck)


@router.get("", response_model=CustomerKeyResponse)
def get_key_info(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> CustomerKeyResponse:
    require_permission(context, "byok.manage")
    ck = service.get_customer_key(db, tenant_id=context.tenant_id)
    if ck is None:
        raise not_found("BYOK não configurado para este tenant")
    return CustomerKeyResponse.model_validate(ck)


@router.post("/encrypt", response_model=EncryptResponse)
def encrypt_data(
    payload: EncryptRequest,
    master_key_b64: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> EncryptResponse:
    """Cifra dados usando a DEK do tenant. master_key_b64 enviado via query param."""
    require_permission(context, "byok.manage")
    try:
        ct = service.encrypt_for_tenant(
            db,
            tenant_id=context.tenant_id,
            plaintext=payload.plaintext,
            master_key_b64=master_key_b64,
        )
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return EncryptResponse(ciphertext_b64=ct)


@router.post("/decrypt", response_model=DecryptResponse)
def decrypt_data(
    payload: DecryptRequest,
    master_key_b64: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DecryptResponse:
    require_permission(context, "byok.manage")
    try:
        pt = service.decrypt_for_tenant(
            db,
            tenant_id=context.tenant_id,
            ciphertext_b64=payload.ciphertext_b64,
            master_key_b64=master_key_b64,
        )
    except (ValueError, NotImplementedError) as exc:
        raise bad_request(str(exc)) from exc
    return DecryptResponse(plaintext=pt)


@router.post("/rotate", response_model=CustomerKeyResponse)
def rotate_key(
    old_master_key_b64: str,
    new_master_key_b64: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> CustomerKeyResponse:
    require_permission(context, "byok.manage")
    try:
        ck = service.rotate_key(
            db,
            tenant_id=context.tenant_id,
            old_master_key_b64=old_master_key_b64,
            new_master_key_b64=new_master_key_b64,
        )
    except (ValueError, NotImplementedError) as exc:
        raise bad_request(str(exc)) from exc
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="byok.rotated",
        resource_type="customer_key",
        resource_id=ck.id,
    )
    db.commit()
    db.refresh(ck)
    return CustomerKeyResponse.model_validate(ck)
