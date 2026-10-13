"""Diffusion inpaint renderer (SD1.5-inpaint ONNX export)."""
from __future__ import annotations

from pathlib import Path

import numpy as np


class SDInpaintRenderer:
    def __init__(self, weights: Path, device: str = "cpu") -> None:
        import onnxruntime as ort

        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if device.startswith("cuda")
            else ["CPUExecutionProvider"]
        )
        self._sess = ort.InferenceSession(str(weights), providers=providers)

    def inpaint(
        self,
        person: np.ndarray,
        warped: np.ndarray,
        mask: np.ndarray,
        steps: int,
        guidance: float,
        seed: int,
    ) -> np.ndarray:
        """Run the diffusion sampler and return an RGB uint8 image.

        The ONNX graph exposes a single `pipeline` input that bundles
        (image, mask, warped, steps, guidance, seed) as a packed fp16
        buffer to avoid per-step round trips on the Python side.
        """
        packed = self._pack(person, warped, mask, steps, guidance, seed)
        out = self._sess.run(None, {"pipeline": packed})[0]
        return np.clip(out, 0, 255).astype(np.uint8)

    @staticmethod
    def _pack(
        person: np.ndarray,
        warped: np.ndarray,
        mask: np.ndarray,
        steps: int,
        guidance: float,
        seed: int,
    ) -> np.ndarray:
        h, w = person.shape[:2]
        scalars = np.array([steps, guidance, seed], dtype=np.float32)
        buf = np.concatenate(
            [
                person.astype(np.float16).reshape(-1),
                warped.astype(np.float16).reshape(-1),
                mask.astype(np.float16).reshape(-1),
                scalars,
            ]
        )
        return buf[None]