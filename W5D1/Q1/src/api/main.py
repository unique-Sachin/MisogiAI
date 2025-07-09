import os
import tempfile
import shutil
from pathlib import Path
from typing import List
# External dependencies (marked with type ignore to satisfy linters if stubs are missing)
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from src.core.rag_engine import MedicalRAGEngine
from src.core.document_processor import MedicalDocumentProcessor

app = FastAPI(title="Medical AI Assistant API")

# Include monitoring endpoints (metrics, health, etc.)
from src.api.monitoring_endpoints import router as monitoring_router

# Register routers
app.include_router(monitoring_router)

# Initialize RAG engine and document processor
rag_engine = MedicalRAGEngine()
doc_processor = MedicalDocumentProcessor()

# Store for tracking document processing status
processing_status = {}

class QueryRequest(BaseModel):
    query: str
    user_id: str | None = None

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str

class DocumentProcessingStatus(BaseModel):
    document_id: str
    filename: str
    status: str  # "pending", "processing", "completed", "failed"
    chunks_processed: int
    error_message: str | None = None

def process_document_background(document_id: str, file_path: str, filename: str):
    """Background task to process uploaded document."""
    try:
        processing_status[document_id] = {
            "filename": filename,
            "status": "processing",
            "chunks_processed": 0,
            "error_message": None
        }
        
        # Process the document
        chunks_processed = doc_processor.process_documents([file_path])
        
        # Update status
        processing_status[document_id] = {
            "filename": filename,
            "status": "completed",
            "chunks_processed": chunks_processed,
            "error_message": None
        }
        
        # Clean up temporary file
        os.remove(file_path)
        
    except Exception as e:
        processing_status[document_id] = {
            "filename": filename,
            "status": "failed",
            "chunks_processed": 0,
            "error_message": str(e)
        }
        
        # Clean up temporary file on error
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/v1/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload a PDF document for processing."""
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported"
        )
    
    # Generate document ID
    import uuid
    document_id = str(uuid.uuid4())
    
    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"{document_id}_{file.filename}")
        
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize processing status
        processing_status[document_id] = {
            "filename": file.filename or "unknown.pdf",
            "status": "pending",
            "chunks_processed": 0,
            "error_message": None
        }
        
        # Start background processing
        background_tasks.add_task(
            process_document_background,
            document_id,
            temp_file_path,
            file.filename or "unknown.pdf"
        )
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename or "unknown.pdf",
            status="pending",
            message="Document uploaded successfully. Processing started."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )

@app.get("/api/v1/documents/status/{document_id}", response_model=DocumentProcessingStatus)
async def get_document_status(document_id: str):
    """Get the processing status of a document."""
    
    if document_id not in processing_status:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    status_info = processing_status[document_id]
    
    return DocumentProcessingStatus(
        document_id=document_id,
        filename=status_info["filename"],
        status=status_info["status"],
        chunks_processed=status_info["chunks_processed"],
        error_message=status_info.get("error_message")
    )

@app.get("/api/v1/documents/list")
async def list_documents():
    """List all uploaded documents and their status."""
    
    documents = []
    for doc_id, status_info in processing_status.items():
        documents.append({
            "document_id": doc_id,
            "filename": status_info["filename"],
            "status": status_info["status"],
            "chunks_processed": status_info["chunks_processed"],
            "error_message": status_info.get("error_message")
        })
    
    return {"documents": documents, "total_count": len(documents)}

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system."""
    
    if document_id not in processing_status:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    # Remove from processing status
    del processing_status[document_id]
    
    # Note: In a production system, you would also remove the document
    # chunks from the vector database and any associated metadata
    
    return {"message": f"Document {document_id} deleted successfully"}

@app.post("/api/v1/query")
async def query_endpoint(payload: QueryRequest):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        result = rag_engine.query(payload.query)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
        "documents_processed": len([d for d in processing_status.values() if d["status"] == "completed"])
    }

@app.get("/")
async def root():
    return {"message": "Medical AI Assistant API", "docs": "/docs"} 