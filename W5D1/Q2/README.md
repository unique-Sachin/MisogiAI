# Local RAG Pipeline (WIP)

This repository contains an experimental Retrieval-Augmented Generation (RAG) system for customer-support queries. It runs **entirely locally** with an optional fallback to OpenAI.

## Quickstart

```bash
# 1. Clone repo & enter directory
$ git clone <repo>
$ cd Q2

# 2. Create and activate virtual env (Python ≥3.9)
$ python3 -m venv .venv
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. (Optional) Pull local Llama3 model via Ollama
$ ollama pull llama3.1:8b

# 5. Index the knowledge-base (once)
$ python -c "from app.retriever import build_index; build_index()"

# 6. Launch Streamlit UI
$ streamlit run ui/streamlit_app.py
```

Set `OPENAI_API_KEY` in your environment to enable GPT-4o-mini fallback.

---

See `prd.md` for full product requirements. 