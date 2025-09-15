"""
Simple utility functions for loading models and PCA vectors.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Tuple
import numpy as np


def load_model(model_name: str, device: str = "cuda:0") -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """
    Load model and tokenizer.

    Args:
        model_name: HuggingFace model identifier
        device: Device to load model on

    Returns:
        Tuple of (model, tokenizer)
    """
    print(f"Loading tokenizer for {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Set padding token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    print(f"Loading model {model_name} to {device}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.bfloat16
    )
    model = model.to(device)
    model.eval()

    # Gemma3 uses 'hidden_act_dim' instead of 'hidden_size'
    hidden_dim = getattr(model.config, 'hidden_size', None) or getattr(model.config, 'hidden_act_dim', 'unknown')
    print(f"Model loaded successfully. Hidden dimension: {hidden_dim}")
    return model, tokenizer


def load_pca_vectors(path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load PCA components from a .pt file.

    Args:
        path: Path to the .pt file containing PCA components

    Returns:
        Tuple of (components, variance_explained) where:
        - components: numpy array of shape (n_components, hidden_size)
        - variance_explained: numpy array of shape (n_components,)
    """
    print(f"Loading PCA vectors from {path}...")
    data = torch.load(path, weights_only=False)

    # The file contains a dict with 'pca' key containing the sklearn PCA object
    pca = data['pca']
    components = pca.components_  # Shape: (n_components, hidden_size)

    # Get variance explained for each component
    variance_explained = pca.explained_variance_ratio_

    print(f"Loaded {components.shape[0]} PCA components")
    print(f"Shape: {components.shape}")
    print(f"Variance explained by first 10 PCs: {variance_explained[:10].sum():.3f}")

    return components, variance_explained