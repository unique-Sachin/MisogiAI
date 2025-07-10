"""Wrapper around ChromaDB persistent index using Sentence-Transformers."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from sentence_transformers import SentenceTransformer

EMBED_MODEL = os.getenv("EMBED_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
INDEX_DIR = Path(os.getenv("INDEX_DIR", "app/index_store"))
INDEX_DIR.mkdir(parents=True, exist_ok=True)


class EmbeddingIndex:
    """Lightweight wrapper to add/query documents per intent collection."""

    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=str(INDEX_DIR))
        self.model = SentenceTransformer(EMBED_MODEL)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_documents(self, collection: str, docs: List[str], ids: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        embeddings = self.model.encode(docs).tolist()
        col = self.client.get_or_create_collection(collection)
        if metadata:
            col.add(ids=ids, embeddings=embeddings, documents=docs, metadatas=metadata)  # type: ignore[arg-type]
        else:
            col.add(ids=ids, embeddings=embeddings, documents=docs)

    def query(self, collection: str, query_text: str, k: int = 4) -> List[str]:
        """Legacy method - returns only documents for backward compatibility."""
        col = self.client.get_or_create_collection(collection)
        emb = self.model.encode([query_text]).tolist()[0]
        res = col.query(query_embeddings=[emb], n_results=k)
        return res["documents"][0] if res["documents"] else []

    def query_with_references(self, collection: str, query_text: str, k: int = 4) -> List[Dict[str, Any]]:
        """Enhanced query that returns documents with their source references."""
        col = self.client.get_or_create_collection(collection)
        emb = self.model.encode([query_text]).tolist()[0]
        res = col.query(query_embeddings=[emb], n_results=k)
        
        if not res["documents"] or not res["documents"][0]:
            return []
        
        results = []
        documents = res["documents"][0]
        ids = res["ids"][0] if res["ids"] else []
        metadatas = res["metadatas"][0] if res["metadatas"] else []
        distances = res["distances"][0] if res["distances"] else []
        
        for i, doc in enumerate(documents):
            result = {
                "content": doc,
                "id": ids[i] if i < len(ids) else f"chunk_{i}",
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distances[i] if i < len(distances) else 0.0
            }
            results.append(result)
        
        return results 