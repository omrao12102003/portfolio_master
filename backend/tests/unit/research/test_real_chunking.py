import json
from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.ingestion import ResearchDocumentLoader

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "data" / "research" / "metadata" / "corpus.json"


def test_real_sec_documents_produce_retrieval_chunks():
    metadata = json.loads(CORPUS.read_text())
    loader = ResearchDocumentLoader()
    chunker = FinancialDocumentChunker(
        chunk_size=500,
        overlap=75,
    )

    for item in metadata["documents"]:
        document = loader.load(
            ROOT / item["path"],
            item["document_id"],
            item["title"],
            item["source_url"],
            item["published_date"],
        )

        chunks = chunker.chunk(document)

        assert len(chunks) > 10
        assert all(chunk.document_id == item["document_id"] for chunk in chunks)
        assert all(chunk.source == item["source_url"] for chunk in chunks)
        assert all(chunk.published_date == item["published_date"] for chunk in chunks)
        assert all(chunk.content.strip() for chunk in chunks)

        chunk_ids = [chunk.chunk_id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))
