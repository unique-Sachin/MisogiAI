from app import retriever


class StubIndexWithReferences:
    """Stubbed EmbeddingIndex that returns canned documents with references."""

    def query(self, collection: str, query_text: str, k: int = 4):
        # Return predictable docs irrespective of input
        return [f"doc_{i}" for i in range(k)]

    def query_with_references(self, collection: str, query_text: str, k: int = 4):
        # Return predictable docs with metadata
        return [
            {
                "content": f"doc_{i}",
                "id": f"test_file_{i}",
                "metadata": {
                    "source_file": f"technical/test_file_{i}.txt",
                    "file_name": f"test_file_{i}.txt",
                    "chunk_index": i,
                    "intent": "technical",
                    "file_stem": f"test_file_{i}"
                },
                "distance": 0.1 * i
            }
            for i in range(k)
        ]


def test_retrieve_with_references(monkeypatch):
    """retrieve_with_references should return documents with source metadata."""
    # Swap the real index with a stub instance
    monkeypatch.setattr(retriever, "index", StubIndexWithReferences(), raising=True)

    results = retriever.retrieve_with_references("dummy query", intent="technical", k=2)

    assert len(results) == 2
    assert results[0]["content"] == "doc_0"
    assert results[0]["metadata"]["source_file"] == "technical/test_file_0.txt"
    assert results[0]["metadata"]["chunk_index"] == 0
    assert results[0]["distance"] == 0.0

    assert results[1]["content"] == "doc_1"
    assert results[1]["metadata"]["source_file"] == "technical/test_file_1.txt"
    assert results[1]["metadata"]["chunk_index"] == 1
    assert results[1]["distance"] == 0.1


def test_retrieve_legacy_still_works(monkeypatch):
    """Legacy retrieve function should still work for backward compatibility."""
    # Swap the real index with a stub instance
    monkeypatch.setattr(retriever, "index", StubIndexWithReferences(), raising=True)

    docs = retriever.retrieve("dummy query", intent="technical", k=3)

    assert docs == ["doc_0", "doc_1", "doc_2"] 