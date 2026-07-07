from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.modules.audit.service import sanitize_audit_details


def _register(client: TestClient) -> tuple[dict, dict[str, str]]:
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Ops Tester",
            "email": f"ops-{uuid4().hex[:8]}@rulees.dev",
            "password": "rulees123",
            "organization_name": "Tenant Ops",
        },
    )
    assert response.status_code == 200
    data = response.json()
    return data, {
        "Authorization": f"Bearer {data['access_token']}",
        "X-Tenant-Id": data["tenant"]["id"],
    }


def _meeting_with_rule(client: TestClient, auth: dict, headers: dict[str, str]) -> tuple[str, dict]:
    project = client.post(
        "/api/projects",
        headers=headers,
        json={"name": "Projeto Ledger Ops", "description": ""},
    )
    assert project.status_code == 200
    meeting = client.post(
        f"/api/projects/{project.json()['id']}/meetings",
        headers=headers,
        json={"title": "Reuniao Ledger Ops", "objective": "Validar ledger"},
    )
    assert meeting.status_code == 200
    meeting_id = meeting.json()["id"]
    assert client.post(
        f"/api/meetings/{meeting_id}/consent",
        headers=headers,
        json={"text_version": "v1", "accepted_scope": {"audio": True, "transcription": True}},
    ).status_code == 200
    assert client.post(f"/api/meetings/{meeting_id}/start", headers=headers).status_code == 200

    with client.websocket_connect(f"/ws/meetings/{meeting_id}?token={auth['access_token']}") as ws:
        ws.receive_json()
        ws.send_json(
            {
                "event_id": "rule-ops-1",
                "event_type": "audio.chunk",
                "payload": {
                    "text": "Quando o cadastro estiver incompleto, deve bloquear aprovacao automatica."
                },
            }
        )
        while True:
            event = ws.receive_json()
            if event["event_type"] == "system.ack":
                break

    state = client.get(f"/api/meetings/{meeting_id}/state", headers=headers)
    assert state.status_code == 200
    rule = next(item for item in state.json()["rules"] if item["status"] == "needs_review")
    return meeting_id, rule


def test_rule_lifecycle_evidence_exports_costs_audit_and_metrics() -> None:
    with TestClient(app) as client:
        auth, headers = _register(client)
        meeting_id, rule = _meeting_with_rule(client, auth, headers)

        evidence = client.get(f"/api/rules/{rule['id']}/evidence", headers=headers)
        assert evidence.status_code == 200
        assert evidence.json()[0]["normalized_text"].startswith("Quando o cadastro")

        approved = client.post(f"/api/rules/{rule['id']}/approve", headers=headers)
        assert approved.status_code == 200
        assert approved.json()["quality_details"]["evidence_count"] == 1

        lifecycle = client.get(f"/api/rules/{rule['id']}/lifecycle-events", headers=headers)
        assert lifecycle.status_code == 200
        assert {event["event_type"] for event in lifecycle.json()} == {"rule.approved"}

        replacement = client.post(
            f"/api/rules/{rule['id']}/replace",
            headers=headers,
            json={
                "rule_text": "Quando o cadastro estiver incompleto, deve exigir revisao manual.",
                "condition_text": "Cadastro incompleto",
                "result_text": "Exigir revisao manual",
                "change_reason": "Fluxo ajustado",
            },
        )
        assert replacement.status_code == 200
        assert replacement.json()["status"] == "needs_review"

        replaced_lifecycle = client.get(f"/api/rules/{rule['id']}/lifecycle-events", headers=headers)
        assert any(event["event_type"] == "rule.replaced" for event in replaced_lifecycle.json())

        document = client.post(f"/api/meetings/{meeting_id}/documents/generate", headers=headers)
        assert document.status_code == 200
        document_id = document.json()["id"]

        markdown = client.get(f"/api/documents/{document_id}/export/markdown", headers=headers)
        assert markdown.status_code == 200
        assert markdown.headers["content-type"].startswith("text/markdown")
        assert "# Documento funcional" in markdown.text

        jira_job = client.post(
            f"/api/documents/{document_id}/export-jobs",
            headers=headers,
            json={"format": "jira"},
        )
        assert jira_job.status_code == 200
        assert jira_job.json()["payload"]["metadata"]["document_id"] == document_id

        jobs = client.get(f"/api/documents/{document_id}/export-jobs", headers=headers)
        assert jobs.status_code == 200
        assert jobs.json()[0]["format"] == "jira"

        billing = client.get("/api/billing/status", headers=headers)
        assert billing.status_code == 200
        assert any(item["estimated_cost_usd"] > 0 for item in billing.json()["estimated_costs"])

        filtered_audit = client.get("/api/audit/logs?action=rule.replace", headers=headers)
        assert filtered_audit.status_code == 200
        assert {item["action"] for item in filtered_audit.json()} == {"rule.replace"}

        metrics = client.get("/metrics")
        assert metrics.status_code == 200
        assert "rulees_http_requests_total" in metrics.text


def test_audit_details_are_sanitized() -> None:
    assert sanitize_audit_details(
        {
            "token": "abc",
            "nested": {"password": "secret", "safe": "ok"},
        }
    ) == {
        "token": "[redacted]",
        "nested": {"password": "[redacted]", "safe": "ok"},
    }


def test_p1_templates_gaps_summary_and_beta_feedback() -> None:
    with TestClient(app) as client:
        _auth, headers = _register(client)
        project = client.post(
            "/api/projects",
            headers=headers,
            json={"name": "Projeto P1", "description": "MVP forte"},
        )
        assert project.status_code == 200
        project_id = project.json()["id"]

        templates = client.get("/api/meetings/templates", headers=headers)
        assert templates.status_code == 200
        assert {template["key"] for template in templates.json()} >= {"discovery", "rules_validation"}

        meeting = client.post(
            f"/api/projects/{project_id}/meetings/from-template",
            headers=headers,
            json={"template_key": "discovery", "title": "Descoberta P1"},
        )
        assert meeting.status_code == 200
        assert "Agenda:" in meeting.json()["objective"]
        meeting_id = meeting.json()["id"]

        gaps = client.get(f"/api/projects/{project_id}/gaps/summary", headers=headers)
        assert gaps.status_code == 200
        assert gaps.json()["meetings_without_transcript"] == 1
        assert gaps.json()["readiness_score"] < 100

        summary = client.get(f"/api/meetings/{meeting_id}/summary", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["meeting_id"] == meeting_id
        assert summary.json()["next_steps"]

        feedback = client.post(
            "/api/feedback/beta",
            headers=headers,
            json={"project_id": project_id, "rating": 5, "category": "ux", "comment": "Fluxo claro"},
        )
        assert feedback.status_code == 200
        assert feedback.json()["rating"] == 5

        feedback_list = client.get("/api/feedback/beta", headers=headers)
        assert feedback_list.status_code == 200
        assert feedback_list.json()[0]["comment"] == "Fluxo claro"
