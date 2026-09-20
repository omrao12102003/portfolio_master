from __future__ import annotations

from dataclasses import dataclass

from app.research.embeddings import EmbeddingProvider
from app.research.vector_store import ResearchVectorStore, VectorSearchResult


@dataclass(frozen=True)
class RetrievalFilters:
    company: str | None = None
    ticker: str | None = None
    document_type: str | None = None
    published_before: str | None = None
    section: str | None = None


class SemanticResearchRetriever:
    def __init__(
        self,
        store: ResearchVectorStore,
        provider: EmbeddingProvider,
    ) -> None:
        self.store = store
        self.provider = provider

    def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
        filters: RetrievalFilters | None = None,
    ) -> list[VectorSearchResult]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if limit < 1:
            raise ValueError("limit must be positive.")

        query_embedding = self.provider.embed(query)

        active_filters = filters or RetrievalFilters()

        return self.store.search(
            query_embedding,
            limit=limit,
            published_before=active_filters.published_before,
            company=active_filters.company,
            ticker=active_filters.ticker,
            document_type=active_filters.document_type,
            section=active_filters.section,
        )
