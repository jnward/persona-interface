"""
Minimal activation steering implementation for PC-based steering.
Focused on our specific needs: layer 22, multiple PCs, simple addition.
"""

import torch
import numpy as np
from contextlib import contextmanager
from typing import Dict, Optional


class SteeringHook:
    """
    Simple steering hook for Gemma-3-12b at layer 22.
    Applies PC vectors with specified magnitudes using naive addition.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        pca_vectors: np.ndarray,
        pc_values: Dict[int, float],
        layer: int = 22
    ):
        """
        Initialize steering with PC vectors and magnitudes.

        Args:
            model: The Gemma model
            pca_vectors: Array of PC vectors, shape (n_components, hidden_size)
            pc_values: Dict mapping PC index to magnitude (e.g., {0: 1000, 3: -2000})
            layer: Which layer to apply steering at (default: 22)
        """
        self.model = model
        self.pca_vectors = pca_vectors
        self.pc_values = pc_values
        self.layer = layer
        self._hook_handle = None

        # Prepare the combined steering vector
        self.steering_vector = self._prepare_steering_vector()

    def _prepare_steering_vector(self) -> torch.Tensor:
        """
        Combine multiple PC vectors according to their magnitudes using simple addition.

        Returns:
            Combined steering vector of shape (hidden_size,)
        """
        # Get model device and dtype
        p = next(self.model.parameters())
        device = p.device
        dtype = p.dtype

        # Initialize with zeros
        hidden_size = self.pca_vectors.shape[1]
        steering_vector = torch.zeros(hidden_size, device=device, dtype=dtype)

        # Naively add each PC vector scaled by its magnitude
        for pc_index, magnitude in self.pc_values.items():
            if pc_index < 0 or pc_index >= len(self.pca_vectors):
                print(f"Warning: PC{pc_index+1} out of range (0-{len(self.pca_vectors)-1}), skipping")
                continue

            # Get the PC vector and convert to tensor
            pc_vector = torch.tensor(
                self.pca_vectors[pc_index],
                device=device,
                dtype=dtype
            )

            # Add scaled vector to the combined steering vector (simple addition)
            steering_vector += magnitude * pc_vector

        return steering_vector

    def _get_layer_module(self):
        """
        Get the specific layer module for Gemma model.
        Gemma uses: model.model.layers[layer_index]
        """
        # For Gemma models, the layers are at model.model.layers
        if hasattr(self.model, 'model') and hasattr(self.model.model, 'layers'):
            layers = self.model.model.layers
        elif hasattr(self.model, 'language_model') and hasattr(self.model.language_model, 'layers'):
            # Alternative path for some model configurations
            layers = self.model.language_model.layers
        else:
            raise ValueError(
                "Could not find layer list. Model structure may be different than expected."
            )

        if self.layer < 0 or self.layer >= len(layers):
            raise ValueError(f"Layer {self.layer} out of range (0-{len(layers)-1})")

        return layers[self.layer]

    def _create_hook(self):
        """
        Create a forward hook that adds the steering vector to activations.
        """
        def hook_fn(module, input, output):
            # Handle different output formats (tensor vs tuple)
            if isinstance(output, tuple):
                # Many transformer layers return (hidden_states, ...)
                hidden_states = output[0]
                # Add steering vector to all positions
                modified_hidden_states = hidden_states + self.steering_vector
                return (modified_hidden_states, *output[1:])
            else:
                # Direct tensor output
                return output + self.steering_vector

        return hook_fn

    def register(self):
        """
        Register the steering hook.
        """
        if self._hook_handle is not None:
            raise RuntimeError("Hook already registered")

        layer_module = self._get_layer_module()
        self._hook_handle = layer_module.register_forward_hook(self._create_hook())

    def remove(self):
        """
        Remove the steering hook.
        """
        if self._hook_handle is not None:
            self._hook_handle.remove()
            self._hook_handle = None


@contextmanager
def apply_steering(
    model: torch.nn.Module,
    pca_vectors: Optional[np.ndarray],
    pc_values: Optional[Dict[int, float]],
    layer: int = 22
):
    """
    Context manager for applying PC-based steering during generation.

    Usage:
        with apply_steering(model, pca_vectors, {0: 1000, 3: -2000}):
            # Generate text with steering applied
            outputs = model.generate(...)

    Args:
        model: The language model
        pca_vectors: Array of PC vectors (can be None if no steering)
        pc_values: Dict mapping PC index to magnitude (can be None or empty)
        layer: Which layer to apply steering at
    """
    # Check if steering is actually requested
    if not pc_values or pca_vectors is None:
        # No steering requested, just yield without modification
        yield
    else:
        # Apply steering
        hook = SteeringHook(model, pca_vectors, pc_values, layer)
        hook.register()
        try:
            yield
        finally:
            hook.remove()