import json

from sqlalchemy.orm import Session

from app.modules.decisions.models import Decision
from app.modules.rules_ledger.service import normalize_text


DECISION_HINTS = (
    "fica aprovado",
    "foi aprovado",
    "aprovado",
    "decidimos",
    "decidido",
    "fica definido",
    "foi definido",
    "vamos lançar",
    "vamos lancar",
    "será lançado",
    "sera lancado",
)


def should_detect_decision(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in DECISION_HINTS)


def decision_type_for(text: str) -> str:
    lowered = text.lower()
    if "aprovado" in lowered:
        return "approval"
    if "prazo" in lowered or "data" in lowered:
        return "deadline_definition"
    if "responsável" in lowered or "responsavel" in lowered:
        return "owner_definition"
    return "business_decision"


def create_detected_decision(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    meeting_id: str,
    text: str,
    source_chunk_id: str,
    decision_type: str | None = None,
    confidence_score: float | None = None,
) -> Decision:
    """Cria uma decisao detectada a partir de um chunk de transcricao.

    ``decision_type``/``confidence_score`` sao opcionais e, quando fornecidos
    (ex.: extraidos por um LLM real), sobrescrevem os defaults heuristicos --
    chamadas existentes sem esses kwargs mantem o comportamento exato de antes.
    """
    decision = Decision(
        tenant_id=tenant_id,
        project_id=project_id,
        meeting_id=meeting_id,
        decision_text=normalize_text(text),
        decision_type=decision_type or decision_type_for(text),
        status="detected",
        responsible_area=None,
        confidence_score=confidence_score if confidence_score is not None else 0.8,
        source_chunk_ids=json.dumps([source_chunk_id]),
    )
    db.add(decision)
    return decision
