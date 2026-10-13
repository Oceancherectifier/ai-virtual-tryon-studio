"""VITON-HD style thin-plate-spline garment warp."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ai_virtual_tryon.core.pose import Keypoints


class VitonWarp:
    """Warp a flat-lay garment image onto a person's torso.

    Uses the ONNX TPS regressor to predict control-point offsets, then
    applies a grid_sample-style bilinear warp to produce (garment_rgb,
    mask). Returns uint8 HWC RGB and uint8 HW mask.
    """

    def __init__(self, weights: Path, device: str = "cpu") -> None:
        import onnxruntime as ort

        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if device.startswith("cuda")
            else ["CPUExecutionProvider"]
        )
        self._sess = ort.InferenceSession(str(weights), providers=providers)

    def warp(
        self,
        garment_rgb: np.ndarray,
        keypoints: Keypoints,
        resolution: tuple[int, int],
    ) -> tuple[np.ndarray, np.ndarray]:
        import cv2

        target_w, target_h = resolution
        g = cv2.resize(garment_rgb, (target_w, target_h), interpolation=cv2.INTER_AREA)
        kp = keypoints.xy.astype(np.float32)[None]
        offsets = self._sess.run(None, {"keypoints": kp})[0][0]  # (P, 2)
        grid = self._grid(target_w, target_h)
        src = grid + offsets.reshape(-1, 2)[: grid.shape[0]]
        warped = cv2.remap(
            g, src[..., 0], src[..., 1], interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0),
        )
        mask = cv2.remap(
            np.full_like(g[..., 0], 255, dtype=np.uint8),
            src[..., 0], src[..., 1], interpolation=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT, borderValue=0,
        )
        return warped, mask

    @staticmethod
    def _grid(w: int, h: int) -> np.ndarray:
        ys, xs = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
        return np.stack([xs, ys], axis=-1).astype(np.float32)