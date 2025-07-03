from typing import List, Dict

from .storage import all_documents

SNIPPET_RADIUS = 40  # characters around match

def search_documents(query: str) -> List[Dict]:
    """Return list of {id, title, matched_snippet}. Case-insensitive substring search."""
    if not query:
        return []
    results = []
    q_lower = query.lower()
    for doc in all_documents():
        content_lower = doc.get("content", "").lower()
        idx = content_lower.find(q_lower)
        if idx != -1:
            start = max(0, idx - SNIPPET_RADIUS)
            end = idx + len(query) + SNIPPET_RADIUS
            snippet = doc["content"][start:end].replace("\n", " ")
            results.append({
                "id": doc["id"],
                "title": doc.get("title", ""),
                "matched_snippet": snippet.strip()
            })
    return results 