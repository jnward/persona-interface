"""
FastAPI backend for persona steering interface.
Single endpoint for stateless text generation with optional PC-based steering.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import traceback

import config
from schemas import GenerationRequest, GenerationResponse
from model_utils import load_model, load_pca_vectors
from generation import generate_text


# Global variables for model and PCA vectors
MODEL = None
TOKENIZER = None
PCA_COMPONENTS = None
PCA_VARIANCE = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - load model on startup.
    """
    global MODEL, TOKENIZER, PCA_COMPONENTS, PCA_VARIANCE

    # Startup
    print("Starting persona steering backend...")
    try:
        MODEL, TOKENIZER = load_model(config.MODEL_NAME, config.DEVICE)
        PCA_COMPONENTS, PCA_VARIANCE = load_pca_vectors(config.PCA_VECTORS_PATH)
        print("Model and PCA vectors loaded successfully!")
    except Exception as e:
        print(f"Failed to initialize: {e}")
        traceback.print_exc()
        raise

    yield

    # Shutdown
    print("Shutting down persona steering backend...")


# Create FastAPI app
app = FastAPI(
    title="Persona Steering API",
    description="API for steering Gemma-3-12b with PC vectors",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "model_loaded": MODEL is not None,
        "pca_loaded": PCA_COMPONENTS is not None
    }


@app.post("/api/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest):
    """
    Generate text with optional PC-based steering.

    This is the single stateless endpoint that handles all generation cases:
    - Normal generation (with num_tokens)
    - Step-by-step mode (num_tokens=1)
    - Regeneration (frontend removes last message)
    - Mid-generation steering changes (frontend sends partial message)
    """
    try:
        # Check that model is loaded
        if MODEL is None or TOKENIZER is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        # Convert message objects to dicts
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Extract PC values from steering config
        pc_values = request.steering_config.get("pc_values", {})

        # For Phase 1, we'll just do basic generation without steering
        # In Phase 2, we'll use the pc_values to apply steering
        content, terminating = generate_text(
            model=MODEL,
            tokenizer=TOKENIZER,
            messages=messages,
            num_tokens=request.num_tokens,
            steering_config=request.steering_config if pc_values else None,
            is_partial=request.is_partial
        )

        return GenerationResponse(
            content=content,
            terminating=terminating
        )

    except Exception as e:
        print(f"Error during generation: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/info")
async def get_info():
    """
    Get information about loaded model and PCA components.
    Useful for debugging and frontend initialization.
    """
    if MODEL is None:
        return {"error": "Model not loaded"}

    num_pcs = len(PCA_COMPONENTS) if PCA_COMPONENTS is not None else 0

    return {
        "model_name": config.MODEL_NAME,
        "steering_layer": config.STEERING_LAYER,
        "num_pca_components": num_pcs,
        "variance_explained_first_10": (
            PCA_VARIANCE[:10].tolist() if PCA_VARIANCE is not None else []
        ),
        "total_variance_first_10": (
            float(PCA_VARIANCE[:10].sum()) if PCA_VARIANCE is not None else 0
        )
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=False  # Set to True for development
    )