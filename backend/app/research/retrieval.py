from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchDocument:
    document_id: str
    title: str
    source: str
    content: str
    published_date: str | None = None


@dataclass(frozen=True)
class ResearchChunk:
    document_id: str
    title: str
    source: str
    content: str
    published_date: str | None = None
    chunk_index: int = 0


class ResearchRetriever:
    def __init__(self, documents: list[ResearchDocument]) -> None:
        self.documents = list(documents)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[ResearchChunk]:
        if not query.strip():
            raise ValueError("Research query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be positive.")

        query_terms = self._terms(query)
        scored: list[tuple[int, ResearchChunk]] = []

        for document in self.documents:
            for chunk in self._chunk_document(document):
                score = self._score(query_terms, chunk.content)
                if score > 0:
                    scored.append((score, chunk))

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].document_id,
                item[1].chunk_index,
            )
        )

        return [chunk for _, chunk in scored[:top_k]]

    @staticmethod
    def _terms(text: str) -> set[str]:
        return {
            term
            for term in re.findall(r"[a-zA-Z0-9]+", text.lower())
            if len(term) > 2
        }

    @staticmethod
    def _score(query_terms: set[str], content: str) -> int:
        content_terms = ResearchRetriever._terms(content)
        return len(query_terms & content_terms)

    @staticmethod
    def _chunk_document(
        document: ResearchDocument,
        chunk_size: int = 800,
    ) -> list[ResearchChunk]:
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive.")

        words = document.content.split()
        chunks: list[ResearchChunk] = []

        for index in range(0, len(words), chunk_size):
            content = " ".join(words[index:index + chunk_size])
            chunks.append(
                ResearchChunk(
                    document_id=document.document_id,
                    title=document.title,
                    source=document.source,
                    content=content,
                    published_date=document.published_date,
                    chunk_index=index // chunk_size,
                )
            )

        return chunks
