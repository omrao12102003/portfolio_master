from dataclasses import dataclass

from app.research.grounded_reporting import (
    build_grounded_context,
    build_grounded_research_report,
)
from app.research.reporting import ReportEvidence, ReportMetric, ResearchReport
from app.research.semantic_retrieval import RetrievalFilters, SemanticResearchRetriever


@dataclass(frozen=True)
class InvestmentWorkflowResult:
    report: ResearchReport
    evidence_count: int
    sources: list[str]


class InvestmentResearchWorkflow:
    def __init__(self, retriever: SemanticResearchRetriever):
        self.retriever = retriever

    def build_report(
        self,
        *,
        question: str,
        title: str,
        summary: str,
        metrics: list[ReportMetric],
        ticker: str | None = None,
        company: str | None = None,
        published_before: str | None = None,
        section: str | None = None,
        findings: list[str] | None = None,
        methodology: list[str] | None = None,
        limitations: list[str] | None = None,
        top_k: int = 5,
    ) -> InvestmentWorkflowResult:
        filters = RetrievalFilters(
            ticker=ticker,
            company=company,
            published_before=published_before,
            section=section,
        )

        results = self.retriever.search(
            question,
            filters=filters,
            top_k=top_k,
        )

        evidence = [
            ReportEvidence(
                title=result.title,
                source=result.source,
                content=result.content,
                relevance=float(result.score),
            )
            for result in results
        ]

        context = build_grounded_context(
            question=question,
            metrics=metrics,
            methodology=methodology,
            limitations=limitations,
            evidence=evidence,
        )

        report = build_grounded_research_report(
            title=title,
            summary=summary,
            context=context,
            findings=findings,
        )

        sources = list(dict.fromkeys(item.source for item in evidence))

        return InvestmentWorkflowResult(
            report=report,
            evidence_count=len(evidence),
            sources=sources,
        )
