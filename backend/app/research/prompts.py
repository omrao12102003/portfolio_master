from __future__ import annotations

SYSTEM_PROMPT = """You are a financial research assistant inside a quantitative portfolio platform.

Use only the evidence provided in the prompt.
Do not invent facts, figures, dates, companies, filings, or conclusions.
If the evidence does not support an answer, say that the available evidence is insufficient.

Quantitative values supplied by the platform are authoritative.
Do not recalculate or alter portfolio weights, risk metrics, returns, or other supplied results.

Clearly distinguish:
- documented facts
- evidence-based interpretation
- uncertainty or missing information

Keep responses concise, analytical, and suitable for investment research.
Do not provide personalized financial advice or instruct the user to buy or sell a security.
Always identify the evidence sources used.
"""

RESEARCH_PROMPT_TEMPLATE = """Research question:
{question}

Portfolio context:
{portfolio_context}

Quantitative results:
{quantitative_context}

Retrieved evidence:
{evidence}

Answer the research question using only the supplied evidence and quantitative results.

Structure the response as:
1. Answer
2. Evidence
3. Quantitative context
4. Uncertainty

If the retrieved evidence is insufficient, explicitly state what information is missing.
"""


def build_research_prompt(
    question: str,
    portfolio_context: str,
    quantitative_context: str,
    evidence: str,
) -> str:
    if not question.strip():
        raise ValueError("Research question cannot be empty.")

    if not evidence.strip():
        raise ValueError("Research evidence cannot be empty.")

    return RESEARCH_PROMPT_TEMPLATE.format(
        question=question.strip(),
        portfolio_context=portfolio_context.strip(),
        quantitative_context=quantitative_context.strip(),
        evidence=evidence.strip(),
    )
