"""Image helpers shared across stages."""
from __future__ import annotations

import numpy as np


def normalize_orientation(rgb: np.ndarray) -> np.ndarray:
    """Ensure portrait orientation for person photos.

    If the image is landscape, rotate 90 degrees clockwise so the pose
    estimator sees a vertical subject. Garment flat-lays should NOT be
    passed through this — callers choose.
    """
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"expected HWC RGB, got shape {rgb.shape}")
    if rgb.shape[1] > rgb.shape[0]:
        return np.rot90(rgb, k=-1).copy()
    return rgb