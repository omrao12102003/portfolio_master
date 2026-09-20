from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_readiness_endpoint():
    response = client.get("/api/readiness")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ready"
    assert payload["database_configured"] is True
    assert payload["cors_configured"] is True
