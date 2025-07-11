"""Question answering pipeline using Pinecone + GPT-4o-mini."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from openai import OpenAI  # type: ignore

from app.core.config import get_settings
from app.services.embedding import model as embedding_model
from app.services.vector.client import get_vector_client

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def answer_question(
    question: str,
    companies: Optional[List[str]] = None,
    time_range: Optional[str] = None,
    top_k: int = 5,
) -> Dict[str, object]:
    """Retrieve relevant context and generate answer using GPT-4o-mini."""
    if not openai_client:
        return {
            "answer": "OpenAI API key not configured",
            "sources": [],
            "cached": False,
        }
    
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

   
    # res = vector_client.query(vector=q_embedding.tolist(), top_k=top_k)
    # print(f'res: {res}')

    # res = vector_client.query(vector=vec, top_k=payload.top_k)
    

    # if pc_filter.get("ticker") or pc_filter.get("quarter"):
    #     results = vector_client.query(vector=q_embedding.tolist(), top_k=top_k, filter=pc_filter)
    # else:
    results = vector_client.query(vector=q_embedding.tolist(), top_k=top_k)
        # print(f'results: {results}')
    

    # Extract contexts and sources
    contexts: List[str] = []
    sources: List[str] = []
    for match in results.matches:  # type: ignore[attr-defined]
        metadata = getattr(match, "metadata", None)
        logger.debug("Match %s metadata: %s", match.id, metadata)  # type: ignore[attr-defined]
        if not metadata:
            continue

        text = metadata.get("text", "")
        contexts.append(text)
        doc_id = metadata.get("document_id")
        if not doc_id:
            # fallback to vector id prefix before ':' if present
            doc_id = str(match.id).split(":")[0]  # type: ignore[attr-defined]
        sources.append(str(doc_id))

    prompt = _build_prompt(question, contexts)

    completion = openai_client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = completion.choices[0].message.content  # type: ignore[index]

    return {
        "answer": str(answer) if answer else "",
        "sources": sources,
        "cached": False,  # caching layer TBD
    }


def _build_prompt(question: str, contexts: List[str]) -> str:
    context_text = "\n\n".join(contexts)
    return (
        "You are a financial analysis assistant. Using the following context, answer the question.\n\n"
        f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer:"
    ) 