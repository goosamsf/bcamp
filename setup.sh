#!/bin/bash
# Initial setup: create venv and install all dependencies

cd "$(dirname "$0")"

echo "Setting up Educational Packet Analyzer..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build RAG FAISS index
echo ""
echo "Building RAG knowledge base index..."
python -c "
from rag.vector_store import build_vector_store
build_vector_store()
print('RAG index built successfully!')
"

echo ""
echo "Setup complete!"
echo ""
echo "To run the service:"
echo "  Terminal 1: bash run_backend.sh"
echo "  Terminal 2: bash run_frontend.sh"
echo ""
echo "Don't forget to set your API key in .env:"
echo "  OPENAI_API_KEY=sk-..."
