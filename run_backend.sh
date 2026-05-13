#!/bin/bash
# Run the FastAPI backend server

cd "$(dirname "$0")"
source .venv/bin/activate

echo "Starting Educational Packet Analyzer Backend..."
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

python -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
