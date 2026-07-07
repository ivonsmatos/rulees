"""Testes deterministicos do classificador combinado ao vivo (Observer + Inquisitor + Decision).

Nenhum destes testes faz chamada de rede real: o provider "openai"/"ollama" e
exercitado com clientes falsos via monkeypatch, para provar que qualquer falha
(sem API key, excecao, timeout, resposta nao-JSON, campos alucinados) cai
automaticamente e deterministicamente para a heuristica local -- a regra de
ouro "Falha de IA nao derruba reuniao".
"""

import asyncio
import time

from app.core.settings import Settings
from app.modules.ai_agents import llm_classifier


RULE_TEXT = "Quando o cliente tiver investimento acima de R$ 15000, deve receber 1% de cashback."
QUESTION_TEXT = "Cliente premium terá benefício especial."
DECISION_TEXT = "Fica aprovado que a primeira versão será lançada para clientes premium."


class _FakeOpenAIClient:
    def __init__(self, payload=None, exc=None, delay=0.0, model="fake-gpt", usage=None):
        self.payload = payload
        self.exc = exc
        self.delay = delay
        self.model = model
        self.usage = usage

    def chat_json(self, messages, temperature=0.1, max_tokens=600):
        if self.delay:
            time.sleep(self.delay)
        if self.exc:
            raise self.exc
        return self.payload

    def chat_json_with_usage(self, messages, temperature=0.1, max_tokens=600):
        if self.delay:
            time.sleep(self.delay)
        if self.exc:
            raise self.exc
        return self.payload, self.usage


class _FakeOllamaClient:
    def __init__(self, raw="", model="fake-llama"):
        self.raw = raw
        self.model = model

    def chat(self, messages, temperature=0.1, max_tokens=600):
        return self.raw


def _run(text: str):
    return asyncio.run(llm_classifier.classify_transcript_text(text))


def test_heuristic_default_provider_matches_existing_behavior() -> None:
    result = _run(RULE_TEXT)
    assert result.engine == "heuristic"
    assert result.model_name == "local_heuristic"
    assert result.prompt_version == "local_v1"
    assert result.is_rule_candidate is True
    assert result.rule_confidence == 0.76
    assert result.rule_condition_text is None
    assert result.rule_result_text is None
    assert result.warnings == []


def test_heuristic_question_and_decision_detection() -> None:
    question_result = _run(QUESTION_TEXT)
    assert question_result.is_question_candidate is True
    assert question_result.question_gap_type == "ambiguous_term"
    assert question_result.question_confidence == 0.74

    decision_result = _run(DECISION_TEXT)
    assert decision_result.is_decision_candidate is True
    assert decision_result.decision_type == "approval"
    assert decision_result.decision_confidence == 0.8


