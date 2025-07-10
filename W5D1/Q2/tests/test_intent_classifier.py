from app.intent_classifier import classify_intent


class DummyRouter:
    """Stub LLM router that returns a canned JSON payload."""

    def generate(self, prompt: str, stream: bool = False):  # noqa: D401
        # Always return a valid JSON payload for technical intent
        return ['{"intent": "technical"}']


def test_classify_intent_parses_json(monkeypatch):
    """classify_intent should correctly parse the intent from the router response."""
    # Patch the router inside the module with our dummy implementation
    monkeypatch.setattr(
        "app.intent_classifier.router",
        DummyRouter(),
        raising=True,
    )

    intent = classify_intent("How do I reset my password?")
    assert intent == "technical"


def test_classify_intent_fallback(monkeypatch):
    """If the router returns an invalid response classify_intent falls back to technical."""

    class BadRouter:  # noqa: D401
        def generate(self, prompt: str, stream: bool = False):
            return ["not-a-json-response"]

    monkeypatch.setattr("app.intent_classifier.router", BadRouter(), raising=True)

    intent = classify_intent("Some strange query")
    # Should fall back to technical when parsing fails
    assert intent == "technical" 