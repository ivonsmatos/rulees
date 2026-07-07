import json
from typing import Any

from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog

SENSITIVE_KEYS = {"password", "token", "access_token", "authorization", "secret", "api_key"}


def sanitize_audit_details(value: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, item in value.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = "[redacted]"
        elif isinstance(item, dict):
            sanitized[key] = sanitize_audit_details(item)
        else:
            sanitized[key] = item
    return sanitized


def write_audit_log(
    db: Session,
    *,
    tenant_id: str,
    user_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    log = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(sanitize_audit_details(details or {}), ensure_ascii=False),
    )
    db.add(log)
    return log
