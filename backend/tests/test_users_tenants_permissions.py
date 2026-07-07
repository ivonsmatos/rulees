from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def _register(client: TestClient, name: str, organization_name: str) -> tuple[dict, dict[str, str]]:
    email_prefix = name.lower().replace(" ", "-")
    email = f"{email_prefix}-{uuid4().hex[:8]}@rulees.dev"
    response = client.post(
        "/api/auth/register",
        json={
            "name": name,
            "email": email,
            "password": "rulees123",
            "organization_name": organization_name,
        },
    )
    assert response.status_code == 200
    data = response.json()
    headers = {
        "Authorization": f"Bearer {data['access_token']}",
        "X-Tenant-Id": data["tenant"]["id"],
    }
    return data, headers


def test_tenant_invites_project_members_cross_tenant_and_viewer_read_only() -> None:
    with TestClient(app) as client:
        admin, admin_headers = _register(client, "Admin User", "Tenant Admin")
        viewer, viewer_home_headers = _register(client, "Viewer User", "Tenant Viewer")
        other, other_headers = _register(client, "Other User", "Tenant Other")

        project = client.post(
            "/api/projects",
            headers=admin_headers,
            json={"name": "Projeto Permissoes", "description": "RBAC completo"},
        )
        assert project.status_code == 200
        project_id = project.json()["id"]

        creator_members = client.get(f"/api/projects/{project_id}/members", headers=admin_headers)
        assert creator_members.status_code == 200
        assert creator_members.json()[0]["user_id"] == admin["user"]["id"]

        members_before = client.get("/api/auth/tenant/members", headers=admin_headers)
        assert members_before.status_code == 200
        assert {item["user_id"] for item in members_before.json()} == {admin["user"]["id"]}

        invite = client.post(
            "/api/auth/tenant/invites",
            headers=admin_headers,
            json={"email": viewer["user"]["email"], "role": "viewer"},
        )
        assert invite.status_code == 200
        invite_data = invite.json()
        assert invite_data["status"] == "pending"
        assert invite_data["role"] == "viewer"

        pending = client.get("/api/auth/invites/pending", headers=viewer_home_headers)
        assert pending.status_code == 200
        assert pending.json()[0]["id"] == invite_data["id"]
        assert pending.json()[0]["tenant"]["id"] == admin["tenant"]["id"]

        mismatch_accept = client.post(
            f"/api/auth/tenant/invites/{invite_data['id']}/accept",
            headers=other_headers,
        )
        assert mismatch_accept.status_code == 404

        accept = client.post(
            f"/api/auth/tenant/invites/{invite_data['id']}/accept",
            headers={"Authorization": f"Bearer {viewer['access_token']}"},
        )
        assert accept.status_code == 200
        assert accept.json()["role"] == "viewer"

        viewer_tenants = client.get("/api/auth/tenants", headers=viewer_home_headers)
        assert viewer_tenants.status_code == 200
        tenant_roles = {item["tenant"]["id"]: item["role"] for item in viewer_tenants.json()}
        assert tenant_roles[admin["tenant"]["id"]] == "viewer"
        assert tenant_roles[viewer["tenant"]["id"]] == "admin"

        viewer_target_headers = {
            "Authorization": f"Bearer {viewer['access_token']}",
            "X-Tenant-Id": admin["tenant"]["id"],
        }
        viewer_me = client.get("/api/auth/me", headers=viewer_target_headers)
        assert viewer_me.status_code == 200
        assert viewer_me.json()["tenant"]["role"] == "viewer"

        members_after = client.get("/api/auth/tenant/members", headers=admin_headers)
        assert members_after.status_code == 200
        assert {item["user_id"] for item in members_after.json()} == {
            admin["user"]["id"],
            viewer["user"]["id"],
        }

        project_member = client.post(
            f"/api/projects/{project_id}/members",
            headers=admin_headers,
            json={"user_id": viewer["user"]["id"], "role": "viewer"},
        )
        assert project_member.status_code == 200
        assert project_member.json()["user_id"] == viewer["user"]["id"]
        assert project_member.json()["role"] == "viewer"

        project_members = client.get(f"/api/projects/{project_id}/members", headers=viewer_target_headers)
        assert project_members.status_code == 200
        assert {item["user_id"] for item in project_members.json()} == {
            admin["user"]["id"],
            viewer["user"]["id"],
        }

        assert client.get(f"/api/projects/{project_id}", headers=viewer_target_headers).status_code == 200
        assert client.post(
            "/api/projects",
            headers=viewer_target_headers,
            json={"name": "Bloqueado", "description": ""},
        ).status_code == 403
        assert client.post(
            f"/api/projects/{project_id}/meetings",
            headers=viewer_target_headers,
            json={"title": "Bloqueado", "objective": ""},
        ).status_code == 403
        assert client.post(
            f"/api/projects/{project_id}/members",
            headers=viewer_target_headers,
            json={"user_id": viewer["user"]["id"], "role": "member"},
        ).status_code == 403

        assert client.get(f"/api/projects/{project_id}", headers=other_headers).status_code == 404
        assert client.get(f"/api/projects/{project_id}/members", headers=other_headers).status_code == 404


def test_manager_cannot_assign_admin_role() -> None:
    with TestClient(app) as client:
        admin, admin_headers = _register(client, "Role Admin", "Tenant Roles")
        manager, manager_home_headers = _register(client, "Role Manager", "Tenant Manager")
        target, _target_headers = _register(client, "Role Target", "Tenant Target")

        invite = client.post(
            "/api/auth/tenant/invites",
            headers=admin_headers,
            json={"email": manager["user"]["email"], "role": "manager"},
        )
        assert invite.status_code == 200
        accepted = client.post(
            f"/api/auth/tenant/invites/{invite.json()['id']}/accept",
            headers={"Authorization": f"Bearer {manager['access_token']}"},
        )
        assert accepted.status_code == 200

        manager_headers = {
            "Authorization": f"Bearer {manager['access_token']}",
            "X-Tenant-Id": admin["tenant"]["id"],
        }
        admin_invite = client.post(
            "/api/auth/tenant/invites",
            headers=manager_headers,
            json={"email": target["user"]["email"], "role": "admin"},
        )
        assert admin_invite.status_code == 403

        member_invite = client.post(
            "/api/auth/tenant/invites",
            headers=manager_headers,
            json={"email": target["user"]["email"], "role": "member"},
        )
        assert member_invite.status_code == 200

        admin_members = client.get("/api/auth/tenant/members", headers=admin_headers)
        manager_member = next(item for item in admin_members.json() if item["user_id"] == manager["user"]["id"])
        promote = client.patch(
            f"/api/auth/tenant/members/{manager_member['id']}",
            headers=manager_headers,
            json={"role": "admin"},
        )
        assert promote.status_code == 403
