"""Pipeline evaluation on test set producing CSV report."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd
from sklearn.metrics import accuracy_score

from app.intent_classifier import classify_intent
from app.retriever import retrieve
from app.llm_router import LLMRouter

router = LLMRouter()


def _load_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else []


def evaluate(test_path: str = "data/test_queries.json", gold_path: str = "data/gold_responses.json") -> None:
    tests = _load_json(Path(test_path))
    gold = {item["query"]: item["response"] for item in _load_json(Path(gold_path))}

    true_intents, pred_intents, util_scores, latencies, responses = [], [], [], [], []

    for sample in tests:
        query = sample["query"]
        true_intents.append(sample["intent"])

        pred_intent = classify_intent(query)
        pred_intents.append(pred_intent)

        context_chunks = retrieve(query, pred_intent)
        prompt = "\n".join(context_chunks) + "\n\nUser: " + query

        # Simple non-streaming call for metric consistency
        reply = "".join(router.generate(prompt, stream=False))
        responses.append(reply)

        # Context-utilization heuristic
        matches = sum(1 for chunk in context_chunks if chunk[:60] in reply)
        util_scores.append(matches / len(context_chunks) if context_chunks else 0)

        latencies.append(None)  # placeholder, could time per request

    df = pd.DataFrame(
        {
            "query": [t["query"] for t in tests],
            "intent_true": true_intents,
            "intent_pred": pred_intents,
            "context_utilization": util_scores,
            "response": responses,
        }
    )

    Path("reports").mkdir(exist_ok=True)
    df.to_csv("reports/evaluation_results.csv", index=False)

    print("Intent accuracy:", accuracy_score(true_intents, pred_intents)) 