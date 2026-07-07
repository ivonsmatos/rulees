from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


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


def test_meeting_participants_consent_revocation_lifecycle_and_heartbeat() -> None:
    with TestClient(app) as client:
        admin, admin_headers = _register(client, "Meeting Admin", "Tenant Meetings")
        member, _member_headers = _register(client, "Meeting Member", "Tenant Member")

        project = client.post(
            "/api/projects",
            headers=admin_headers,
            json={"name": "Projeto Reunioes", "description": ""},
        )
        assert project.status_code == 200
        project_id = project.json()["id"]

        invite = client.post(
            "/api/auth/tenant/invites",
            headers=admin_headers,
            json={"email": member["user"]["email"], "role": "member"},
        )
        assert invite.status_code == 200
        assert client.post(
            f"/api/auth/tenant/invites/{invite.json()['id']}/accept",
            headers={"Authorization": f"Bearer {member['access_token']}"},
        ).status_code == 200

        meeting = client.post(
            f"/api/projects/{project_id}/meetings",
            headers=admin_headers,
            json={"title": "Reuniao Contratos", "objective": "Validar status"},
        )
        assert meeting.status_code == 200
        meeting_id = meeting.json()["id"]

        participants = client.get(f"/api/meetings/{meeting_id}/participants", headers=admin_headers)
        assert participants.status_code == 200
        assert participants.json()[0]["role"] == "owner"

        added = client.post(
            f"/api/meetings/{meeting_id}/participants",
            headers=admin_headers,
            json={"user_id": member["user"]["id"], "role": "participant", "consent_required": True},
        )
        assert added.status_code == 200

        assert client.post(
            f"/api/meetings/{meeting_id}/consent",
            headers=admin_headers,
            json={"text_version": "v1", "accepted_scope": {"audio": True}},
        ).status_code == 200

        start_blocked = client.post(f"/api/meetings/{meeting_id}/start", headers=admin_headers)
        assert start_blocked.status_code == 400

        member_target_headers = {
            "Authorization": f"Bearer {member['access_token']}",
            "X-Tenant-Id": admin["tenant"]["id"],
        }
        assert client.post(
            f"/api/meetings/{meeting_id}/consent",
            headers=member_target_headers,
            json={"text_version": "v1", "accepted_scope": {"audio": True}},
        ).status_code == 200

        revoked = client.post(
            f"/api/meetings/{meeting_id}/consent/revoke",
            headers=member_target_headers,
            json={"reason": "Sem disponibilidade"},
        )
        assert revoked.status_code == 200
        assert revoked.json()["revoked_at"] is not None

        start_blocked_after_revoke = client.post(f"/api/meetings/{meeting_id}/start", headers=admin_headers)
        assert start_blocked_after_revoke.status_code == 400

        assert client.post(
            f"/api/meetings/{meeting_id}/consent",
            headers=member_target_headers,
            json={"text_version": "v1", "accepted_scope": {"audio": True}},
        ).status_code == 200

        started = client.post(f"/api/meetings/{meeting_id}/start", headers=admin_headers)
        assert started.status_code == 200
        assert started.json()["status"] == "active"

        with client.websocket_connect(f"/ws/meetings/{meeting_id}?token={admin['access_token']}") as ws:
            assert ws.receive_json()["event_type"] == "client.connected"
            ws.send_json({"event_id": "ping-1", "event_type": "system.ping", "payload": {}})
            pong = ws.receive_json()
            assert pong["event_id"] == "ping-1"
            assert pong["event_type"] == "system.pong"
            assert "server_time" in pong["payload"]
            ws.send_json({"event_id": "resume-1", "event_type": "client.resume_connection", "payload": {}})
            resumed = ws.receive_json()
            assert resumed["event_type"] == "client.connection_ready"
            assert resumed["payload"]["resumed"] is True
            ws.send_json(
                {
                    "event_id": "partial-1",
                    "event_type": "audio.chunk",
                    "payload": {
                        "text": "fala parcial de teste",
                        "is_final": False,
                        "start_time": 1.0,
                        "end_time": 1.8,
                        "speaker_label": "speaker_1",
                    },
                }
            )
            partial = ws.receive_json()
            assert partial["event_type"] == "transcript.partial"
            assert partial["payload"]["is_final"] is False
            assert partial["payload"]["speaker_label"] == "speaker_1"
            assert partial["payload"]["start_time"] == 1.0
            assert ws.receive_json()["event_type"] == "system.ack"

        assert client.post(f"/api/meetings/{meeting_id}/pause", headers=admin_headers).status_code == 200
        assert client.post(f"/api/meetings/{meeting_id}/resume", headers=admin_headers).status_code == 200
        assert client.post(f"/api/meetings/{meeting_id}/finish", headers=admin_headers).status_code == 200

        lifecycle = client.get(f"/api/meetings/{meeting_id}/lifecycle-events", headers=admin_headers)
        assert lifecycle.status_code == 200
        event_types = {event["event_type"] for event in lifecycle.json()}
        assert {
            "meeting.created",
            "participant.added",
            "consent.accepted",
            "consent.revoked",
            "meeting.started",
            "meeting.paused",
            "meeting.resumed",
            "meeting.finished",
        }.issubset(event_types)


def test_document_generation_writes_extended_agent_runs() -> None:
    with TestClient(app) as client:
        admin, headers = _register(client, "Agent Admin", "Tenant Agents")
        project = client.post(
            "/api/projects",
            headers=headers,
            json={"name": "Projeto Agentes", "description": ""},
        )
        assert project.status_code == 200
        meeting = client.post(
            f"/api/projects/{project.json()['id']}/meetings",
            headers=headers,
            json={"title": "Reuniao Agentes", "objective": "Gerar documento"},
        )
        assert meeting.status_code == 200
        meeting_id = meeting.json()["id"]
        assert client.post(
            f"/api/meetings/{meeting_id}/consent",
            headers=headers,
            json={"text_version": "v1", "accepted_scope": {"audio": True}},
        ).status_code == 200
        assert client.post(f"/api/meetings/{meeting_id}/start", headers=headers).status_code == 200

        with client.websocket_connect(f"/ws/meetings/{meeting_id}?token={admin['access_token']}") as ws:
            ws.receive_json()
            ws.send_json(
                {
                    "event_id": "rule-1",
                    "event_type": "audio.chunk",
                    "payload": {
                        "text": "Quando o cliente tiver saldo acima de R$ 5000, deve receber atendimento prioritario."
                    },
                }
            )
            while True:
                event = ws.receive_json()
                if event["event_type"] == "system.ack":
                    break

        state = client.get(f"/api/meetings/{meeting_id}/state", headers=headers)
        rule = next(item for item in state.json()["rules"] if item["status"] == "needs_review")
        assert client.post(f"/api/rules/{rule['id']}/approve", headers=headers).status_code == 200
        document = client.post(f"/api/meetings/{meeting_id}/documents/generate", headers=headers)
        assert document.status_code == 200

        runs = client.get(f"/api/meetings/{meeting_id}/agent-runs", headers=headers)
        assert runs.status_code == 200
        run_data = runs.json()
        names = {run["agent_name"] for run in run_data}
        assert {"Requirements", "Tech Writer", "Traceability", "Compliance"}.issubset(names)
        for run in run_data:
            assert run["metadata"]["latency_ms"] is not None
            assert "output_schema" in run["metadata"]
