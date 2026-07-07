"""
API Keys service.

Geração: secret = "rlk_" + 40 chars random → prefix = secret[:12], hash = sha256(secret).
Verificação: recebe raw key → extrai prefix → busca by prefix → compare hash.
"""

import hashlib
import json
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.api_keys.models import ApiKey


_PREFIX_HEAD = "rlk_"
_KEY_BYTES = 30  # 40 chars base64url after encoding


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_api_key(
    db: Session,
    *,
    tenant_id: str,
    name: str,
    scopes: list[str],
    expires_at: datetime | None,
    created_by: str,
) -> tuple[ApiKey, str]:
    """Cria e retorna (ApiKey persistida, raw_key). raw_key NÃO é salvo — mostrar só uma vez."""
    random_part = secrets.token_urlsafe(_KEY_BYTES)
    raw_key = _PREFIX_HEAD + random_part
    prefix = raw_key[:12]

    key = ApiKey(
        tenant_id=tenant_id,
        name=name,
        key_prefix=prefix,
        key_hash=_hash_key(raw_key),
        scopes=json.dumps(scopes),
        expires_at=expires_at,
        created_by=created_by,
    )
    db.add(key)
    db.flush()
    return key, raw_key


def verify_api_key(db: Session, raw_key: str) -> ApiKey | None:
    """Valida raw_key e retorna ApiKey ativa, ou None se inválida/expirada."""
    if len(raw_key) < 12:
        return None
    prefix = raw_key[:12]
    api_key = db.query(ApiKey).filter(
        ApiKey.key_prefix == prefix,
        ApiKey.is_active == True,  # noqa: E712
        ApiKey.revoked_at.is_(None),
    ).first()
    if api_key is None:
        return None
    if api_key.key_hash != _hash_key(raw_key):
        return None
    now = datetime.now(timezone.utc)
    if api_key.expires_at and api_key.expires_at.replace(tzinfo=timezone.utc) < now:
        return None
    # update last_used_at without triggering full flush
    api_key.last_used_at = now
    db.add(api_key)
    return api_key


def list_api_keys(db: Session, *, tenant_id: str) -> list[ApiKey]:
    return db.query(ApiKey).filter(
        ApiKey.tenant_id == tenant_id,
        ApiKey.revoked_at.is_(None),
    ).order_by(ApiKey.created_at.desc()).all()


def revoke_api_key(db: Session, *, tenant_id: str, key_id: str) -> ApiKey | None:
    key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.tenant_id == tenant_id,
    ).first()
    if key is None:
        return None
    key.revoked_at = datetime.now(timezone.utc)
    key.is_active = False
    db.add(key)
    return key


def get_scopes(api_key: ApiKey) -> list[str]:
    try:
        return json.loads(api_key.scopes)
    except Exception:
        return ["read"]
