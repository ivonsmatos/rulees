"""Testes da estimativa de custo real por token de LLM (nao a taxa fixa por evento)."""

from app.modules.billing.service import estimate_llm_cost_usd


def test_estimate_cost_unknown_model_returns_none() -> None:
    assert estimate_llm_cost_usd("modelo-desconhecido", prompt_tokens=100, total_tokens=150) is None


def test_estimate_cost_known_model_uses_prompt_and_output_rates() -> None:
    cost = estimate_llm_cost_usd("gpt-4o-mini", prompt_tokens=1000, total_tokens=1500)
    # 1000 tokens de input a 0.15/1M + 500 tokens de output a 0.60/1M
    expected = (1000 * 0.15 + 500 * 0.60) / 1_000_000
    assert cost == expected


def test_estimate_cost_accounts_for_hidden_reasoning_tokens() -> None:
    """Modelos "thinking" (ex.: gemini-2.5-flash) gastam tokens de raciocinio que
    nao aparecem em completion_tokens mas sao cobrados como saida -- a formula usa
    total_tokens - prompt_tokens, nao completion_tokens, para nao subestimar custo."""
    # total_tokens bem maior que prompt+completion visiveis (tokens de raciocinio ocultos)
    cost = estimate_llm_cost_usd("gemini-2.5-flash", prompt_tokens=477, total_tokens=1000)
    expected = (477 * 0.30 + 523 * 2.50) / 1_000_000
    assert cost == expected


def test_estimate_cost_never_negative_when_total_below_prompt() -> None:
    """Guarda defensiva: se total_tokens vier menor que prompt_tokens (resposta
    inconsistente do provider), a base de saida e zerada, nunca negativa."""
    cost = estimate_llm_cost_usd("gpt-4o-mini", prompt_tokens=100, total_tokens=50)
    expected = (100 * 0.15 + 0 * 0.60) / 1_000_000
    assert cost == expected
