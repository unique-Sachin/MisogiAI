"""Intent classifier using few-shot prompt with LLMRouter."""
from __future__ import annotations

import json
import re
from typing import Literal

from app.llm_router import LLMRouter

router = LLMRouter()

TIntent = Literal["technical", "billing", "feature_request"]

_FEW_SHOT_PROMPT = """You are an intent classification assistant. Classify the USER query into one of the intents below. Respond ONLY with a JSON object in the form {{\"intent\": \"<intent>\"}}.

Available intents:
- technical           → Technical Support
- billing             → Billing/Account Issues
- feature_request     → Feature Requests

Examples:
User: "How do I reset my password?"
Assistant: {{"intent": "technical"}}

User: "Can you add dark mode?"
Assistant: {{"intent": "feature_request"}}

User: "Why was I charged twice?"
Assistant: {{"intent": "billing"}}

Now classify the following query:
USER: \"{query}\"
Assistant:
"""  # noqa: E501


_JSON_RE = re.compile(r"\{.*}\s*", re.S)


def classify_intent(query: str) -> TIntent:
    prompt = _FEW_SHOT_PROMPT.format(query=query)
    result_text = "".join(router.generate(prompt, stream=False))

    match = _JSON_RE.search(result_text)
    if match:
        try:
            payload = json.loads(match.group())
            intent = payload.get("intent", "").lower()
            if intent in ("technical", "billing", "feature_request"):
                return intent  # type: ignore[return-value]
        except Exception:
            pass
    # Fallback: default to technical
    return "technical"  # type: ignore[return-value] 