import json
from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.embeddings import HashEmbeddingProvider
from app.research.ingestion import ResearchDocumentLoader
from app.research.retrieval import ResearchDocument
from app.research.semantic_retrieval import RetrievalFilters, SemanticResearchRetriever
from app.research.vector_store import ResearchVectorStore, index_chunks

ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "data/research/metadata/corpus.json"
RAW_ROOT = ROOT / "data/research/raw/sec"


def load_corpus() -> list[dict]:
    return json.loads(CORPUS_PATH.read_text())["documents"]


def build_real_chunks() -> tuple[list, list[dict]]:
    chunker = FinancialDocumentChunker(chunk_size=500, overlap=75)
    chunks = []
    metadata = []

    for item in load_corpus():
        path = ROOT / item["path"]
        document = ResearchDocumentLoader().load(
            path,
            item["document_id"],
            item["title"],
            item["source"],
        )

        document = ResearchDocument(
            document_id=document.document_id,
            title=document.title,
            source=document.source,
            published_date=item["published_date"],
            content=document.content,
        )

        document_chunks = chunker.chunk(document)
        chunks.extend(document_chunks)

        metadata.extend(
            {
                "company": item["company"],
                "ticker": item["ticker"],
                "document_type": item["document_type"],
            }
            for _ in document_chunks
        )

    return chunks, metadata


def test_real_corpus_semantic_retrieval():
    provider = HashEmbeddingProvider(dimension=256)
    store = ResearchVectorStore(
        "postgresql://localhost/portfolio_master",
        provider.dimension,
    )
    store.initialize()

    chunks, metadata = build_real_chunks()

    for document in load_corpus():
        store.delete_document(document["document_id"])

    index_chunks(store, provider, chunks)

    retriever = SemanticResearchRetriever(store, provider)

    results = retriever.retrieve(
        "revenue and financial performance",
        limit=5,
    )

    assert results
    assert all(result.content for result in results)
    assert all(result.similarity >= -1.0 for result in results)

    for document in load_corpus():
        store.delete_document(document["document_id"])


def test_real_corpus_company_filter():
    provider = HashEmbeddingProvider(dimension=256)
    store = ResearchVectorStore(
        "postgresql://localhost/portfolio_master",
        provider.dimension,
    )
    store.initialize()

    chunks, metadata = build_real_chunks()

    for document in load_corpus():
        store.delete_document(document["document_id"])

    index_chunks(store, provider, chunks, metadata)

    retriever = SemanticResearchRetriever(store, provider)

    results = retriever.retrieve(
        "risk factors",
        limit=10,
        filters=RetrievalFilters(ticker="AAPL"),
    )

    assert results
    assert all(result.document_id.startswith("aapl") for result in results)

    for document in load_corpus():
        store.delete_document(document["document_id"])


def test_real_corpus_historical_cutoff():
    provider = HashEmbeddingProvider(dimension=256)
    store = ResearchVectorStore(
        "postgresql://localhost/portfolio_master",
        provider.dimension,
    )
    store.initialize()

    chunks, metadata = build_real_chunks()

    for document in load_corpus():
        store.delete_document(document["document_id"])

    index_chunks(store, provider, chunks, metadata)

    retriever = SemanticResearchRetriever(store, provider)

    results = retriever.retrieve(
        "financial performance",
        limit=20,
        filters=RetrievalFilters(
            published_before="2025-08-01",
        ),
    )

    assert results
    assert all(
        result.published_date is not None
        and result.published_date <= "2025-08-01"
        for result in results
    )

    for document in load_corpus():
        store.delete_document(document["document_id"])
