#!/bin/bash
# Run the Streamlit frontend

cd "$(dirname "$0")"
source .venv/bin/activate

echo "Starting Educational Packet Analyzer Frontend..."
echo "Frontend: http://localhost:8501"
echo ""

streamlit run frontend/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