def test_llm_success_path_parses_grounded_fields(monkeypatch) -> None:
    settings = Settings(llm_provider="openai", openai_api_key="test-key", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    fake_client = _FakeOpenAIClient(
        payload={
            "is_rule_candidate": True,
            "rule_confidence": 0.91,
            "rule_condition_text": "cliente tiver investimento acima de R$ 15000",
            "rule_result_text": "deve receber 1% de cashback",
            "is_question_candidate": False,
            "is_decision_candidate": False,
        }
    )
    monkeypatch.setattr(llm_classifier, "get_openai_client", lambda: fake_client)

    result = _run(RULE_TEXT)

    assert result.engine == "llm_openai"
    assert result.model_name == "fake-gpt"
    assert result.prompt_version == "combined_classifier_v1"
    assert result.is_rule_candidate is True
    assert result.rule_confidence == 0.91
    assert result.rule_condition_text == "cliente tiver investimento acima de R$ 15000"
    assert result.rule_result_text == "deve receber 1% de cashback"
    assert result.warnings == []


def test_llm_success_path_captures_real_token_usage(monkeypatch) -> None:
    """Custo real por chamada depende de capturar prompt/completion tokens reais
    da resposta do provider (nao uma estimativa fixa por tipo de evento)."""
    settings = Settings(llm_provider="openai", openai_api_key="test-key", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    fake_client = _FakeOpenAIClient(
        payload={"is_rule_candidate": False, "is_question_candidate": False, "is_decision_candidate": False},
        usage={"prompt_tokens": 120, "completion_tokens": 40, "total_tokens": 160},
    )
    monkeypatch.setattr(llm_classifier, "get_openai_client", lambda: fake_client)

    result = _run(RULE_TEXT)

    assert result.usage == {"prompt_tokens": 120, "completion_tokens": 40, "total_tokens": 160}


def test_ollama_success_path_has_no_token_usage(monkeypatch) -> None:
    settings = Settings(llm_provider="ollama", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    monkeypatch.setattr(
        llm_classifier,
        "get_ollama_client",
        lambda: _FakeOllamaClient(raw='{"is_rule_candidate": false}'),
    )

    result = _run(RULE_TEXT)

    assert result.usage is None


def test_llm_ungrounded_numbers_are_discarded(monkeypatch) -> None:
    """Anti-alucinacao: se o LLM inventar um numero que nao esta na transcricao
    original, a extracao estruturada da regra e descartada (nunca vira regra)."""
    settings = Settings(llm_provider="openai", openai_api_key="test-key", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    fake_client = _FakeOpenAIClient(
        payload={
            "is_rule_candidate": True,
            "rule_confidence": 0.9,
            "rule_condition_text": "cliente tiver investimento acima de R$ 99999",
            "rule_result_text": "deve receber 5% de cashback",
            "is_question_candidate": False,
            "is_decision_candidate": False,
        }
    )
    monkeypatch.setattr(llm_classifier, "get_openai_client", lambda: fake_client)

    result = _run(RULE_TEXT)

    assert result.is_rule_candidate is False
    assert any(w["code"] == "LLM_UNGROUNDED_RULE_FIELDS" for w in result.warnings)


def test_gemini_success_path_uses_openai_compat_client(monkeypatch) -> None:
    """Gemini reaproveita o OpenAIClient via camada de compatibilidade -- mesmo
    contrato chat_json, so troca o factory (get_gemini_client em vez de
    get_openai_client) e a base_url/model."""
    settings = Settings(llm_provider="gemini", gemini_api_key="test-key", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    fake_client = _FakeOpenAIClient(
        payload={
            "is_rule_candidate": True,
            "rule_confidence": 0.85,
            "rule_condition_text": "cliente tiver investimento acima de R$ 15000",
            "rule_result_text": "deve receber 1% de cashback",
            "is_question_candidate": False,
            "is_decision_candidate": False,
        },
        model="gemini-2.5-flash",
    )
    monkeypatch.setattr(llm_classifier, "get_gemini_client", lambda: fake_client)

    result = _run(RULE_TEXT)

    assert result.engine == "llm_gemini"
    assert result.model_name == "gemini-2.5-flash"
    assert result.is_rule_candidate is True
    assert result.rule_confidence == 0.85
    assert result.warnings == []


def test_gemini_client_unavailable_falls_back_to_heuristic(monkeypatch) -> None:
    settings = Settings(llm_provider="gemini", gemini_api_key="", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    monkeypatch.setattr(llm_classifier, "get_gemini_client", lambda: None)

    result = _run(RULE_TEXT)

    assert result.engine == "heuristic"
    assert result.is_rule_candidate is True
    assert any(w["code"] == "LLM_CLIENT_UNAVAILABLE" for w in result.warnings)


def test_llm_client_unavailable_falls_back_to_heuristic(monkeypatch) -> None:
    settings = Settings(llm_provider="openai", openai_api_key="", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    monkeypatch.setattr(llm_classifier, "get_openai_client", lambda: None)

    result = _run(RULE_TEXT)

    assert result.engine == "heuristic"
    assert result.is_rule_candidate is True
    assert result.rule_confidence == 0.76
    assert any(w["code"] == "LLM_CLIENT_UNAVAILABLE" for w in result.warnings)


def test_llm_call_exception_falls_back_to_heuristic(monkeypatch) -> None:
    settings = Settings(llm_provider="openai", openai_api_key="test-key", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    fake_client = _FakeOpenAIClient(exc=RuntimeError("network down"))
    monkeypatch.setattr(llm_classifier, "get_openai_client", lambda: fake_client)

    result = _run(DECISION_TEXT)

    assert result.engine == "heuristic"
    assert result.is_decision_candidate is True
    assert any(w["code"] == "LLM_CALL_FAILED" for w in result.warnings)


def test_llm_timeout_falls_back_to_heuristic(monkeypatch) -> None:
    settings = Settings(llm_provider="openai", openai_api_key="test-key", llm_timeout_seconds=0.05)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    fake_client = _FakeOpenAIClient(payload={"is_rule_candidate": False}, delay=1.0)
    monkeypatch.setattr(llm_classifier, "get_openai_client", lambda: fake_client)

    result = _run(DECISION_TEXT)

    assert result.engine == "heuristic"
    assert any(w["code"] == "LLM_TIMEOUT" for w in result.warnings)


def test_ollama_non_json_response_falls_back_to_heuristic(monkeypatch) -> None:
    settings = Settings(llm_provider="ollama", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    monkeypatch.setattr(llm_classifier, "get_ollama_client", lambda: _FakeOllamaClient(raw="not json at all"))

    result = _run(QUESTION_TEXT)

    assert result.engine == "heuristic"
    assert result.is_question_candidate is True
    assert any(w["code"] == "LLM_EMPTY_RESPONSE" for w in result.warnings)


def test_ollama_success_path_extracts_json_from_noisy_text(monkeypatch) -> None:
    settings = Settings(llm_provider="ollama", llm_timeout_seconds=5.0)
    monkeypatch.setattr(llm_classifier, "get_settings", lambda: settings)
    raw = (
        "Aqui esta minha analise:\n"
        '{"is_rule_candidate": false, "is_question_candidate": true, '
        '"question_text": "Qual e o criterio de cliente premium?", '
        '"question_reason": "Termo ambiguo mencionado.", '
        '"question_gap_type": "ambiguous_term", "question_priority": "high", '
        '"question_confidence": 0.88, "is_decision_candidate": false}\n'
        "Espero que ajude."
    )
    monkeypatch.setattr(llm_classifier, "get_ollama_client", lambda: _FakeOllamaClient(raw=raw))

    result = _run(QUESTION_TEXT)

    assert result.engine == "llm_ollama"
    assert result.model_name == "fake-llama"
    assert result.is_question_candidate is True
    assert result.question_gap_type == "ambiguous_term"
    assert result.question_confidence == 0.88
    assert result.warnings == []
