"""Embedding model wrappers for Phase 2.

Each class exposes:
    encode(texts: List[str]) -> np.ndarray  # shape (len(texts), dim)

Usage:
    from embedding_models import Word2VecEmbedder, BertEmbedder, SentenceBERTEmbedder, OpenAIEmbedder
    embedder = SentenceBERTEmbedder()
    vectors = embedder.encode(["some text", ...])
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shelve
import time
from pathlib import Path
from typing import Dict, List

import numpy as np  # type: ignore
from tqdm import tqdm  # type: ignore
import torch  # type: ignore

__all__ = [
    "Word2VecEmbedder",
    "BertEmbedder",
    "SentenceBERTEmbedder",
    "OpenAIEmbedder",
]

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


class Word2VecEmbedder:
    """Average pre-trained Word2Vec vectors (GoogleNews 300d)."""

    def __init__(self):
        import gensim.downloader as api  # type: ignore

        self.model = api.load("word2vec-google-news-300")
        self.dim = self.model.vector_size
        self.token_re = re.compile(r"[A-Za-z]+")

    def _tokenize(self, text: str) -> List[str]:
        return self.token_re.findall(text.lower())

    def encode(self, texts: List[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, txt in enumerate(texts):
            toks = [t for t in self._tokenize(txt) if t in self.model]
            if toks:
                vecs = [self.model[t] for t in toks]
                out[i] = np.mean(vecs, axis=0)
        return out


class BertEmbedder:
    """CLS-token embedding from bert-base-uncased."""

    def __init__(self, model_name: str = "bert-base-uncased", device: str | None = None):
        from transformers import AutoModel, AutoTokenizer  # type: ignore

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")  # type: ignore[attr-defined]
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        self.dim = self.model.config.hidden_size

    @staticmethod
    def _batch(iterable, n=32):
        for i in range(0, len(iterable), n):
            yield iterable[i : i + n]

    @torch.no_grad()  # type: ignore
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        all_vecs: List[np.ndarray] = []
        for batch in self._batch(texts, batch_size):
            inputs = self.tokenizer(batch, padding=True, truncation=True, return_tensors="pt").to(self.device)
            outputs = self.model(**inputs)
            cls_vec = outputs.last_hidden_state[:, 0, :].cpu().numpy()  # CLS token
            all_vecs.append(cls_vec.astype(np.float32))
        return np.vstack(all_vecs)


class SentenceBERTEmbedder:
    """SentenceTransformer all-MiniLM-L6-v2 (384-d)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str | None = None):
        from sentence_transformers import SentenceTransformer  # type: ignore

        self.device = device
        self.model = SentenceTransformer(model_name, device=device)
        self.dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: List[str], batch_size: int = 64) -> np.ndarray:  # type: ignore[override]
        vecs = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True)
        return vecs.astype(np.float32)


class OpenAIEmbedder:
    """OpenAI ada-002 embeddings with local caching to respect budget limits."""

    def __init__(self, model_name: str = "text-embedding-ada-002", cache_path: Path | None = None):
        import openai  # type: ignore

        self.openai = openai
        self.openai.api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai.api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set.")
        self.model_name = model_name
        self.dim = 1536  # ada-002 output size
        self.cache_path = cache_path or CACHE_DIR / "openai_embeddings.db"
        # Use shelve for a simple key-value store (persistent dict)
        self._store = shelve.open(str(self.cache_path))

    def _hash(self, text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def _query_api(self, batch: List[str]) -> List[List[float]]:
        response = self.openai.Embedding.create(model=self.model_name, input=batch)  # type: ignore[attr-defined]
        # API returns list of dicts in order
        return [d["embedding"] for d in sorted(response.data, key=lambda x: x["index"])]

    def encode(self, texts: List[str], batch_size: int = 100) -> np.ndarray:  # type: ignore[override]
        vectors: List[np.ndarray] = []
        uncached_indices: Dict[int, str] = {}
        for idx, t in enumerate(texts):
            h = self._hash(t)
            if h in self._store:
                vectors.append(np.array(self._store[h], dtype=np.float32))
            else:
                vectors.append(None)  # placeholder
                uncached_indices[idx] = h

        # Fetch uncached texts in batches
        pending_texts = [texts[i] for i in uncached_indices]
        for i in tqdm(range(0, len(pending_texts), batch_size), desc="OpenAI batches"):
            batch_texts = pending_texts[i : i + batch_size]
            try:
                batch_vecs = self._query_api(batch_texts)
            except Exception as e:
                print("OpenAI API error, sleeping 5s…", e)
                time.sleep(5)
                batch_vecs = self._query_api(batch_texts)
            for txt, vec in zip(batch_texts, batch_vecs):
                h = self._hash(txt)
                self._store[h] = vec  # cache

        # Now build final matrix
        for i, v in enumerate(vectors):
            if v is None:
                h = uncached_indices[i]
                v = np.array(self._store[h], dtype=np.float32)
                vectors[i] = v
        return np.vstack(vectors)

    def __del__(self):
        try:
            self._store.close()
        except Exception:
            pass 