# Financial-Intel RAG Service

A **retrieval-augmented generation (RAG)** micro-service that turns unstructured financial documents into an interactive Q&A experience.

* 💡 FastAPI + Uvicorn – HTTP API
* 🗄️ Pinecone – vector database
* 🧠 Sentence-Transformers – embeddings (`all-MiniLM-L6-v2`, 384-d)
* 📝 OpenAI (gpt-4o-mini by default) – answer generation
* ⚙️ Celery + Redis – background ingestion pipeline
* 🐳 Docker Compose – one-command deployment

---

## 1 Quick start (Docker)

```bash
# 1. Clone and enter the repo
$ git clone <repo-url> && cd Q3

# 2. Create a .env file with your secrets
$ cp .env.example .env        # edit values

# 3. Build & run everything
$ docker compose up --build   # api  ➕ worker ➕ redis
```

The API will be available at <http://localhost:8000> (Swagger UI at `/docs`).

### Required environment variables
| Variable | Example | Description |
|----------|---------|-------------|
| `PINECONE_API_KEY`      | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | Pinecone secret key |
| `PINECONE_ENVIRONMENT`  | `us-east1-gcp` | Region / cloud where your index lives |
| `PINECONE_INDEX_NAME`   | `financial-intel-index` | Existing index name (must be **created manually** with dimension **384**) |
| `PINECONE_DIMENSION`    | `384` | Vector size (must match embedding model) |
| `OPENAI_API_KEY`        | `sk-…` | Key for chat completion model |
| `REDIS_BROKER_URL`      | `redis://redis:6379/0` | Celery broker URI |
| `CELERY_QUEUE`          | `financial_rag` | Worker queue name |

> ℹ️ The repo ships with sensible defaults; anything missing will raise a helpful error at start-up.

### File storage
Uploaded documents are kept in a shared Docker volume and mounted at `/tmp/financial_docs` inside both the **api** and **worker** containers. Override with `UPLOAD_DIR` if desired.

---

## 2 Running locally (no Docker)

```bash
# 1. Python 3.11+ & virtualenv
$ python -m venv .venv && source .venv/bin/activate

# 2. Install deps
$ pip install -r requirements.txt

# 3. Export the same env vars as above (or create .env)

# 4. Start services
$ uvicorn app.main:app --reload               # web api
$ celery -A app.core.celery_app.celery_app \
         worker -l info -Q financial_rag \
         --concurrency=1                      # ingestion worker
```

Redis must be running locally (e.g. via Docker `docker run -p 6379:6379 redis:7-alpine`).

---

## 3 API overview

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/api/v1/health` | Liveness probe |
| `POST` | `/api/v1/documents/upload` | Upload a PDF/TXT/… file; triggers async ingestion |
| `POST` | `/api/v1/query` | Ask a question; returns `answer` + `sources` |
| `GET`  | `/api/v1/embedding/status` | Ensures embedding model is loaded |
| `GET`  | `/api/v1/pinecone/status`  | Connection + index stats (vector counts, etc.) |
| `POST` | `/api/v1/pinecone/test_query` | Raw similarity search (debug helper) |

Example query:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What was the company revenue in Q4 2023?"}'
```

Response:
```json
{
  "answer": "The company reported revenue of $1.23 B in Q4 2023.",
  "sources": [
    "994ac1e8-61e9-4af8-880f-b67e3a832d22"
  ],
  "cached": false
}
```

---

## 4 Document ingestion flow

```mermaid
flowchart TD
    A[Upload file] -->|/documents/upload| B(Save to volume)
    B -->|Celery task| C[Parse & extract text]
    C --> D[Chunk (~1-2k chars)]
    D --> E[Embed (all-MiniLM-L6-v2)]
    E --> F[Upsert to Pinecone]
```

* **Parser** supports PDFs, text and simple HTML (extendable via `app/services/ingestion/parser.py`).
* Each chunk is stored with metadata `{document_id, chunk_id, text}`.

---

## 5 Testing

```bash
pytest -q
```

The sample test verifies the `/health` route. Extend with more cases under `tests/`.

---

## 6 Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `embedding/status` fails | Container out of memory | Increase worker memory or switch to even smaller model in `model.py` |
| `pinecone/status` recursion error | Non-serialisable SDK objects | Already handled – update repo |
| `/query` returns empty `sources` | Index empty or wrong dimension | Confirm vector_count > 0 and dimension = 384 |
| `TypeError: Client.__init__(proxies=…)` | `httpx 0.27+` incompatible with OpenAI 1.30 | Requirements pin `httpx<0.27`; reinstall |

---

## 7 Project structure

```
app/
  api/            # FastAPI routes
  core/           # config, celery setup
  services/
    embedding/    # model loader
    ingestion/    # parser, chunker, celery tasks
    qa/           # question-answer pipeline
    vector/       # Pinecone client wrapper
Dockerfile        # runtime image
docker-compose.yml
prd.md            # product requirements doc
requirements.txt
```

---

## 8 Acknowledgements

* [Pinecone](https://www.pinecone.io/) – serverless vector DB
* [OpenAI](https://platform.openai.com/) – GPT-4o-mini
* [Sentence-Transformers](https://www.sbert.net/) – open-source embeddings
* [FastAPI](https://fastapi.tiangolo.com/) – modern web framework 