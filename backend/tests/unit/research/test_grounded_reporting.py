import pytest

from app.research.grounded_reporting import (
    build_grounded_context,
    build_grounded_research_report,
    grounded_evidence_sources,
    has_primary_source_evidence,
)
from app.research.reporting import ReportEvidence, ReportMetric


def test_grounded_context_requires_question():
    with pytest.raises(ValueError, match="question"):
        build_grounded_context(
            question="",
            metrics=[ReportMetric("Sharpe", 1.1)],
        )


def test_grounded_context_requires_metrics():
    with pytest.raises(ValueError, match="quantitative metric"):
        build_grounded_context(question="Assess portfolio", metrics=[])


def test_grounded_report_preserves_quantitative_context():
    context = build_grounded_context(
        question="Assess portfolio risk",
        metrics=[
            ReportMetric("Sharpe", 1.2),
            ReportMetric("VaR", 0.011),
        ],
        methodology=["Historical VaR"],
        evidence=[
            ReportEvidence(
                "Apple 10-K",
                "SEC",
                "Primary filing evidence.",
                0.95,
            )
        ],
    )

    report = build_grounded_research_report(
        title="Portfolio Risk Research",
        summary="Risk was evaluated using deterministic metrics.",
        context=context,
        findings=["Risk metrics were calculated by the quantitative engine."],
    )

    assert len(report.metrics) == 2
    assert len(report.evidence) == 1
    assert "Methodology: Historical VaR" in report.limitations


def test_evidence_sources_are_unique():
    context = build_grounded_context(
        question="Research",
        metrics=[ReportMetric("Sharpe", 1.0)],
        evidence=[
            ReportEvidence("A", "SEC", "Evidence A"),
            ReportEvidence("B", "SEC", "Evidence B"),
            ReportEvidence("C", "Company", "Evidence C"),
        ],
    )

    assert grounded_evidence_sources(context) == ["SEC", "Company"]


def test_primary_source_detection():
    context = build_grounded_context(
        question="Research",
        metrics=[ReportMetric("Return", 0.1)],
        evidence=[
            ReportEvidence("10-K", "SEC", "Annual filing evidence."),
        ],
    )

    assert has_primary_source_evidence(context)


def test_non_primary_source_detection():
    context = build_grounded_context(
        question="Research",
        metrics=[ReportMetric("Return", 0.1)],
        evidence=[
            ReportEvidence("Commentary", "Research note", "Secondary evidence."),
        ],
    )

    assert not has_primary_source_evidence(context)
