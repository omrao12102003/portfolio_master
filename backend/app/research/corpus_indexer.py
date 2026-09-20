from __future__ import annotations

from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.corpus_evaluation import build_real_corpus
from app.research.embeddings import EmbeddingProvider
from app.research.vector_store import ResearchVectorStore


class FinancialCorpusIndexer:
    def __init__(
        self,
        store: ResearchVectorStore,
        provider: EmbeddingProvider,
        chunker: FinancialDocumentChunker | None = None,
    ) -> None:
        self.store = store
        self.provider = provider
        self.chunker = chunker or FinancialDocumentChunker()

    def index(self, metadata_path: Path) -> int:
        chunks, metadata = build_real_corpus(
            metadata_path,
            self.chunker,
        )

        if not chunks:
            raise ValueError("Financial corpus contains no chunks.")

        document_ids = sorted({chunk.document_id for chunk in chunks})

        for document_id in document_ids:
            self.store.delete_document(document_id)

        embeddings = self.provider.embed_many(
            [chunk.content for chunk in chunks]
        )

        self.store.upsert(
            chunks,
            embeddings,
            metadata,
        )

        return len(chunks)
