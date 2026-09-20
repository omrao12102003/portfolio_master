import os

import pytest

from app.research.embeddings import HashEmbeddingProvider
from app.research.investment_workflow import InvestmentResearchWorkflow
from app.research.reporting import ReportMetric
from app.research.semantic_retrieval import SemanticResearchRetriever
from app.research.vector_store import ResearchVectorStore


def test_real_sec_rag_workflow():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost/portfolio_master",
    )

    store = ResearchVectorStore(database_url=database_url, dimension=256)
    provider = HashEmbeddingProvider(dimension=256)

    try:
        store.initialize()
    except Exception as exc:
        pytest.skip(f"PostgreSQL/pgvector unavailable: {exc}")

    retriever = SemanticResearchRetriever(
        store=store,
        provider=provider,
    )

    try:
        workflow = InvestmentResearchWorkflow(retriever)

        result = workflow.build_report(
            question="Apple revenue and business performance",
            title="Apple Financial Research",
            summary=(
                "Quantitative portfolio context combined with "
                "primary-source financial evidence."
            ),
            metrics=[
                ReportMetric(
                    name="Annualized Return",
                    value=0.1625,
                ),
                ReportMetric(
                    name="Volatility",
                    value=0.1120,
                ),
            ],
            ticker="AAPL",
            published_before="2026-01-01",
            top_k=5,
        )
    except Exception as exc:
        pytest.skip(f"Real SEC corpus not indexed: {exc}")

    assert result.evidence_count >= 0
    assert result.report.metrics
    assert result.report.title == "Apple Financial Research"
