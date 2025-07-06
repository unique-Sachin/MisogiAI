import os

# Vector store persistence location
VECTOR_STORE_PATH = os.environ.get("VECTOR_STORE_PATH", "vector_store")

# OpenAI settings (can be swapped by changing provider implementation)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
COMPLETION_MODEL = os.environ.get("COMPLETION_MODEL", "gpt-4o-mini")

# Retrieval / generation parameters
top_k_default = os.environ.get("TOP_K", "4")
TOP_K = int(top_k_default) if top_k_default.isdigit() else 4
max_tokens_default = os.environ.get("MAX_TOKENS", "256")
MAX_TOKENS = int(max_tokens_default) if max_tokens_default.isdigit() else 256

# Chunking
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "50")) 