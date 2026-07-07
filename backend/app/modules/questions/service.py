import json

from sqlalchemy.orm import Session

from app.modules.questions.models import OpenQuestion
from app.modules.rules_ledger.service import normalize_text


def should_suggest_question(text: str) -> bool:
    lowered = text.lower()
    return (
        "?" in text
        or "precisamos definir" in lowered
        or "não ficou claro" in lowered
        or "nao ficou claro" in lowered
        or "cliente premium" in lowered
        or "benefício especial" in lowered
        or "beneficio especial" in lowered
    )


def build_question_text(text: str) -> tuple[str, str, str, str]:
    lowered = text.lower()
    if "cliente premium" in lowered:
        return (
            "Qual é o critério objetivo para classificar um cliente como premium?",
            "A fala menciona cliente premium sem deixar a elegibilidade verificável.",
            "ambiguous_term",
            "high",
        )
    if "benefício especial" in lowered or "beneficio especial" in lowered:
        return (
            "Qual benefício especial deve ser aplicado e em quais condições?",
            "A fala menciona benefício especial sem detalhar resultado ou condição.",
            "missing_result",
            "high",
        )
    return (
        normalize_text(text),
        "A fala indica uma dúvida ou lacuna que precisa de confirmação humana.",
        "open_question",
        "medium",
    )


def create_open_question(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    meeting_id: str,
    text: str,
    source_chunk_id: str,
    question_text: str | None = None,
    reason: str | None = None,
    gap_type: str | None = None,
    priority: str | None = None,
    confidence_score: float | None = None,
) -> OpenQuestion:
    """Cria uma pergunta aberta a partir de um chunk de transcricao.

    ``question_text``/``reason``/``gap_type``/``priority``/``confidence_score``
    sao opcionais e, quando fornecidos (ex.: extraidos por um LLM real),
    sobrescrevem os defaults heuristicos de ``build_question_text`` --
    chamadas existentes sem esses kwargs mantem o comportamento exato de antes.
    """
    default_text, default_reason, default_gap_type, default_priority = build_question_text(text)
    question = OpenQuestion(
        tenant_id=tenant_id,
        project_id=project_id,
        meeting_id=meeting_id,
        question_text=question_text or default_text,
        reason=reason or default_reason,
        gap_type=gap_type or default_gap_type,
        priority=priority or default_priority,
        status="open",
        confidence_score=confidence_score if confidence_score is not None else 0.74,
        source_chunk_ids=json.dumps([source_chunk_id]),
    )
    db.add(question)
    return question
