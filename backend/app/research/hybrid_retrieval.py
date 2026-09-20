from __future__ import annotations

import re
from dataclasses import dataclass

from app.research.semantic_retrieval import RetrievalFilters, SemanticResearchRetriever
from app.research.vector_store import VectorSearchResult


@dataclass(frozen=True)
class RankedEvidence:
    chunk_id: str
    document_id: str
    title: str
    source: str
    published_date: str | None
    section: str
    content: str
    semantic_score: float
    lexical_score: float
    final_score: float


class HybridResearchRetriever:
    def __init__(
        self,
        semantic_retriever: SemanticResearchRetriever,
        semantic_weight: float = 0.7,
        lexical_weight: float = 0.3,
    ) -> None:
        if semantic_weight < 0 or lexical_weight < 0:
            raise ValueError("Retrieval weights cannot be negative.")

        total = semantic_weight + lexical_weight
        if total <= 0:
            raise ValueError("At least one retrieval weight must be positive.")

        self.semantic_retriever = semantic_retriever
        self.semantic_weight = semantic_weight / total
        self.lexical_weight = lexical_weight / total

    def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
        candidate_limit: int | None = None,
        filters: RetrievalFilters | None = None,
    ) -> list[RankedEvidence]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if limit < 1:
            raise ValueError("limit must be positive.")

        candidates = self.semantic_retriever.retrieve(
            query,
            limit=candidate_limit or max(limit * 4, 10),
            filters=filters,
        )

        query_terms = self._terms(query)
        ranked: list[RankedEvidence] = []

        for candidate in candidates:
            lexical_score = self._lexical_score(query_terms, candidate)
            semantic_score = self._semantic_score(candidate)

            final_score = (
                self.semantic_weight * semantic_score
                + self.lexical_weight * lexical_score
            )

            ranked.append(
                RankedEvidence(
                    chunk_id=candidate.chunk_id,
                    document_id=candidate.document_id,
                    title=candidate.title,
                    source=candidate.source,
                    published_date=candidate.published_date,
                    section=candidate.section,
                    content=candidate.content,
                    semantic_score=semantic_score,
                    lexical_score=lexical_score,
                    final_score=final_score,
                )
            )

        ranked.sort(
            key=lambda item: (-item.final_score, item.chunk_id)
        )

        return ranked[:limit]

    @staticmethod
    def _terms(text: str) -> set[str]:
        return {
            term
            for term in re.findall(r"[a-z0-9]+", text.lower())
            if len(term) > 1
        }

    @classmethod
    def _lexical_score(
        cls,
        query_terms: set[str],
        candidate: VectorSearchResult,
    ) -> float:
        if not query_terms:
            return 0.0

        content_terms = cls._terms(candidate.content)
        title_terms = cls._terms(candidate.title)
        section_terms = cls._terms(candidate.section)

        if not content_terms:
            return 0.0

        content_overlap = len(query_terms & content_terms) / len(query_terms)
        title_overlap = len(query_terms & title_terms) / len(query_terms)
        section_overlap = len(query_terms & section_terms) / len(query_terms)

        return min(
            1.0,
            content_overlap + (0.25 * title_overlap) + (0.15 * section_overlap),
        )

    @staticmethod
    def _semantic_score(candidate: VectorSearchResult) -> float:
        distance = float(candidate.distance)
        return max(0.0, min(1.0, 1.0 - distance))
