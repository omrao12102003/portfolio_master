import pytest

from app.research.reporting import (
    ReportEvidence,
    ReportMetric,
    build_portfolio_report,
    build_research_report,
    build_risk_report,
    render_markdown,
    report_to_dict,
    validate_report_evidence,
)


def test_research_report():
    report = build_research_report(
        title="Apple Research",
        summary="Revenue and margins were reviewed.",
        findings=["Revenue growth was positive."],
        metrics=[ReportMetric("Sharpe", 1.25)],
        evidence=[
            ReportEvidence(
                "Apple 10-K",
                "SEC",
                "Annual filing evidence.",
                0.9,
            )
        ],
        limitations=["Historical information does not guarantee future results."],
    )

    assert report.report_type == "research"
    assert report.metrics[0].value == pytest.approx(1.25)


def test_portfolio_report_requires_metrics():
    with pytest.raises(ValueError, match="at least one metric"):
        build_portfolio_report(
            title="Portfolio",
            summary="Summary",
            metrics=[],
        )


def test_risk_report_requires_metrics():
    with pytest.raises(ValueError, match="at least one metric"):
        build_risk_report(
            title="Risk",
            summary="Summary",
            metrics=[],
        )


def test_report_serialization_and_markdown():
    report = build_portfolio_report(
        title="Portfolio Report",
        summary="Portfolio summary.",
        metrics=[ReportMetric("Volatility", 0.12, "annualized")],
    )

    payload = report_to_dict(report)
    markdown = render_markdown(report)

    assert payload["report_type"] == "portfolio"
    assert payload["metrics"][0]["value"] == pytest.approx(0.12)
    assert "# Portfolio Report" in markdown
    assert "Volatility" in markdown


def test_evidence_validation():
    report = build_research_report(
        title="Research",
        summary="Summary",
        findings=[],
        evidence=[
            ReportEvidence(
                "Source",
                "SEC",
                "Evidence",
            )
        ],
    )

    validate_report_evidence(report)


def test_invalid_evidence():
    report = build_research_report(
        title="Research",
        summary="Summary",
        findings=[],
        evidence=[ReportEvidence("", "SEC", "Evidence")],
    )

    with pytest.raises(ValueError, match="evidence title"):
        validate_report_evidence(report)
