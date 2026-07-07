from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.modules.audit.models import AuditLog


def _register(client: TestClient, name: str) -> tuple[dict, dict[str, str]]:
    response = client.post(
        "/api/auth/register",
        json={
            "name": name,
            "email": f"{name.lower().replace(' ', '-')}-{uuid4().hex[:8]}@rulees.dev",
            "password": "rulees123",
            "organization_name": f"Tenant {name}",
        },
    )
    assert response.status_code == 200
    data = response.json()
    return data, {
        "Authorization": f"Bearer {data['access_token']}",
        "X-Tenant-Id": data["tenant"]["id"],
    }


def _document(client: TestClient, auth: dict, headers: dict[str, str]) -> tuple[str, str]:
    project = client.post("/api/projects", headers=headers, json={"name": "Projeto P2", "description": "Busca privada"})
    assert project.status_code == 200
    project_id = project.json()["id"]
    meeting = client.post(
        f"/api/projects/{project_id}/meetings",
        headers=headers,
        json={"title": "Reuniao P2", "objective": "Documento e busca"},
    )
    assert meeting.status_code == 200
    meeting_id = meeting.json()["id"]
    assert client.post(
        f"/api/meetings/{meeting_id}/consent",
        headers=headers,
        json={"text_version": "v1", "accepted_scope": {"audio": True}},
    ).status_code == 200
    assert client.post(f"/api/meetings/{meeting_id}/start", headers=headers).status_code == 200
    with client.websocket_connect(f"/ws/meetings/{meeting_id}?token={auth['access_token']}") as ws:
        ws.receive_json()
        ws.send_json(
            {
                "event_id": "p2-1",
                "event_type": "audio.chunk",
                "payload": {"text": "Quando o cliente disser palavra secreta alfa, deve gerar alerta interno."},
            }
        )
        while True:
            event = ws.receive_json()
            if event["event_type"] == "system.ack":
                break
    document = client.post(f"/api/meetings/{meeting_id}/documents/generate", headers=headers)
    assert document.status_code == 200
    return project_id, document.json()["id"]


def test_p2_exports_comments_notifications_search_analytics_and_signed_storage() -> None:
    with TestClient(app) as client:
        auth, headers = _register(client, "P2 Admin")
        member, _member_headers = _register(client, "P2 Member")
        invite = client.post(
            "/api/auth/tenant/invites",
            headers=headers,
            json={"email": member["user"]["email"], "role": "member"},
        )
        assert invite.status_code == 200
        assert client.post(
            f"/api/auth/tenant/invites/{invite.json()['id']}/accept",
            headers={"Authorization": f"Bearer {member['access_token']}"},
        ).status_code == 200
        member_target_headers = {
            "Authorization": f"Bearer {member['access_token']}",
            "X-Tenant-Id": auth["tenant"]["id"],
        }

        project_id, document_id = _document(client, auth, headers)

        excel = client.get(f"/api/documents/{document_id}/export/excel", headers=headers)
        assert excel.status_code == 200
        assert excel.content[:2] == b"PK"

        signed = client.get(f"/api/documents/{document_id}/export/excel/signed-url", headers=headers)
        assert signed.status_code == 200
        signed_download = client.get(signed.json()["url"])
        assert signed_download.status_code == 200
        assert signed_download.content[:2] == b"PK"

        revision = client.post(
            f"/api/documents/{document_id}/versions",
            headers=headers,
            json={"content": "# Revisao\nConteudo alterado palavra secreta alfa.", "change_reason": "Teste diff"},
        )
        assert revision.status_code == 200
        diff = client.get(f"/api/documents/{document_id}/versions/diff?from_version=1&to_version=2", headers=headers)
        assert diff.status_code == 200
        assert any(line["kind"] == "added" for line in diff.json()["lines"])

        comment = client.post(
            "/api/comments",
            headers=headers,
            json={
                "project_id": project_id,
                "resource_type": "document",
                "resource_id": document_id,
                "body": "Comentario P2",
            },
        )
        assert comment.status_code == 200
        comments = client.get(f"/api/comments?resource_type=document&resource_id={document_id}", headers=headers)
        assert comments.status_code == 200
        assert comments.json()[0]["body"] == "Comentario P2"

        notifications = client.get("/api/notifications", headers=member_target_headers)
        assert notifications.status_code == 200
        assert notifications.json()[0]["title"] == "Novo comentario"

        search = client.get("/api/search/global?query=secreta", headers=headers)
        assert search.status_code == 200
        assert any(item["source_type"] in {"document", "transcript_chunk", "business_rule"} for item in search.json())

        analytics = client.get("/api/analytics/summary", headers=headers)
        assert analytics.status_code == 200
        assert analytics.json()["comments_total"] >= 1

        other_auth, other_headers = _register(client, "P2 Other")
        leaked_doc = client.get(f"/api/documents/{document_id}/export/excel/signed-url", headers=other_headers)
        assert leaked_doc.status_code == 404
        leaked_search = client.get("/api/search/global?query=secreta", headers=other_headers)
        assert leaked_search.status_code == 200
        assert leaked_search.json() == []
        _ = other_auth


def test_audit_retention_and_observability_status() -> None:
    with TestClient(app) as client:
        auth, headers = _register(client, "Ops Admin")
        with SessionLocal() as db:
            db.add(
                AuditLog(
                    tenant_id=auth["tenant"]["id"],
                    user_id=auth["user"]["id"],
                    action="old.event",
                    resource_type="test",
                    details="{}",
                    created_at=datetime.now(timezone.utc) - timedelta(days=400),
                )
            )
            db.commit()
        retention = client.post("/api/audit/retention/run?retention_days=365", headers=headers)
        assert retention.status_code == 200
        assert retention.json()["deleted_logs"] >= 1

        status = client.get("/observability/status")
        assert status.status_code == 200
        data = status.json()
        assert data["opentelemetry"]["enabled"] is True
        assert "sentry" in data
