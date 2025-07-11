"""Pinecone vector database client wrapper.

This module encapsulates Pinecone initialization and provides helper
functions for upserting and querying vectors.
"""
from __future__ import annotations

import logging
# New Pinecone SDK (>=3.x)
from typing import Any, Dict, Sequence

from pinecone import Pinecone, ServerlessSpec  # type: ignore
from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorMetadata(BaseModel):
    document_id: str
    chunk_id: int
    text: str
    # Extend with additional fields (e.g., ticker, quarter) as needed


class PineconeClient:
    """Singleton wrapper around Pinecone index (client >=3.x)."""

    def __init__(self) -> None:
        settings = get_settings()

        # Create Pinecone client instance
        self.pc = Pinecone(api_key=settings.pinecone_api_key)

        # Derive cloud/region from environment string like "us-east1-gcp" or fallback
        env_parts = settings.pinecone_environment.split("-")
        if len(env_parts) >= 2:
            cloud = env_parts[-1]
            region = "-".join(env_parts[:-1])
        else:
            cloud = "aws"
            region = settings.pinecone_environment

        if settings.pinecone_index_name not in self.pc.list_indexes().names():
            logger.info("Creating Pinecone index '%s' (dim=%s)", settings.pinecone_index_name, settings.pinecone_dimension)
            self.pc.create_index(
                name=settings.pinecone_index_name,
                dimension=settings.pinecone_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=cloud, region=region),
            )

        self.index = self.pc.Index(settings.pinecone_index_name)
        logger.info("Pinecone index '%s' is ready", settings.pinecone_index_name)

    # --------------------------- Public API --------------------------- #

    def upsert(
        self,
        ids: Sequence[str],
        vectors: Sequence[Sequence[float]],
        metadatas: Sequence[Dict[str, Any]],
        namespace: str | None = None,
    ) -> None:
        """Upsert vectors into the index."""
        namespace = namespace or "default"
        # Transform to new API vector dicts
        pc_vectors = [
            {
                "id": vec_id,
                "values": vec,
                "metadata": meta,
            }
            for vec_id, vec, meta in zip(ids, vectors, metadatas)
        ]
        self.index.upsert(vectors=pc_vectors, namespace=namespace)

    def query(
        self,
        vector: Sequence[float],
        top_k: int = 5,
        namespace: str | None = None,
        filter: Dict[str, Any] | None = None,
    ) -> pinecone.QueryResponse:  # type: ignore
        """Query similar vectors from the index."""
        namespace = namespace or "default"
        return self.index.query(vector=vector, top_k=top_k, namespace=namespace, filter=filter, include_metadata=True)


_VECTOR_CLIENT: PineconeClient | None = None


def get_vector_client() -> PineconeClient:
    """Return a global Pinecone client instance (singleton)."""
    global _VECTOR_CLIENT  # noqa: PLW0603
    if _VECTOR_CLIENT is None:
        _VECTOR_CLIENT = PineconeClient()
    return _VECTOR_CLIENT 