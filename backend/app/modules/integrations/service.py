"""
Integrations service — Jira, Confluence e Azure DevOps.

Padrão de segurança:
- config_json é armazenado criptografado quando BYOK estiver ativo; neste módulo
  guardamos JSON plain por enquanto (sem BYOK) — tokens são dados de configuração
  gerenciados pelo admin, não PII do usuário final.
- Nunca logar tokens/senhas — audit redact via SENSITIVE_KEYS.
- Todas chamadas externas usam httpx com timeout explícito.
"""

import json
from datetime import datetime, timezone
from typing import Any

import httpx

from app.modules.integrations.models import IntegrationConfig, IntegrationDispatch


_TIMEOUT = httpx.Timeout(30.0)


# ── Config CRUD ───────────────────────────────────────────────────────────────

def create_integration(
    db,
    *,
    tenant_id: str,
    provider: str,
    label: str,
    config: dict[str, Any],
    created_by: str,
) -> IntegrationConfig:
    obj = IntegrationConfig(
        tenant_id=tenant_id,
        provider=provider,
        label=label,
        config_json=json.dumps(config),
        created_by=created_by,
    )
    db.add(obj)
    db.flush()
    return obj


def list_integrations(db, *, tenant_id: str) -> list[IntegrationConfig]:
    return db.query(IntegrationConfig).filter(
        IntegrationConfig.tenant_id == tenant_id,
    ).order_by(IntegrationConfig.created_at.desc()).all()


def get_integration(db, *, tenant_id: str, integration_id: str) -> IntegrationConfig | None:
    return db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_id,
        IntegrationConfig.tenant_id == tenant_id,
    ).first()


def update_integration(
    db,
    obj: IntegrationConfig,
    *,
    label: str | None,
    config: dict[str, Any] | None,
    is_active: bool | None,
) -> IntegrationConfig:
    if label is not None:
        obj.label = label
    if config is not None:
        obj.config_json = json.dumps(config)
    if is_active is not None:
        obj.is_active = is_active
    obj.updated_at = datetime.now(timezone.utc)
    db.add(obj)
    return obj


def delete_integration(db, obj: IntegrationConfig) -> None:
    db.delete(obj)


# ── Test connection ───────────────────────────────────────────────────────────

