# Intelligent Email Response System (IERS)

An automated batch worker that retrieves unread Gmail messages, looks up relevant company policies via a local Chroma vector DB, drafts AI-powered replies, and sends templated responses back to the sender.

---
## Prerequisites
1. **Python 3.11+**  
2. **Google Cloud project** with Gmail API enabled.  
3. **OpenAI account / API key** (or compatible LLM that follows OpenAI SDK).
4. (Optional) **Redis** instance if you want caching.

---
## Quick-start
```bash
# clone repo …
cd IERS
python3 -m venv .venv           # create virtual-env
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env             # then edit with your secrets
```

### Environment variables
| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — |Required. Key used to call the LLM that drafts replies. |
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` |Path to OAuth client JSON downloaded from Google Cloud. |
| `REDIS_URL` | `redis://localhost:6379/0` |Redis connection string for caching prompts/context. |
| `BATCH_SIZE` | `10` |Max unread emails fetched per batch run. |
| `EMAIL_SIGNATURE` | `Acme Corp Support Team` |Signature appended to every reply. |
| `EMAIL_DISCLAIMER` | *confidential disclaimer* |Footer disclaimer text. |
| `CHROMA_DIR` | `chroma_db` |Directory on disk where Chroma persists vectors + metadata. |
| `ANONYMIZED_TELEMETRY` | `FALSE` |Set to `FALSE` to fully silence Chroma telemetry warnings. |

> Copy `.env.example` to `.env` and fill in the blanks.

---
## Google OAuth setup (credentials.json)
1. **Create a Cloud project** → Enable *Gmail API*.
2. **Configure OAuth consent screen:**
   *User type* Internal (Workspace) or External. Add yourself under *Test users* if External.
3. **Create credentials → OAuth client ID → Desktop app**.  
   Download the JSON and save it as `credentials.json` in the project root (or adjust `GOOGLE_CREDENTIALS_FILE`).
4. **First run** will pop a browser window → select your Gmail account → grant `gmail.modify` permission.  A `token.json` file is created for silent refreshes thereafter.

---
## Ingesting policies
Place Markdown/TXT/PDF files under the `policies/` tree, organised by department (folder name becomes metadata):
```
policies/
  hr/leave.md
  it/password-reset.md
  finance/expense-policy.md
```
Then run:
```bash
python -m iers.policy_ingest --dir policies/
```
This embeds the docs and stores them in the local Chroma DB.

---
## Running the worker
### One-off batch via API
```bash
uvicorn main:app --reload &        # starts FastAPI on :8000
curl -X POST http://localhost:8000/run-batch
```
### Direct call
```bash
python - <<'PY'
from iers.worker import process_batch
process_batch()
PY
```
Each run fetches up to `BATCH_SIZE` newest unread messages, drafts replies, sends them, and marks them as read.

---
## Testing
Lightweight smoke tests (no external services are hit):
```bash
python -m venv .testenv && source .testenv/bin/activate
pip install -r test-requirements.txt
pytest -q
```

---
## Frequently Asked
**Q: Chroma prints “Failed to send telemetry event …” once on startup**  
A: We turn telemetry off in code, but you can also set `ANONYMIZED_TELEMETRY=FALSE` to mute the warning.

**Q: Can I change email templates?**  
A: Edit / add Jinja files under the `templates/` directory. The default is `email_default.jinja`.

**Q: How do I add more policy departments?**  
A: Create a sub-folder under `policies/` and drop docs there. Re-run the ingestion script.

---
Enjoy your automated, policy-aware inbox! 🎉 