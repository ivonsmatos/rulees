"""
Classificador combinado do fluxo AO VIVO (Observer + Inquisitor + Decision).

Por padrão (``settings.llm_provider == "heuristic"``) usa exclusivamente as
funções heurísticas já existentes (regex/keyword matching), sem nenhuma
chamada de rede -- isso mantém o comportamento byte-idêntico ao atual e é o
que roda nos testes (``tests/conftest.py`` nunca seta ``LLM_PROVIDER``).

Quando ``settings.llm_provider`` é ``"openai"`` ou ``"ollama"``, monta um único
prompt combinado pedindo classificação de regra + pergunta + decisão em uma
resposta JSON estruturada (evita 3 chamadas separadas e ajuda a meta de
latência de "regra clara detectada em até 20-30s" do doc de lançamento).

Regra de ouro (doc de lançamento): "Falha de IA não derruba reunião". Qualquer
exceção -- timeout, erro de rede, client ausente por falta de API key, JSON
inválido/incompleto -- cai automaticamente para a heurística determinística e
anota um warning; NUNCA propaga para quem chamou.

Regras anti-alucinação aplicadas aqui, independente do engine:
  - ``source_chunk_id`` nunca é decidido neste módulo -- é sempre o chunk real
    de transcrição, atribuído por quem chama (`realtime/websocket.py`).
  - Regra candidata nunca nasce aprovada (isso é garantido em
    ``rules_ledger.service.create_candidate_rule``, que sempre usa
    ``RuleStatus.needs_review``).
  - O LLM só pode extrair ``condition_text``/``result_text`` a partir do texto
    real transcrito; se ele introduzir números/valores que não aparecem no
    texto original (parafraseando ao ponto de inventar prazo/valor/condição),
    a extração daquele campo é descartada e cai para heurística (ver
    ``_grounded_in_source``).
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from app.core.settings import Settings, get_settings
from app.modules.ai_agents.ollama_adapter import get_ollama_client
from app.modules.ai_agents.openai_adapter import get_openai_client
from app.modules.decisions.service import decision_type_for, should_detect_decision
from app.modules.questions.service import build_question_text, should_suggest_question
from app.modules.rules_ledger.service import looks_like_rule, normalize_text

logger = logging.getLogger(__name__)

Engine = Literal["heuristic", "llm_openai", "llm_ollama"]

PROMPT_VERSION_HEURISTIC = "local_v1"
PROMPT_VERSION_LLM = "combined_classifier_v1"

_ALLOWED_GAP_TYPES = {"ambiguous_term", "missing_result", "open_question"}
_ALLOWED_PRIORITIES = {"high", "medium", "low"}
_ALLOWED_DECISION_TYPES = {"approval", "deadline_definition", "owner_definition", "business_decision"}

_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?%?")


@dataclass
class ClassificationWarning:
    code: str
    message: str
    severity: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "severity": self.severity}


@dataclass
class ClassificationResult:
    """Contrato de saída do classificador combinado ao vivo.

    ``engine``/``model_name``/``prompt_version`` refletem o que REALMENTE
    produziu o resultado (podem divergir do provider configurado se houve
    fallback automático para heurística).
    """

    engine: Engine
    model_name: str
    prompt_version: str

    is_rule_candidate: bool = False
    rule_confidence: float = 0.0
    rule_condition_text: str | None = None
    rule_result_text: str | None = None

    is_question_candidate: bool = False
    question_text: str | None = None
    question_reason: str | None = None
    question_gap_type: str | None = None
    question_priority: str | None = None
    question_confidence: float = 0.0

    is_decision_candidate: bool = False
    decision_type: str | None = None
    decision_confidence: float = 0.0

    warnings: list[dict[str, Any]] = field(default_factory=list)


class _LLMUnavailable(Exception):
    """Sinaliza que o LLM não pôde ser usado; sempre resolvida com fallback heurístico."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


# ── Heurística (fallback/seam determinístico -- usado em testes) ──────────────


