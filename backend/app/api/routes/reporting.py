from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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

router = APIRouter(prefix="/research/reports", tags=["research-reports"])


class EvidenceRequest(BaseModel):
    title: str
    source: str
    content: str
    relevance: float = Field(default=0.0, ge=0.0)


class MetricRequest(BaseModel):
    name: str
    value: float
    unit: str | None = None


class ResearchReportRequest(BaseModel):
    title: str
    summary: str
    findings: list[str] = Field(default_factory=list)
    metrics: list[MetricRequest] = Field(default_factory=list)
    evidence: list[EvidenceRequest] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class PortfolioReportRequest(ResearchReportRequest):
    pass


class RiskReportRequest(ResearchReportRequest):
    pass


def _evidence(items: list[EvidenceRequest]) -> list[ReportEvidence]:
    return [ReportEvidence(**item.model_dump()) for item in items]


def _metrics(items: list[MetricRequest]) -> list[ReportMetric]:
    return [ReportMetric(**item.model_dump()) for item in items]


@router.post("/research")
def research_report(request: ResearchReportRequest) -> dict:
    try:
        report = build_research_report(
            title=request.title,
            summary=request.summary,
            findings=request.findings,
            metrics=_metrics(request.metrics),
            evidence=_evidence(request.evidence),
            limitations=request.limitations,
        )
        validate_report_evidence(report)
        return report_to_dict(report) | {"markdown": render_markdown(report)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/portfolio")
def portfolio_report(request: PortfolioReportRequest) -> dict:
    try:
        report = build_portfolio_report(
            title=request.title,
            summary=request.summary,
            findings=request.findings,
            metrics=_metrics(request.metrics),
            evidence=_evidence(request.evidence),
            limitations=request.limitations,
        )
        validate_report_evidence(report)
        return report_to_dict(report) | {"markdown": render_markdown(report)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/risk")
def risk_report(request: RiskReportRequest) -> dict:
    try:
        report = build_risk_report(
            title=request.title,
            summary=request.summary,
            findings=request.findings,
            metrics=_metrics(request.metrics),
            evidence=_evidence(request.evidence),
            limitations=request.limitations,
        )
        validate_report_evidence(report)
        return report_to_dict(report) | {"markdown": render_markdown(report)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
