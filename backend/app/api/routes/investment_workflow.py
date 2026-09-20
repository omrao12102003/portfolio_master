from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.research.investment_workflow import InvestmentResearchWorkflow
from app.research.reporting import ReportMetric, render_markdown, report_to_dict
from app.research.semantic_retrieval import SemanticResearchRetriever
from app.research.vector_store import ResearchVectorStore

router = APIRouter(
    prefix="/research/workflow",
    tags=["investment-workflow"],
)


class WorkflowMetricRequest(BaseModel):
    name: str
    value: float
    unit: str | None = None


class InvestmentWorkflowRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    question: str = Field(..., min_length=1, max_length=2000)
    summary: str = Field(..., min_length=1, max_length=5000)
    metrics: list[WorkflowMetricRequest]
    ticker: str | None = None
    company: str | None = None
    published_before: str | None = None
    section: str | None = None
    findings: list[str] = Field(default_factory=list, max_length=20)
    methodology: list[str] = Field(default_factory=list, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=20)
    top_k: int = Field(default=5, ge=1, le=20)


def _build_workflow() -> InvestmentResearchWorkflow:
    store = ResearchVectorStore()
    retriever = SemanticResearchRetriever(store)
    return InvestmentResearchWorkflow(retriever)


@router.post("/report")
def create_investment_report(request: InvestmentWorkflowRequest) -> dict:
    try:
        workflow = _build_workflow()

        result = workflow.build_report(
            question=request.question,
            title=request.title,
            summary=request.summary,
            metrics=[
                ReportMetric(
                    name=item.name,
                    value=item.value,
                    unit=item.unit,
                )
                for item in request.metrics
            ],
            ticker=request.ticker,
            company=request.company,
            published_before=request.published_before,
            section=request.section,
            findings=request.findings,
            methodology=request.methodology,
            limitations=request.limitations,
            top_k=request.top_k,
        )

        payload = report_to_dict(result.report)
        payload["markdown"] = render_markdown(result.report)
        payload["workflow"] = {
            "evidence_count": result.evidence_count,
            "sources": result.sources,
        }

        return payload

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
