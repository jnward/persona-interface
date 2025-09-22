#!/bin/bash
# Start the persona steering backend server

echo "Starting Persona Steering Backend..."
echo "=================================="

cd /workspace/persona-interface/backend

CONFIG_OUTPUT=$(python - <<'PY'
import config
print(config.MODEL_NAME)
print(config.PCA_VECTORS_PATH)
print(config.STEERING_LAYER)
PY
)

MODEL_NAME=$(echo "$CONFIG_OUTPUT" | sed -n '1p')
PCA_PATH=$(echo "$CONFIG_OUTPUT" | sed -n '2p')
STEERING_LAYER=$(echo "$CONFIG_OUTPUT" | sed -n '3p')

echo "Model: ${MODEL_NAME}"
echo "PCA vectors: ${PCA_PATH}"
echo "Steering layer: ${STEERING_LAYER}"
echo "API: http://localhost:8000"
echo "=================================="

# Run the server
python main.py