def _heuristic_classification(text: str) -> ClassificationResult:
    result = ClassificationResult(
        engine="heuristic",
        model_name="local_heuristic",
        prompt_version=PROMPT_VERSION_HEURISTIC,
    )

    if looks_like_rule(text):
        result.is_rule_candidate = True
        result.rule_confidence = 0.76

    if should_suggest_question(text):
        question_text, reason, gap_type, priority = build_question_text(text)
        result.is_question_candidate = True
        result.question_text = question_text
        result.question_reason = reason
        result.question_gap_type = gap_type
        result.question_priority = priority
        result.question_confidence = 0.74

    if should_detect_decision(text):
        result.is_decision_candidate = True
        result.decision_type = decision_type_for(text)
        result.decision_confidence = 0.8

    return result


# ── Entry point público ────────────────────────────────────────────────────────


async def classify_transcript_text(text: str) -> ClassificationResult:
    """Classifica um chunk final de transcrição normalizada em regra/pergunta/decisão.

    Nunca levanta exceção: qualquer falha do LLM cai para a heurística com um
    warning anexado ao resultado.
    """
    settings = get_settings()
    provider = settings.llm_provider

    if provider not in ("openai", "ollama"):
        return _heuristic_classification(text)

    engine: Engine = "llm_openai" if provider == "openai" else "llm_ollama"
    try:
        return await _run_llm_classification(text, provider=provider, engine=engine, settings=settings)
    except _LLMUnavailable as exc:
        logger.info("Fallback para heuristica (%s): %s", exc.code, exc.message)
        fallback = _heuristic_classification(text)
        fallback.warnings.append(ClassificationWarning(exc.code, exc.message, "medium").to_dict())
        return fallback
    except Exception as exc:  # pragma: no cover -- defensivo, nunca deve propagar (regra: IA nao derruba reuniao)
        logger.exception("Erro inesperado na classificacao via LLM (%s); usando heuristica.", provider)
        fallback = _heuristic_classification(text)
        fallback.warnings.append(
            ClassificationWarning("LLM_UNEXPECTED_ERROR", f"Erro inesperado: {exc}", "high").to_dict()
        )
        return fallback


# ── Caminho LLM real (OpenAI / Ollama) ─────────────────────────────────────────

_COMBINED_SYSTEM_PROMPT = """Voce e um pipeline de analise de reunioes de requisitos de negocio (Rulees).
Analise APENAS a fala fornecida (ja transcrita e normalizada) e classifique em ate tres dimensoes independentes:
1) e uma regra de negocio candidata (condicao + resultado)?
2) indica uma pergunta/lacuna que precisa de confirmacao humana?
3) registra uma decisao de negocio (aprovacao, prazo, responsavel etc)?

REGRAS OBRIGATORIAS (anti-alucinacao):
- NUNCA invente valores numericos, prazos, percentuais ou condicoes que nao estejam
  explicitamente no texto fornecido.
- Se nao houver evidencia clara para uma dimensao, marque o campo correspondente
  como false/null -- nao force uma classificacao positiva.
- condition_text e result_text devem ser extraidos literalmente do sentido do texto,
  nunca parafraseados a ponto de mudar o significado.

Responda APENAS com um JSON valido, sem markdown e sem comentarios, no formato exato:
{
  "is_rule_candidate": bool,
  "rule_confidence": 0.0-1.0,
  "rule_condition_text": string|null,
  "rule_result_text": string|null,
  "is_question_candidate": bool,
  "question_text": string|null,
  "question_reason": string|null,
  "question_gap_type": "ambiguous_term"|"missing_result"|"open_question"|null,
  "question_priority": "high"|"medium"|"low"|null,
  "question_confidence": 0.0-1.0,
  "is_decision_candidate": bool,
  "decision_type": "approval"|"deadline_definition"|"owner_definition"|"business_decision"|null,
  "decision_confidence": 0.0-1.0
}
"""


def _build_messages(text: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": _COMBINED_SYSTEM_PROMPT},
        {"role": "user", "content": f"Fala transcrita:\n\n{text}"},
    ]


