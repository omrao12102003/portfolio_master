from fastapi.testclient import TestClient

from app.main import app
from app.research.client import LLMResponse
from app.research.service import ResearchService

client = TestClient(app)


class FakeLLMClient:
    def generate(self, prompt: str) -> LLMResponse:
        assert "Revenue increased" in prompt
        assert "Return: 8%" in prompt
        return LLMResponse(
            content="The supplied evidence indicates stronger revenue performance.",
            model="test-model",
        )


def test_research_answer_endpoint(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.research.ResearchService",
        lambda: ResearchService(FakeLLMClient()),
    )

    response = client.post(
        "/research/answer",
        json={
            "question": "What explains the portfolio company performance?",
            "portfolio_context": "Portfolio contains SPY.",
            "quantitative_context": "Return: 8%.",
            "evidence": [
                {
                    "document_id": "doc-1",
                    "title": "Annual Report",
                    "source": "company.com/report",
                    "content": "Revenue increased during the reporting period.",
                    "published_date": "2025-12-31",
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"].startswith("The supplied evidence")
    assert data["model"] == "test-model"
    assert data["sources"] == ["company.com/report"]


def test_research_answer_requires_evidence():
    response = client.post(
        "/research/answer",
        json={
            "question": "What happened?",
            "portfolio_context": "Portfolio",
            "quantitative_context": "Metrics",
            "evidence": [],
        },
    )

    assert response.status_code == 422


def test_research_answer_returns_service_error_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/research/answer",
        json={
            "question": "What happened?",
            "portfolio_context": "Portfolio",
            "quantitative_context": "Metrics",
            "evidence": [
                {
                    "document_id": "doc-1",
                    "title": "Annual Report",
                    "source": "company.com/report",
                    "content": "Revenue increased.",
                }
            ],
        },
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
