# Add parent directory to Python path so we can import from app/
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.llm_router import LLMRouter


class StubRouter(LLMRouter):
    """Subclass LLMRouter to allow monkeypatching of internal methods."""

    pass


def test_llm_router_fallback_to_openai(monkeypatch):
    """LLMRouter should fall back to OpenAI when Ollama fails."""
    router = StubRouter()

    # 1. Force _generate_ollama to raise an error to trigger fallback.
    def raise_ollama(prompt: str, stream: bool):  # noqa: D401
        raise RuntimeError("Ollama unavailable")

    monkeypatch.setattr(router, "_generate_ollama", raise_ollama, raising=True)

    # 2. Replace _generate_openai with a stub returning deterministic text.
    def fake_openai(prompt: str, stream: bool):  # noqa: D401
        yield "Hello from OpenAI"

    monkeypatch.setattr(router, "_generate_openai", fake_openai, raising=True)

    # 3. Ensure OPENAI_API_KEY is present so fallback path is allowed.
    monkeypatch.setattr("app.llm_router.OPENAI_API_KEY", "dummy", raising=False)

    tokens = list(router.generate("Hi", stream=False))

    assert tokens == ["Hello from OpenAI"] 