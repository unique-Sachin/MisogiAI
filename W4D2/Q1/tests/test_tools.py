import pytest
from fastapi.testclient import TestClient  # type: ignore

from document_analyzer.main import app

client = TestClient(app)

def test_add_and_analyze_document():
    doc_content = "OpenAI builds advanced AI systems."
    add_resp = client.post("/add_document", json={
        "document_data": {
            "title": "AI News",
            "author": "Reporter",
            "date": "2025-07-02",
            "content": doc_content,
            "metadata": {"category": "Tech", "language": "English"}
        }
    })
    assert add_resp.status_code == 200
    doc_id = add_resp.json()["document_id"]

    analyze_resp = client.post("/analyze_document", json={"document_id": doc_id})
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert "sentiment" in data
    assert "keywords" in data
    assert "readability" in data
    assert "stats" in data


def test_sentiment_endpoint():
    resp = client.post("/get_sentiment", json={"text": "I love AI."})
    assert resp.status_code == 200
    assert resp.json()["sentiment"] in ["positive", "negative", "neutral"]


def test_extract_keywords_default_limit():
    resp = client.post("/extract_keywords", json={"text": "AI transforms technology and society."})
    assert resp.status_code == 200
    assert len(resp.json()["keywords"]) <= 5


def test_search_documents():
    # Using earlier added document
    resp = client.post("/search_documents", json={"query": "OpenAI"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list) 