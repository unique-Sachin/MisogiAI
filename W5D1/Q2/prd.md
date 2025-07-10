# PRD: Local RAG Pipeline with Intent Detection and Evaluation

## 📌 Overview

We are building a local Retrieval-Augmented Generation (RAG) system for customer support at a SaaS company. The system will classify incoming user queries into three intent categories and route them through tailored processing pipelines. It must support both local LLM (Llama3.1:8b via Ollama) and OpenAI GPT-4, with fallback and streaming capabilities.

---

## 🎯 Goals

- Enable accurate classification of customer queries into:
  - Technical Support
  - Billing/Account Issues
  - Feature Requests
- Perform retrieval of relevant knowledge base content using embeddings
- Generate high-quality responses using LLMs
- Evaluate performance across multiple metrics
- Provide a Streamlit-based interface for testing, visualization, and A/B comparison

---

## 🧱 Core Components

### 1. LLM Router

- **Primary LLM**: Local Llama3.1:8b via Ollama
- **Fallback LLM**: OpenAI GPT-4o-mini
- Streaming support for responses from both LLMs
- **Fallback triggers** (configurable):
  - No response or malformed JSON from Ollama
  - Connection or parsing error
  - Ollama API timeout > 10 s
  - (Minor low-quality generations are logged but do **not** trigger fallback)

### 2. Intent Classifier

- Prompt-based classification (few-shot)
- Output: `{"intent": "technical" | "billing" | "feature_request"}`

### 3. Embedding & Retrieval

- **Model**: `paraphrase-multilingual-MiniLM-L12-v2` (from `sentence-transformers`)
- Vector DB: **ChromaDB**
- Separate collection per intent type
- Document format: plain `.txt` / `.md` files in `app/knowledge_base/<intent>/`
- Fixed-size token chunking: 512 tokens with 50-token overlap
- Top-k context chunks retrieved per query (k = 4, configurable via env var `RETRIEVER_TOP_K`)

### 4. Prompt Templates

- One template per intent type
- Each template includes:
  - Role prompt
  - Injected context
  - User query

### 5. Evaluation Module

- Run on 60 labeled test queries (20 per intent)
- Metrics:
  - Intent Classification Accuracy
  - Cosine Similarity to Gold Response
  - Context Utilization Score (heuristic: % of retrieved chunks quoted in response)
  - Response Time
  - Token Usage (OpenAI: API usage field; Ollama: estimated via tiktoken; log prompt, completion & total)

### 6. Streamlit UI

- Input: User query
- Output: Intent, retrieved context, streamed LLM response
- A/B toggle: Llama (local) vs OpenAI
- Evaluation dashboard (metrics visualization)
- Streaming implemented via `st.chat_message` incremental updates
- If local LLM is failing, show the error message and fallback to OpenAI

---

## 📦 Testing

- Unit tests for each component
- Integration tests for the pipeline
- End-to-end tests for the Streamlit app

---

## 📂 File Structure

```bash
├── app/
│   ├── llm_router.py
│   ├── intent_classifier.py
│   ├── retriever.py
│   ├── evaluator.py
│   ├── templates/
│   ├── knowledge_base/
│   │   ├── technical/
│   │   ├── billing/
│   │   └── feature_request/
│   └── embedding_index.py
├── ui/
│   └── streamlit_app.py
├── data/
│   ├── test_queries.json
│   └── gold_responses.json
├── reports/
│   └── evaluation_results.csv
├── requirements.txt
└── README.md