from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.modules.ai_agents.orchestration import analyze_transcript_text, is_langgraph_available


def _register(client: TestClient, name: str, organization_name: str) -> tuple[dict, dict[str, str]]:
    email_prefix = name.lower().replace(" ", "-")
    response = client.post(
        "/api/auth/register",
        json={
            "name": name,
            "email": f"{email_prefix}-{uuid4().hex[:8]}@rulees.dev",
            "password": "rulees123",
            "organization_name": organization_name,
        },
    )
    assert response.status_code == 200
    data = response.json()
    return data, {
        "Authorization": f"Bearer {data['access_token']}",
        "X-Tenant-Id": data["tenant"]["id"],
    }


def test_langgraph_is_installed_and_used_as_engine() -> None:
    assert is_langgraph_available() is True
    result = analyze_transcript_text(
        "Quando o cliente tiver investimento acima de R$ 15000, deve receber 1% de cashback."
    )
    assert result["engine"] == "langgraph"
    assert result["is_rule_candidate"] is True
    assert result["quality_details"]["score"] >= 0


def test_analyze_transcript_classifies_question_and_decision() -> None:
    question_result = analyze_transcript_text("Por que o desconto nao se aplica a clientes antigos?")
    assert question_result["is_question_candidate"] is True

    decision_result = analyze_transcript_text("Ficou decidido que o time vai usar o novo fluxo de aprovacao.")
    assert decision_result["is_decision_candidate"] is True


def test_analyze_preview_endpoint_requires_auth_and_returns_engine_state() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/ai-agents/analyze-preview",
            json={"text": "Quando o cliente cancelar o plano, o acesso deve ser bloqueado imediatamente."},
        )
        assert response.status_code == 401

        _admin, headers = _register(client, "Orchestration Admin", "Tenant Orchestration")
        response = client.post(
            "/api/ai-agents/analyze-preview",
            headers=headers,
            json={"text": "Quando o cliente cancelar o plano, o acesso deve ser bloqueado imediatamente."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["engine"] == "langgraph"
        assert data["is_rule_candidate"] is True
        assert "score" in data["quality_details"]
