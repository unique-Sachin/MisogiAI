# Smart Article Categorizer

An end-to-end demo that classifies news articles into six categories (Tech, Finance, Healthcare, Sports, Politics, Entertainment) using modern NLP embeddings and Logistic-Regression classifiers.  It ships with a FastAPI inference backend and a Streamlit UI.

---

## Table of Contents
1. Features
2. Project Structure
3. Quick-start
4. Detailed Workflow
5. REST API
6. Streamlit UI
7. Re-running Experiments
8. Future Work

---

## 1  Features
* 🔤 Embeddings: BERT (CLS) & Sentence-BERT (MiniLM-L6).  
* 🧮 Classifiers: scikit-learn Logistic Regression (one per embedding).  
* 📊 Evaluation: Accuracy, macro Precision/Recall/F1, confusion matrices (saved to `reports/metrics.json`).  
* ⚡ FastAPI service (`/predict`) – < 1 s latency on Apple Silicon CPU.  
* 🎛 Streamlit front-end with sample articles, probability bar-charts and real-time predictions.

## 2  Project Structure
```
Q1/
├── data/                 # CSV splits produced by Phase 1
├── embeddings/           # *.npy files produced by Phase 2
├── models/               # *.joblib classifiers (Phase 3)
├── reports/metrics.json  # Metrics & confusion matrices (Phase 5)
├── src/
│   ├── build_dataset.py      # Phase 1 – acquire + preprocess data
│   ├── build_embeddings.py   # Phase 2 – generate embeddings
│   ├── embedding_models.py   # Embedders
│   ├── train_models.py       # Phase 3 – train classifiers
│   ├── evaluate_models.py    # Phase 5 – compute metrics
│   └── api.py                # FastAPI backend
├── streamlit_app.py      # Streamlit UI
├── requirements.txt
├── prd.md                # Original product requirements doc
└── README.md             # ← you are here
```

## 3  Quick-start
### 3.1 Clone & Install
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2 Run the Trained Demo
Trained models & embeddings are already committed.
```
# 1 Start the backend
PYTHONPATH=src uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# 2 In a new terminal start the Streamlit UI
streamlit run streamlit_app.py --server.headless false
```
Navigate to <http://localhost:8501> and start classifying!

## 4  Detailed Workflow (optional re-run)
1. **Phase 1 – Data**  
   ```bash
   python -m src.build_dataset            # Downloads AG News + BBC, cleans & splits
   ```
2. **Phase 2 – Embeddings**  
   ```bash
   PYTHONPATH=src python src/build_embeddings.py --models bert sentencebert --splits train val test
   ```
3. **Phase 3 – Train**  
   ```bash
   PYTHONPATH=src python src/train_models.py --models bert sentencebert --val_split val
   ```
4. **Phase 5 – Evaluate**  
   ```bash
   PYTHONPATH=src python src/evaluate_models.py --models bert sentencebert --split test
   cat reports/metrics.json | jq
   ```

> **Note:** Word2Vec is disabled (no compatible `gensim` wheel for Python 3.13) and OpenAI embeddings need an API key + budget.

## 5  REST API
```
POST /predict
Content-Type: application/json
{
  "text": "<news article>"
}
```
Response:
```json
{
  "bert": {
    "label": "Tech",
    "probs": {"Tech":0.68, "Finance":0.12, ...}
  },
  "sentencebert": {
    "label": "Tech",
    "probs": {"Tech":0.90, ...}
  }
}
```

## 6  Streamlit UI
* Sample articles in the sidebar for 1-click testing.  
* "Classify" button calls the backend and draws per-model bar-charts.  
* Backend URL can be overridden: `export BACKEND_URL=http://127.0.0.1:8001`.

## 7  Re-running Experiments
If you tweak preprocessing or add models:
```
rm -rf embeddings/ models/ reports/
# then repeat Phases 2-5 above
```

## 8  Future Work
* Re-enable Word2Vec when `gensim` wheels are available for Python 3.13.  
* Plug in OpenAI `text-embedding-ada-002` with on-disk caching.  
* Add UMAP embedding cluster plot to Streamlit.  
* Containerize with Docker for easier deployment.

---
© 2025 Smart Article Categorizer Demo 