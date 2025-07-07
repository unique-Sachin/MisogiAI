"""Build embeddings for dataset splits.

Embeddings stored in embeddings/{model}/{split}.npy
Labels stored in embeddings/labels_{split}.npy once.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from tqdm import tqdm  # type: ignore

from embedding_models import (
    Word2VecEmbedder,
    BertEmbedder,
    SentenceBERTEmbedder,
    OpenAIEmbedder,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_DIR = Path(__file__).resolve().parent.parent / "embeddings"
OUT_DIR.mkdir(exist_ok=True)

SPLITS = ["train", "val", "test"]
EMBEDDERS = {
    "word2vec": Word2VecEmbedder,
    "bert": BertEmbedder,
    "sentencebert": SentenceBERTEmbedder,
    # OpenAI embedder is optional due to API cost; triggered via flag
    "openai": OpenAIEmbedder,
}


def load_texts(split: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(DATA_DIR / f"{split}.csv")
    return df["clean_text" if "clean_text" in df.columns else "text"].tolist(), df["category"].values


def save_embeddings(model_name: str, split: str, X: np.ndarray):
    path = OUT_DIR / model_name
    path.mkdir(exist_ok=True)
    np.save(path / f"{split}.npy", X)


def save_labels(split: str, y: np.ndarray):
    np.save(OUT_DIR / f"labels_{split}.npy", y)


def main(models: List[str], splits: List[str]):
    # Save labels once
    for split in splits:
        _, y = load_texts(split)
        save_labels(split, y)

    for model_name in models:
        print(f"== Building embeddings for {model_name} ==")
        embedder = EMBEDDERS[model_name]()
        for split in splits:
            texts, _ = load_texts(split)
            X = embedder.encode(texts)
            save_embeddings(model_name, split, X)
            print(f"Saved {model_name}/{split} embeddings: {X.shape}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=list(EMBEDDERS.keys()), help="Models to compute")
    parser.add_argument("--splits", nargs="*", default=SPLITS, help="Dataset splits")
    args = parser.parse_args()
    main(args.models, args.splits) 