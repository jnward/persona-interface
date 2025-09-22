#!/usr/bin/env python3
"""Utility for trimming persona PCA checkpoints to a fixed number of components."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Trim a persona PCA checkpoint to the requested number of principal "
            "components and optionally remove the per-position raw vectors."
        )
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the source PCA .pt file",
    )
    parser.add_argument(
        "--components",
        "-c",
        type=int,
        required=True,
        help="Number of principal components to keep",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional output path. Defaults to overwriting the input file in place.",
    )
    parser.add_argument(
        "--keep-vectors",
        action="store_true",
        help=(
            "Keep the 'vectors' field (trimmed to the requested components). "
            "By default this field is removed entirely to minimise file size."
        ),
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help=(
            "Do not create an automatic .bak copy when writing in-place. "
            "Ignored when --output is provided."
        ),
    )
    return parser.parse_args()


def ensure_backup(path: Path) -> Path:
    """Create a non-destructive backup alongside *path* and return it."""

    suffix = path.suffix or ""
    base = path.with_suffix("")
    counter = 0

    while True:
        candidate = base.with_suffix(f"{suffix}.bak" + (str(counter) if counter else ""))
        if not candidate.exists():
            shutil.copy2(path, candidate)
            return candidate
        counter += 1


def _trim_numpy(array: np.ndarray, count: int) -> np.ndarray:
    return array[..., :count].copy()


def _trim_tensor(tensor: torch.Tensor, count: int) -> torch.Tensor:
    if tensor.shape[0] <= count:
        return tensor.clone()
    return tensor[:count].clone()


def trim_vectors(vectors: Dict[str, Iterable[torch.Tensor]], count: int) -> Dict[str, list[torch.Tensor]]:
    trimmed: Dict[str, list[torch.Tensor]] = {}
    for key, tensor_list in vectors.items():
        trimmed[key] = [_trim_tensor(t, count) for t in tensor_list]
    return trimmed


def trim_checkpoint(data: dict, keep_components: int, keep_vectors: bool) -> Tuple[int, int]:
    if "pca" not in data:
        raise KeyError("Checkpoint does not contain a 'pca' entry")

    pca = data["pca"]
    original_components = int(pca.components_.shape[0])

    if keep_components <= 0:
        raise ValueError("--components must be positive")

    if keep_components >= original_components:
        raise ValueError(
            f"Requested {keep_components} components, but checkpoint only has "
            f"{original_components}. Nothing to trim."
        )

    # Trim PCA-related arrays
    pca.components_ = pca.components_[:keep_components]
    pca.explained_variance_ = pca.explained_variance_[:keep_components]
    pca.explained_variance_ratio_ = pca.explained_variance_ratio_[:keep_components]
    pca.singular_values_ = pca.singular_values_[:keep_components]
    if hasattr(pca, "noise_variance_") and pca.noise_variance_ is not None:
        nv = pca.noise_variance_
        if isinstance(nv, np.ndarray):
            pca.noise_variance_ = nv[:keep_components]

    pca.n_components = keep_components
    pca.n_components_ = keep_components

    # Additional metadata arrays saved alongside the PCA object
    if "variance_explained" in data:
        data["variance_explained"] = data["variance_explained"][:keep_components]
    if "pca_transformed" in data:
        data["pca_transformed"] = data["pca_transformed"][:, :keep_components]
    data["n_components"] = keep_components

    if "vectors" in data:
        if keep_vectors:
            data["vectors"] = trim_vectors(data["vectors"], keep_components)
        else:
            data.pop("vectors")

    return original_components, keep_components


def save_checkpoint(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    torch.save(data, tmp_path)
    tmp_path.replace(output_path)


def main() -> None:
    args = parse_args()

    input_path = args.input.resolve()
    output_path = args.output.resolve() if args.output else input_path

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Loading PCA checkpoint from {input_path}")
    data = torch.load(input_path, map_location="cpu", weights_only=False)

    original, kept = trim_checkpoint(
        data,
        keep_components=args.components,
        keep_vectors=args.keep_vectors,
    )

    if output_path == input_path and not args.no_backup:
        backup_path = ensure_backup(input_path)
        print(f"Created backup at {backup_path}")

    print(f"Saving trimmed checkpoint with {kept}/{original} components to {output_path}")
    save_checkpoint(data, output_path)
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - surface clear error to CLI
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
