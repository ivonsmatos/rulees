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


def test_project_edit_archive_glossary_templates_and_tenant_isolation() -> None:
    with TestClient(app) as client:
        admin, admin_headers = _register(client, "Project Admin", "Tenant Projects")
        _other, other_headers = _register(client, "Project Other", "Tenant Other Projects")

        project = client.post(
            "/api/projects",
            headers=admin_headers,
            json={"name": "Projeto Original", "description": "Descricao inicial"},
        )
        assert project.status_code == 200
        project_id = project.json()["id"]

        updated = client.patch(
            f"/api/projects/{project_id}",
            headers=admin_headers,
            json={"name": "Projeto Editado", "description": "Descricao editada"},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Projeto Editado"

        term = client.post(
            f"/api/projects/{project_id}/glossary",
            headers=admin_headers,
            json={
                "term": "Lead qualificado",
                "definition": "Contato com perfil e interesse validado",
                "aliases": ["MQL", "lead pronto"],
            },
        )
        assert term.status_code == 200
        term_data = term.json()
        assert term_data["aliases"] == ["MQL", "lead pronto"]

        term_update = client.patch(
            f"/api/projects/{project_id}/glossary/{term_data['id']}",
            headers=admin_headers,
            json={
                "term": "Lead qualificado",
                "definition": "Contato validado por marketing e vendas",
                "aliases": ["MQL"],
            },
        )
        assert term_update.status_code == 200
        assert term_update.json()["definition"] == "Contato validado por marketing e vendas"

        glossary = client.get(f"/api/projects/{project_id}/glossary", headers=admin_headers)
        assert glossary.status_code == 200
        assert glossary.json()[0]["term"] == "Lead qualificado"

        template = client.post(
            "/api/projects/templates",
            headers=admin_headers,
            json={
                "name": "Template Discovery",
                "description": "Projeto para descoberta de regras",
                "default_objective": "Mapear regras de negocio",
                "default_glossary_terms": [
                    {
                        "term": "SLA",
                        "definition": "Acordo de nivel de servico",
                        "aliases": ["prazo"],
                    }
                ],
            },
        )
        assert template.status_code == 200
        template_data = template.json()
        assert template_data["default_glossary_terms"][0]["term"] == "SLA"

        templates = client.get("/api/projects/templates", headers=admin_headers)
        assert templates.status_code == 200
        assert {item["id"] for item in templates.json()} == {template_data["id"]}

        templated_project = client.post(
            f"/api/projects/templates/{template_data['id']}/projects",
            headers=admin_headers,
            json={"name": "Projeto do Template"},
        )
        assert templated_project.status_code == 200
        templated_project_id = templated_project.json()["id"]

        templated_glossary = client.get(
            f"/api/projects/{templated_project_id}/glossary",
            headers=admin_headers,
        )
        assert templated_glossary.status_code == 200
        assert templated_glossary.json()[0]["term"] == "SLA"

        cross_tenant_project = client.get(f"/api/projects/{project_id}", headers=other_headers)
        assert cross_tenant_project.status_code == 404
        cross_tenant_glossary = client.get(f"/api/projects/{project_id}/glossary", headers=other_headers)
        assert cross_tenant_glossary.status_code == 404
        cross_tenant_template = client.post(
            f"/api/projects/templates/{template_data['id']}/projects",
            headers=other_headers,
            json={"name": "Projeto bloqueado"},
        )
        assert cross_tenant_template.status_code == 404

        archived = client.post(f"/api/projects/{project_id}/archive", headers=admin_headers)
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"
        assert archived.json()["archived_at"] is not None

        blocked_update = client.patch(
            f"/api/projects/{project_id}",
            headers=admin_headers,
            json={"name": "Projeto Arquivado", "description": ""},
        )
        assert blocked_update.status_code == 400

        blocked_glossary = client.post(
            f"/api/projects/{project_id}/glossary",
            headers=admin_headers,
            json={"term": "Novo termo", "definition": "", "aliases": []},
        )
        assert blocked_glossary.status_code == 400

        audit = client.get("/api/audit/logs", headers=admin_headers)
        assert audit.status_code == 200
        audit_actions = {item["action"] for item in audit.json()}
        assert {
            "project.update",
            "project.archive",
            "project.glossary.create",
            "project.glossary.update",
            "project.template.create",
            "project.template.use",
        }.issubset(audit_actions)


def test_member_can_view_project_details_but_cannot_mutate_project() -> None:
    with TestClient(app) as client:
        admin, admin_headers = _register(client, "Project Owner", "Tenant Project Roles")
        member, _member_home_headers = _register(client, "Project Member", "Tenant Member Home")

        project = client.post(
            "/api/projects",
            headers=admin_headers,
            json={"name": "Projeto de Leitura", "description": ""},
        )
        assert project.status_code == 200
        project_id = project.json()["id"]

        invite = client.post(
            "/api/auth/tenant/invites",
            headers=admin_headers,
            json={"email": member["user"]["email"], "role": "member"},
        )
        assert invite.status_code == 200
        accepted = client.post(
            f"/api/auth/tenant/invites/{invite.json()['id']}/accept",
            headers={"Authorization": f"Bearer {member['access_token']}"},
        )
        assert accepted.status_code == 200

        member_headers = {
            "Authorization": f"Bearer {member['access_token']}",
            "X-Tenant-Id": admin["tenant"]["id"],
        }
        visible = client.get(f"/api/projects/{project_id}/glossary", headers=member_headers)
        assert visible.status_code == 200
        assert client.get("/api/projects/templates", headers=member_headers).status_code == 200
        assert client.patch(
            f"/api/projects/{project_id}",
            headers=member_headers,
            json={"name": "Nao pode", "description": ""},
        ).status_code == 403
        assert client.post(f"/api/projects/{project_id}/archive", headers=member_headers).status_code == 403
        assert client.post(
            f"/api/projects/{project_id}/glossary",
            headers=member_headers,
            json={"term": "Bloqueado", "definition": "", "aliases": []},
        ).status_code == 403
