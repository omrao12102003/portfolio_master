from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.research.grounded_reporting import (
    build_grounded_context,
    build_grounded_research_report,
    grounded_evidence_sources,
    has_primary_source_evidence,
)
from app.research.reporting import (
    ReportEvidence,
    ReportMetric,
    render_markdown,
    report_to_dict,
)

router = APIRouter(
    prefix="/research/reports",
    tags=["grounded-research"],
)


class GroundedEvidenceRequest(BaseModel):
    title: str
    source: str
    content: str
    relevance: float = Field(default=0.0, ge=0.0)


class GroundedMetricRequest(BaseModel):
    name: str
    value: float
    unit: str | None = None


class GroundedReportRequest(BaseModel):
    title: str
    question: str
    summary: str
    findings: list[str] = Field(default_factory=list)
    metrics: list[GroundedMetricRequest]
    methodology: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    evidence: list[GroundedEvidenceRequest] = Field(default_factory=list)


def _metrics(
    items: list[GroundedMetricRequest],
) -> list[ReportMetric]:
    return [ReportMetric(**item.model_dump()) for item in items]


def _evidence(
    items: list[GroundedEvidenceRequest],
) -> list[ReportEvidence]:
    return [ReportEvidence(**item.model_dump()) for item in items]


@router.post("/grounded")
def grounded_report(request: GroundedReportRequest) -> dict:
    try:
        context = build_grounded_context(
            question=request.question,
            metrics=_metrics(request.metrics),
            methodology=request.methodology,
            limitations=request.limitations,
            evidence=_evidence(request.evidence),
        )

        report = build_grounded_research_report(
            title=request.title,
            summary=request.summary,
            context=context,
            findings=request.findings,
        )

        payload = report_to_dict(report)
        payload["markdown"] = render_markdown(report)
        payload["grounding"] = {
            "evidence_count": len(context.evidence),
            "sources": grounded_evidence_sources(context),
            "has_primary_source_evidence": has_primary_source_evidence(context),
            "quantitative_metric_count": len(context.quantitative.metrics),
        }

        return payload

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
