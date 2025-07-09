import os
from typing import List

from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class CustomSentenceTransformerEmbeddings(Embeddings):
    """Thin wrapper around SentenceTransformer to comply with LangChain's Embeddings interface."""

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist() 