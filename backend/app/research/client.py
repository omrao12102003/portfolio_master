from __future__ import annotations

from dataclasses import dataclass

from app.research.config import ResearchConfig


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str


class LLMClient:
    def __init__(self, config: ResearchConfig | None = None) -> None:
        self.config = config or ResearchConfig.from_environment()

    def generate(self, prompt: str) -> LLMResponse:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if not self.config.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("The OpenAI package is not installed.") from exc

        client = OpenAI(api_key=self.config.api_key)
        response = client.responses.create(
            model=self.config.model,
            input=prompt,
            temperature=self.config.temperature,
        )

        content = response.output_text.strip()

        if not content:
            raise RuntimeError("The LLM returned an empty response.")

        return LLMResponse(content=content, model=self.config.model)
