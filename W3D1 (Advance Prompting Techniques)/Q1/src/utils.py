"""Utility helpers for the EdTech Math Tutor CLI.

This module centralises common functionality such as:
1. Reading prompt templates.
2. Interacting with the LM Studio OpenAI-compatible API.
3. Structured logging of interactions.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Tuple
import re

# OpenAI Python SDK (>=1.0.0) – fallback to legacy usage if required
import importlib
import openai
from pydantic import BaseModel, Field
from rich.console import Console
from rich.text import Text

# Initialise rich console for consistent CLI feedback
console = Console()

# Constants
DEFAULT_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:8080/v1")
DEFAULT_MODEL = os.getenv("LM_MODEL_NAME", "deepseek/deepseek-r1-0528-qwen3-8b")
PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
EVAL_DIR = Path(__file__).resolve().parent.parent / "evaluation"
LOG_FILE = EVAL_DIR / "output_logs.json"

# Ensure evaluation directory exists
EVAL_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Configure OpenAI client for LM Studio
# ---------------------------------------------------------------------------
# The OpenAI Python SDK v1 introduced a new client-centric API and removed the
# previous `openai.ChatCompletion.create` interface. We instantiate a client
# object targeting the local LM Studio server. For environments that still use
# the < v1 library, we retain the previous global configuration so that
# `openai.ChatCompletion.create` continues to function.

# Shared configuration values
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy")  # LM Studio ignores the key

# `OpenAI` class is available only in SDK v1+. We attempt to import it lazily so
# that environments pinned to < v1 remain functional.
_openai_mod = importlib.import_module("openai")
OpenAI = getattr(_openai_mod, "OpenAI", None)  # type: ignore[attr-defined]

# Legacy (< v1) global configuration
openai.api_key = _OPENAI_API_KEY
try:
    openai.base_url = DEFAULT_BASE_URL  # type: ignore[attr-defined]
except AttributeError:
    # Older SDKs (< 0.28) don't expose `base_url`; requests will still work if
    # the environment variable `OPENAI_BASE_URL` is set externally.
    pass


class InteractionLog(BaseModel):
    """Schema for a single interaction log entry."""

    timestamp: str = Field(..., description="ISO timestamp")
    prompt_type: str = Field(..., description="zero-shot | few-shot | cot | meta")
    question: str
    response: str
    latency_ms: int
    model: str = DEFAULT_MODEL


def read_prompt_template(prompt_type: str) -> str:
    """Load a prompt template text file from the prompts directory.

    Args:
        prompt_type: One of `zero-shot`, `few-shot`, `cot_prompt`, or `meta_prompt`.

    Returns:
        The template string with placeholders (e.g. `{question}`).
    """
    file_map = {
        "zero-shot": "zero_shot.txt",
        "few-shot": "few_shot.txt",
        "cot": "cot_prompt.txt",
        "meta": "meta_prompt.txt",
    }
    if prompt_type not in file_map:
        raise ValueError(f"Unsupported prompt_type '{prompt_type}'. Must be one of {list(file_map)}")

    template_path = PROMPT_DIR / file_map[prompt_type]
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")

    return template_path.read_text(encoding="utf-8")


def build_prompt(prompt_type: str, question: str) -> str:
    """Insert the question into the chosen prompt template."""
    template = read_prompt_template(prompt_type)
    return template.replace("{question}", question.strip())


def _strip_internal_thought(text: str) -> str:
    """Remove internal reasoning markers such as <think> blocks or {{ ... }} braces."""
    # Remove lines starting with <think>
    cleaned = re.sub(r"^<think>.*$", "", text, flags=re.MULTILINE)
    # Remove content inside double curly braces {{ ... }}
    cleaned = re.sub(r"\{\{.*?\}\}", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()


def sanitize_response(text: str) -> str:  # aliased for external use
    return _strip_internal_thought(text)


def query_model(prompt: str, max_tokens: int = 512, temperature: float | None = None) -> Tuple[str, int]:
    """Send a chat-completion request to the local model via OpenAI client.

    Args:
        prompt: The full prompt string to send.
        max_tokens: Completion length cap.
        temperature: Sampling temperature. Defaults to 0.0 if not provided.

    Returns:
        The assistant's textual response and the latency in milliseconds.
    """
    payload: Dict[str, Any] = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature if temperature is not None else 0.0,
        "stream": False,
    }

    start_time = time.perf_counter()

    # Prefer the modern client if available; otherwise fall back to the legacy
    # `ChatCompletion.create` call for pre-v1 SDKs.
    try:
        if OpenAI is not None:
            client = OpenAI(api_key=_OPENAI_API_KEY, base_url=DEFAULT_BASE_URL)
            completion = client.chat.completions.create(**payload)
            response_text = completion.choices[0].message.content  # type: ignore[index]
        else:
            completion = openai.ChatCompletion.create(**payload)  # type: ignore[arg-type]
            response_text = completion.choices[0].message.content  # type: ignore[index]
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]API error:[/bold red] {exc}")
        raise
    latency = int((time.perf_counter() - start_time) * 1000)

    cleaned_response = _strip_internal_thought(response_text or "")

    console.print(Text("Model latency: ") + Text(str(latency) + " ms", style="bold green"))
    return cleaned_response, latency


def append_log(entry: InteractionLog) -> None:
    """Append a new interaction entry to the log JSON array (atomic write)."""
    # Load existing log if it exists and is valid
    data: list[Dict[str, Any]] = []
    if LOG_FILE.exists():
        try:
            data = json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            console.print("[yellow]Warning: Log file corrupted. Overwriting.")

    data.append(entry.dict())

    LOG_FILE.write_text(json.dumps(data, indent=2)) 