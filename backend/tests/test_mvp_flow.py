from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_mvp_flow_detects_rule_and_generates_document() -> None:
    email = f"flow-{uuid4().hex[:8]}@rulees.dev"

    with TestClient(app) as client:
        auth = client.post(
            "/api/auth/register",
            json={
                "name": "Flow Tester",
                "email": email,
                "password": "rulees123",
                "organization_name": "Flow Tenant",
            },
        )
        assert auth.status_code == 200
        auth_data = auth.json()
        token = auth_data["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Tenant-Id": auth_data["tenant"]["id"],
        }

        project = client.post(
            "/api/projects",
            headers=headers,
            json={"name": "Projeto Flow", "description": "Fluxo principal"},
        )
        assert project.status_code == 200
        project_id = project.json()["id"]

        other_auth = client.post(
            "/api/auth/register",
            json={
                "name": "Other Tester",
                "email": f"other-{uuid4().hex[:8]}@rulees.dev",
                "password": "rulees123",
                "organization_name": "Other Tenant",
            },
        )
        assert other_auth.status_code == 200
        other_data = other_auth.json()
        other_headers = {
            "Authorization": f"Bearer {other_data['access_token']}",
            "X-Tenant-Id": other_data["tenant"]["id"],
        }
        cross_tenant_rag = client.get(
            f"/api/projects/{project_id}/rag/search?query=cashback",
            headers=other_headers,
        )
        assert cross_tenant_rag.status_code == 404

        meeting = client.post(
            f"/api/projects/{project_id}/meetings",
            headers=headers,
            json={"title": "Reuniao Flow", "objective": "Validar MVP"},
        )
        assert meeting.status_code == 200
        meeting_id = meeting.json()["id"]

        blocked = client.post(f"/api/meetings/{meeting_id}/start", headers=headers)
        assert blocked.status_code == 400

        consent = client.post(
            f"/api/meetings/{meeting_id}/consent",
            headers=headers,
            json={
                "text_version": "v1",
                "accepted_scope": {
                    "audio": True,
                    "transcription": True,
                    "ai_analysis": True,
                },
            },
        )
        assert consent.status_code == 200

        started = client.post(f"/api/meetings/{meeting_id}/start", headers=headers)
        assert started.status_code == 200
        assert started.json()["status"] == "active"

        with client.websocket_connect(f"/ws/meetings/{meeting_id}?token={token}") as ws:
            assert ws.receive_json()["event_type"] == "client.connected"
            ws.send_json(
                {
                    "event_id": "bad-audio-1",
                    "event_type": "audio.chunk",
                    "payload": {"audio_base64": "@@@", "mime_type": "audio/webm"},
                }
            )
            invalid_audio = ws.receive_json()
            assert invalid_audio["event_id"] == "bad-audio-1"
            assert invalid_audio["event_type"] == "error.validation"
            assert invalid_audio["payload"]["code"] == "INVALID_AUDIO_CHUNK"

            ws.send_json(
                {
                    "event_id": "audio-real-1",
                    "event_type": "audio.chunk",
                    "payload": {
                        "audio_base64": "UklGRg==",
                        "mime_type": "audio/webm",
                        "sequence": 1,
                    },
                }
            )
            audio_events = []
            while True:
                event = ws.receive_json()
                audio_events.append(event)
                if event["event_type"] == "system.ack":
                    break
            audio_transcript = next(
                event for event in audio_events if event["event_type"] == "transcript.final"
            )
            assert audio_transcript["event_id"] == "audio-real-1"
            assert audio_transcript["payload"]["source"] == "stt_mock"
            assert "aguardando STT" in audio_transcript["payload"]["normalized_text"]

            chunks = [
                "Quando o cliente tiver investimento acima de R$ 15000, deve receber 1% de cashback.",
                "Quando o cliente tiver investimento acima de R$ 15000, deve receber 1% de cashback.",
                "Cliente premium terá benefício especial.",
                "Fica aprovado que a primeira versão será lançada para clientes premium.",
            ]
            events = []
            for text in chunks:
                ws.send_json({"event_type": "audio.chunk", "payload": {"text": text}})
                while True:
                    event = ws.receive_json()
                    events.append(event)
                    if event["event_type"] == "system.ack":
                        break

        event_types = {event["event_type"] for event in events}
        assert "transcript.final" in event_types
        assert "ai.rule.detected" in event_types
        assert "ai.question.suggested" in event_types
        assert "ai.decision.detected" in event_types

        rag_search = client.get(
            f"/api/projects/{project_id}/rag/search?query=cashback cliente investimento",
            headers=headers,
        )
        assert rag_search.status_code == 200
        assert rag_search.json()
        assert rag_search.json()[0]["source_type"] == "business_rule"

        state = client.get(f"/api/meetings/{meeting_id}/state", headers=headers)
        assert state.status_code == 200
        state_data = state.json()
        assert any(rule["status"] == "conflict_detected" for rule in state_data["rules"])
        rule = next(rule for rule in state_data["rules"] if rule["status"] == "needs_review")
        assert rule["status"] == "needs_review"
        assert state_data["questions"][0]["status"] == "open"
        assert state_data["decisions"][0]["status"] == "detected"

        approved = client.post(f"/api/rules/{rule['id']}/approve", headers=headers)
        assert approved.status_code == 200
        assert approved.json()["status"] == "approved"
        approved_rule_code = approved.json()["code"]

        document = client.post(
            f"/api/meetings/{meeting_id}/documents/generate", headers=headers
        )
        assert document.status_code == 200
        assert approved_rule_code in document.json()["content"]
        assert "Duvidas abertas" in document.json()["content"]
        assert "Decisoes detectadas" in document.json()["content"]
        document_id = document.json()["id"]

        document_sections = client.get(
            f"/api/documents/{document_id}/sections", headers=headers
        )
        assert document_sections.status_code == 200
        assert {section["section_key"] for section in document_sections.json()} == {
            "summary",
            "rules",
            "evidence",
            "questions",
            "decisions",
        }

        document_versions = client.get(
            f"/api/documents/{document_id}/versions", headers=headers
        )
        assert document_versions.status_code == 200
        assert document_versions.json()[0]["version_number"] == 1

        pdf = client.get(
            f"/api/documents/{document_id}/export/pdf", headers=headers
        )
        assert pdf.status_code == 200
        assert pdf.headers["content-type"] == "application/pdf"

        document_revision = client.post(
            f"/api/documents/{document_id}/versions",
            headers=headers,
            json={
                "content": f"{document.json()['content']}\n\n## Revisao\nConteudo revisado.",
                "change_reason": "Revisao manual do documento funcional",
            },
        )
        assert document_revision.status_code == 200
        assert document_revision.json()["status"] == "draft"

        document_versions_after_revision = client.get(
            f"/api/documents/{document_id}/versions", headers=headers
        )
        assert document_versions_after_revision.status_code == 200
        assert {
            version["version_number"]
            for version in document_versions_after_revision.json()
        } == {1, 2}

        versions_after_approval = client.get(
            f"/api/rules/{rule['id']}/versions", headers=headers
        )
        assert versions_after_approval.status_code == 200
        assert any(
            version["change_reason"] == "Aprovacao humana"
            for version in versions_after_approval.json()
        )

        revised = client.post(
            f"/api/rules/{rule['id']}/versions",
            headers=headers,
            json={
                "rule_text": "Quando o pedido estiver cancelado, deve bloquear emissao de nota fiscal.",
                "condition_text": "Pedido cancelado",
                "result_text": "Bloquear emissao de nota fiscal",
                "change_reason": "Ajuste de regra apos revisao humana",
            },
        )
        assert revised.status_code == 200
        assert revised.json()["version_number"] == 2
        assert revised.json()["status"] == "needs_review"

        versions_after_revision = client.get(
            f"/api/rules/{rule['id']}/versions", headers=headers
        )
        assert versions_after_revision.status_code == 200
        assert {version["version_number"] for version in versions_after_revision.json()} == {
            1,
            2,
        }

        audit_logs = client.get("/api/audit/logs", headers=headers)
        assert audit_logs.status_code == 200
        audit_actions = {log["action"] for log in audit_logs.json()}
        assert {
            "meeting.start",
            "rule.approve",
            "rule.version.create",
            "document.generate",
            "document.version.create",
        }.issubset(audit_actions)

        usage = client.get("/api/usage/summary", headers=headers)
        assert usage.status_code == 200
        usage_types = {item["event_type"] for item in usage.json()}
        assert {
            "audio_chunk_received",
            "ai_rule_detected",
            "ai_question_suggested",
            "ai_decision_detected",
            "rag_conflict_checked",
            "rule_approved",
            "rule_version_created",
            "document_generated",
            "document_version_created",
            "pdf_exported",
        }.issubset(usage_types)

        billing = client.get("/api/billing/status", headers=headers)
        assert billing.status_code == 200
        billing_data = billing.json()
        assert billing_data["plan_name"] == "trial"
        assert any(
            item["event_type"] == "audio_chunk_received" and item["remaining"] >= 0
            for item in billing_data["limits"]
        )

        agent_runs = client.get(f"/api/meetings/{meeting_id}/agent-runs", headers=headers)
        assert agent_runs.status_code == 200
        agent_run_data = agent_runs.json()
        agent_names = {run["agent_name"] for run in agent_run_data}
        assert {"Scribe", "Observer", "RAG Guardian", "Rule Quality", "Inquisitor", "Decision"}.issubset(agent_names)
        observer_run = next(run for run in agent_run_data if run["agent_name"] == "Observer")
        assert observer_run["schema_version"] == "1.0"
        assert observer_run["input_reference"]["source_type"] == "transcript_chunk"
        assert observer_run["output"]["detected_items"][0]["rule_candidate"][
            "source_references"
        ][0]["source_type"] == "transcript_chunk"
        rag_run = next(run for run in agent_run_data if run["agent_name"] == "RAG Guardian")
        assert rag_run["output"]["history_verified"] is True
        assert rag_run["output"]["recommended_status"] in {
            "needs_review",
            "conflict_detected",
        }
        quality_run = next(run for run in agent_run_data if run["agent_name"] == "Rule Quality")
        assert quality_run["output"]["score"] >= 0
        assert "checks" in quality_run["output"]
