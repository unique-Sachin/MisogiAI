# pyright: reportGeneralTypeIssues=false

from functools import lru_cache
from typing import Dict, List

import textstat
from transformers import pipeline  # type: ignore
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Lazy load heavy models

@lru_cache()
def _sentiment_pipeline():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

@lru_cache()
def _nlp():
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Fallback to blank English model if the small model is not installed
        nlp = spacy.blank("en")
    # Ensure we have sentence segments
    if "sentencizer" not in nlp.pipe_names and "parser" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")
    return nlp

# Analysis helpers

def get_sentiment(text: str) -> str:
    if not text.strip():
        return "neutral"
    result = _sentiment_pipeline()(text[:512])[0]  # type: ignore  # limit for speed
    label = result["label"].lower()
    if label == "positive":
        return "positive"
    if label == "negative":
        return "negative"
    return "neutral"

def extract_keywords(text: str, limit: int = 5) -> List[str]:
    if not text.strip():
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))  # type: ignore
    tfidf = vectorizer.fit_transform([text])
    scores = tfidf.toarray()[0]
    indices = np.argsort(scores)[::-1][:limit]  # type: ignore
    features = vectorizer.get_feature_names_out()
    return [features[i] for i in indices if scores[i] > 0]

def readability_score(text: str) -> float:
    # Flesch Reading Ease
    try:
        return float(textstat.flesch_reading_ease(text))
    except Exception:
        return 0.0

def basic_stats(text: str) -> Dict[str, int]:
    doc = _nlp()(text)
    words = [t for t in doc if not t.is_space]
    sentences = list(doc.sents)
    return {
        "word_count": len(words),
        "sentence_count": len(sentences)
    }

def analyze_document_content(text: str, keyword_limit: int = 5) -> Dict:
    return {
        "sentiment": get_sentiment(text),
        "keywords": extract_keywords(text, limit=keyword_limit),
        "readability": readability_score(text),
        "stats": basic_stats(text),
    } 