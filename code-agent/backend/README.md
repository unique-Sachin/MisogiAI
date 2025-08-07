# Code Agent Backend

A LangGraph-powered backend for the Code Agent VS Code extension, built with FastAPI and OpenAI GPT-3.5 Turbo.

## Features

- 🤖 **LangGraph Integration**: Linear conversation flow with state management
- 🚀 **FastAPI**: High-performance async API
- 🧠 **OpenAI GPT-3.5 Turbo**: Intelligent code assistance
- 🔄 **State Management**: Conversation context and flow control
- 📡 **CORS Support**: Ready for frontend integration

## Architecture

The backend uses a simple linear graph structure:

```
Input → Processing → LLM → Response
```

### Nodes:

1. **Input Node**: Validates and processes user input
2. **Processing Node**: Enhances input with context and metadata
3. **LLM Node**: Generates response using OpenAI GPT-3.5 Turbo
4. **Response Node**: Formats and finalizes the output

## Quick Start

### 1. Setup Environment

```bash
# Navigate to backend directory
cd backend

# Run the startup script (recommended)
./start.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure OpenAI API Key

Edit `.env` file:
```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
PORT=8000
HOST=localhost
```

### 3. Start the Server

```bash
# Using the startup script
./start.sh

# Or manually
python main.py
```

## API Endpoints

### Health Check
```http
GET /
GET /health
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Help me write a Python function",
  "conversation_id": "optional-conversation-id"
}
```

Response:
```json
{
  "response": "I'd be happy to help you write a Python function...",
  "conversation_id": "uuid-here",
  "status": "success"
}
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── models.py            # Pydantic models and state definitions
├── graph.py             # LangGraph implementation
├── requirements.txt     # Python dependencies
├── start.sh            # Startup script
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install fastapi uvicorn python-dotenv

# Run with auto-reload
uvicorn main:app --reload --host localhost --port 8000
```

### Testing the API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, help me with Python"}'
```

## Integration with VS Code Extension

The backend is designed to work with the Code Agent VS Code extension. The extension should make HTTP requests to:

```
http://localhost:8000/chat
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `PORT` | Server port | 8000 |
| `HOST` | Server host | localhost |

## Dependencies

- **FastAPI**: Modern web framework
- **LangGraph**: Graph-based conversation flow
- **LangChain**: LLM integration utilities
- **OpenAI**: GPT-3.5 Turbo integration
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

## Future Enhancements

- [ ] Conversation persistence (database)
- [ ] Streaming responses
- [ ] Authentication/authorization
- [ ] Rate limiting
- [ ] Conversation history management
- [ ] Multiple LLM providers
- [ ] Custom prompts and templates

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Run `pip install -r requirements.txt`
2. **OpenAI API Error**: Check your API key in `.env`
3. **Port already in use**: Change `PORT` in `.env`

### Logs

The application logs important events. Check console output for debugging information.

## License

This project is part of the Code Agent VS Code extension.
