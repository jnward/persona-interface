"""
Minimal activation steering implementation for PC-based steering.
Focused on our specific needs: layer 22, multiple PCs, addition only.
"""

import torch
import numpy as np
from contextlib import contextmanager
from typing import Dict, List, Optional


class SimpleActivationSteering:
    """
    Simplified activation steering for Gemma-3-12b at layer 22.
    Applies PC vectors with specified magnitudes using addition intervention.
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
        self._hooks = []

        # Prepare the combined steering vector
        self.steering_vector = self._prepare_steering_vector()

    def _prepare_steering_vector(self) -> torch.Tensor:
        """
        Combine multiple PC vectors according to their magnitudes.

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

        # Add each PC vector scaled by its magnitude
        for pc_index, magnitude in self.pc_values.items():
            if pc_index < 0 or pc_index >= len(self.pca_vectors):
                print(f"Warning: PC{pc_index+1} out of range, skipping")
                continue

            # Get the PC vector and convert to tensor
            pc_vector = torch.tensor(
                self.pca_vectors[pc_index],
                device=device,
                dtype=dtype
            )

            # Add scaled vector to the combined steering vector
            steering_vector += magnitude * pc_vector

        return steering_vector

    def _get_layer_module(self):
        """
        Get the specific layer module for Gemma model.
        Gemma uses: model.language_model.layers[layer_index]
        """
        # For Gemma-3-12b, the layers are at model.language_model.layers
        if hasattr(self.model, 'language_model'):
            # This is the path for Gemma models
            layers = self.model.language_model.layers
        elif hasattr(self.model, 'model') and hasattr(self.model.model, 'layers'):
            # Alternative path for some model configurations
            layers = self.model.model.layers
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
                modified_hidden_states = hidden_states + self.steering_vector
                return (modified_hidden_states, *output[1:])
            else:
                # Direct tensor output
                return output + self.steering_vector

        return hook_fn

    def __enter__(self):
        """
        Register the steering hook when entering context.
        """
        layer_module = self._get_layer_module()
        hook = layer_module.register_forward_hook(self._create_hook())
        self._hooks.append(hook)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Remove hooks when exiting context.
        """
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()


@contextmanager
def apply_steering(
    model: torch.nn.Module,
    pca_vectors: np.ndarray,
    pc_values: Dict[int, float],
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
        pca_vectors: Array of PC vectors
        pc_values: Dict mapping PC index to magnitude
        layer: Which layer to apply steering at
    """
    if not pc_values:
        # No steering requested, just yield without modification
        yield
    else:
        # Apply steering
        with SimpleActivationSteering(model, pca_vectors, pc_values, layer):
            yield


def validate_pc_values(pc_values: Dict[int, float], num_components: int) -> Dict[int, float]:
    """
    Validate and clean PC values.

    Args:
        pc_values: Dict mapping PC index to magnitude
        num_components: Total number of available PC components

    Returns:
        Cleaned dict with valid PC indices only
    """
    valid_values = {}

    for pc_index, magnitude in pc_values.items():
        if pc_index < 0:
            print(f"Warning: Negative PC index {pc_index} ignored")
            continue
        if pc_index >= num_components:
            print(f"Warning: PC{pc_index+1} exceeds available components ({num_components}), ignored")
            continue
        if abs(magnitude) < 1e-6:
            # Skip near-zero values
            continue

        valid_values[pc_index] = magnitude

    return valid_values