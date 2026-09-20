import pytest

from app.research.client import LLMClient
from app.research.config import ResearchConfig


def test_empty_prompt_is_rejected():
    client = LLMClient(
        ResearchConfig(
            provider="openai",
            model="test-model",
            api_key="test-key",
            temperature=0.1,
        )
    )

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        client.generate("")


def test_missing_api_key_is_rejected(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    client = LLMClient(
        ResearchConfig(
            provider="openai",
            model="test-model",
            api_key=None,
            temperature=0.1,
        )
    )

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        client.generate("Explain this portfolio.")
