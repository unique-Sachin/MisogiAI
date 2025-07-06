from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DocumentChunk:
    """A chunk of text derived from a document along with metadata."""
    id: str
    text: str
    metadata: Dict[str, str]

@dataclass
class QueryLog:
    query: str
    answer: str
    citations: List[Dict[str, str]]
    category: str 