def test_connection(integration: IntegrationConfig) -> dict[str, Any]:
    """Testa conectividade com o provider sem persistir nada."""
    cfg = json.loads(integration.config_json)
    provider = integration.provider
    try:
        if provider == "jira":
            return _test_jira(cfg)
        if provider == "confluence":
            return _test_confluence(cfg)
        if provider == "azure_devops":
            return _test_azure_devops(cfg)
        return {"success": False, "message": f"Provider desconhecido: {provider}"}
    except httpx.TimeoutException:
        return {"success": False, "message": "Timeout ao conectar com o provider"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def _test_jira(cfg: dict) -> dict:
    url = str(cfg["base_url"]).rstrip("/") + "/rest/api/3/myself"
    resp = httpx.get(url, auth=(cfg["email"], cfg["api_token"]), timeout=_TIMEOUT)
    if resp.status_code == 200:
        data = resp.json()
        return {"success": True, "message": f"Conectado como {data.get('displayName', '?')}"}
    return {"success": False, "message": f"HTTP {resp.status_code}: {resp.text[:200]}"}


def _test_confluence(cfg: dict) -> dict:
    url = str(cfg["base_url"]).rstrip("/") + "/wiki/rest/api/space/" + cfg["space_key"]
    resp = httpx.get(url, auth=(cfg["email"], cfg["api_token"]), timeout=_TIMEOUT)
    if resp.status_code == 200:
        return {"success": True, "message": "Espaço Confluence acessível"}
    return {"success": False, "message": f"HTTP {resp.status_code}: {resp.text[:200]}"}


def _test_azure_devops(cfg: dict) -> dict:
    org_url = str(cfg["org_url"]).rstrip("/")
    project = cfg["project"]
    url = f"{org_url}/{project}/_apis/wit/workitemtypes?api-version=7.1"
    resp = httpx.get(url, auth=("", cfg["personal_access_token"]), timeout=_TIMEOUT)
    if resp.status_code == 200:
        return {"success": True, "message": "Azure DevOps acessível"}
    return {"success": False, "message": f"HTTP {resp.status_code}: {resp.text[:200]}"}


# ── Dispatch ──────────────────────────────────────────────────────────────────

def dispatch_document(
    db,
    *,
    integration: IntegrationConfig,
    document_id: str,
    payload: dict[str, Any],
    dispatched_by: str,
) -> IntegrationDispatch:
    dispatch = IntegrationDispatch(
        tenant_id=integration.tenant_id,
        integration_id=integration.id,
        document_id=document_id,
        status="pending",
        dispatched_by=dispatched_by,
    )
    db.add(dispatch)
    db.flush()

    cfg = json.loads(integration.config_json)
    try:
        if integration.provider == "jira":
            ext_id, ext_url = _send_jira(cfg, payload)
        elif integration.provider == "confluence":
            ext_id, ext_url = _send_confluence(cfg, payload)
        elif integration.provider == "azure_devops":
            ext_id, ext_url = _send_azure_devops(cfg, payload)
        else:
            raise ValueError(f"Provider não suportado: {integration.provider}")

        dispatch.status = "success"
        dispatch.external_id = ext_id
        dispatch.external_url = ext_url
    except Exception as exc:
        dispatch.status = "error"
        dispatch.error_message = str(exc)[:1024]
    finally:
        dispatch.completed_at = datetime.now(timezone.utc)
        db.add(dispatch)

    return dispatch


def _send_jira(cfg: dict, payload: dict) -> tuple[str, str]:
    base = str(cfg["base_url"]).rstrip("/")
    issue_type = cfg.get("issue_type", "Story")
    body = {
        "fields": {
            "project": {"key": cfg["project_key"]},
            "summary": payload.get("summary", "Documento Rulees"),
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [
                    {"type": "text", "text": payload.get("description", "")}
                ]}],
            },
            "issuetype": {"name": issue_type},
            "labels": payload.get("labels", ["rulees"]),
        }
    }
    resp = httpx.post(
        f"{base}/rest/api/3/issue",
        json=body,
        auth=(cfg["email"], cfg["api_token"]),
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["key"], f"{base}/browse/{data['key']}"


def _send_confluence(cfg: dict, payload: dict) -> tuple[str, str]:
    base = str(cfg["base_url"]).rstrip("/")
    body: dict[str, Any] = {
        "type": "page",
        "title": payload.get("title", "Documento Rulees"),
        "space": {"key": cfg["space_key"]},
        "body": payload.get("body", {
            "storage": {"value": "", "representation": "storage"},
        }),
    }
    if cfg.get("parent_page_id"):
        body["ancestors"] = [{"id": cfg["parent_page_id"]}]
    resp = httpx.post(
        f"{base}/wiki/rest/api/content",
        json=body,
        auth=(cfg["email"], cfg["api_token"]),
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    page_url = f"{base}/wiki{data['_links']['webui']}"
    return data["id"], page_url


def _send_azure_devops(cfg: dict, payload: dict) -> tuple[str, str]:
    org_url = str(cfg["org_url"]).rstrip("/")
    project = cfg["project"]
    work_item_type = cfg.get("work_item_type", "User Story")
    body = [
        {"op": "add", "path": "/fields/System.Title", "value": payload.get("summary", "Documento Rulees")},
        {"op": "add", "path": "/fields/System.Description", "value": payload.get("description", "")},
        {"op": "add", "path": "/fields/System.Tags", "value": "Rulees"},
    ]
    resp = httpx.post(
        f"{org_url}/{project}/_apis/wit/workitems/${work_item_type}?api-version=7.1",
        json=body,
        headers={"Content-Type": "application/json-patch+json"},
        auth=("", cfg["personal_access_token"]),
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    item_id = str(data["id"])
    item_url = data.get("_links", {}).get("html", {}).get("href", "")
    return item_id, item_url
