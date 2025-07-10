"""LLM Router: routes prompts to local Ollama Llama 3 model with fallback to OpenAI GPT-4o-mini.

Environment variables:
    OPENAI_API_KEY          – required for OpenAI fallback
    OPENAI_MODEL            – default: "gpt-4o-mini"
    OLLAMA_URL              – default: "http://localhost:11434"
    OLLAMA_MODEL            – default: "llama3:8b"
    OLLAMA_TIMEOUT          – seconds before triggering fallback (default 10)
"""
from __future__ import annotations

import json
import os
import sys
from typing import Generator, Iterable

import requests
import openai

# ---------------------------------------------------------------------------
# Configuration via env vars
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "10"))


if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


class LLMRouter:
    """Send prompt to Ollama; on failure fall back to OpenAI."""

    def generate(self, prompt: str, stream: bool = False, force_openai: bool = False) -> Iterable[str]:
        """Yield tokens/strings of the model response.

        Args:
            prompt: Full prompt to send.
            stream: Whether to stream tokens as they arrive.
            force_openai: If True, skip Ollama and use OpenAI directly.
        """
        # If force_openai is True, skip Ollama entirely
        if force_openai:
            if not OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY env var not set – required for OpenAI.")
            yield from self._generate_openai(prompt, stream=stream)
            return

        # Try local model first.
        try:
            yield from self._generate_ollama(prompt, stream=stream)
            return  # success – don't fall back
        except Exception as exc:  # pragma: no cover – fallback path
            print(f"[LLMRouter] Ollama failed → {exc}. Falling back to OpenAI.", file=sys.stderr)

        # Fallback to OpenAI
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY env var not set – required for fallback.")
        yield from self._generate_openai(prompt, stream=stream)

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _generate_ollama(self, prompt: str, *, stream: bool) -> Generator[str, None, None]:
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": stream}
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=OLLAMA_TIMEOUT, stream=stream)
        resp.raise_for_status()

        if stream:
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode())
                token = data.get("response", "")
                if token:
                    yield token
        else:
            data = resp.json()
            text = data.get("response", "")
            if not text:
                raise RuntimeError("Empty response from Ollama")
            yield text

    def _generate_openai(self, prompt: str, *, stream: bool) -> Generator[str, None, None]:
        kwargs = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
        }
        if stream:
            for chunk in openai.chat.completions.create(**kwargs):
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta
        else:
            resp = openai.chat.completions.create(**kwargs)
            yield resp.choices[0].message.content 