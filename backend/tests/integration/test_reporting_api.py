from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_research_report_api():
    response = client.post(
        "/research/reports/research",
        json={
            "title": "AAPL Research",
            "summary": "Financial performance review.",
            "findings": ["Revenue growth was positive."],
            "metrics": [{"name": "Sharpe", "value": 1.2}],
            "evidence": [
                {
                    "title": "Apple 10-K",
                    "source": "SEC",
                    "content": "Annual filing evidence.",
                    "relevance": 0.9,
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["report_type"] == "research"
    assert payload["metrics"][0]["value"] == 1.2
    assert "markdown" in payload


def test_portfolio_report_api():
    response = client.post(
        "/research/reports/portfolio",
        json={
            "title": "Portfolio Report",
            "summary": "Portfolio analytics.",
            "metrics": [{"name": "Volatility", "value": 0.12}],
        },
    )

    assert response.status_code == 200
    assert response.json()["report_type"] == "portfolio"


def test_risk_report_api():
    response = client.post(
        "/research/reports/risk",
        json={
            "title": "Risk Report",
            "summary": "Portfolio risk review.",
            "metrics": [{"name": "VaR", "value": 0.011}],
        },
    )

    assert response.status_code == 200
    assert response.json()["report_type"] == "risk"
