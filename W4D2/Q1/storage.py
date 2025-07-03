import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from filelock import FileLock

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

STORAGE_FILE = DATA_DIR / "documents.json"
LOCK_FILE = STORAGE_FILE.with_suffix(".lock")

# Ensure the JSON file exists
if not STORAGE_FILE.exists():
    STORAGE_FILE.write_text("[]", encoding="utf-8")

_lock = FileLock(str(LOCK_FILE))

def _load_documents() -> List[Dict[str, Any]]:
    with _lock:
        with STORAGE_FILE.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Re-initialize corrupted file
                return []

def _save_documents(docs: List[Dict[str, Any]]) -> None:
    with _lock:
        with STORAGE_FILE.open("w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)

# Public helper functions

def add_document(doc: Dict[str, Any]) -> int:
    """Add a document and return its new id."""
    docs = _load_documents()
    next_id = (max(d["id"] for d in docs) + 1) if docs else 1
    doc["id"] = next_id
    docs.append(doc)
    _save_documents(docs)
    return next_id

def get_document(doc_id: int) -> Optional[Dict[str, Any]]:
    docs = _load_documents()
    return next((d for d in docs if d["id"] == doc_id), None)

def all_documents() -> List[Dict[str, Any]]:
    return _load_documents() 