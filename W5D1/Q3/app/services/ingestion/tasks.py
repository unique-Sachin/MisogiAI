"""Celery tasks for document ingestion."""
from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import List

from app.core.celery_app import celery_app
from app.services.embedding import model as embedding_model
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.parser import parse_document
from app.services.vector.client import VectorMetadata, get_vector_client

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/financial_docs"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@celery_app.task(name="ingest_document")
def ingest_document_task(file_path_str: str, document_id: str | None = None) -> str:  # type: ignore[valid-type]
    """Parse, chunk, embed, and upsert a document into Pinecone.

    Args:
        file_path_str: Path to the uploaded file.
        document_id: Optional existing document ID (for re-upload/re-processing).

    Returns:
        The document ID used for vector metadata.
    """
    file_path = Path(file_path_str)
    document_id = document_id or str(uuid.uuid4())
    logger.info("Starting ingestion for %s (doc_id=%s)", file_path.name, document_id)

    text, content_type = parse_document(file_path)
    if not text.strip():
        logger.warning("No text extracted from %s", file_path)
        return document_id

    chunks: List[str] = chunk_text(text)
    embeddings = embedding_model.encode(chunks)

    vector_client = get_vector_client()

    ids = [f"{document_id}:{i}" for i in range(len(chunks))]
    metadatas = [VectorMetadata(document_id=document_id, chunk_id=i, text=chunk).dict() for i, chunk in enumerate(chunks)]

    vector_client.upsert(ids=ids, vectors=embeddings.tolist(), metadatas=metadatas)

    logger.info("Completed ingestion for document %s with %d chunks", document_id, len(chunks))
    return document_id 