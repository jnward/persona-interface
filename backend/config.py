"""Configuration settings for the persona steering backend."""

import json
from pathlib import Path
from typing import Any, Dict

DEBUG = False

BACKEND_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = BACKEND_ROOT / "model_config.json"


def _load_model_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Model configuration file not found at {CONFIG_FILE}."
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    current_model = data.get("current_model")
    models = data.get("models", {})

    if not current_model:
        raise ValueError("`current_model` is not set in model_config.json")

    if current_model not in models:
        raise ValueError(
            f"Model '{current_model}' not found in model_config.json."
        )

    settings = models[current_model]

    required_keys = ["pca_path"]
    missing = [key for key in required_keys if key not in settings]
    if missing:
        raise ValueError(
            f"Model '{current_model}' is missing required keys: {', '.join(missing)}"
        )

    return {
        "name": current_model,
        "settings": settings,
        "available_models": models,
    }


_CONFIG = _load_model_config()

# Model configuration
MODEL_NAME = _CONFIG["name"]
DEVICE = _CONFIG["settings"].get("device", "auto")

# PCA vectors configuration
PCA_VECTORS_PATH = str(
    BACKEND_ROOT / _CONFIG["settings"].get("pca_path", "")
)
STEERING_LAYER = _CONFIG["settings"].get("steering_layer", 22)

# Export list of available models for convenience
AVAILABLE_MODELS = list(_CONFIG["available_models"].keys())

# Generation defaults
DEFAULT_MAX_TOKENS = 100
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_REPETITION_PENALTY = 1.1
DO_SAMPLE = not DEBUG  # Set to False for debug mode

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
