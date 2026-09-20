from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_contract():
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload


def test_readiness_contract():
    response = client.get("/api/readiness")

    assert response.status_code == 200
    payload = response.json()

    assert set(
        [
            "status",
            "environment",
            "database_configured",
            "cors_configured",
        ]
    ).issubset(payload)


def test_grounded_report_validation_contract():
    response = client.post(
        "/research/reports/grounded",
        json={
            "title": "Validation Report",
            "question": "Assess risk",
            "summary": "A deterministic report.",
            "metrics": [
                {
                    "name": "Sharpe",
                    "value": 1.2,
                }
            ],
        },
    )

    assert response.status_code == 200


def test_workflow_rejects_empty_title():
    response = client.post(
        "/research/workflow/report",
        json={
            "title": "",
            "question": "Assess risk",
            "summary": "Summary",
            "metrics": [
                {
                    "name": "Sharpe",
                    "value": 1.2,
                }
            ],
        },
    )

    assert response.status_code == 422


def test_workflow_rejects_excessive_top_k():
    response = client.post(
        "/research/workflow/report",
        json={
            "title": "Report",
            "question": "Assess risk",
            "summary": "Summary",
            "metrics": [
                {
                    "name": "Sharpe",
                    "value": 1.2,
                }
            ],
            "top_k": 21,
        },
    )

    assert response.status_code == 422