def _extract_json(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start < 0 or end <= start:
            return None
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            return None


async def _run_llm_classification(
    text: str, *, provider: str, engine: Engine, settings: Settings
) -> ClassificationResult:
    messages = _build_messages(text)

    if provider == "openai":
        client = get_openai_client()
        if client is None:
            raise _LLMUnavailable(
                "LLM_CLIENT_UNAVAILABLE", "OPENAI_API_KEY nao configurada; usando heuristica."
            )
        model_name = client.model

        def call() -> dict[str, Any] | None:
            return client.chat_json(messages, temperature=0.1, max_tokens=600)

    else:
        client = get_ollama_client()
        model_name = client.model

        def call() -> dict[str, Any] | None:
            raw = client.chat(messages, temperature=0.1, max_tokens=600)
            return _extract_json(raw)

    try:
        payload = await asyncio.wait_for(
            asyncio.to_thread(call), timeout=settings.llm_timeout_seconds
        )
    except TimeoutError as exc:
        raise _LLMUnavailable(
            "LLM_TIMEOUT", f"Timeout ({settings.llm_timeout_seconds}s) ao chamar {provider}."
        ) from exc
    except _LLMUnavailable:
        raise
    except Exception as exc:
        raise _LLMUnavailable("LLM_CALL_FAILED", f"Falha ao chamar {provider}: {exc}") from exc

    if not isinstance(payload, dict):
        raise _LLMUnavailable("LLM_EMPTY_RESPONSE", f"Resposta vazia ou nao-JSON do {provider}.")

    result, warnings = _parse_llm_payload(payload, original_text=text, engine=engine, model_name=model_name)
    result.warnings = [w.to_dict() for w in warnings]
    return result


def _numbers_in(text: str) -> set[str]:
    return set(_NUMBER_RE.findall(text))


def _grounded_in_source(original: str, *fragments: str | None) -> bool:
    """Anti-alucinacao: nenhum numero/valor novo pode aparecer em `fragments`
    que nao esteja presente no texto original transcrito."""
    original_numbers = _numbers_in(original)
    for fragment in fragments:
        if not fragment:
            continue
        if _numbers_in(fragment) - original_numbers:
            return False
    return True


def _clamp01(value: Any, *, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, parsed))


def _clean_str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _parse_llm_payload(
    payload: dict[str, Any], *, original_text: str, engine: Engine, model_name: str
) -> tuple[ClassificationResult, list[ClassificationWarning]]:
    result = ClassificationResult(engine=engine, model_name=model_name, prompt_version=PROMPT_VERSION_LLM)
    warnings: list[ClassificationWarning] = []

    if bool(payload.get("is_rule_candidate")):
        condition_text = _clean_str(payload.get("rule_condition_text"))
        result_text = _clean_str(payload.get("rule_result_text"))
        if not _grounded_in_source(original_text, condition_text, result_text):
            warnings.append(
                ClassificationWarning(
                    "LLM_UNGROUNDED_RULE_FIELDS",
                    "condition_text/result_text contem valores nao presentes na transcricao original; "
                    "descartando extracao estruturada do LLM para esta regra (rule_text permanece o texto real).",
                    "high",
                )
            )
        else:
            result.is_rule_candidate = True
            result.rule_confidence = _clamp01(payload.get("rule_confidence"), default=0.7)
            result.rule_condition_text = condition_text
            result.rule_result_text = result_text

    if bool(payload.get("is_question_candidate")):
        question_text = _clean_str(payload.get("question_text")) or normalize_text(original_text)
        result.is_question_candidate = True
        result.question_text = question_text
        result.question_reason = (
            _clean_str(payload.get("question_reason"))
            or "A fala indica uma duvida ou lacuna que precisa de confirmacao humana."
        )
        gap_type = payload.get("question_gap_type")
        result.question_gap_type = gap_type if gap_type in _ALLOWED_GAP_TYPES else "open_question"
        priority = payload.get("question_priority")
        result.question_priority = priority if priority in _ALLOWED_PRIORITIES else "medium"
        result.question_confidence = _clamp01(payload.get("question_confidence"), default=0.7)

    if bool(payload.get("is_decision_candidate")):
        decision_type = payload.get("decision_type")
        result.is_decision_candidate = True
        result.decision_type = decision_type if decision_type in _ALLOWED_DECISION_TYPES else "business_decision"
        result.decision_confidence = _clamp01(payload.get("decision_confidence"), default=0.7)

    return result, warnings
