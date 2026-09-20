from fastapi.testclient import TestClient

from app.main import app


class FakeWorkflow:
    def build_report(self, **kwargs):
        from app.research.investment_workflow import InvestmentWorkflowResult
        from app.research.reporting import ReportEvidence, ReportMetric, build_research_report

        report = build_research_report(
            title=kwargs["title"],
            summary=kwargs["summary"],
            findings=["Quantitative results are deterministic."],
            metrics=[ReportMetric("Sharpe", 1.2)],
            evidence=[
                ReportEvidence(
                    "Apple 2025 10-K",
                    "SEC",
                    "Primary filing evidence.",
                    0.95,
                )
            ],
            limitations=["Historical results are not forecasts."],
        )

        return InvestmentWorkflowResult(
            report=report,
            evidence_count=1,
            sources=["SEC"],
        )


client = TestClient(app)


def test_investment_workflow_api(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.investment_workflow._build_workflow",
        lambda: FakeWorkflow(),
    )

    response = client.post(
        "/research/workflow/report",
        json={
            "title": "Apple Investment Report",
            "question": "Assess Apple risk",
            "summary": "Quantitative risk and primary-source evidence.",
            "ticker": "AAPL",
            "metrics": [
                {"name": "Sharpe", "value": 1.2},
            ],
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["workflow"]["evidence_count"] == 1
    assert payload["workflow"]["sources"] == ["SEC"]
    assert payload["metrics"][0]["name"] == "Sharpe"
    assert "Apple Investment Report" in payload["markdown"]
