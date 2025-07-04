# MCP Discord Server

A multi-tenant FastAPI service that lets AI models interact with Discord through a secure HTTP interface.  
Core features include API-key auth with RBAC, per-tenant Discord bot tokens, audit logging, rate-limiting, and a real-time WebSocket inspector.

---

## 🚀 Quick start

```bash
# 1. Clone repo & create virtual-env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp env.example .env               # edit values (especially DISCORD_BOT_TOKEN)

# 3. PostgreSQL (local)
./setup_postgres.sh               # creates database mcp_discord / user mcp_user

# 4. Initialise DB (tables + bootstrap tenant & key)
python3 init_db.py

# 5. Run server
uvicorn app.main:app --reload

# 6. Docs
open http://localhost:8000/docs    # Swagger UI
```

> **Bootstrap admin key**: `bootstrap-admin-key` – use this once to create real keys, then revoke it.

---

## 🗂️ Project structure

```
Q1/
├── app/                # FastAPI application
│   ├── api/            #   –– HTTP route modules (admin, discord, inspector)
│   ├── core/           #   –– config, db, security, rate-limit
│   ├── middleware/     #   –– audit logger
│   ├── models/         #   –– SQLAlchemy models (Tenant, APIKey, AuditLog)
│   ├── schemas/        #   –– Pydantic schemas
│   └── services/       #   –– Discord REST client
├── tests/              # pytest suite (SQLite, mocked Discord)
├── manual_testing_guide.md
├── test_helper.py       # interactive CLI tester
├── setup_postgres.sh    # dev DB bootstrap
└── init_db.py           # creates tables + bootstrap data
```

---

## 🔑 Authentication & Roles

| Role | Description                 |
|------|-----------------------------|
| admin| Manage API-keys & inspector |
| write| Send / delete messages      |
| read | Read channel / messages     |

Supply the key via `X-API-Key` header.  All endpoints are tenant-scoped through the key.

---

## 📡 HTTP Endpoints (v1)

### Admin (admin role)
| Method | Path                | Description            |
|--------|---------------------|------------------------|
| POST   | /admin/api-keys     | Create new API key     |
| GET    | /admin/api-keys     | List keys              |
| DELETE | /admin/api-keys/{id}| Revoke key             |
| WS     | /inspector/ws       | Real-time audit feed   |

### Discord
| Role  | Method | Path                     | Description |
|-------|--------|--------------------------|-------------|
| write | POST   | /discord/send_message    | Send message |
| read  | GET    | /discord/messages        | Recent msgs  |
| read  | GET    | /discord/channel_info    | Channel meta |
| write | DELETE | /discord/delete_message  | Delete msg   |
| read  | POST   | /discord/search_messages | Keyword find |

Rate-limits: **100 req/min global**, **10 req/min per-endpoint** (configurable via `.env`).

---

## 🧪 Testing

```bash
pytest -v                         # unit + integration (SQLite, mocks)
coverage html                     # coverage report (>80%)

# Interactive smoke tests
python3 test_helper.py            # generates keys, hits endpoints
```

`manual_testing_guide.md` shows raw curl commands and WebSocket inspector usage.

---

## 🛡️ Security notes

* API keys are SHA-256 hashed in DB; secrets shown **once** on creation.
* Rate-limiting via [slowapi].
* AuditLog persisted to DB and streamed to inspector.
* All sensitive values come from environment variables (.env for dev).

---

## 📝 PRD & Docs

See `prd.md` for the original product requirements.  
`TESTING_SUMMARY.md` captures recent manual/automated results.

---

## ✨ Roadmap ideas

* Tenant self-service dashboard
* Discord gateway (WS) support for real-time events
* Token rotation endpoint (admin)
* Docker Compose for zero-setup dev

Contributions welcome! 🎉 