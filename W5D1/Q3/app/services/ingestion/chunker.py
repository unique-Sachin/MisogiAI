"""Simple text chunking utilities."""
from __future__ import annotations

from typing import List


def chunk_text(text: str, max_length: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks.

    Args:
        text: The input text to chunk.
        max_length: Maximum characters per chunk.
        overlap: Overlap characters between chunks.

    Returns:
        List of text chunks.
    """
    if max_length <= overlap:
        raise ValueError("max_length must be greater than overlap")

    chunks: List[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_length, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += max_length - overlap

    return chunks 