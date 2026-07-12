from typing import Any

from fastapi.testclient import TestClient


def test_liveness(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "transitops-api"}


def test_versioned_health(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-request"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request"
    assert response.json() == {
        "name": "TransitOps",
        "environment": "test",
        "version": "0.1.0",
        "status": "ok",
    }


def test_readiness_skips_database_by_default(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "skipped",
        "redis": "skipped",
        "storage": "skipped",
    }


def test_readiness_reports_database_failure(
    client: TestClient,
    monkeypatch: Any,
) -> None:
    from app.api.v1 import health

    async def unavailable() -> bool:
        return False

    monkeypatch.setattr(health.get_settings(), "database_check_on_startup", True)
    monkeypatch.setattr(health, "check_database", unavailable)
    response = client.get("/api/v1/health/ready", headers={"X-Request-ID": "db-check"})

    assert response.status_code == 503
    payload = response.json()
    assert payload["code"] == "DATABASE_UNAVAILABLE"
    assert payload["message"] == "One or more backend dependencies are not ready."
    assert payload["details"]["database"] is False
    assert isinstance(payload["details"]["redis"], bool)
    assert isinstance(payload["details"]["storage"], bool)
    assert payload["request_id"] == "db-check"
