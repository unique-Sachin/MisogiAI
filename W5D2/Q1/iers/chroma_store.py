from typing import List, Tuple
import os
from pathlib import Path

from chromadb import PersistentClient  # type: ignore
from chromadb.config import Settings  # type: ignore
from chromadb.utils import embedding_functions  # type: ignore

from .embeddings import embed

CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")
_COLLECTION = "policies"

class _IERSEmbedding:
    """Adapter exposing our embed() as a list of lists for Chroma (expects `input` parameter)."""

    def __call__(self, input: List[str]):  # type: ignore
        return embed(input).tolist()

class ChromaStore:
    """Lightweight wrapper around a persistent Chroma collection."""

    def __init__(self, collection_name: str = _COLLECTION, persist_dir: str = CHROMA_DIR):
        self.client = PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=_IERSEmbedding(),
        )

    def add_texts(self, texts: List[str], metadatas: List[dict]):
        # Use stable ids (len + index) if none provided
        start_idx = self.collection.count()
        ids = [f"doc_{start_idx + i}" for i in range(len(texts))]
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int = 5, filters: dict | None = None) -> List[Tuple[str, float, dict]]:
        res = self.collection.query(query_texts=[query], n_results=k, where=filters or {})
        docs = res["documents"][0]
        dists = res["distances"][0]
        metas = res.get("metadatas", [[{}]])[0]
        return list(zip(docs, dists, metas)) 