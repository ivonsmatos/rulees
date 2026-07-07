from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.headers["x-request-id"]


def test_request_id_header_is_preserved() -> None:
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-Id": "test-request-id"})
        assert response.status_code == 200
        assert response.headers["x-request-id"] == "test-request-id"


def test_dependency_health_shape() -> None:
    with TestClient(app) as client:
        response = client.get("/health/dependencies")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] in {"ok", "degraded"}
        component_names = {component["name"] for component in payload["components"]}
        assert {"database", "redis", "storage"}.issubset(component_names)
        for component in payload["components"]:
            assert component["status"] in {"ok", "error"}
            assert "latency_ms" in component


def test_security_headers_are_set() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "no-referrer"
