from dataclasses import dataclass

from app.research.investment_workflow import InvestmentResearchWorkflow
from app.research.reporting import ReportMetric


@dataclass(frozen=True)
class FakeResult:
    title: str
    source: str
    content: str
    score: float


class FakeRetriever:
    def retrieve(self, query, *, filters, limit):
        assert query == "Assess Apple risk"
        assert filters.ticker == "AAPL"
        assert limit == 2

        return [
            FakeResult(
                title="Apple 2025 10-K",
                source="SEC",
                content="Primary filing evidence.",
                score=0.95,
            ),
            FakeResult(
                title="Apple annual filing",
                source="SEC",
                content="Additional filing evidence.",
                score=0.80,
            ),
        ]


def test_workflow_builds_grounded_report():
    workflow = InvestmentResearchWorkflow(FakeRetriever())

    result = workflow.build_report(
        question="Assess Apple risk",
        title="Apple Risk Report",
        summary="Risk was evaluated using quantitative metrics and filing evidence.",
        metrics=[ReportMetric("Sharpe", 1.2)],
        ticker="AAPL",
        top_k=2,
    )

    assert result.evidence_count == 2
    assert result.sources == ["SEC"]
    assert result.report.metrics[0].name == "Sharpe"
    assert len(result.report.evidence) == 2


def test_workflow_preserves_limitations_and_methodology():
    workflow = InvestmentResearchWorkflow(FakeRetriever())

    result = workflow.build_report(
        question="Assess Apple risk",
        title="Apple Risk Report",
        summary="Summary",
        metrics=[ReportMetric("VaR", 0.01)],
        ticker="AAPL",
        methodology=["Historical VaR"],
        limitations=["Historical results are not forecasts."],
        top_k=2,
    )

    assert "Methodology: Historical VaR" in result.report.limitations
    assert "Historical results are not forecasts." in result.report.limitations
