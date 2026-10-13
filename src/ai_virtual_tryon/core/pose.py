"""Pose estimation interface."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Keypoints:
    xy: np.ndarray      # (K, 2) float32, pixel coords
    conf: np.ndarray    # (K,) float32 in [0, 1]
    score: float        # overall detection score


class PoseEstimator:
    """Protocol-style base — subclasses implement `infer`."""

    name: str = "base"

    def infer(self, person_rgb: np.ndarray) -> Keypoints:
        raise NotImplementedError