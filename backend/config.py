"""
Configuration settings for the persona steering backend.
"""
DEBUG = False

# Model configuration
MODEL_NAME = "google/gemma-3-12b-it"
DEVICE = "cuda:0"

# PCA vectors configuration
PCA_VECTORS_PATH = "/workspace/persona-subspace/roles/pca/layer22_pos23.pt"
STEERING_LAYER = 22

# Generation defaults
DEFAULT_MAX_TOKENS = 100
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_REPETITION_PENALTY = 1.1
DO_SAMPLE = not DEBUG  # Set to False for debug mode

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000