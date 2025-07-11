from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from pydantic import BaseModel

from app.services.ingestion.tasks import ingest_document_task
from app.services.qa.pipeline import answer_question

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    companies: Optional[List[str]] = None
    time_range: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    cached: bool = False


class DebugQueryRequest(BaseModel):
    text: str
    top_k: int = 5


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/pinecone/status")
async def pinecone_status():
    """Check Pinecone connection and index status."""
    try:
        from app.services.vector.client import get_vector_client
        from app.core.config import get_settings
        
        vector_client = get_vector_client()
        settings = get_settings()
        
        import json
        from collections.abc import Mapping

        # Get index stats – convert to plain dict
        raw_stats = vector_client.index.describe_index_stats()

        if hasattr(raw_stats, "to_dict"):
            stats_data = raw_stats.to_dict()
        elif hasattr(raw_stats, "model_dump"):
            # pydantic model
            stats_data = raw_stats.model_dump(mode="python")  # type: ignore[attr-defined]
        elif isinstance(raw_stats, (str, bytes)):
            try:
                stats_data = json.loads(raw_stats)
            except Exception:  # pragma: no cover
                stats_data = {"raw": raw_stats}
        elif isinstance(raw_stats, Mapping):
            stats_data = dict(raw_stats)
        else:
            # Fallback – stringify to guarantee JSON-serialisable
            stats_data = json.loads(json.dumps(raw_stats, default=str))

        # List index names (each item may be a complex object)
        idx_list_raw = vector_client._pc.list_indexes()
        available_indexes: list[str] = []
        for item in idx_list_raw:
            name = getattr(item, "name", None) or (
                item["name"] if isinstance(item, Mapping) and "name" in item else None
            )
            if name:
                available_indexes.append(str(name))

        return {
            "status": "connected",
            "index_name": settings.pinecone_index_name,
            "stats": stats_data,
            "available_indexes": available_indexes,
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e)
        }


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest):
    """Process a natural language financial query."""
    result = answer_question(
        question=payload.question,
        companies=payload.companies,
        time_range=payload.time_range,
    )
    return QueryResponse(
        answer=str(result["answer"]),
        sources=[str(s) for s in result.get("sources", [])],  # type: ignore[arg-type]
        cached=bool(result["cached"]),
    )


@router.post("/pinecone/test_query")
async def pinecone_test_query(payload: DebugQueryRequest):
    """Return raw Pinecone matches for debugging similarity search."""
    from app.services.embedding import model as embedding_model
    from app.services.vector.client import get_vector_client

    vector_client = get_vector_client()
    vec = embedding_model.encode([payload.text])[0].tolist()

    res = vector_client.query(vector=vec, top_k=payload.top_k)

    # Build a lightweight serialisable response
    matches = [
        {
            "id": m.id,  # type: ignore[attr-defined]
            "score": getattr(m, "score", None),
            "text": (m.metadata.get("text") if getattr(m, "metadata", None) else None),  # type: ignore[attr-defined]
        }
        for m in res.matches  # type: ignore[attr-defined]
    ]

    return {"matches": matches}


@router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a document for ingestion (placeholder)."""
    # Save uploaded file to disk
    import uuid, os, shutil
    from pathlib import Path

    file_id = str(uuid.uuid4())
    upload_dir = Path(os.getenv("UPLOAD_DIR", "/tmp/financial_docs"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{file_id}_{file.filename}"

    with file_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    # Enqueue ingestion task
    ingest_document_task.delay(str(file_path), file_id)

    return {"document_id": file_id, "status": "processing"}


@router.get("/companies/{ticker}/metrics")
async def get_company_metrics(ticker: str):
    """Retrieve cached company metrics (placeholder)."""
    # TODO: Implement cache retrieval
    return {"ticker": ticker, "metrics": {}, "cached": False} 


@router.get("/embedding/status")
async def embedding_status():
    """Check embedding model status."""
    try:
        from app.services.embedding import model as embedding_model
        
        # Try to load the model
        test_text = ["Hello world"]
        embeddings = embedding_model.encode(test_text)
        
        return {
            "status": "ok",
            "embedding_dimension": len(embeddings[0]),
            "test_embedding_shape": embeddings.shape
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        } 