#!/bin/bash
# Start the persona steering backend server

echo "Starting Persona Steering Backend..."
echo "=================================="
echo "Model: google/gemma-3-12b-it"
echo "PCA vectors: layer 22"
echo "API: http://localhost:8000"
echo "=================================="

cd /workspace/persona-interface/backend

# Run the server
python main.py