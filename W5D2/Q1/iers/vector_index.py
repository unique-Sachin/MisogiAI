# numpy optional for faiss fallback; import lazily if needed
# Attempt to import FAISS. On some systems the import may raise non-ImportError
# exceptions due to ABI mismatches (e.g., compiled against an older NumPy).
# We therefore catch *any* Exception and not just ImportError.
try:
    import faiss  # type: ignore
    _FAISS_AVAILABLE = True
except Exception:  # pragma: no cover
    # FAISS is not available (e.g., unsupported Python version). We fall back to a simple
    # NumPy-based implementation that offers the same public API but without the
    # performance benefits of FAISS. This keeps the rest of the codebase unchanged.
    _FAISS_AVAILABLE = False

import json
from typing import List, Tuple

import os
from .embeddings import embed

INDEX_PATH = "vector.index"

class VectorIndex:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.ids: List[str] = []

        if _FAISS_AVAILABLE:
            self.index = faiss.IndexFlatL2(dim)
        else:
            # Define a minimal in-memory fallback index using Python lists so code continues to work
            import numpy as np  # type: ignore

            class _SimpleIndex:
                def __init__(self, dim):
                    self.vectors = np.empty((0, dim), dtype=np.float32)

                def add(self, vecs):
                    self.vectors = np.vstack([self.vectors, vecs])

                def search(self, vec, k):
                    if self.vectors.size == 0:
                        return np.array([[ ]], dtype='float32'), np.array([[ ]], dtype='int64')
                    dists = np.linalg.norm(self.vectors - vec, axis=1)
                    idx = np.argsort(dists)[:k]
                    return np.array([dists[idx]]), np.array([idx])

            self.index = _SimpleIndex(dim)

    def add_texts(self, texts, metadata):
        vectors = embed(texts)
        self.index.add(vectors)
        self.ids.extend(metadata)

    def search(self, query: str, k: int = 5):
        vec = embed([query])

        distances, indices = self.index.search(vec, k)

        results: List[Tuple[str, float]] = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.ids):
                results.append((self.ids[idx], float(dist)))
        return results

    def save(self, path: str = INDEX_PATH, meta_path: str = "metadata.json"):
        faiss.write_index(self.index, path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.ids, f)

    def load(self, path: str = INDEX_PATH, meta_path: str = "metadata.json"):
        if os.path.exists(path):
            self.index = faiss.read_index(path)
            self.dim = self.index.d
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.ids = json.load(f)
            return True
        return False 