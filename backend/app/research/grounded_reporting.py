from dataclasses import dataclass

from app.research.reporting import (
    ReportEvidence,
    ReportMetric,
    ResearchReport,
    build_research_report,
    validate_report_evidence,
)


@dataclass(frozen=True)
class QuantitativeContext:
    metrics: list[ReportMetric]
    methodology: list[str]
    limitations: list[str]


@dataclass(frozen=True)
class GroundedResearchContext:
    question: str
    quantitative: QuantitativeContext
    evidence: list[ReportEvidence]


def build_grounded_context(
    *,
    question: str,
    metrics: list[ReportMetric],
    methodology: list[str] | None = None,
    limitations: list[str] | None = None,
    evidence: list[ReportEvidence] | None = None,
) -> GroundedResearchContext:
    if not question.strip():
        raise ValueError("question must not be empty")
    if not metrics:
        raise ValueError("grounded reports require at least one quantitative metric")

    context = GroundedResearchContext(
        question=question.strip(),
        quantitative=QuantitativeContext(
            metrics=list(metrics),
            methodology=[item.strip() for item in methodology or [] if item.strip()],
            limitations=[item.strip() for item in limitations or [] if item.strip()],
        ),
        evidence=list(evidence or []),
    )

    validate_report_evidence(
        ResearchReport(
            report_type="research",
            title="validation",
            summary="validation",
            findings=[],
            metrics=context.quantitative.metrics,
            evidence=context.evidence,
            limitations=context.quantitative.limitations,
        )
    )

    return context


def build_grounded_research_report(
    *,
    title: str,
    summary: str,
    context: GroundedResearchContext,
    findings: list[str] | None = None,
) -> ResearchReport:
    combined_limitations = list(context.quantitative.limitations)

    if context.quantitative.methodology:
        combined_limitations.append(
            "Methodology: " + "; ".join(context.quantitative.methodology)
        )

    return build_research_report(
        title=title,
        summary=summary,
        findings=findings or [],
        metrics=context.quantitative.metrics,
        evidence=context.evidence,
        limitations=combined_limitations,
    )


def grounded_evidence_sources(
    context: GroundedResearchContext,
) -> list[str]:
    return list(dict.fromkeys(item.source for item in context.evidence))


def has_primary_source_evidence(
    context: GroundedResearchContext,
) -> bool:
    return any(
        item.source.strip().lower() in {"sec", "sec filing", "annual report"}
        for item in context.evidence
    )
