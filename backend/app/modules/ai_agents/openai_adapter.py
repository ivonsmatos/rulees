"""
Adapter LLM para provedores compatíveis com a API de chat completions da OpenAI.

Configuração via settings: LLM_PROVIDER=openai, OPENAI_API_KEY, OPENAI_MODEL,
OPENAI_BASE_URL (permite apontar para qualquer endpoint compatível).

Uso:
    from app.modules.ai_agents.openai_adapter import get_openai_client
    client = get_openai_client()
    if client is not None:
        raw = client.chat_json([{"role": "user", "content": "..."}])
"""

import json
from typing import Any

import httpx


class OpenAIClient:
    """Cliente mínimo para a Chat Completions API (OpenAI e compatíveis)."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 20.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout_seconds)

    def _post_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> dict[str, Any]:
        """Chamada síncrona a /chat/completions. Retorna o corpo completo da resposta
        (inclui ``usage`` com contagem real de tokens, quando o provider expõe)."""
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=body,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1024,
        json_mode: bool = True,
    ) -> str:
        """Chamada síncrona a /chat/completions. Retorna o texto da resposta."""
        data = self._post_chat_completion(messages, temperature, max_tokens, json_mode)
        return data["choices"][0]["message"]["content"]

    @staticmethod
    def _parse_json_payload(raw: str) -> dict[str, Any] | None:
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

    def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> dict[str, Any] | None:
        """Chama o modelo e faz parse do JSON retornado. None em caso de falha."""
        raw = self.chat(messages, temperature=temperature, max_tokens=max_tokens, json_mode=True)
        return self._parse_json_payload(raw)

    def chat_json_with_usage(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> tuple[dict[str, Any] | None, dict[str, int] | None]:
        """Como `chat_json`, mas também retorna a contagem real de tokens (``usage``),
        quando o provider a expõe -- usado para estimar custo real por chamada."""
        data = self._post_chat_completion(messages, temperature, max_tokens, json_mode=True)
        content = data["choices"][0]["message"]["content"]
        usage_raw = data.get("usage") or {}
        usage: dict[str, int] | None = None
        if usage_raw:
            usage = {
                "prompt_tokens": int(usage_raw.get("prompt_tokens", 0)),
                "completion_tokens": int(usage_raw.get("completion_tokens", 0)),
                "total_tokens": int(usage_raw.get("total_tokens", 0)),
            }
        return self._parse_json_payload(content), usage

    def health(self) -> bool:
        try:
            resp = httpx.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=httpx.Timeout(5.0),
            )
            return resp.status_code == 200
        except Exception:
            return False


def get_openai_client() -> OpenAIClient | None:
    """Factory a partir das settings. Retorna None se não houver API key configurada."""
    from app.core.settings import get_settings

    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAIClient(
        api_key=settings.openai_api_key,
        model=getattr(settings, "openai_model", "gpt-4o-mini"),
        base_url=getattr(settings, "openai_base_url", "https://api.openai.com/v1"),
    )
