from __future__ import annotations

from dataclasses import dataclass

from app.research.client import LLMClient
from app.research.prompts import SYSTEM_PROMPT, build_research_prompt


@dataclass(frozen=True)
class ResearchAnswer:
    answer: str
    model: str
    sources: list[str]


class ResearchService:
    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    def answer(
        self,
        question: str,
        portfolio_context: str,
        quantitative_context: str,
        evidence: list[dict[str, str]],
    ) -> ResearchAnswer:
        if not evidence:
            raise ValueError("At least one evidence item is required.")

        evidence_text = self._format_evidence(evidence)
        research_prompt = build_research_prompt(
            question,
            portfolio_context,
            quantitative_context,
            evidence_text,
        )
        prompt = f"{SYSTEM_PROMPT}\n\n{research_prompt}"

        response = self.client.generate(prompt)

        sources = [
            item["source"]
            for item in evidence
            if item.get("source", "").strip()
        ]

        return ResearchAnswer(
            answer=response.content,
            model=response.model,
            sources=sources,
        )

    @staticmethod
    def _format_evidence(evidence: list[dict[str, str]]) -> str:
        formatted: list[str] = []

        for index, item in enumerate(evidence, start=1):
            source = item.get("source", "").strip()
            content = item.get("content", "").strip()

            if not source:
                raise ValueError(f"Evidence item {index} is missing a source.")

            if not content:
                raise ValueError(f"Evidence item {index} is missing content.")

            formatted.append(f"[Source {index}] {source}\n{content}")

        return "\n\n".join(formatted)
