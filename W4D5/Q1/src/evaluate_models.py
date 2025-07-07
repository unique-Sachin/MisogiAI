"""Evaluate trained classifiers on the test split and write metrics JSON.

Usage:
    PYTHONPATH=src python src/evaluate_models.py --models bert sentencebert --split test

Metrics saved to reports/metrics.json in the form:
{
    "bert": {
        "accuracy": 0.9,
        "precision_macro": 0.9,
        ...
    },
    ...
}
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import joblib  # type: ignore
import numpy as np  # type: ignore
from sklearn.metrics import (  # type: ignore
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

EMBED_DIR = Path(__file__).resolve().parent.parent / "embeddings"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def load_data(model: str, split: str):
    X = np.load(EMBED_DIR / model / f"{split}.npy")
    y = np.load(EMBED_DIR / f"labels_{split}.npy", allow_pickle=True)
    return X, y


def evaluate_model(model: str, split: str) -> Dict[str, float | list | Dict[str, float]]:
    clf_path = MODEL_DIR / f"{model}.joblib"
    if not clf_path.exists():
        raise FileNotFoundError(f"Model file missing: {clf_path}")

    clf = joblib.load(clf_path)
    X, y_true = load_data(model, split)

    y_pred = clf.predict(X)
    y_prob = clf.predict_proba(X)

    acc = float(accuracy_score(y_true, y_pred))

    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    conf = confusion_matrix(y_true, y_pred).tolist()

    return {
        "accuracy": acc,
        "precision_macro": float(prec),
        "recall_macro": float(rec),
        "f1_macro": float(f1),
        "classification_report": report,
        "confusion_matrix": conf,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=["bert", "sentencebert"], help="Models to evaluate")
    parser.add_argument("--split", default="test", help="Dataset split to evaluate on")
    args = parser.parse_args()

    metrics: Dict[str, dict] = {}
    for model in args.models:
        print(f"Evaluating {model}…")
        try:
            metrics[model] = evaluate_model(model, args.split)
        except FileNotFoundError as e:
            print("Skipping", model, "->", e)

    out_path = REPORT_DIR / "metrics.json"
    with out_path.open("w") as f:
        json.dump(metrics, f, indent=2)
    print("Saved", out_path)


if __name__ == "__main__":
    main() 