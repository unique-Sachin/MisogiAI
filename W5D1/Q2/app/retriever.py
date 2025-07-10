"""Retriever that builds/queries Chroma index with fixed-size token chunks."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any

from app.embedding_index import EmbeddingIndex

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
KB_ROOT = Path("app/knowledge_base")

index = EmbeddingIndex()

# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------

def _chunk_text(text: str) -> List[str]:
    """Very simple whitespace-based chunking on token count (approx)."""
    words = text.split()
    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for i in range(0, len(words), step):
        chunk_words = words[i : i + CHUNK_SIZE]
        chunks.append(" ".join(chunk_words))
    return chunks


# ---------------------------------------------------------------------------
# Build index (can be called offline)
# ---------------------------------------------------------------------------

def build_index() -> None:
    for intent_dir in KB_ROOT.iterdir():
        if not intent_dir.is_dir():
            continue
        intent = intent_dir.name
        docs, ids, metadata = [], [], []
        for path in intent_dir.glob("**/*"):
            if path.suffix not in {".txt", ".md"} or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for j, chunk in enumerate(_chunk_text(text)):
                docs.append(chunk)
                chunk_id = f"{path.stem}_{j}"
                ids.append(chunk_id)
                # Store metadata about the source file
                metadata.append({
                    "source_file": str(path.relative_to(KB_ROOT)),
                    "file_name": path.name,
                    "chunk_index": j,
                    "intent": intent,
                    "file_stem": path.stem
                })
        if docs:
            index.add_documents(intent, docs, ids, metadata)
            print(f"Indexed {len(docs)} chunks for {intent}")


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------

def retrieve(query: str, intent: str, k: int = 4) -> List[str]:
    """Legacy retrieve function - returns only document content."""
    return index.query(intent, query, k=k)


def retrieve_with_references(query: str, intent: str, k: int = 4) -> List[Dict[str, Any]]:
    """Enhanced retrieve function that returns documents with source references."""
    return index.query_with_references(intent, query, k=k)


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🔨 Building knowledge base index...")
    build_index()
    print("✅ Index building complete!") 