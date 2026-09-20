from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.research.database import get_database_url
from app.research.retrieval import ResearchDocument, ResearchRetriever
from app.research.service import ResearchService
from app.research.store import ResearchDocumentStore

router = APIRouter(prefix="/research", tags=["research"])


class ResearchDocumentRequest(BaseModel):
    document_id: str
    title: str
    source: str
    content: str
    published_date: str | None = None


class ResearchRetrievalRequest(BaseModel):
    query: str
    documents: list[ResearchDocumentRequest] = Field(min_length=1)
    top_k: int = Field(default=5, ge=1)


class ResearchEvidenceResponse(BaseModel):
    document_id: str
    title: str
    source: str
    content: str
    published_date: str | None
    chunk_index: int


class ResearchRetrievalResponse(BaseModel):
    query: str
    results: list[ResearchEvidenceResponse]


class ResearchAnswerRequest(BaseModel):
    question: str
    portfolio_context: str = ""
    quantitative_context: str = ""
    evidence: list[ResearchDocumentRequest] = Field(min_length=1)


class ResearchAnswerResponse(BaseModel):
    answer: str
    model: str
    sources: list[str]


class ResearchDocumentResponse(BaseModel):
    document_id: str
    title: str
    source: str
    content: str
    published_date: str | None


@router.post(
    "/documents",
    response_model=ResearchDocumentResponse,
)
def create_research_document(
    request: ResearchDocumentRequest,
) -> ResearchDocumentResponse:
    try:
        document = ResearchDocument(
            document_id=request.document_id,
            title=request.title,
            source=request.source,
            content=request.content,
            published_date=request.published_date,
        )
        store = ResearchDocumentStore(get_database_url())
        store.initialize()
        store.upsert(document)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ResearchDocumentResponse(
        document_id=document.document_id,
        title=document.title,
        source=document.source,
        content=document.content,
        published_date=document.published_date,
    )


@router.get(
    "/documents",
    response_model=list[ResearchDocumentResponse],
)
def list_research_documents() -> list[ResearchDocumentResponse]:
    try:
        store = ResearchDocumentStore(get_database_url())
        store.initialize()
        documents = store.list_documents()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return [
        ResearchDocumentResponse(
            document_id=document.document_id,
            title=document.title,
            source=document.source,
            content=document.content,
            published_date=document.published_date,
        )
        for document in documents
    ]


@router.get(
    "/documents/{document_id}",
    response_model=ResearchDocumentResponse,
)
def get_research_document(
    document_id: str,
) -> ResearchDocumentResponse:
    try:
        store = ResearchDocumentStore(get_database_url())
        store.initialize()
        document = store.get(document_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if document is None:
        raise HTTPException(status_code=404, detail="Research document not found.")

    return ResearchDocumentResponse(
        document_id=document.document_id,
        title=document.title,
        source=document.source,
        content=document.content,
        published_date=document.published_date,
    )


@router.delete("/documents/{document_id}")
def delete_research_document(document_id: str) -> dict[str, bool]:
    try:
        store = ResearchDocumentStore(get_database_url())
        store.initialize()
        deleted = store.delete(document_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="Research document not found.")

    return {"deleted": True}


@router.post("/retrieve", response_model=ResearchRetrievalResponse)
def retrieve_research(
    request: ResearchRetrievalRequest,
) -> ResearchRetrievalResponse:
    try:
        documents = [
            ResearchDocument(
                document_id=document.document_id,
                title=document.title,
                source=document.source,
                content=document.content,
                published_date=document.published_date,
            )
            for document in request.documents
        ]

        retriever = ResearchRetriever(documents)
        results = retriever.retrieve(request.query, top_k=request.top_k)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ResearchRetrievalResponse(
        query=request.query,
        results=[
            ResearchEvidenceResponse(
                document_id=result.document_id,
                title=result.title,
                source=result.source,
                content=result.content,
                published_date=result.published_date,
                chunk_index=result.chunk_index,
            )
            for result in results
        ],
    )


@router.post("/answer", response_model=ResearchAnswerResponse)
def answer_research(
    request: ResearchAnswerRequest,
) -> ResearchAnswerResponse:
    try:
        service = ResearchService()

        evidence = [
            {
                "source": document.source,
                "content": document.content,
            }
            for document in request.evidence
        ]

        result = service.answer(
            question=request.question,
            portfolio_context=request.portfolio_context,
            quantitative_context=request.quantitative_context,
            evidence=evidence,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ResearchAnswerResponse(
        answer=result.answer,
        model=result.model,
        sources=result.sources,
    )
