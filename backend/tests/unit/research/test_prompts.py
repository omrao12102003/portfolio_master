import pytest

from app.research.prompts import SYSTEM_PROMPT, build_research_prompt


def test_system_prompt_contains_core_guardrails():
    assert "Do not invent facts" in SYSTEM_PROMPT
    assert "Quantitative values supplied by the platform are authoritative" in SYSTEM_PROMPT
    assert "Always identify the evidence sources used" in SYSTEM_PROMPT


def test_build_research_prompt_includes_context():
    prompt = build_research_prompt(
        question="What explains the portfolio risk?",
        portfolio_context="Portfolio contains SPY and QQQ.",
        quantitative_context="Volatility: 12%.",
        evidence="Annual report states revenue increased.",
    )

    assert "What explains the portfolio risk?" in prompt
    assert "Portfolio contains SPY and QQQ." in prompt
    assert "Volatility: 12%." in prompt
    assert "Annual report states revenue increased." in prompt


@pytest.mark.parametrize("question", ["", "   "])
def test_empty_question_is_rejected(question):
    with pytest.raises(ValueError, match="Research question"):
        build_research_prompt(
            question=question,
            portfolio_context="Portfolio",
            quantitative_context="Metrics",
            evidence="Evidence",
        )


def test_empty_evidence_is_rejected():
    with pytest.raises(ValueError, match="Research evidence"):
        build_research_prompt(
            question="What happened?",
            portfolio_context="Portfolio",
            quantitative_context="Metrics",
            evidence="",
        )
