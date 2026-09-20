from __future__ import annotations

import argparse
from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.corpus_indexer import FinancialCorpusIndexer
from app.research.database import get_database_url
from app.research.embeddings import HashEmbeddingProvider
from app.research.vector_store import ResearchVectorStore


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index the configured financial research corpus."
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/research/metadata/corpus.json"),
    )
    parser.add_argument("--dimension", type=int, default=256)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=75)
    args = parser.parse_args()

    store = ResearchVectorStore(get_database_url(), args.dimension)
    store.initialize()

    indexer = FinancialCorpusIndexer(
        store=store,
        provider=HashEmbeddingProvider(dimension=args.dimension),
        chunker=FinancialDocumentChunker(
            chunk_size=args.chunk_size,
            overlap=args.overlap,
        ),
    )

    count = indexer.index(args.metadata)
    print(f"Indexed {count} research chunks.")


if __name__ == "__main__":
    main()
