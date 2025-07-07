"""FastAPI backend for Smart Article Categorizer.

Run:
    PYTHONPATH=src ./.venv/bin/uvicorn api:app --reload --host 0.0.0.0 --port 8000

POST /predict
    {
        "text": "<article text>"
    }
Returns JSON with predictions from BERT and Sentence-BERT models.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import joblib  # type: ignore
import numpy as np  # type: ignore
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from embedding_models import BertEmbedder, SentenceBERTEmbedder

# --------------------
# App setup
# --------------------
app = FastAPI(title="Smart Article Categorizer API", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ArticleRequest(BaseModel):
    text: str = Field(..., description="News article content")


# --------------------
# Load models & embedders at startup
# --------------------
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

try:
    bert_clf = joblib.load(MODEL_DIR / "bert.joblib")
    sbert_clf = joblib.load(MODEL_DIR / "sentencebert.joblib")
except FileNotFoundError as e:
    raise RuntimeError("Trained model files not found. Make sure Phase 3 has been run.") from e

CATEGORIES: List[str] = bert_clf.classes_.tolist()

# Embedders (heavy models) are loaded once
bert_embedder = BertEmbedder()
sbert_embedder = SentenceBERTEmbedder()


# --------------------
# Helper
# --------------------

def probs_to_dict(probs: np.ndarray) -> Dict[str, float]:
    return {cat: float(p) for cat, p in zip(CATEGORIES, probs)}


# --------------------
# Routes
# --------------------

@app.post("/predict")
def predict(req: ArticleRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    # Encode
    bert_vec = bert_embedder.encode([text])
    sbert_vec = sbert_embedder.encode([text])

    # Predict
    bert_probs = bert_clf.predict_proba(bert_vec)[0]
    sbert_probs = sbert_clf.predict_proba(sbert_vec)[0]

    return {
        "bert": {
            "label": CATEGORIES[int(np.argmax(bert_probs))],
            "probs": probs_to_dict(bert_probs),
        },
        "sentencebert": {
            "label": CATEGORIES[int(np.argmax(sbert_probs))],
            "probs": probs_to_dict(sbert_probs),
        },
    } 