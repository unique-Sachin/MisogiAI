
# 📄 Product Requirements Document (PRD)

## Project Title:  
**Document Analyzer MCP-Compatible Tool Server**

## 1. 🧠 Overview

The Document Analyzer MCP Server is a backend application that stores text documents with metadata and exposes a set of standardized tools compatible with the **Model Context Protocol (MCP)**. These tools provide analysis features such as sentiment detection, keyword extraction, readability scoring, and basic document statistics. The system is designed to allow AI agents (e.g., OpenAI GPTs) to call these tools using structured tool invocation patterns.

---

## 2. 🎯 Goals

- Provide structured tool interfaces (MCP-compatible) for text analysis
- Store and retrieve documents with metadata
- Enable full and partial document analysis via programmable tool calls
- Return responses in standardized JSON format
- Expose callable tools for integration with LLMs via MCP

---

## 3. 🧱 Tech Stack

- **Programming Language:** Python 3.11+
- **API Framework:** FastAPI
- **NLP Library:** spaCy
- **Sentiment Analysis:** transformers (e.g., distilbert-base-uncased-finetuned-sst-2-english)
- **Keyword Extraction:** TF-IDF using scikit-learn
- **Readability Scoring:** textstat
- **Document Storage:** JSON files (local storage)
- **Search:** Basic string matching
- **Testing:** pytest

---

## 4. 📂 Data Model

### Document Schema (JSON)
```json
{
  "id": 1,
  "title": "Sample Document",
  "author": "John Doe",
  "date": "2025-07-01",
  "content": "Full text of the document goes here.",
  "metadata": {
    "category": "News",
    "language": "English"
  }
}
```

---

## 5. 🛠 MCP-Compatible Tool Functions

### Tool: `add_document`
- **Description:** Add a new document to the system
- **Input:**
  ```json
  {
    "document_data": {
      "title": "string",
      "author": "string",
      "date": "string",
      "content": "string",
      "metadata": { "category": "string", "language": "string" }
    }
  }
  ```
- **Output:**
  ```json
  { "document_id": 1 }
  ```

---

### Tool: `analyze_document`
- **Description:** Perform full analysis of a stored document
- **Input:**
  ```json
  { "document_id": 1 }
  ```
- **Output:**
  ```json
  {
    "sentiment": "positive",
    "keywords": ["ai", "document", "nlp"],
    "readability": 65.4,
    "stats": {
      "word_count": 150,
      "sentence_count": 10
    }
  }
  ```

---

### Tool: `get_sentiment`
- **Description:** Analyze sentiment of any text
- **Input:**
  ```json
  { "text": "string" }
  ```
- **Output:**
  ```json
  { "sentiment": "positive" }
  ```

---

### Tool: `extract_keywords`
- **Description:** Extract top N keywords from input text
- **Input:**
  ```json
  {
    "text": "string",
    "limit": 5
  }
  ```
- **Output:**
  ```json
  { "keywords": ["term1", "term2", "term3"] }
  ```

---

### Tool: `search_documents`
- **Description:** Search documents for a query term
- **Input:**
  ```json
  { "query": "string" }
  ```
- **Output:**
  ```json
  [
    {
      "id": 1,
      "title": "Sample Document",
      "matched_snippet": "...partial text..."
    }
  ]
  ```

---

## 6. 📊 Document Analysis Logic

| Feature            | Tool Used           | Description |
|-------------------|---------------------|-------------|
| Sentiment         | distilbert-sst-2    | Uses polarißty score to classify as positive, negative, or neutral |
| Keywords          | TF-IDF via scikit-learn | Extracts top N terms by importance |
| Readability       | textstat            | Uses Flesch Reading Ease score |
| Basic Stats       | spaCy               | Counts words and sentences using language model |

---

## 7. 🧪 Testing Plan

- Unit tests for each tool function and endpoint
- Sample test documents to validate sentiment, keyword, and readability outputs
- Testing framework: `pytest`
- Coverage target: 90%

---

## 8. 📁 Folder Structure

```
document_analyzer/
├── main.py                # FastAPI server
├── tools.py               # MCP tool definitions and logic
├── analyzer.py            # NLP analysis functions
├── storage.py             # JSON-based document handling
├── search.py              # Query matching logic
├── data/
│   └── documents.json     # Document storage
├── tests/
│   └── test_tools.py      # Test suite
├── requirements.txt
└── README.md
```

---

## 9. 📝 Notes

- This server acts as a callable tool suite for LLMs via the Model Context Protocol
- No UI is required
- All outputs should follow standardized JSON schema
- Tools are designed to be safely and predictably callable by AI systems
