"""Embedding service using sentence-transformers Qwen3-Embedding-0.6B.

This module provides a simple wrapper around the SentenceTransformer model
for encoding text and computing similarities.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

import numpy as np  # type: ignore
from sentence_transformers import SentenceTransformer, util  # type: ignore


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    """Load an embedding model, starting with smaller models for memory efficiency."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Try models in order of increasing size/memory requirements
    models_to_try = [
        "all-MiniLM-L6-v2",  # 384 dimensions, ~23MB
        # "paraphrase-MiniLM-L3-v2",  # 384 dimensions, ~18MB  
        # "Qwen/Qwen3-Embedding-0.6B"  # 1024 dimensions, ~600MB
    ]
    
    for model_name in models_to_try:
        try:
            logger.info(f"Attempting to load model: {model_name}")
            return SentenceTransformer(model_name)
        except Exception as e:
            logger.warning(f"Failed to load {model_name}: {e}")
            continue
    
    # If all models fail, raise the last exception
    raise RuntimeError("Failed to load any embedding model")


def encode(texts: List[str]) -> np.ndarray:
    """Encode a list of texts into normalized embedding vectors.

    Args:
        texts: List of input strings.

    Returns:
        NumPy array of shape (len(texts), embedding_dim) with float32 dtype.
    """
    model = _load_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.astype(np.float32)


def similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between two sets of embeddings.

    Args:
        a: Embedding matrix of shape (m, d).
        b: Embedding matrix of shape (n, d).

    Returns:
        Cosine similarity matrix of shape (m, n).
    """
    # Convert to torch tensors for util.cos_sim
    import torch  # type: ignore

    a_t = torch.from_numpy(a)  # type: ignore[attr-defined]
    b_t = torch.from_numpy(b)  # type: ignore[attr-defined]
    sim = util.cos_sim(a_t, b_t)
    return sim.cpu().numpy() 