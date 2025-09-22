# Persona Interface

Interactive demo of steering with model persona PC vectors, based on Christina Lu’s work: https://github.com/lu-christina/persona-subspace

## Backend (FastAPI + Gemma)

```bash
cd backend
uv sync
export HF_TOKEN="hf_your_token_here"  # Hugging Face access token for Gemma
uv run ./run_server.sh
```

The API listens on `http://localhost:8000`.

## Frontend (static build)

Serve the prebuilt bundle from `frontend/out` with any static file server. For example:

```bash
python -m http.server --directory frontend/out 3000
```

Open `http://localhost:3000` in your browser while the backend is running.
