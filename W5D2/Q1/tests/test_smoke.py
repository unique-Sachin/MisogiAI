import importlib
import sys, types
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Global stub of sentence_transformers to prevent heavy import
fake_st = types.ModuleType("sentence_transformers")
class _DummyModel:
    def encode(self, texts, convert_to_numpy=True, show_progress_bar=False):
        import numpy as np
        return np.zeros((len(texts), 384), dtype='float32')
fake_st.SentenceTransformer = lambda name: _DummyModel()
sys.modules.setdefault("sentence_transformers", fake_st)

# Stub google modules to avoid heavy deps
google_pkg = types.ModuleType("google")
sys.modules.setdefault("google", google_pkg)

google_auth = types.ModuleType("google.auth")
google_pkg.auth = google_auth
sys.modules["google.auth"] = google_auth

google_auth_transport = types.ModuleType("google.auth.transport")
google_auth.transport = google_auth_transport
sys.modules["google.auth.transport"] = google_auth_transport

google_auth_transport_requests = types.ModuleType("google.auth.transport.requests")
def _dummy_request(*args, **kwargs):
    pass
google_auth_transport_requests.Request = _dummy_request
google_auth_transport.requests = google_auth_transport_requests
sys.modules["google.auth.transport.requests"] = google_auth_transport_requests

google_oauth2_credentials = types.ModuleType("google.oauth2.credentials")
google_pkg.oauth2 = types.ModuleType("google.oauth2")
google_pkg.oauth2.credentials = google_oauth2_credentials
sys.modules["google.oauth2" ] = google_pkg.oauth2
google_pkg.oauth2.credentials = google_oauth2_credentials
sys.modules["google.oauth2.credentials"] = google_oauth2_credentials
google_oauth2_credentials.Credentials = type("_DummyCred", (), {})

google_auth_oauthlib_flow = types.ModuleType("google_auth_oauthlib.flow")
google_auth_oauthlib_flow.InstalledAppFlow = types.SimpleNamespace(from_client_secrets_file=lambda *a, **k: types.SimpleNamespace(run_local_server=lambda port: None))
sys.modules["google_auth_oauthlib.flow"] = google_auth_oauthlib_flow

googleapiclient_discovery = types.ModuleType("googleapiclient.discovery")
googleapiclient_discovery.build = lambda *args, **kwargs: types.SimpleNamespace(users=lambda: types.SimpleNamespace(messages=lambda: types.SimpleNamespace(list=lambda *a, **k: types.SimpleNamespace(execute=lambda: {}))))
sys.modules["googleapiclient.discovery"] = googleapiclient_discovery

# Stub redis module
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules["redis"].from_url = lambda *a, **k: types.SimpleNamespace(get=lambda k: None, set=lambda *a, **k: None)

sys.modules.setdefault("openai", types.ModuleType("openai"))
sys.modules["openai"].OpenAI = lambda api_key=None: types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda *a, **k: types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="OK"))]))))

sys.modules.setdefault("tenacity", types.ModuleType("tenacity"))
sys.modules["tenacity"].retry = lambda *a, **k: (lambda f: f)
sys.modules["tenacity"].wait_exponential = lambda *a, **k: None
sys.modules["tenacity"].stop_after_attempt = lambda *a, **k: None

sys.modules.setdefault("chromadb", types.ModuleType("chromadb"))
chromadb_persistent = types.ModuleType("chromadb.PersistentClient")
class _FakeClient:
    def __init__(self, path=None):
        self.collections = {}
    def get_or_create_collection(self, name, embedding_function):
        coll = self.collections.get(name)
        if not coll:
            coll = types.SimpleNamespace(
                add=lambda ids, documents, metadatas: None,
                query=lambda query_texts, n_results: {"documents": [["policy"*10]], "distances": [[0.1]], "metadatas": [[{}]]},
                count=lambda: 0,
            )
            self.collections[name] = coll
        return coll
chromadb_persistent.PersistentClient = _FakeClient
sys.modules["chromadb"] = types.ModuleType("chromadb")
sys.modules["chromadb"].PersistentClient = _FakeClient
sys.modules["chromadb.utils"] = types.ModuleType("chromadb.utils")
sys.modules["chromadb.utils"].embedding_functions = types.ModuleType("chromadb.utils.embedding_functions")


def test_health():
    main = importlib.import_module("main")
    assert main.health() == {"status": "ok"}


def test_config_defaults():
    from iers.config import settings
    assert settings.BATCH_SIZE == 10
    assert settings.EMBEDDING_MODEL


def test_vector_index_in_memory(monkeypatch):
    import importlib
    # Provide fake faiss before importing VectorIndex
    import sys, types, numpy as np

    fake_faiss = types.ModuleType("faiss")
    class _FakeIndex:
        def __init__(self, dim):
            self.vectors = []
            self.dim = dim
        def add(self, vecs):
            self.vectors.extend(vecs)
        def search(self, vec, k):
            n = len(self.vectors)
            indices = np.arange(n)[:k]
            dists = np.zeros_like(indices, dtype='float32')
            return np.array([dists]), np.array([indices])
    fake_faiss.IndexFlatL2 = _FakeIndex
    fake_faiss.write_index = lambda *args, **kwargs: None
    fake_faiss.read_index = lambda path: _FakeIndex(384)
    sys.modules["faiss"] = fake_faiss

    from iers.vector_index import VectorIndex, embed as true_embed

    # Patch embed to return deterministic small vectors without heavy model
    def fake_embed(texts):
        # simple hash-based embedding
        return np.array([[float(sum(map(ord, t)) % 1000) for _ in range(384)] for t in texts], dtype='float32')

    monkeypatch.setattr("iers.vector_index.embed", fake_embed)

    idx = VectorIndex()
    idx.add_texts(["policy one", "policy two"], ["doc1", "doc2"])
    results = idx.search("policy", k=1)
    assert results 