"""
Providers de embeddings para o RAG.

- DeterministicHashEmbeddingProvider: hash local (padrão, sem custo/API externa,
  mantém compatibilidade com o índice nativo pgvector de 64 dimensões).
- OpenAIEmbeddingProvider: usa a API de embeddings da OpenAI (text-embedding-3-small,
  1536 dim), requer OPENAI_API_KEY.
- OllamaEmbeddingProvider: usa um modelo local via Ollama (dimensão variável).

Selecionado via settings.embedding_provider ("deterministic" | "openai" | "ollama").
Fallback automático para deterministic em caso de erro de rede/configuração.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

EMBEDDING_DIMENSION = 64


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ÿ]+", text.lower())


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, text: str) -> list[float]: ...


class DeterministicHashEmbeddingProvider:
    """Embedding local determinístico (hash de tokens). Sem custo, sem API externa."""

    name = "rulees-hash-v1"
    dimension = EMBEDDING_DIMENSION

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in _tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimension
            weight = 1.0 + (digest[2] / 255)
            vector[index] += weight
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class OpenAIEmbeddingProvider:
    """Embedding real via API da OpenAI. Requer OPENAI_API_KEY configurada."""

    name = "text-embedding-3-small"
    dimension = 1536

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        self.api_key = api_key
        self.model = model
        self.name = model

    def embed(self, text: str) -> list[float]:
        import httpx

        resp = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": text[:8000]},
            timeout=httpx.Timeout(30.0),
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]


class OllamaEmbeddingProvider:
    """Embedding via modelo local rodando no Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.name = f"ollama:{model}"

    def embed(self, text: str) -> list[float]:
        from app.modules.ai_agents.ollama_adapter import OllamaClient

        client = OllamaClient(base_url=self.base_url, model=self.model)
        return client.embed(text)


def get_embedding_provider() -> EmbeddingProvider:
    """Factory baseada em settings. Fallback seguro para o provider determinístico."""
    from app.core.settings import get_settings

    settings = get_settings()
    provider_name = getattr(settings, "embedding_provider", "deterministic")

    if provider_name == "openai":
        api_key = getattr(settings, "openai_api_key", "")
        if api_key:
            return OpenAIEmbeddingProvider(api_key=api_key)
    elif provider_name == "ollama":
        return OllamaEmbeddingProvider(
            base_url=getattr(settings, "ollama_base_url", "http://localhost:11434"),
            model=getattr(settings, "ollama_model", "llama3"),
        )

    return DeterministicHashEmbeddingProvider()


def embed_with_fallback(text: str) -> tuple[list[float], str]:
    """
    Gera embedding usando o provider configurado.
    Em caso de erro (rede, API indisponível), cai para o provider determinístico
    para nunca quebrar o fluxo de RAG.
    Retorna (vetor, nome_do_modelo_usado).
    """
    provider = get_embedding_provider()
    try:
        vector = provider.embed(text)
        if vector:
            return vector, provider.name
    except Exception:
        pass
    fallback = DeterministicHashEmbeddingProvider()
    return fallback.embed(text), fallback.name
