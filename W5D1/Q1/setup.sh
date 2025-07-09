#!/bin/bash

# Setup script for local development

echo "Setting up local development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file and add your OPENAI_API_KEY"
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY"
echo "2. Activate the virtual environment: source .venv/bin/activate"
echo "3. Run the API: uvicorn src.api.main:app --reload --port 8000"
echo "4. Test the API: curl http://localhost:8000/api/v1/health" 