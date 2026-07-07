"""
SCIM 2.0 router — User e Group provisioning para enterprise IdPs.

Auth: Bearer API Key com scope "scim".
Base path: /scim/v2

Spec: RFC 7643 / RFC 7644.
"""

import json

from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, not_found, unauthorized
from app.db.session import get_db
from app.modules.api_keys.service import verify_api_key, get_scopes
from app.modules.auth.models import TenantMember, User

router = APIRouter(prefix="/scim/v2", tags=["scim"])

_SCIM_CT = "application/scim+json"


# ── Auth helper ───────────────────────────────────────────────────────────────

def _scim_auth(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> tuple[str, str]:
    """Valida Bearer API Key com scope 'scim'. Retorna (tenant_id, key_id)."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized("SCIM requer Bearer API Key com scope 'scim'")
    raw_key = authorization[7:]
    key = verify_api_key(db, raw_key)
    if key is None:
        raise unauthorized("API Key inválida ou expirada")
    if "scim" not in get_scopes(key):
        raise unauthorized("API Key sem escopo 'scim'")
    db.commit()  # persiste last_used_at
    return key.tenant_id, key.id


# ── SCIM User schema helper ───────────────────────────────────────────────────

def _user_to_scim(user: User, tenant_id: str) -> dict:
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user.id,
        "userName": user.email,
        "name": {"formatted": user.name, "displayName": user.name},
        "emails": [{"value": user.email, "primary": True}],
        "active": user.is_active,
        "meta": {
            "resourceType": "User",
            "created": user.created_at.isoformat(),
            "location": f"/scim/v2/Users/{user.id}",
        },
    }


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/Users")
def list_users(
    startIndex: int = 1,
    count: int = 100,
    filter: str | None = None,
    auth: tuple = Depends(_scim_auth),
    db: Session = Depends(get_db),
) -> Response:
    tenant_id, _ = auth
    query = (
        select(User)
        .join(TenantMember, TenantMember.user_id == User.id)
        .where(TenantMember.tenant_id == tenant_id)
        .order_by(User.created_at.asc())
    )
    # filtro básico: userName eq "..."
    if filter:
        import re
        m = re.match(r'userName\s+eq\s+"([^"]+)"', filter, re.IGNORECASE)
        if m:
            query = query.where(User.email == m.group(1).lower())

    all_users = list(db.scalars(query))
    total = len(all_users)
    page = all_users[(startIndex - 1): (startIndex - 1 + count)]
    body = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": total,
        "startIndex": startIndex,
        "itemsPerPage": len(page),
        "Resources": [_user_to_scim(u, tenant_id) for u in page],
    }
    return Response(content=json.dumps(body), media_type=_SCIM_CT)


@router.post("/Users", status_code=201)
def create_user(
    request_body: dict,
    auth: tuple = Depends(_scim_auth),
    db: Session = Depends(get_db),
) -> Response:
    tenant_id, _ = auth
    email = (request_body.get("userName") or "").lower().strip()
    if not email:
        raise bad_request("userName obrigatório")

    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        # garante membership e retorna
        _ensure_membership(db, existing.id, tenant_id)
        db.commit()
        return Response(
            content=json.dumps(_user_to_scim(existing, tenant_id)),
            media_type=_SCIM_CT,
            status_code=201,
        )

    name_obj = request_body.get("name", {})
    display_name = (
        name_obj.get("formatted")
        or name_obj.get("displayName")
        or email
    )
    import secrets as _secrets
    import hashlib as _hashlib
    pwd_hash = "scim_provisioned_" + _hashlib.sha256(_secrets.token_bytes(16)).hexdigest()

    user = User(name=display_name, email=email, password_hash=pwd_hash)
    is_active = request_body.get("active", True)
    user.is_active = is_active
    db.add(user)
    db.flush()

    _ensure_membership(db, user.id, tenant_id)
    db.commit()
    return Response(
        content=json.dumps(_user_to_scim(user, tenant_id)),
        media_type=_SCIM_CT,
        status_code=201,
    )


@router.get("/Users/{user_id}")
def get_user(
    user_id: str,
    auth: tuple = Depends(_scim_auth),
    db: Session = Depends(get_db),
) -> Response:
    tenant_id, _ = auth
    user = _get_tenant_user(db, user_id=user_id, tenant_id=tenant_id)
    return Response(content=json.dumps(_user_to_scim(user, tenant_id)), media_type=_SCIM_CT)


@router.put("/Users/{user_id}")
def replace_user(
    user_id: str,
    request_body: dict,
    auth: tuple = Depends(_scim_auth),
    db: Session = Depends(get_db),
) -> Response:
    tenant_id, _ = auth
    user = _get_tenant_user(db, user_id=user_id, tenant_id=tenant_id)
    name_obj = request_body.get("name", {})
    new_name = name_obj.get("formatted") or name_obj.get("displayName")
    if new_name:
        user.name = new_name
    if "active" in request_body:
        user.is_active = bool(request_body["active"])
    db.add(user)
    db.commit()
    return Response(content=json.dumps(_user_to_scim(user, tenant_id)), media_type=_SCIM_CT)


@router.patch("/Users/{user_id}")
def patch_user(
    user_id: str,
    request_body: dict,
    auth: tuple = Depends(_scim_auth),
    db: Session = Depends(get_db),
) -> Response:
    tenant_id, _ = auth
    user = _get_tenant_user(db, user_id=user_id, tenant_id=tenant_id)
    for op in request_body.get("Operations", []):
        operation = op.get("op", "").lower()
        path = op.get("path", "")
        value = op.get("value")
        if operation == "replace":
            if path == "active" or path == "active":
                user.is_active = bool(value)
            elif path in ("name.formatted", "displayName"):
                user.name = str(value)
        elif operation == "add" and path == "active":
            user.is_active = bool(value)
    db.add(user)
    db.commit()
    return Response(content=json.dumps(_user_to_scim(user, tenant_id)), media_type=_SCIM_CT)


@router.delete("/Users/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    auth: tuple = Depends(_scim_auth),
    db: Session = Depends(get_db),
) -> None:
    """Desprovisionamento: desativa o usuário no tenant (soft delete)."""
    tenant_id, _ = auth
    user = _get_tenant_user(db, user_id=user_id, tenant_id=tenant_id)
    user.is_active = False
    db.add(user)
    # Remove membership no tenant
    member = db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == user_id,
        )
    )
    if member:
        db.delete(member)
    db.commit()


# ── Groups (read-only — mapeado para roles) ───────────────────────────────────

@router.get("/Groups")
def list_groups(
    auth: tuple = Depends(_scim_auth),
    db: Session = Depends(get_db),
) -> Response:
    tenant_id, _ = auth
    # Grupos = roles existentes no tenant
    members = list(db.scalars(
        select(TenantMember).where(TenantMember.tenant_id == tenant_id)
    ))
    role_map: dict[str, list[dict]] = {}
    for m in members:
        role_map.setdefault(m.role, []).append({"value": m.user_id})

    groups = [
        {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
            "id": f"{tenant_id}:{role}",
            "displayName": role,
            "members": role_map[role],
        }
        for role in role_map
    ]
    body = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(groups),
        "startIndex": 1,
        "itemsPerPage": len(groups),
        "Resources": groups,
    }
    return Response(content=json.dumps(body), media_type=_SCIM_CT)


# ── ServiceProviderConfig ─────────────────────────────────────────────────────

@router.get("/ServiceProviderConfig")
def service_provider_config() -> dict:
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "patch": {"supported": True},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": False},
        "authenticationSchemes": [
            {
                "name": "OAuth Bearer Token",
                "description": "API Key com escopo 'scim'",
                "specUri": "http://www.rfc-editor.org/info/rfc6750",
                "type": "oauthbearertoken",
                "primary": True,
            }
        ],
        "meta": {"resourceType": "ServiceProviderConfig", "location": "/scim/v2/ServiceProviderConfig"},
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ensure_membership(db: Session, user_id: str, tenant_id: str) -> TenantMember:
    existing = db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == user_id,
        )
    )
    if existing:
        return existing
    member = TenantMember(tenant_id=tenant_id, user_id=user_id, role="member")
    db.add(member)
    db.flush()
    return member


def _get_tenant_user(db: Session, *, user_id: str, tenant_id: str) -> User:
    user = db.scalar(
        select(User)
        .join(TenantMember, TenantMember.user_id == User.id)
        .where(User.id == user_id, TenantMember.tenant_id == tenant_id)
    )
    if user is None:
        raise not_found("Usuário não encontrado neste tenant")
    return user
