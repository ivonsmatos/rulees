"""
Adapter LLM para o Gemini (Google), via camada de compatibilidade com a API da OpenAI.

O Gemini expõe um endpoint compatível com a Chat Completions API da OpenAI em
``https://generativelanguage.googleapis.com/v1beta/openai`` (mesmo formato de
request/response, incluindo `response_format: {"type": "json_object"}`). Por isso
reaproveitamos `OpenAIClient` (já testado, com timeout e parse de JSON com fallback
de extração) em vez de duplicar um cliente HTTP inteiro só para trocar a URL base.

Configuração via settings: LLM_PROVIDER=gemini, GEMINI_API_KEY, GEMINI_MODEL.

Uso:
    from app.modules.ai_agents.gemini_adapter import get_gemini_client
    client = get_gemini_client()
    if client is not None:
        raw = client.chat_json([{"role": "user", "content": "..."}])
"""

from app.modules.ai_agents.openai_adapter import OpenAIClient


def get_gemini_client() -> OpenAIClient | None:
    """Factory a partir das settings. Retorna None se não houver API key configurada."""
    from app.core.settings import get_settings

    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    return OpenAIClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        base_url=settings.gemini_base_url,
    )
