"""Train Logistic Regression classifiers for each embedding model.

Usage:
    PYTHONPATH=src python src/train_models.py --models bert sentencebert --val_split val

Embeddings should exist under embeddings/{model}/{split}.npy.
Trained models are saved to models/{model}.joblib.
Evaluation metrics printed to stdout.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib  # type: ignore
import numpy as np  # type: ignore
from sklearn.linear_model import LogisticRegression  # type: ignore
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix  # type: ignore

EMBED_DIR = Path(__file__).resolve().parent.parent / "embeddings"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

SPLITS = ["train", "val"]


def load_data(model_name: str, split: str):
    X_path = EMBED_DIR / model_name / f"{split}.npy"
    y_path = EMBED_DIR / f"labels_{split}.npy"
    if not X_path.exists():
        raise FileNotFoundError(f"Embeddings not found: {X_path}")
    X = np.load(X_path)
    y = np.load(y_path, allow_pickle=True)
    return X, y


def train_and_eval(model_name: str, val_split: str = "val") -> None:
    print(f"\n=== Training Logistic Regression for {model_name} ===")
    try:
        X_train, y_train = load_data(model_name, "train")
    except FileNotFoundError:
        print("Train embeddings missing – using", val_split, "split for both training and evaluation.")
        X_train, y_train = load_data(model_name, val_split)
    X_val, y_val = load_data(model_name, val_split)

    clf = LogisticRegression(
        max_iter=2000,
        multi_class="multinomial",
        solver="lbfgs",
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    preds = clf.predict(X_val)
    acc = accuracy_score(y_val, preds)
    print(f"Validation accuracy: {acc:.4f}")
    print(classification_report(y_val, preds))
    print("Confusion matrix:\n", confusion_matrix(y_val, preds))

    # Save model
    out_path = MODEL_DIR / f"{model_name}.joblib"
    joblib.dump(clf, out_path)
    print("Saved model to", out_path.relative_to(Path.cwd()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=[d.name for d in EMBED_DIR.iterdir() if d.is_dir()])
    parser.add_argument("--val_split", default="val", help="Split to evaluate on (val or test)")
    args = parser.parse_args()

    for m in args.models:
        train_and_eval(m, args.val_split) 