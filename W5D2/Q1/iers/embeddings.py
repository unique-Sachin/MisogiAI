from functools import lru_cache
from sentence_transformers import SentenceTransformer
from .config import settings

@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer(settings.EMBEDDING_MODEL)

def embed(texts):
    model = _model()
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False) 