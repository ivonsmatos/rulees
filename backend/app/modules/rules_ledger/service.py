import json
import re
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.rules_ledger.models import BusinessRule, RuleLifecycleEvent, RuleVersion
from app.shared.enums import RuleStatus

RULE_HINTS = (
    "deve",
    "precisa",
    "quando",
    "se ",
    "somente",
    "obrigatorio",
    "permitido",
    "bloqueado",
    "cliente",
    "regra",
)


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned[:2000]


def looks_like_rule(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in RULE_HINTS) and len(lowered.split()) >= 5


def next_rule_code(db: Session, tenant_id: str, project_id: str) -> str:
    count = db.scalar(
        select(func.count(BusinessRule.id)).where(
            BusinessRule.tenant_id == tenant_id,
            BusinessRule.project_id == project_id,
        )
    )
    return f"RULE-{(count or 0) + 1:03d}"


def calculate_rule_quality_details(
    *,
    rule_text: str,
    condition_text: str | None = None,
    result_text: str | None = None,
    source_chunk_ids: list[str] | None = None,
    confidence_score: float = 0.72,
) -> dict:
    lowered = rule_text.lower()
    has_condition = bool(condition_text) or "quando" in lowered or "se " in lowered
    has_result = bool(result_text) or any(term in lowered for term in ("deve", "precisa", "bloque", "permit"))
    evidence_count = len(source_chunk_ids or [])
    checks = [
        {
            "key": "condition",
            "label": "Condicao explicita",
            "passed": has_condition,
            "weight": 25,
        },
        {
            "key": "result",
            "label": "Resultado esperado",
            "passed": has_result,
            "weight": 25,
        },
        {
            "key": "evidence",
            "label": "Evidencia ligada a transcricao",
            "passed": evidence_count > 0,
            "weight": 20,
        },
        {
            "key": "confidence",
            "label": "Confianca minima",
            "passed": confidence_score >= 0.7,
            "weight": 15,
        },
        {
            "key": "length",
            "label": "Texto suficientemente descritivo",
            "passed": len(rule_text.split()) >= 8,
            "weight": 15,
        },
    ]
    score = sum(check["weight"] for check in checks if check["passed"])
    missing = [check["label"] for check in checks if not check["passed"]]
    return {
        "score": score,
        "checks": checks,
        "missing": missing,
        "evidence_count": evidence_count,
    }


def serialize_quality_details(details: dict) -> str:
    return json.dumps(details, ensure_ascii=False)


def create_candidate_rule(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    meeting_id: str,
    rule_text: str,
    source_chunk_id: str,
    condition_text: str | None = None,
    result_text: str | None = None,
    confidence_score: float = 0.76,
) -> BusinessRule:
    """Cria uma regra candidata a partir de um chunk de transcricao.

    ``condition_text``/``result_text``/``confidence_score`` sao opcionais e,
    quando fornecidos (ex.: extraidos por um LLM real), sobrescrevem os
    defaults heuristicos -- chamadas existentes sem esses kwargs mantem o
    comportamento exato de antes. Regra anti-alucinacao: mesmo com LLM, a
    regra NUNCA nasce aprovada -- sempre ``RuleStatus.needs_review``.
    """
    normalized = normalize_text(rule_text)
    source_chunk_ids = [source_chunk_id]
    quality_details = calculate_rule_quality_details(
        rule_text=normalized,
        condition_text=condition_text,
        result_text=result_text,
        source_chunk_ids=source_chunk_ids,
        confidence_score=confidence_score,
    )
    rule = BusinessRule(
        code=next_rule_code(db, tenant_id, project_id),
        tenant_id=tenant_id,
        project_id=project_id,
        meeting_id=meeting_id,
        rule_text=normalized,
        condition_text=condition_text.strip() if condition_text else None,
        result_text=result_text.strip() if result_text else None,
        status=RuleStatus.needs_review,
        confidence_score=confidence_score,
        quality_score=quality_details["score"],
        quality_details=serialize_quality_details(quality_details),
        source_chunk_ids=json.dumps(source_chunk_ids),
    )
    db.add(rule)
    return rule


def create_rule_version(
    db: Session,
    rule: BusinessRule,
    *,
    created_by: str | None = None,
    change_reason: str = "Snapshot automatico",
) -> RuleVersion:
    version = RuleVersion(
        tenant_id=rule.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        rule_id=rule.id,
        version_number=rule.version_number,
        status=rule.status,
        rule_text=rule.rule_text,
        condition_text=rule.condition_text,
        result_text=rule.result_text,
        source_chunk_ids=rule.source_chunk_ids,
        change_reason=change_reason,
        created_by=created_by,
    )
    db.add(version)
    return version


def revise_rule(
    rule: BusinessRule,
    *,
    rule_text: str,
    condition_text: str | None,
    result_text: str | None,
) -> BusinessRule:
    rule.rule_text = normalize_text(rule_text)
    rule.condition_text = condition_text.strip() if condition_text else None
    rule.result_text = result_text.strip() if result_text else None
    try:
        source_chunk_ids = json.loads(rule.source_chunk_ids)
    except json.JSONDecodeError:
        source_chunk_ids = []
    if not isinstance(source_chunk_ids, list):
        source_chunk_ids = []
    quality_details = calculate_rule_quality_details(
        rule_text=rule.rule_text,
        condition_text=rule.condition_text,
        result_text=rule.result_text,
        source_chunk_ids=[str(item) for item in source_chunk_ids],
        confidence_score=rule.confidence_score,
    )
    rule.quality_score = quality_details["score"]
    rule.quality_details = serialize_quality_details(quality_details)
    rule.version_number += 1
    rule.status = RuleStatus.needs_review
    rule.approved_by = None
    rule.approved_at = None
    rule.revoked_at = None
    rule.archived_at = None
    return rule


def approve_rule(rule: BusinessRule, user_id: str) -> BusinessRule:
    if rule.status == RuleStatus.rejected:
        rule.status = RuleStatus.needs_review
    rule.status = RuleStatus.approved
    rule.approved_by = user_id
    rule.approved_at = datetime.now(timezone.utc)
    return rule


def reject_rule(rule: BusinessRule) -> BusinessRule:
    rule.status = RuleStatus.rejected
    return rule


def write_rule_lifecycle_event(
    db: Session,
    *,
    rule: BusinessRule,
    user_id: str | None,
    event_type: str,
    from_status: str | None,
    to_status: str | None,
    details: dict | None = None,
) -> RuleLifecycleEvent:
    event = RuleLifecycleEvent(
        tenant_id=rule.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        rule_id=rule.id,
        user_id=user_id,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        details=json.dumps(details or {}, ensure_ascii=False),
    )
    db.add(event)
    return event
