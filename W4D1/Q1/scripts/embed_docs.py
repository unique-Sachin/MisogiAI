"""Script: embed_docs.py

1. Downloads or loads local MCP documentation (markdown/pdf)
2. Chunks the text using LangChain loaders & text splitters
3. Generates embeddings via OpenAI
4. Upserts vectors into a Pinecone index

This is a skeleton; fill in the TODOs as implementation proceeds.
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv


"""Handle LangChain >=0.2.x (new split packages) and fallback to older paths."""

# 1. Try the new package names first
try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader  # type: ignore
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
    from langchain_openai import OpenAIEmbeddings  # type: ignore
except ImportError:
    # 2. Fallback to pre-0.2 import paths
    try:
        from langchain.document_loaders import PyPDFLoader, TextLoader  # type: ignore
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
        from langchain.embeddings import OpenAIEmbeddings  # type: ignore
    except ImportError:
        PyPDFLoader = TextLoader = RecursiveCharacterTextSplitter = OpenAIEmbeddings = None  # type: ignore

# Pinecone import (optional)
try:
    import pinecone  # type: ignore
except ImportError:  # pragma: no cover
    pinecone = None  # type: ignore

DOCS_PATH = Path("data/mcp_docs")

# 👉 Fill this list with publicly available MCP documentation URLs
SOURCE_URLS = [
    # Example placeholders (replace with real links)
    "https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/CONTRIBUTING.md",
    "https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/CODE_OF_CONDUCT.md",
    # "/Users/sachinmishra/Documents/MISOGI/W4D1/Q1/scripts/MCP.pdf"
    
]

# Ensure docs directory exists
DOCS_PATH.mkdir(parents=True, exist_ok=True)


def fetch_documents(urls: list[str]) -> None:
    """Download documents from URLs into DOCS_PATH if not already present."""
    import mimetypes
    import requests
    from tqdm import tqdm

    for url in tqdm(urls, desc="Downloading MCP docs"):
        filename = url.split("/")[-1]
        target = DOCS_PATH / filename
        if target.exists():
            continue
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"⚠️  Failed to download {url}: {resp.status_code}")
            continue

        # Infer extension if missing
        if "." not in filename:
            ext = mimetypes.guess_extension(resp.headers.get("content-type", "")) or ".md"
            filename += ext
            target = DOCS_PATH / filename

        with open(target, "wb") as f:
            f.write(resp.content)
        print(f"✓ Saved {filename}")


def load_documents() -> List[str]:
    """Load raw text of MCP docs from DOCS_PATH. Extend as needed."""
    texts: List[str] = []
    for file_path in DOCS_PATH.rglob("*"):
        if file_path.suffix.lower() == ".pdf" and PyPDFLoader is not None:
            loader = PyPDFLoader(str(file_path))
            texts.extend([page.page_content for page in loader.load()])
        elif file_path.suffix.lower() in {".md", ".txt"} and TextLoader is not None:
            loader = TextLoader(str(file_path))
            texts.append(loader.load()[0].page_content)
    return texts


def main():
    load_dotenv()

    if any(v is None for v in (RecursiveCharacterTextSplitter, OpenAIEmbeddings, pinecone)):
        raise ImportError("Please install langchain, openai, and pinecone-client packages first.")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = os.getenv("PINECONE_ENV")
    index_name = os.getenv("INDEX_NAME")


    if not all([openai_api_key, pinecone_api_key, pinecone_env, index_name]):
        raise RuntimeError("Missing one or more required environment variables.")

    # 1. Load documents
    fetch_documents(SOURCE_URLS)

    raw_texts = load_documents()
    if not raw_texts:
        raise FileNotFoundError(
            f"No documents found in {DOCS_PATH}. Please add docs manually or update SOURCE_URLS."
        )

    # 2. Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # type: ignore[operator]
    docs = splitter.create_documents(raw_texts)

    # 3. Generate embeddings
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)  # type: ignore[operator]

    # 4. Initialize Pinecone (v3 client)
    try:
        from pinecone import Pinecone, ServerlessSpec  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("pinecone-client>=3 is required. Run `pip install pinecone-client --upgrade`." ) from exc

    pc = Pinecone(api_key=pinecone_api_key)

    # Create index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        # Attempt to infer cloud provider from env string, fallback to 'aws'
        # _env = pinecone_env or ""
        # cloud = "gcp" if "gcp" in _env else "aws"
        # region = _env.replace("-gcp", "").replace("-aws", "")

        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="dotproduct",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)

    # 5. Upsert
    batch = []
    for i, doc in enumerate(docs):
        metadata = {"source": doc.metadata.get("source", "unknown"), "chunk": i}
        batch.append((f"doc-{i}", embeddings.embed_query(doc.page_content), metadata))
        # upsert in batches of 100
        if len(batch) == 100:
            index.upsert(batch)
            batch = []
    if batch:
        index.upsert(batch)

    print("✅ Finished embedding and uploading documents to Pinecone.")


if __name__ == "__main__":
    main() 