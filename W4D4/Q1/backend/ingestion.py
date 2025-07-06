from __future__ import annotations

import os
import uuid
from typing import List

import docx # type: ignore
from pypdf import PdfReader # type: ignore
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore

from . import config
from .models import DocumentChunk

# ------------------ Text Extraction ------------------

def _extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text())
    return "\n".join(texts)

def _extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def _extract_text_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


_extractors = {
    ".pdf": _extract_text_from_pdf,
    ".docx": _extract_text_from_docx,
    ".txt": _extract_text_from_txt,
}


# ------------------ Chunking ------------------

def _split_into_chunks(text: str, size: int, overlap: int) -> List[str]:
    """Use LangChain RecursiveCharacterTextSplitter for robust chunking."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


# ------------------ Public Ingest Function ------------------

def ingest_document(file_path: str) -> List[DocumentChunk]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in _extractors:
        raise ValueError(f"Unsupported file type: {ext}")

    print(f"[Ingest] Extracting text from {file_path}")
    text = _extractors[ext](file_path)

    print("[Ingest] Splitting into chunks (LangChain)…")
    raw_chunks = _split_into_chunks(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    doc_chunks: List[DocumentChunk] = []
    for i, chunk_text in enumerate(tqdm(raw_chunks)):
        chunk_id = str(uuid.uuid4())
        metadata = {
            "source_path": os.path.basename(file_path),
            "chunk_index": str(i),
        }
        doc_chunks.append(DocumentChunk(id=chunk_id, text=chunk_text, metadata=metadata))
    return doc_chunks 