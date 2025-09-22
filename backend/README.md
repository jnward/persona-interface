# Persona Steering Backend

Minimal FastAPI backend for steering Gemma-3 with PCA-based persona vectors.

## Phase 1 Status: ✅ Complete

### What's Implemented
- ✅ Single stateless `/api/generate` endpoint
- ✅ Model loading (Gemma-3-12b-it)
- ✅ PCA vector loading from pre-computed file
- ✅ Basic text generation without steering
- ✅ Chat template application for multi-turn conversations
- ✅ End-of-turn token detection
- ✅ Support for step-by-step generation (num_tokens=1)

### Project Structure
```
backend/
├── main.py              # FastAPI application with single endpoint
├── generation.py        # Text generation logic
├── model_utils.py       # Model and PCA vector loading
├── steering.py          # Steering implementation (ready for Phase 2)
├── schemas.py          # Pydantic models
├── config.py           # Configuration settings
├── requirements.txt    # Dependencies
├── test_api.py        # Test script
└── run_server.sh      # Server startup script
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
./run_server.sh
# Or directly:
python main.py
```

The server will:
1. Read `model_config.json` to determine which Gemma model to load
2. Resolve the target device (set `"device": "auto"` to pick CUDA → MPS → CPU)
3. Load the selected model (defaults to `google/gemma-3-12b-it`)
4. Load the matching PCA vectors from `backend/pca/<model>_pca.pt`
5. Start listening on `http://localhost:8000`

### Selecting a Model

Edit `backend/model_config.json` to switch between `google/gemma-3-12b-it` and `google/gemma-3-4b-it` (or add new entries). Update `current_model` and ensure the `pca_path` points to the corresponding PCA file.

### 3. Test the API
```bash
# In another terminal:
python test_api.py
```

## API Endpoints

### POST /api/generate
Generate text with optional steering (steering not active in Phase 1).

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "steering_config": {"pc_values": {}},
  "num_tokens": 50
}
```

**Response:**
```json
{
  "content": "Hi there! How can I help you today?",
  "terminating": true
}
```

### GET /api/info
Get information about loaded model and PCA components.

### GET /
Health check endpoint.

## Next Steps (Phase 2)

To enable steering, we need to:
1. Update `generation.py` to use steering context manager
2. Test with various PC values
3. Handle multiple concurrent PCs (may need scaling/normalization)

The steering implementation is already prepared in `steering.py` and ready to be integrated.
