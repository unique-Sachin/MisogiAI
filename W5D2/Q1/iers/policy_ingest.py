import argparse, os, glob
from pathlib import Path
from typing import List

from .chroma_store import ChromaStore

SUPPORTED_EXTS = {".md", ".txt"}

def _read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            import pdfminer.high_level as pdf_high  # type: ignore
            return pdf_high.extract_text(str(path))
        except Exception:
            raise RuntimeError("pdfminer.six required for PDF ingestion. pip install pdfminer.six")
    return path.read_text(encoding="utf-8", errors="ignore")


def ingest(directory: str):
    store = ChromaStore()
    paths = [p for p in Path(directory).rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
    if not paths:
        print("No supported documents found.")
        return

    docs: List[str] = []
    metas: List[dict] = []
    for p in paths:
        text = _read_file(p)
        docs.append(text)
        metas.append({"path": str(p), "department": p.parent.name.lower()})

    store.add_texts(docs, metas)
    print(f"Ingested {len(docs)} documents into Chroma.")


def main():
    parser = argparse.ArgumentParser(description="Ingest policy documents into Chroma DB")
    parser.add_argument("--dir", required=True, help="Directory containing policy docs")
    args = parser.parse_args()
    ingest(args.dir)

if __name__ == "__main__":
    main() 