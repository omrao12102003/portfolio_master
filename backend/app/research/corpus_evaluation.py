from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.research.chunking import FinancialDocumentChunker, ResearchChunk
from app.research.hybrid_retrieval import HybridResearchRetriever
from app.research.ingestion import ResearchDocumentLoader
from app.research.semantic_retrieval import (
    RetrievalFilters,
    SemanticResearchRetriever,
)


@dataclass(frozen=True)
class EvaluationQuery:
    query_id: str
    query: str
    ticker: str
    relevant_terms: tuple[str, ...]
    cutoff: str


@dataclass(frozen=True)
class EvaluationResult:
    query_id: str
    method: str
    precision_at_5: float
    recall_at_5: float
    reciprocal_rank: float


def load_corpus_metadata(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text())
    return data["documents"]


def build_real_corpus(
    metadata_path: Path,
    chunker: FinancialDocumentChunker,
) -> tuple[list[ResearchChunk], list[dict[str, str | None]]]:
    metadata = load_corpus_metadata(metadata_path)
    loader = ResearchDocumentLoader()

    chunks: list[ResearchChunk] = []
    chunk_metadata: list[dict[str, str | None]] = []

    for item in metadata:
        document_path = Path(item["path"])
        if not document_path.is_absolute():
            backend_root = metadata_path.resolve().parents[3]
            document_path = backend_root / document_path

        document = loader.load(
            document_path,
            item["document_id"],
            item["title"],
            item["source"],
        )

        document = type(document)(
            document_id=document.document_id,
            title=document.title,
            source=document.source,
            published_date=item["published_date"],
            content=document.content,
        )

        document_chunks = chunker.chunk(document)
        chunks.extend(document_chunks)

        for _ in document_chunks:
            chunk_metadata.append(
                {
                    "company": item["company"],
                    "ticker": item["ticker"],
                    "document_type": item["document_type"],
                }
            )

    return chunks, chunk_metadata


def evaluate_queries(
    queries: list[EvaluationQuery],
    semantic: SemanticResearchRetriever,
    hybrid: HybridResearchRetriever,
    corpus_chunks: list[ResearchChunk],
) -> list[EvaluationResult]:
    results: list[EvaluationResult] = []

    for evaluation_query in queries:
        filters = RetrievalFilters(
            ticker=evaluation_query.ticker,
            published_before=evaluation_query.cutoff,
        )

        eligible_chunks = [
            chunk
            for chunk in corpus_chunks
            if chunk.document_id.lower().startswith(
                evaluation_query.ticker.lower()
            )
            and chunk.published_date is not None
            and chunk.published_date <= evaluation_query.cutoff
        ]

        relevant_ids = {
            chunk.chunk_id
            for chunk in eligible_chunks
            if any(
                term.lower() in chunk.content.lower()
                for term in evaluation_query.relevant_terms
            )
        }

        for method, retriever in (
            ("semantic", semantic),
            ("hybrid", hybrid),
        ):
            retrieved = retriever.retrieve(
                evaluation_query.query,
                limit=5,
                filters=filters,
            )

            retrieved_ids = [item.chunk_id for item in retrieved]
            relevant_retrieved = [
                chunk_id
                for chunk_id in retrieved_ids
                if chunk_id in relevant_ids
            ]

            precision = (
                len(relevant_retrieved) / len(retrieved_ids)
                if retrieved_ids
                else 0.0
            )

            recall = (
                len(relevant_retrieved) / len(relevant_ids)
                if relevant_ids
                else 0.0
            )

            reciprocal_rank = 0.0
            for index, chunk_id in enumerate(retrieved_ids, start=1):
                if chunk_id in relevant_ids:
                    reciprocal_rank = 1.0 / index
                    break

            results.append(
                EvaluationResult(
                    query_id=evaluation_query.query_id,
                    method=method,
                    precision_at_5=precision,
                    recall_at_5=recall,
                    reciprocal_rank=reciprocal_rank,
                )
            )

    return results
