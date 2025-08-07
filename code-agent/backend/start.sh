#!/bin/bash

# Code Agent Backend Startup Script

echo "🚀 Starting Code Agent Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
if pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Trying alternative approach..."
    echo "🔧 Installing packages individually..."
    pip install fastapi uvicorn python-dotenv pydantic requests
    pip install "openai>=1.6.1,<2.0.0"
    pip install langchain langchain-openai langgraph
    pip install python-multipart
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "🔑 Please edit .env file and add your OPENAI_API_KEY"
    echo "📝 You can start with a test key and replace it later."
    echo ""
fi

# Check if OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "⚠️  OPENAI_API_KEY not set in .env file"
    echo "🔑 The server will start but AI responses won't work without a valid key"
    echo "💡 You can test the health endpoint at http://localhost:8000/health"
fi

echo "✅ Environment setup complete!"

# Verify that packages are installed
echo "🔍 Verifying installation..."
if python -c "import fastapi, uvicorn, openai, langchain, langgraph" 2>/dev/null; then
    echo "✅ All required packages are available!"
else
    echo "❌ Some packages are missing. Please check the installation."
    echo "📋 You can try installing manually:"
    echo "   pip install fastapi uvicorn python-dotenv"
    echo "   pip install 'openai>=1.6.1,<2.0.0'"
    echo "   pip install langchain langchain-openai langgraph"
    exit 1
fi

echo "🏃 Starting FastAPI server..."
echo ""
echo "🌐 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""

# Start the server
python main.py
