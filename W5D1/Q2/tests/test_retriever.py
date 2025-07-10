from app import retriever


class StubIndex:
    """Stubbed EmbeddingIndex that returns canned documents."""

    def query(self, collection: str, query_text: str, k: int = 4):  # noqa: D401
        # Return predictable docs irrespective of input
        return [f"doc_{i}" for i in range(k)]


def test_retrieve_uses_index(monkeypatch):
    """retrieve should delegate to the EmbeddingIndex query and return its result."""
    # Swap the real index with a stub instance
    monkeypatch.setattr(retriever, "index", StubIndex(), raising=True)

    docs = retriever.retrieve("dummy query", intent="technical", k=3)

    assert docs == ["doc_0", "doc_1", "doc_2"] 