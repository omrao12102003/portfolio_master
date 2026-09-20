from app.research.config import ResearchConfig


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("RESEARCH_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("RESEARCH_LLM_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RESEARCH_LLM_TEMPERATURE", raising=False)

    config = ResearchConfig.from_environment()

    assert config.provider == "openai"
    assert config.model == "gpt-5-mini"
    assert config.api_key is None
    assert config.temperature == 0.1


def test_config_reads_environment(monkeypatch):
    monkeypatch.setenv("RESEARCH_LLM_PROVIDER", "openai")
    monkeypatch.setenv("RESEARCH_LLM_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("RESEARCH_LLM_TEMPERATURE", "0.2")

    config = ResearchConfig.from_environment()

    assert config.provider == "openai"
    assert config.model == "test-model"
    assert config.api_key == "test-key"
    assert config.temperature == 0.2
