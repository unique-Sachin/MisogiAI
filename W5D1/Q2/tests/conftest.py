"""Global test configuration – stub heavy external dependencies (openai, chromadb, etc.)."""

import sys
import types
from types import SimpleNamespace

# ---------------------------------------------------------------------------
# Stub `openai` to avoid installing the real package (heavy, requires network)
# ---------------------------------------------------------------------------
openai_stub = types.ModuleType("openai")
openai_stub.api_key = None  # type: ignore[attr-defined]

# Minimal chat/completions interface used in LLMRouter fallback path
class _DummyChatCompletions:  # noqa: D401
    @staticmethod
    def create(*args, **kwargs):  # noqa: D401
        # Return a structure mimicking the OpenAI SDK response
        choice = SimpleNamespace(
            delta=SimpleNamespace(content="dummy"),
            message=SimpleNamespace(content="dummy"),
        )
        return SimpleNamespace(choices=[choice])

openai_stub.chat = SimpleNamespace(completions=_DummyChatCompletions)  # type: ignore[attr-defined]

sys.modules["openai"] = openai_stub

# ---------------------------------------------------------------------------
# Stub `chromadb` with minimal API surface used by EmbeddingIndex
# ---------------------------------------------------------------------------
chromadb_stub = types.ModuleType("chromadb")

class _DummyCollection:  # noqa: D401
    def add(self, ids, embeddings, documents):  # noqa: D401
        pass

    def query(self, query_embeddings, n_results):  # noqa: D401
        # Return empty lists for documents so downstream code can handle gracefully
        return {"documents": [[]]}

class _DummyPersistentClient:  # noqa: D401
    def __init__(self, *args, **kwargs):  # noqa: D401
        pass

    def get_or_create_collection(self, name):  # noqa: D401
        return _DummyCollection()

chromadb_stub.PersistentClient = _DummyPersistentClient  # type: ignore[attr-defined]

sys.modules["chromadb"] = chromadb_stub

# ---------------------------------------------------------------------------
# Stub `sentence_transformers` to avoid heavy ML model download
# ---------------------------------------------------------------------------
sentence_transformers_stub = types.ModuleType("sentence_transformers")

class _DummySentenceTransformer:  # noqa: D401
    def __init__(self, *args, **kwargs):  # noqa: D401
        pass

    def encode(self, docs):  # noqa: D401
        # Return deterministic zero vectors of length 768
        return [[0.0] * 768 for _ in docs]

sentence_transformers_stub.SentenceTransformer = _DummySentenceTransformer  # type: ignore[attr-defined]
sys.modules["sentence_transformers"] = sentence_transformers_stub 