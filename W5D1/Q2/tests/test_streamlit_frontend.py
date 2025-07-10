import pytest

# Skip this suite entirely if the experimental Streamlit testing API is not available
streamlit_test = pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest


# ---------------------------------------------------------------------------
# Helper stubs to isolate the frontend from external services
# ---------------------------------------------------------------------------


def _patch_business_logic(monkeypatch):
    """Replace heavy backend calls with lightweight stubs for testing."""

    # Stub the intent classifier → always returns "technical"
    monkeypatch.setattr(
        "app.intent_classifier.classify_intent",
        lambda query: "technical",
        raising=True,
    )

    # Stub the retriever → deterministic static context chunks
    monkeypatch.setattr(
        "app.retriever.retrieve",
        lambda query, intent, k: [f"Context chunk {i}" for i in range(1, k + 1)],
        raising=True,
    )

    # Stub the LLMRouter so that it does not make network calls
    class _DummyRouter:
        def generate(self, prompt: str, stream: bool = True):  # noqa: D401
            text = "Hello, this is a canned response."
            if stream:
                for token in text:
                    yield token
            else:
                yield text

    monkeypatch.setattr("app.llm_router.LLMRouter", lambda: _DummyRouter(), raising=True)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_full_chat_flow(monkeypatch):
    """Simulate a user sending a prompt and verify UI reacts as expected."""

    _patch_business_logic(monkeypatch)

    # Launch the app under test
    at = AppTest.from_file("ui/streamlit_app.py")

    # Initial render to create widgets
    at.run()

    # Simulate user typing a question in the chat input
    chat_widget = at.chat_input  # type: ignore[attr-defined]
    chat_widget.input("How do I reset my password?")  # type: ignore[attr-defined]
    at.run()

    # Verify that the detected intent markdown was rendered
    assert any("Detected intent:" in md.value for md in at.markdown)

    # Verify that the canned response from the dummy router appears
    assert any("canned response" in md.value.lower() for md in at.markdown) 