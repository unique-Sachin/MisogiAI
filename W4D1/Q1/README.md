# MCP Expert Q&A Chatbot

This repository hosts a Retrieval-Augmented Generation (RAG) chatbot that answers developer questions about the **Model Context Protocol (MCP)**.

## Tech Stack

* **Backend**: FastAPI + LangChain + OpenAI + Pinecone
* **Frontend**: Next.js (App Router) + TailwindCSS
* **Vector Store**: Pinecone

## Local Development

### 1. Backend

```bash
# create & activate a virtual env (optional)
python -m venv .venv && source .venv/bin/activate

# install dependencies
pip install -r backend/requirements.txt

# copy env template and fill your keys
cp backend/env.example backend/.env

# run the API server
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Embedding MCP documentation

# Option A – Auto-download (default)
The script has a `SOURCE_URLS` list with public MCP doc URLs. Just run:

```bash
python scripts/embed_docs.py  # downloads → chunks → embeds → uploads
```

Feel free to edit `scripts/embed_docs.py` → `SOURCE_URLS` to add or replace links.

# Option B – Manual docs
Place your Markdown/PDF files under `data/mcp_docs/` and run the same command:

```bash
python scripts/embed_docs.py
```

### 3. Frontend

The Next.js frontend will be scaffolded under `frontend/` (see project plan). After it's generated, run:

```bash
cd frontend
npm run dev
```

## Deployment

* **Frontend** → Vercel
* **Backend** → Render (Dockerfile to be added)

## Roadmap

1. Finish embedding pipeline
2. Implement LangChain retrieval + OpenAI generation in `/chat` endpoint
3. Scaffold frontend with chat UI
4. Add CI/CD and deployment configs 