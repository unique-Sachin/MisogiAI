# Code Agent - AI-Powered VS Code Extension

A powerful VS Code extension that provides an AI coding assistant with a chat interface, powered by LangGraph and OpenAI GPT-3.5 Turbo.

## Features

### Frontend (VS Code Extension)
- 🤖 **Side Panel Chat Interface**: Copilot-style chat panel
- 💬 **Interactive UI**: Modern chat interface with typing indicators
- 🎨 **VS Code Integration**: Native theming and seamless integration
- ⚡ **Real-time Communication**: Bi-directional messaging

### Backend (Python/FastAPI)
- 🧠 **LangGraph Integration**: Structured conversation flow
- 🚀 **FastAPI**: High-performance async API
- 🔄 **State Management**: Conversation context and history
- 🤖 **OpenAI GPT-3.5 Turbo**: Advanced AI responses

## Architecture

```
VS Code Extension (TypeScript) ↔ FastAPI Backend (Python) ↔ OpenAI GPT-3.5 Turbo
                ↓                            ↓
        Chat Interface UI          LangGraph Flow Engine
```

## Quick Start

### 1. Backend Setup (Required First!)

```bash
# Navigate to backend and start server
cd backend
./start.sh
```

**🔑 Important**: Add your OpenAI API key to `backend/.env`:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 2. Extension Development

```bash
# Install dependencies and compile
npm install
npm run compile

# Start watch mode for development
npm run dev
```

### 3. Test the Complete Integration

1. **Start Backend**: Ensure `http://localhost:8000` is running
2. **Press F5**: Open Extension Development Host  
3. **Find 🤖 Icon**: Look in Activity Bar (left sidebar)
4. **Open Chat Panel**: Click the robot icon
5. **Check Status**: Should show "Connected" (green dot)
6. **Start Chatting**: Real AI responses via OpenAI GPT-3.5 Turbo!

## ✨ What's Working Now

- 🤖 **Real AI Conversations**: Backend integration with OpenAI GPT-3.5 Turbo
- 🔄 **LangGraph Processing**: Structured conversation flow (Input → Processing → LLM → Response)
- 🔌 **Live Connection Status**: Real-time backend connectivity monitoring
- 💬 **Persistent Conversations**: Conversation context maintained per session
- ⚡ **Error Handling**: Graceful fallbacks when backend is unavailable
- 🎨 **Native VS Code UI**: Seamless integration with VS Code theming

## Project Structure

```
code-agent/
├── src/                    # VS Code extension source
│   ├── extension.ts       # Main extension file
│   └── test/             # Extension tests
├── backend/               # Python backend
│   ├── main.py           # FastAPI application
│   ├── graph.py          # LangGraph implementation
│   ├── models.py         # Data models
│   ├── start.sh          # Setup script
│   └── requirements.txt  # Python dependencies
├── package.json          # Extension manifest
└── README.md            # This file
```

## Development

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run in development mode
uvicorn main:app --reload
```

**API Documentation**: http://localhost:8000/docs

### Extension Development

```bash
# Watch mode for auto-compilation
npm run watch

# Run tests
npm test

# Package extension
npm run package
```

## API Integration

The extension communicates with the backend via HTTP requests:

```typescript
// Extension sends messages to backend
const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userInput })
});
```

## Configuration

### Backend Configuration (`backend/.env`)

```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
HOST=localhost
```

### Extension Configuration

The extension automatically connects to `http://localhost:8000` by default.

## Features in Detail

### LangGraph Flow

The backend implements a linear conversation flow:

1. **Input Node**: Validates user input
2. **Processing Node**: Adds context and metadata
3. **LLM Node**: Generates AI response
4. **Response Node**: Formats final output

### Chat Interface

- **Modern UI**: Clean, Copilot-inspired design
- **Interactive Elements**: Clickable example prompts
- **Typing Indicators**: Real-time feedback
- **Message History**: Persistent conversation view
- **Responsive Design**: Adapts to panel size

## Troubleshooting

### Backend Issues

1. **Import errors**: Ensure virtual environment is activated
2. **OpenAI API errors**: Check your API key in `.env`
3. **Port conflicts**: Change `PORT` in `.env`

### Extension Issues

1. **TypeScript errors**: Run `npm run compile`
2. **Chat not working**: Ensure backend is running
3. **Panel not appearing**: Check Activity Bar for 🤖 icon

## Future Enhancements

- [ ] **Code Context Integration**: Include selected code in conversations
- [ ] **File Operations**: Create/edit files based on chat
- [ ] **Conversation Persistence**: Save chat history
- [ ] **Streaming Responses**: Real-time response streaming
- [ ] **Multi-language Support**: Support for various programming languages
- [ ] **Custom Prompts**: User-defined prompt templates

## Requirements

### Backend
- Python 3.8+
- OpenAI API key

### Extension
- VS Code 1.102.0+
- Node.js 16+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

---

## Following extension guidelines

Ensure that you've read through the extensions guidelines and follow the best practices for creating your extension.

* [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

## Working with Markdown

You can author your README using Visual Studio Code. Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
