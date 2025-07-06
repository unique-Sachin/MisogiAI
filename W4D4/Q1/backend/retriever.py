from __future__ import annotations

from typing import Dict, List

from . import config
from .models import DocumentChunk
from .vector_store import SimpleVectorStore

# Helper type
Citation = Dict[str, str]


def _build_prompt(question: str, contexts: List[DocumentChunk]) -> str:
    context_text = "\n---\n".join(
        f"[Source: {c.metadata['source_path']} chunk#{c.metadata['chunk_index']}]\n{c.text}" for c in contexts
    )
    system = (
        "You are an HR onboarding assistant. Answer the employee's question using only the provided context. "
        "Cite sources inline as [chunk#]. If the answer is not in the context, respond with 'I'm not sure.'"
    )
    return f"{system}\n\nContext:\n{context_text}\n\nQuestion: {question}\nAnswer:" 