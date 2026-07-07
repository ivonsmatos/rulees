"""
Ollama LLM adapter para IA local.

Usa a REST API nativa do Ollama (http://localhost:11434).
Configuração via settings: LLM_PROVIDER=ollama, OLLAMA_BASE_URL, OLLAMA_MODEL.

Uso:
    from app.modules.ai_agents.ollama_adapter import OllamaClient
    client = OllamaClient()
    result = client.generate("Extraia regras de negócio: ...")
"""

import json
from typing import Any

import httpx


class OllamaClient:
    """Cliente para Ollama local."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._timeout = httpx.Timeout(120.0)

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Chamada síncrona ao /api/generate. Retorna texto completo."""
        body: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system:
            body["system"] = system
        resp = httpx.post(
            f"{self.base_url}/api/generate",
            json=body,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Chamada ao /api/chat (compatível com OpenAI messages)."""
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        resp = httpx.post(
            f"{self.base_url}/api/chat",
            json=body,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")

    def embed(self, text: str) -> list[float]:
        """Gera embedding via /api/embeddings."""
        resp = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("embedding", [])

    def list_models(self) -> list[str]:
        """Lista modelos disponíveis localmente."""
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=httpx.Timeout(10.0))
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []

    def health(self) -> bool:
        """Verifica se o servidor Ollama está rodando."""
        try:
            resp = httpx.get(f"{self.base_url}/", timeout=httpx.Timeout(5.0))
            return resp.status_code == 200
        except Exception:
            return False


def get_ollama_client() -> OllamaClient:
    """Factory com configuração das settings."""
    from app.core.settings import get_settings
    s = get_settings()
    return OllamaClient(
        base_url=getattr(s, "ollama_base_url", "http://localhost:11434"),
        model=getattr(s, "ollama_model", "llama3"),
    )


# ── Prompts de agente ─────────────────────────────────────────────────────────

_RULE_EXTRACTION_SYSTEM = """
Você é um agente de extração de regras de negócio.
Analise o texto de transcrição e extraia regras de negócio no formato JSON.
Retorne APENAS JSON válido, sem markdown ou explicações.
Formato:
{
  "detected_items": [
    {
      "rule_text": "...",
      "confidence": 0.0-1.0,
      "source_references": ["fala original..."],
      "tags": ["categoria"]
    }
  ],
  "risks": [],
  "dependencies": []
}
"""

_QUESTION_SYSTEM = """
Você é um agente de detecção de lacunas e perguntas abertas.
Analise o texto e identifique dúvidas não resolvidas.
Retorne APENAS JSON válido:
{
  "questions": [
    {
      "question_text": "...",
      "context": "...",
      "source_references": ["fala original..."],
      "priority": "high|medium|low"
    }
  ]
}
"""


def extract_rules_with_ollama(client: OllamaClient, transcript: str) -> dict[str, Any]:
    """Extrai regras usando Ollama."""
    prompt = f"Transcrição:\n\n{transcript}\n\nExtraia as regras de negócio:"
    raw = client.generate(prompt, system=_RULE_EXTRACTION_SYSTEM, temperature=0.1)
    try:
        # tenta extrair JSON mesmo se vier com texto extra
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end]) if start >= 0 else {
            "detected_items": [], "risks": [], "dependencies": []
        }
    except json.JSONDecodeError:
        return {"detected_items": [], "risks": [], "dependencies": []}


def extract_questions_with_ollama(client: OllamaClient, transcript: str) -> dict[str, Any]:
    """Extrai perguntas abertas usando Ollama."""
    prompt = f"Transcrição:\n\n{transcript}\n\nIdentifique dúvidas e lacunas:"
    raw = client.generate(prompt, system=_QUESTION_SYSTEM, temperature=0.2)
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end]) if start >= 0 else {"questions": []}
    except json.JSONDecodeError:
        return {"questions": []}
