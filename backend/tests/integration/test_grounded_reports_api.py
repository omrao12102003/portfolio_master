from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_grounded_report_api():
    response = client.post(
        "/research/reports/grounded",
        json={
            "title": "AAPL Portfolio Research",
            "question": "How should the portfolio risk be interpreted?",
            "summary": "Portfolio risk was evaluated using deterministic quantitative analytics.",
            "findings": [
                "The quantitative metrics were calculated independently of the language model."
            ],
            "metrics": [
                {"name": "Sharpe Ratio", "value": 1.15},
                {"name": "VaR 95%", "value": 0.011},
            ],
            "methodology": [
                "Historical VaR using portfolio return observations."
            ],
            "limitations": [
                "Historical results are not forecasts."
            ],
            "evidence": [
                {
                    "title": "Apple 2025 10-K",
                    "source": "SEC",
                    "content": "Primary-source filing evidence.",
                    "relevance": 0.98,
                }
            ],
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["report_type"] == "research"
    assert payload["grounding"]["evidence_count"] == 1
    assert payload["grounding"]["quantitative_metric_count"] == 2
    assert payload["grounding"]["has_primary_source_evidence"] is True
    assert payload["grounding"]["sources"] == ["SEC"]
    assert "Quantitative metrics" in payload["markdown"]


def test_grounded_report_rejects_missing_metrics():
    response = client.post(
        "/research/reports/grounded",
        json={
            "title": "Invalid Report",
            "question": "Assess risk",
            "summary": "No quantitative context.",
            "metrics": [],
        },
    )

    assert response.status_code == 400
