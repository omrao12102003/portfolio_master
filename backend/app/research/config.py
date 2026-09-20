from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchConfig:
    provider: str
    model: str
    api_key: str | None
    temperature: float

    @classmethod
    def from_environment(cls) -> ResearchConfig:
        return cls(
            provider=os.getenv("RESEARCH_LLM_PROVIDER", "openai"),
            model=os.getenv("RESEARCH_LLM_MODEL", "gpt-5-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("RESEARCH_LLM_TEMPERATURE", "0.1")),
        )
