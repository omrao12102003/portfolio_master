from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_research_retrieval_endpoint():
    response = client.post(
        "/research/retrieve",
        json={
            "query": "revenue growth",
            "documents": [
                {
                    "document_id": "doc-1",
                    "title": "Annual Report",
                    "source": "company.com/report",
                    "content": (
                        "Revenue increased by 12 percent during the year."
                    ),
                    "published_date": "2025-12-31",
                },
                {
                    "document_id": "doc-2",
                    "title": "Investor Presentation",
                    "source": "company.com/investor",
                    "content": "Management expects stronger demand.",
                    "published_date": "2026-01-15",
                },
            ],
            "top_k": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "revenue growth"
    assert len(data["results"]) == 1
    assert data["results"][0]["document_id"] == "doc-1"
    assert data["results"][0]["source"] == "company.com/report"


def test_research_retrieval_rejects_empty_query():
    response = client.post(
        "/research/retrieve",
        json={
            "query": "",
            "documents": [
                {
                    "document_id": "doc-1",
                    "title": "Annual Report",
                    "source": "company.com/report",
                    "content": "Revenue increased.",
                }
            ],
        },
    )

    assert response.status_code == 400


def test_research_retrieval_rejects_empty_documents():
    response = client.post(
        "/research/retrieve",
        json={
            "query": "revenue",
            "documents": [],
        },
    )

    assert response.status_code == 422
