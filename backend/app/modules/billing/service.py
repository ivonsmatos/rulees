import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import payment_required
from app.modules.billing.models import TenantBillingProfile
from app.modules.usage.models import UsageEvent

# Custo aproximado por 1M tokens (USD), por modelo de LLM -- tabelas publicas dos
# provedores, sujeitas a mudanca. Usado so para estimativa exibida ao tenant, nunca
# para cobranca real; ajustar os valores aqui se o preco do provider mudar.
LLM_TOKEN_COST_USD_PER_MILLION: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
}


def estimate_llm_cost_usd(model_name: str, *, prompt_tokens: int, total_tokens: int) -> float | None:
    """Custo estimado usando `total_tokens - prompt_tokens` como base de saida (em
    vez de `completion_tokens`): modelos "thinking" (ex.: gemini-2.5-flash) gastam
    tokens de raciocinio interno que nao aparecem em `completion_tokens`, mas sao
    cobrados como saida pelo provider -- `total_tokens` e a contagem que reflete
    isso corretamente. Para modelos sem raciocinio oculto, completion == total-prompt
    de qualquer forma, entao a formula continua correta."""
    rates = LLM_TOKEN_COST_USD_PER_MILLION.get(model_name)
    if rates is None:
        return None
    output_tokens = max(total_tokens - prompt_tokens, 0)
    return (prompt_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000

PLAN_LIMITS: dict[str, dict[str, float]] = {
    "trial": {
        "meeting_created": 100,
        "audio_chunk_received": 1000,
        "ai_rule_detected": 500,
        "ai_question_suggested": 500,
        "ai_decision_detected": 500,
        "rag_conflict_checked": 500,
        "document_generated": 100,
        "document_version_created": 100,
        "pdf_exported": 100,
        "markdown_exported": 100,
        "excel_exported": 100,
        "export_job_created": 100,
        "rule_version_created": 200,
    },
    "starter": {
        "meeting_created": 500,
        "audio_chunk_received": 10000,
        "ai_rule_detected": 5000,
        "ai_question_suggested": 5000,
        "ai_decision_detected": 5000,
        "rag_conflict_checked": 5000,
        "document_generated": 500,
        "document_version_created": 500,
        "pdf_exported": 500,
        "markdown_exported": 500,
        "excel_exported": 500,
        "export_job_created": 500,
        "rule_version_created": 1000,
    },
    "pro": {},
    "enterprise": {},
}

COST_RATES_USD: dict[str, float] = {
    "audio_chunk_received": 0.0008,
    "ai_rule_detected": 0.002,
    "ai_question_suggested": 0.0015,
    "ai_decision_detected": 0.0015,
    "rag_conflict_checked": 0.0007,
    "document_generated": 0.015,
    "document_version_created": 0.004,
    "pdf_exported": 0.001,
    "markdown_exported": 0.0005,
    "excel_exported": 0.0015,
    "export_job_created": 0.002,
    "rule_version_created": 0.002,
}


def get_or_create_billing_profile(
    db: Session,
    *,
    tenant_id: str,
    plan_name: str = "trial",
) -> TenantBillingProfile:
    profile = db.scalar(
        select(TenantBillingProfile).where(TenantBillingProfile.tenant_id == tenant_id)
    )
    if profile:
        return profile
    profile = TenantBillingProfile(tenant_id=tenant_id, plan_name=plan_name, status="active")
    db.add(profile)
    return profile


def usage_total(db: Session, *, tenant_id: str, event_type: str) -> float:
    total = db.scalar(
        select(func.sum(UsageEvent.quantity)).where(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.event_type == event_type,
        )
    )
    return float(total or 0)


def ensure_billing_limit(
    db: Session,
    *,
    tenant_id: str,
    event_type: str,
    quantity: float = 1.0,
) -> None:
    profile = get_or_create_billing_profile(db, tenant_id=tenant_id)
    limits = PLAN_LIMITS.get(profile.plan_name, PLAN_LIMITS["trial"])
    limit = limits.get(event_type)
    if limit is None:
        return
    used = usage_total(db, tenant_id=tenant_id, event_type=event_type)
    if used + quantity > limit:
        raise payment_required(f"Limite do plano atingido para {event_type}")


def real_llm_cost_usd(db: Session, *, tenant_id: str) -> float:
    """Soma o custo real (nao estimativa fixa) registrado em usage_events do tipo
    `llm_tokens_used`, calculado a partir de tokens reais de cada chamada de LLM."""
    events = db.scalars(
        select(UsageEvent).where(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.event_type == "llm_tokens_used",
        )
    )
    total = 0.0
    for event in events:
        try:
            details = json.loads(event.details)
        except (json.JSONDecodeError, TypeError):
            continue
        cost = details.get("estimated_cost_usd")
        if isinstance(cost, (int, float)):
            total += cost
    return total


def billing_status(db: Session, *, tenant_id: str) -> dict:
    profile = get_or_create_billing_profile(db, tenant_id=tenant_id)
    limits = PLAN_LIMITS.get(profile.plan_name, PLAN_LIMITS["trial"])
    event_types = sorted(set(limits) | set(COST_RATES_USD))
    return {
        "tenant_id": tenant_id,
        "plan_name": profile.plan_name,
        "status": profile.status,
        "limits": [
            {
                "event_type": event_type,
                "used": usage_total(db, tenant_id=tenant_id, event_type=event_type),
                "limit": limit,
                "remaining": max(limit - usage_total(db, tenant_id=tenant_id, event_type=event_type), 0),
            }
            for event_type, limit in sorted(limits.items())
        ],
        "estimated_costs": [
            {
                "event_type": event_type,
                "quantity": usage_total(db, tenant_id=tenant_id, event_type=event_type),
                "unit_cost_usd": COST_RATES_USD.get(event_type, 0),
                "estimated_cost_usd": usage_total(db, tenant_id=tenant_id, event_type=event_type)
                * COST_RATES_USD.get(event_type, 0),
            }
            for event_type in event_types
            if usage_total(db, tenant_id=tenant_id, event_type=event_type) > 0
        ],
        "real_llm_cost_usd": real_llm_cost_usd(db, tenant_id=tenant_id),
    }
