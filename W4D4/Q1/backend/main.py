from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .ingestion import ingest_document

from .providers import OpenAIProvider
from .retriever import _build_prompt
from .vector_store import SimpleVectorStore
from .models import DocumentChunk  # added import

class ChatRequest(BaseModel):
    query: str

app = FastAPI(title="HR Onboarding Knowledge Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HR Onboarding Knowledge Assistant is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Global singletons
provider = OpenAIProvider(
    api_key=config.OPENAI_API_KEY,
    embedding_model=config.EMBEDDING_MODEL,
    completion_model=config.COMPLETION_MODEL,
)

# Build vector store lazily once we know embedding dimension
_vector_store: SimpleVectorStore | None = None


def _get_vector_store(dim: int) -> SimpleVectorStore:
    global _vector_store  # noqa: PLW0603
    if _vector_store is None:
        _vector_store = SimpleVectorStore(dim, path=config.VECTOR_STORE_PATH)
    return _vector_store


@app.post("/upload-doc")
async def upload_document(file: UploadFile = File(...)) -> dict:  # noqa: D401
    """Accepts a document file and indexes it."""
    try:
        safe_name = file.filename or "uploaded_file"
        dest_path = Path("uploaded_docs") / safe_name
        dest_path.parent.mkdir(exist_ok=True)
        with dest_path.open("wb") as fh:
            fh.write(await file.read())

        print(f"[Upload] Processing file: {safe_name}")
        
        # Ingest & embed
        chunks = ingest_document(str(dest_path))
        texts = [c.text for c in chunks]
        
        print(f"[Upload] Generated {len(chunks)} chunks, calling OpenAI API...")
        embeddings = provider.embed(texts)
        print(f"[Upload] Got embeddings of dimension {len(embeddings[0])}")

        store = _get_vector_store(len(embeddings[0]))
        store.add(embeddings, [c.__dict__ for c in chunks])

        return {"chunks_indexed": len(chunks)}
    except Exception as e:
        print(f"[Upload] Error: {e}")
        return {"error": str(e), "chunks_indexed": 0}


@app.post("/chat")
async def chat(request: ChatRequest) -> dict:  # noqa: D401
    """Return answer & citations for a query."""
    # Embed query
    query_embedding = provider.embed([request.query])[0]

    store = _get_vector_store(len(query_embedding))
    results = store.search(query_embedding, k=config.TOP_K)
    doc_chunks = [DocumentChunk(**meta) for meta, _ in results]

    prompt = _build_prompt(request.query, doc_chunks)
    answer = provider.complete(prompt, max_tokens=config.MAX_TOKENS)

    citations: List[dict] = [c.metadata for c in doc_chunks]
    return {"answer": answer, "citations": citations} 