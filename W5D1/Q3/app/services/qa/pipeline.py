"""Question answering pipeline using Pinecone + GPT-4o-mini."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

import openai  # type: ignore

from app.core.config import get_settings
from app.services.embedding import model as embedding_model
from app.services.vector.client import get_vector_client
from app.services.cache.client import get_cache_client

logger = logging.getLogger(__name__)
settings = get_settings()

if settings.openai_api_key:
    openai.api_key = settings.openai_api_key


def answer_question(
    question: str,
    companies: Optional[List[str]] = None,
    time_range: Optional[str] = None,
    top_k: int = 5,
) -> Dict[str, object]:
    """Retrieve relevant context and generate answer using GPT-4o-mini."""
    cache = get_cache_client()

    cache_key = cache.build_query_key(question, companies, time_range)
    cached_val = cache.get(cache_key)
    if cached_val:
        logger.info("Cache hit for query")
        return {**cached_val, "cached": True}

    vector_client = get_vector_client()

    # Encode question
    q_embedding = embedding_model.encode([question])[0]

    # Build filter based on companies/time_range if provided (placeholder)
    pc_filter = {}
    if companies:
        pc_filter["ticker"] = {"$in": companies}
    if time_range:
        pc_filter["quarter"] = time_range  # simplistic

    # Query Pinecone
    results = vector_client.query(vector=q_embedding.tolist(), top_k=top_k, filter=pc_filter if pc_filter else None)

    # Extract contexts and sources
    contexts: List[str] = []
    sources: List[str] = []
    for match in results.matches:  # type: ignore[attr-defined]
        metadata = match.metadata  # type: ignore[attr-defined]
        text = metadata.get("text", "") if metadata else ""
        contexts.append(text)
        if metadata:
            sources.append(metadata.get("document_id", ""))

    prompt = _build_prompt(question, contexts)

    completion = openai.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = completion.choices[0].message.content  # type: ignore[index]

    result = {
        "answer": answer,
        "sources": sources,
    }

    # Determine TTL
    ttl = settings.ttl_historical
    if time_range is None:
        ttl = settings.ttl_realtime

    cache.set(cache_key, result, ttl)

    result["cached"] = False
    return result


def _build_prompt(question: str, contexts: List[str]) -> str:
    context_text = "\n\n".join(contexts)
    return (
        "You are a financial analysis assistant. Using the following context, answer the question.\n\n"
        f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer:"
    ) 