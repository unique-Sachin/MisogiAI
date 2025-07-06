from __future__ import annotations

import json
import math
import os
import pickle
from typing import Dict, List, Tuple


class SimpleVectorStore:
    """Simple in-memory vector store using pure Python for similarity search."""

    def __init__(self, dim: int, path: str):
        self.dim = dim
        self.path = path
        self.embeddings: List[List[float]] = []
        self.metadata: List[Dict] = []
        self._load_if_exists()

    # ---------------------------------------------------------------------
    # Persistence helpers
    # ---------------------------------------------------------------------
    def _embeddings_filepath(self) -> str:
        return os.path.join(self.path, "embeddings.pkl")

    def _meta_filepath(self) -> str:
        return os.path.join(self.path, "meta.json")

    def _load_if_exists(self) -> None:
        if not os.path.exists(self._embeddings_filepath()):
            # Nothing to load yet
            return
        try:
            with open(self._embeddings_filepath(), "rb") as fh:
                self.embeddings = pickle.load(fh)
            with open(self._meta_filepath(), "r", encoding="utf-8") as fh:
                self.metadata = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            print(f"[VectorStore] Failed to load existing index: {exc}")

    def _save(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        with open(self._embeddings_filepath(), "wb") as fh:
            pickle.dump(self.embeddings, fh)
        with open(self._meta_filepath(), "w", encoding="utf-8") as fh:
            json.dump(self.metadata, fh, ensure_ascii=False, indent=2)

    # ---------------------------------------------------------------------
    # Vector math helpers (pure Python)
    # ---------------------------------------------------------------------
    def _dot_product(self, a: List[float], b: List[float]) -> float:
        """Compute dot product of two vectors."""
        return sum(x * y for x, y in zip(a, b))

    def _magnitude(self, vector: List[float]) -> float:
        """Compute magnitude (L2 norm) of a vector."""
        return math.sqrt(sum(x * x for x in vector))

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_prod = self._dot_product(a, b)
        mag_a = self._magnitude(a)
        mag_b = self._magnitude(b)
        
        if mag_a == 0 or mag_b == 0:
            return 0.0
        
        return dot_prod / (mag_a * mag_b)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def add(self, embeddings: List[List[float]], metadatas: List[Dict]) -> None:
        if not embeddings:
            return
        self.embeddings.extend(embeddings)
        self.metadata.extend(metadatas)
        self._save()

    def search(self, embedding: List[float], k: int = 4) -> List[Tuple[Dict, float]]:
        if not self.embeddings:
            return []
        
        # Compute similarities for all stored embeddings
        similarities = []
        for i, stored_embedding in enumerate(self.embeddings):
            sim = self._cosine_similarity(embedding, stored_embedding)
            similarities.append((i, sim))
        
        # Sort by similarity (descending) and take top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_k = similarities[:k]
        
        # Convert to results format (metadata, distance)
        results: List[Tuple[Dict, float]] = []
        for idx, similarity in top_k:
            # Convert similarity to distance (lower = better)
            distance = 1.0 - similarity
            results.append((self.metadata[idx], distance))
        
        return results 