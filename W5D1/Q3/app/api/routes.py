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


@router.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok"}


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