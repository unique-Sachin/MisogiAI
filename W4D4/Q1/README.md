# HR Onboarding Knowledge Assistant

An AI-powered chat tool that helps new employees quickly find answers to HR-related questions by referencing internal policy documents.

## Features

- **Multi-format Document Support**: Upload PDF, DOCX, and TXT files
- **Intelligent Chunking**: Automatically splits documents into meaningful sections
- **Vector Search**: Uses pure Python cosine similarity search (no external dependencies)
- **AI-Powered Answers**: Generates contextual responses with source citations
- **RESTful API**: Simple HTTP endpoints for document upload and chat
- **Pluggable AI Providers**: Easily switch between different LLM providers

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (for embeddings and completions)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   git clone <your-repo-url>
   cd hr-onboarding-assistant
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

### Running the Application

1. **Test the setup** (optional):
   ```bash
   python test_setup.py
   ```

2. **Start the API server**:
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **The API will be available at**: `http://localhost:8000`

### Frontend Setup (Optional)

For a complete user interface:

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Open the web interface**: `http://localhost:3000`

The frontend provides a modern chat interface with document upload and inline citations.

## API Usage

### Upload a Document

```bash
curl -X POST "http://localhost:8000/upload-doc" \
  -F "file=@path/to/your/document.pdf"
```

**Response**:
```json
{
  "chunks_indexed": 15
}
```

### Ask a Question

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vacation days do I get as a new employee?"}'
```

**Response**:
```json
{
  "answer": "As a new employee, you get 15 vacation days per year [chunk#0]. Additional days may be earned based on tenure [chunk#2].",
  "citations": [
    {
      "source_path": "employee_handbook.pdf",
      "chunk_index": "0"
    },
    {
      "source_path": "employee_handbook.pdf", 
      "chunk_index": "2"
    }
  ]
}
```

## Configuration

You can customize the behavior using environment variables:

```bash
# OpenAI Settings
export OPENAI_API_KEY="your-api-key"
export EMBEDDING_MODEL="text-embedding-3-small"
export COMPLETION_MODEL="gpt-4o-mini"

# Retrieval Settings
export TOP_K="4"                    # Number of chunks to retrieve
export MAX_TOKENS="256"             # Max tokens in response

# Chunking Settings
export CHUNK_SIZE="400"             # Words per chunk
export CHUNK_OVERLAP="50"           # Overlapping words between chunks

# Storage
export VECTOR_STORE_PATH="vector_store"  # Where to store the index
```

## Example Queries

- "How many vacation days do I get as a new employee?"
- "What's the process for requesting parental leave?"
- "Can I work remotely and what are the guidelines?"
- "How do I enroll in health insurance?"
- "What are the rules around workplace conduct?"

## Project Structure

```
hr-onboarding-assistant/
├── backend/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── models.py              # Data models
│   ├── main.py                # FastAPI application
│   ├── ingestion.py           # Document processing
│   ├── retriever.py           # RAG pipeline
│   ├── vector_store.py        # FAISS wrapper
│   └── providers/             # AI provider abstractions
│       ├── __init__.py
│       ├── base.py
│       └── openai_provider.py
├── requirements.txt
├── test_setup.py              # Setup verification
└── README.md
```

## Supported File Formats

- **PDF**: Uses pypdf for text extraction
- **DOCX**: Uses python-docx for Word documents  
- **TXT**: Native text file support

## Development

### Adding New AI Providers

1. Create a new provider class in `backend/providers/`:
   ```python
   from .base import EmbeddingsProvider, CompletionProvider
   
   class MyProvider(EmbeddingsProvider, CompletionProvider):
       def embed(self, texts):
           # Your embedding logic
           pass
           
       def complete(self, prompt, max_tokens=256):
           # Your completion logic
           pass
   ```

2. Update the provider in `backend/main.py`:
   ```python
   from .providers import MyProvider
   provider = MyProvider(...)
   ```

### Extending Document Support

Add new extractors to `backend/ingestion.py`:

```python
def _extract_text_from_new_format(path: str) -> str:
    # Your extraction logic
    pass

_extractors[".new_ext"] = _extract_text_from_new_format
```

## Troubleshooting

### Common Issues

1. **PyMuPDF compilation errors**: This project uses `pypdf` instead of `PyMuPDF` to avoid compilation issues on macOS.

2. **FAISS/NumPy compilation errors**: This project uses pure Python for vector operations to avoid any compilation dependencies.

3. **OpenAI API errors**: Make sure your API key is set correctly and has sufficient credits.

4. **Memory issues with large documents**: Adjust `CHUNK_SIZE` to create smaller chunks.

5. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`.

### Getting Help

Run the test script to verify your setup:
```bash
python test_setup.py
```

This will check imports, basic functionality, and document ingestion.

## License

MIT License - feel free to use this for your projects! 