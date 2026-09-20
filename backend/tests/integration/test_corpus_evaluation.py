from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.corpus_evaluation import (
    EvaluationQuery,
    build_real_corpus,
)
from app.research.embeddings import HashEmbeddingProvider
from app.research.hybrid_retrieval import HybridResearchRetriever
from app.research.semantic_retrieval import RetrievalFilters, SemanticResearchRetriever
from app.research.vector_store import ResearchVectorStore

ROOT = Path(__file__).resolve().parents[4]
METADATA = Path(__file__).resolve().parents[2] / "data/research/metadata/corpus.json"


def test_real_corpus_builds():
    chunks, metadata = build_real_corpus(
        METADATA,
        FinancialDocumentChunker(chunk_size=500, overlap=75),
    )

    assert len(chunks) > 400
    assert len(chunks) == len(metadata)
    assert {item["ticker"] for item in metadata} == {"AAPL", "MSFT", "NVDA"}


def test_real_corpus_evaluation_retrieval():
    store = ResearchVectorStore("postgresql://localhost/portfolio_master", 256)
    store.initialize()

    provider = HashEmbeddingProvider(dimension=256)
    chunker = FinancialDocumentChunker(chunk_size=500, overlap=75)

    chunks, metadata = build_real_corpus(METADATA, chunker)

    for ticker in ("AAPL", "MSFT", "NVDA"):
        store.delete_document(ticker)

    store.upsert(chunks, provider.embed_many([chunk.content for chunk in chunks]), metadata)

    semantic = SemanticResearchRetriever(store, provider)
    hybrid = HybridResearchRetriever(semantic)

    queries = [
        EvaluationQuery(
            query_id="aapl-revenue",
            query="Apple revenue net sales",
            ticker="AAPL",
            relevant_terms=("net sales", "revenue"),
            cutoff="2025-12-31",
        ),
        EvaluationQuery(
            query_id="msft-cloud",
            query="Microsoft cloud revenue Azure",
            ticker="MSFT",
            relevant_terms=("Azure", "cloud"),
            cutoff="2025-12-31",
        ),
        EvaluationQuery(
            query_id="nvda-data-center",
            query="NVIDIA data center revenue",
            ticker="NVDA",
            relevant_terms=("Data Center",),
            cutoff="2025-12-31",
        ),
    ]

    for item in queries:
        semantic_results = semantic.retrieve(
            item.query,
            limit=5,
            filters=RetrievalFilters(
                ticker=item.ticker,
                published_before=item.cutoff,
            ),
        )
        hybrid_results = hybrid.retrieve(
            item.query,
            limit=5,
            filters=RetrievalFilters(
                ticker=item.ticker,
                published_before=item.cutoff,
            ),
        )

        assert semantic_results
        assert hybrid_results

        assert all(
            result.published_date <= item.cutoff
            for result in semantic_results
        )

        assert all(
            result.published_date <= item.cutoff
            for result in hybrid_results
        )

        assert all(
            item.ticker in result.chunk_id
            or result.document_id.lower().startswith(item.ticker.lower())
            or result.title
            for result in semantic_results
        )

    for ticker in ("AAPL", "MSFT", "NVDA"):
        store.delete_document(ticker)
