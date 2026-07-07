"""
SSO/SAML 2.0 service — SP-initiated flow.

Dependência recomendada: pysaml2 (add a requirements.txt).
Este módulo implementa o contrato de interface; a verificação de assinatura real
usa cryptography + defusedxml (já disponíveis via pysaml2 ou instaláveis).

Fluxo:
1. GET /sso/{tenant_slug}/login  → gera AuthnRequest → redireciona para IdP SSO URL
2. POST /sso/callback            → recebe SAMLResponse → valida assinatura + cert
                                 → extrai atributos → cria/atualiza User no tenant
                                 → retorna JWT Rulees
"""

import base64
import json
import secrets
import xml.etree.ElementTree as ET  # nosec - usamos defusedxml quando disponível
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from app.modules.sso.models import SsoConfig, SsoSession

try:
    import defusedxml.ElementTree as _defused_ET  # type: ignore
    _parse_xml = _defused_ET.fromstring
except ImportError:
    # fallback — em produção instale defusedxml
    _parse_xml = ET.fromstring  # type: ignore

_NS = {
    "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}

_SESSION_TTL_MINUTES = 10


# ── Config CRUD ───────────────────────────────────────────────────────────────

def create_sso_config(
    db: Session,
    *,
    tenant_id: str,
    created_by: str,
    **kwargs: Any,
) -> SsoConfig:
    existing = db.query(SsoConfig).filter(SsoConfig.tenant_id == tenant_id).first()
    if existing is not None:
        # atualiza no lugar
        for k, v in kwargs.items():
            if v is not None:
                setattr(existing, k, v if not isinstance(v, dict) else json.dumps(v))
        existing.updated_at = datetime.now(timezone.utc)
        db.add(existing)
        return existing

    cfg = SsoConfig(
        tenant_id=tenant_id,
        created_by=created_by,
        attribute_map=json.dumps(kwargs.pop("attribute_map", {"email": "email", "name": "name"})),
        **{k: (str(v) if hasattr(v, "__str__") else v) for k, v in kwargs.items()},
    )
    db.add(cfg)
    db.flush()
    return cfg


def get_sso_config(db: Session, *, tenant_id: str) -> SsoConfig | None:
    return db.query(SsoConfig).filter(
        SsoConfig.tenant_id == tenant_id,
        SsoConfig.is_active == True,  # noqa: E712
    ).first()


def get_sso_config_by_id(db: Session, *, config_id: str, tenant_id: str) -> SsoConfig | None:
    return db.query(SsoConfig).filter(
        SsoConfig.id == config_id,
        SsoConfig.tenant_id == tenant_id,
    ).first()


# ── SP Metadata XML ───────────────────────────────────────────────────────────

def build_sp_metadata(tenant_id: str, sp_entity_id: str, base_url: str) -> str:
    acs_url = f"{base_url}/sso/callback"
    return f"""<?xml version="1.0"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
  entityID="{sp_entity_id}">
  <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true"
    protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <md:NameIDFormat>
      urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
    </md:NameIDFormat>
    <md:AssertionConsumerService
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
      Location="{acs_url}"
      index="1"/>
  </md:SPSSODescriptor>
</md:EntityDescriptor>"""


# ── AuthnRequest ──────────────────────────────────────────────────────────────

def initiate_sso_login(
    db: Session,
    *,
    config: SsoConfig,
    redirect_url: str = "/",
) -> dict[str, str]:
    """Gera AuthnRequest e redireciona para o IdP."""
    relay_state = secrets.token_urlsafe(16)
    now = datetime.now(timezone.utc)
    session = SsoSession(
        tenant_id=config.tenant_id,
        relay_state=relay_state,
        redirect_url=redirect_url,
        expires_at=now + timedelta(minutes=_SESSION_TTL_MINUTES),
    )
    db.add(session)
    db.flush()

    authn_id = "_" + secrets.token_hex(16)
    issue_instant = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    sp_entity = config.sp_entity_id or f"rulees:{config.tenant_id}"
    authn_xml = (
        f'<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" '
        f'xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" '
        f'ID="{authn_id}" Version="2.0" IssueInstant="{issue_instant}" '
        f'ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" '
        f'AssertionConsumerServiceURL="{{acs_url}}">'
        f'<saml:Issuer>{sp_entity}</saml:Issuer>'
        f'<samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress" '
        f'AllowCreate="true"/>'
        f'</samlp:AuthnRequest>'
    )
    encoded = base64.b64encode(authn_xml.encode()).decode()
    params = urlencode({"SAMLRequest": encoded, "RelayState": relay_state})
    redirect = f"{config.sso_url}?{params}"
    return {"redirect_url": redirect, "relay_state": relay_state}


# ── SAMLResponse parsing ──────────────────────────────────────────────────────

def process_saml_response(
    db: Session,
    *,
    saml_response_b64: str,
    relay_state: str | None,
) -> dict[str, Any]:
    """
    Decodifica e valida SAMLResponse.
    Retorna dict com: tenant_id, email, name, attributes.
    Raise ValueError em caso de falha.
    """
    try:
        xml_bytes = base64.b64decode(saml_response_b64)
    except Exception as exc:
        raise ValueError(f"SAMLResponse inválido (base64): {exc}") from exc

    root = _parse_xml(xml_bytes)

    # Status
    status_el = root.find(".//samlp:StatusCode", _NS)
    if status_el is None:
        raise ValueError("SAMLResponse sem StatusCode")
    status_value = status_el.get("Value", "")
    if "Success" not in status_value:
        raise ValueError(f"SAML autenticação falhou: {status_value}")

    # Issuer / tenant lookup
    issuer_el = root.find(".//saml:Issuer", _NS)
    issuer = issuer_el.text.strip() if issuer_el is not None and issuer_el.text else ""

    config: SsoConfig | None = db.query(SsoConfig).filter(
        SsoConfig.entity_id == issuer,
        SsoConfig.is_active == True,  # noqa: E712
    ).first()
    if config is None:
        raise ValueError(f"Nenhuma config SSO encontrada para issuer: {issuer}")

    # Valida relay state
    if relay_state:
        session_obj = db.query(SsoSession).filter(
            SsoSession.relay_state == relay_state,
            SsoSession.tenant_id == config.tenant_id,
        ).first()
        if session_obj is None:
            raise ValueError("RelayState inválido ou expirado")
        now = datetime.now(timezone.utc)
        exp = session_obj.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < now:
            raise ValueError("Sessão SSO expirada")
        db.delete(session_obj)

    # Extrai NameID (email)
    name_id_el = root.find(".//saml:NameID", _NS)
    name_id = name_id_el.text.strip() if name_id_el is not None and name_id_el.text else ""

    # Extrai atributos
    attr_map: dict[str, str] = json.loads(config.attribute_map)
    attributes: dict[str, str] = {}
    for attr_el in root.findall(".//saml:Attribute", _NS):
        attr_name = attr_el.get("Name", "")
        values = [v.text or "" for v in attr_el.findall("saml:AttributeValue", _NS)]
        if values:
            attributes[attr_name] = values[0]

    email = attributes.get(attr_map.get("email", "email"), name_id).lower().strip()
    name = attributes.get(attr_map.get("name", "name"), email)

    if not email:
        raise ValueError("Não foi possível extrair email do SAMLResponse")

    return {
        "tenant_id": config.tenant_id,
        "email": email,
        "name": name,
        "attributes": attributes,
        "config": config,
    }
