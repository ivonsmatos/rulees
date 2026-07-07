import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.security import _b64url_decode, _b64url_encode
from app.core.settings import Settings


def private_storage_path(settings: Settings, *parts: str) -> Path:
    root = settings.resolved_storage_path
    path = root.joinpath(*parts).resolve()
    if root not in path.parents and path != root:
        raise ValueError("Invalid storage path")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_private_file(settings: Settings, *, tenant_id: str, filename: str, content: bytes) -> Path:
    path = private_storage_path(settings, "tenants", tenant_id, filename)
    path.write_bytes(content)
    return path


def create_signed_storage_token(
    settings: Settings,
    *,
    tenant_id: str,
    path: str,
    media_type: str,
    filename: str,
    expires_in_seconds: int | None = None,
) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=expires_in_seconds or settings.signed_url_expire_seconds
    )
    payload = {
        "tenant_id": tenant_id,
        "path": path,
        "media_type": media_type,
        "filename": filename,
        "exp": int(expires_at.timestamp()),
    }
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(settings.secret_key.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256).digest()
    return f"{payload_part}.{_b64url_encode(signature)}"


def verify_signed_storage_token(settings: Settings, token: str) -> dict:
    try:
        payload_part, signature_part = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("Invalid signed URL") from exc
    expected = hmac.new(settings.secret_key.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256).digest()
    actual = _b64url_decode(signature_part)
    if not hmac.compare_digest(actual, expected):
        raise ValueError("Invalid signed URL signature")
    payload = json.loads(_b64url_decode(payload_part))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Signed URL expired")
    path = private_storage_path(settings, *str(payload["path"]).split("/"))
    payload["resolved_path"] = str(path)
    return payload
