import pytest

from app.research.client import LLMResponse
from app.research.service import ResearchService


class FakeLLMClient:
    def __init__(self):
        self.prompt = None

    def generate(self, prompt: str) -> LLMResponse:
        self.prompt = prompt
        return LLMResponse(
            content="The evidence indicates the reported change.",
            model="test-model",
        )


def test_research_service_builds_answer_with_sources():
    client = FakeLLMClient()
    service = ResearchService(client)

    result = service.answer(
        question="What explains the change?",
        portfolio_context="Portfolio contains SPY.",
        quantitative_context="Return: 8%.",
        evidence=[
            {
                "source": "Annual Report 2025",
                "content": "Revenue increased during the reporting period.",
            },
            {
                "source": "Investor Presentation",
                "content": "Management reported stronger demand.",
            },
        ],
    )

    assert result.answer == "The evidence indicates the reported change."
    assert result.model == "test-model"
    assert result.sources == [
        "Annual Report 2025",
        "Investor Presentation",
    ]
    assert "Annual Report 2025" in client.prompt
    assert "Revenue increased" in client.prompt
    assert "Return: 8%" in client.prompt


def test_empty_evidence_is_rejected():
    service = ResearchService(FakeLLMClient())

    with pytest.raises(ValueError, match="At least one evidence"):
        service.answer(
            question="What happened?",
            portfolio_context="Portfolio",
            quantitative_context="Metrics",
            evidence=[],
        )


def test_missing_source_is_rejected():
    service = ResearchService(FakeLLMClient())

    with pytest.raises(ValueError, match="missing a source"):
        service.answer(
            question="What happened?",
            portfolio_context="Portfolio",
            quantitative_context="Metrics",
            evidence=[
                {
                    "source": "",
                    "content": "Evidence",
                }
            ],
        )


def test_missing_content_is_rejected():
    service = ResearchService(FakeLLMClient())

    with pytest.raises(ValueError, match="missing content"):
        service.answer(
            question="What happened?",
            portfolio_context="Portfolio",
            quantitative_context="Metrics",
            evidence=[
                {
                    "source": "Annual Report",
                    "content": "",
                }
            ],
        )
