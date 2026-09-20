from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReportEvidence:
    title: str
    source: str
    content: str
    relevance: float = 0.0


@dataclass(frozen=True)
class ReportMetric:
    name: str
    value: float
    unit: str | None = None


@dataclass(frozen=True)
class ResearchReport:
    report_type: str
    title: str
    summary: str
    findings: list[str]
    metrics: list[ReportMetric]
    evidence: list[ReportEvidence]
    limitations: list[str]


def _format_metric(metric: ReportMetric) -> str:
    if metric.unit:
        return f"{metric.name}: {metric.value:.4f} {metric.unit}"
    return f"{metric.name}: {metric.value:.4f}"


def build_research_report(
    *,
    title: str,
    summary: str,
    findings: list[str],
    evidence: list[ReportEvidence],
    metrics: list[ReportMetric] | None = None,
    limitations: list[str] | None = None,
) -> ResearchReport:
    if not title.strip():
        raise ValueError("title must not be empty")
    if not summary.strip():
        raise ValueError("summary must not be empty")

    return ResearchReport(
        report_type="research",
        title=title.strip(),
        summary=summary.strip(),
        findings=[item.strip() for item in findings if item.strip()],
        metrics=list(metrics or []),
        evidence=list(evidence),
        limitations=list(limitations or []),
    )


def build_portfolio_report(
    *,
    title: str,
    summary: str,
    metrics: list[ReportMetric],
    evidence: list[ReportEvidence] | None = None,
    findings: list[str] | None = None,
    limitations: list[str] | None = None,
) -> ResearchReport:
    if not metrics:
        raise ValueError("portfolio reports require at least one metric")

    return ResearchReport(
        report_type="portfolio",
        title=title.strip(),
        summary=summary.strip(),
        findings=[item.strip() for item in findings or [] if item.strip()],
        metrics=list(metrics),
        evidence=list(evidence or []),
        limitations=list(limitations or []),
    )


def build_risk_report(
    *,
    title: str,
    summary: str,
    metrics: list[ReportMetric],
    findings: list[str] | None = None,
    evidence: list[ReportEvidence] | None = None,
    limitations: list[str] | None = None,
) -> ResearchReport:
    if not metrics:
        raise ValueError("risk reports require at least one metric")

    return ResearchReport(
        report_type="risk",
        title=title.strip(),
        summary=summary.strip(),
        findings=[item.strip() for item in findings or [] if item.strip()],
        metrics=list(metrics),
        evidence=list(evidence or []),
        limitations=list(limitations or []),
    )


def report_to_dict(report: ResearchReport) -> dict[str, Any]:
    return {
        "report_type": report.report_type,
        "title": report.title,
        "summary": report.summary,
        "findings": report.findings,
        "metrics": [
            {
                "name": metric.name,
                "value": metric.value,
                "unit": metric.unit,
            }
            for metric in report.metrics
        ],
        "evidence": [
            {
                "title": item.title,
                "source": item.source,
                "content": item.content,
                "relevance": item.relevance,
            }
            for item in report.evidence
        ],
        "limitations": report.limitations,
    }


def render_markdown(report: ResearchReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        f"**Report type:** {report.report_type}",
        "",
        "## Summary",
        "",
        report.summary,
    ]

    if report.metrics:
        lines.extend(["", "## Quantitative metrics", ""])
        lines.extend(f"- {_format_metric(metric)}" for metric in report.metrics)

    if report.findings:
        lines.extend(["", "## Findings", ""])
        lines.extend(f"- {finding}" for finding in report.findings)

    if report.evidence:
        lines.extend(["", "## Evidence", ""])
        for index, evidence in enumerate(report.evidence, start=1):
            lines.extend(
                [
                    f"### [{index}] {evidence.title}",
                    "",
                    evidence.content,
                    "",
                    f"Source: {evidence.source}",
                ]
            )

    if report.limitations:
        lines.extend(["", "## Limitations", ""])
        lines.extend(f"- {item}" for item in report.limitations)

    return "\n".join(lines)


def validate_report_evidence(report: ResearchReport) -> None:
    for evidence in report.evidence:
        if not evidence.title.strip():
            raise ValueError("evidence title must not be empty")
        if not evidence.source.strip():
            raise ValueError("evidence source must not be empty")
        if not evidence.content.strip():
            raise ValueError("evidence content must not be empty")
