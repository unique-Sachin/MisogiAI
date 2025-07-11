"""Document parsing utilities (PDF, HTML, plain text)."""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Tuple

from bs4 import BeautifulSoup  # type: ignore
from pdfminer.high_level import extract_text  # type: ignore

logger = logging.getLogger(__name__)


def parse_document(file_path: Path, content_type: str | None = None) -> Tuple[str, str]:
    """Parse a document and return (text, detected_type)."""
    if content_type is None:
        content_type = _detect_content_type(file_path)

    try:
        if content_type == "application/pdf":
            text = extract_text(str(file_path))
        elif content_type in {"text/html", "application/xhtml+xml"}:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")
                text = soup.get_text(" ", strip=True)
        else:
            # Assume utf-8 text
            text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to parse document %s: %s", file_path, exc)
        text = ""

    return text, content_type


def _detect_content_type(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix in {".html", ".htm"}:
        return "text/html"
    return "text/plain" 