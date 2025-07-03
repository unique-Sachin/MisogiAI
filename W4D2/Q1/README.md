# Document Analyzer MCP-Compatible Tool Server

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
# download spaCy model (first time only)
python -m spacy download en_core_web_sm
```

## Running the server

```bash
uvicorn document_analyzer.main:app --reload
```

## Tool Endpoints

All endpoints accept/return JSON and mirror the MCP tool contracts described in the PRD.

| HTTP Path | Tool Name | Method |
|-----------|-----------|--------|
| `/add_document` | add_document | POST |
| `/analyze_document` | analyze_document | POST |
| `/get_sentiment` | get_sentiment | POST |
| `/extract_keywords` | extract_keywords | POST |
| `/search_documents` | search_documents | POST |

Example cURL:

```bash
curl -X POST http://127.0.0.1:8000/add_document \
     -H "Content-Type: application/json" \
     -d '{"document_data": {"title": "Sample", "author": "Alice", "date": "2025-07-01", "content": "Hello world.", "metadata": {"category": "News", "language": "English"}}}'
```

## Example calls for every endpoint

1. **Add a document**

```bash
curl -X POST http://127.0.0.1:8000/add_document \
     -H "Content-Type: application/json" \
     -d '{
           "document_data": {
             "title": "AI News",
             "author": "Reporter",
             "date": "2025-07-20",
             "content": "OpenAI releases a new model.",
             "metadata": {"category": "Tech", "language": "English"}
           }
         }'
```

2. **Analyze an existing document** (replace `1` with the desired document_id)

```bash
curl -X POST http://127.0.0.1:8000/analyze_document \
     -H "Content-Type: application/json" \
     -d '{"document_id": 1}'
```

3. **Get sentiment for arbitrary text**

```bash
curl -X POST http://127.0.0.1:8000/get_sentiment \
     -H "Content-Type: application/json" \
     -d '{"text": "I love artificial intelligence!"}'
```

4. **Extract keywords** (limit defaults to 5 if omitted)

```bash
curl -X POST http://127.0.0.1:8000/extract_keywords \
     -H "Content-Type: application/json" \
     -d '{"text": "Machine learning drives many modern applications.", "limit": 3}'
```

5. **Search stored documents**

```bash
curl -X POST http://127.0.0.1:8000/search_documents \
     -H "Content-Type: application/json" \
     -d '{"query": "quantum"}'
``` 