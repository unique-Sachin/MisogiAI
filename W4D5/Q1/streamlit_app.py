"""Streamlit frontend for Smart Article Categorizer.

Run:
    streamlit run streamlit_app.py

Ensure the FastAPI backend is running locally on http://localhost:8000 (default) or set the BACKEND_URL
Streamlit secret.
"""
from __future__ import annotations

import json
import os
from typing import Dict

import pandas as pd  # type: ignore
import requests  # type: ignore
import streamlit as st  # type: ignore

# --------------------
# Config
# --------------------
_default_backend = os.getenv("BACKEND_URL", "http://localhost:8000")
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]  # type: ignore[index]
except Exception:
    BACKEND_URL = _default_backend

st.set_page_config(page_title="Smart Article Categorizer", page_icon="📰", layout="centered")

st.title("📰 Smart Article Categorizer")

# Example articles
EXAMPLES = {
    "Tech": "Apple launches new iPhone with AI-powered camera and faster chip.",
    "Finance": "Stock markets rally as Federal Reserve hints at rate cut.",
    "Healthcare": "New study reveals breakthrough in cancer immunotherapy.",
    "Sports": "Lionel Messi scores hat-trick to secure title for Inter Miami.",
    "Politics": "Senate passes bipartisan infrastructure bill after months of debate.",
    "Entertainment": "Blockbuster movie breaks box office records on opening weekend.",
}

# Sidebar
with st.sidebar:
    st.header("Sample Articles")
    for cat, txt in EXAMPLES.items():
        if st.button(cat):
            st.session_state["article_text"] = txt
    st.markdown("---")
    st.markdown("Backend: **%s**" % BACKEND_URL)

# Main input area
text = st.text_area("Paste a news article:", value=st.session_state.get("article_text", ""), height=300)
cols = st.columns(2)

with cols[0]:
    submit = st.button("Classify", type="primary")
with cols[1]:
    if st.button("Clear"):
        st.session_state["article_text"] = ""
        st.experimental_rerun()

if submit:
    if not text.strip():
        st.warning("Please enter article text before classifying.")
    else:
        with st.spinner("Contacting model backend…"):
            try:
                resp = requests.post(f"{BACKEND_URL}/predict", json={"text": text}, timeout=30)
            except requests.RequestException as e:
                st.error(f"Request failed: {e}")
                st.stop()

        if resp.status_code != 200:
            st.error(f"Backend error {resp.status_code}: {resp.text}")
            st.stop()

        data: Dict[str, Dict[str, Dict[str, float] | str]] = resp.json()

        st.success("Predictions ready!")

        for model_name, result in data.items():
            st.subheader(f"{model_name.upper()} Prediction: {result['label']}")
            probs: Dict[str, float] = result["probs"]  # type: ignore[assignment]
            df = pd.DataFrame({"category": list(probs.keys()), "probability": list(probs.values())})
            df = df.sort_values("probability", ascending=False)
            st.bar_chart(df.set_index("category")) 