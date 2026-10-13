"""DWPose-style ONNX pose estimator.

Runtime: onnxruntime >= 1.18. Accepts BGR->RGB uint8 HWC, returns COCO-17
keypoints rescaled to the input resolution.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ai_virtual_tryon.core.pose import Keypoints, PoseEstimator


class OnnxPoseEstimator(PoseEstimator):
    name = "dwpose-onnx"

    _MEAN = np.array([123.675, 116.28, 103.53], dtype=np.float32)
    _STD = np.array([58.395, 57.12, 57.375], dtype=np.float32)

    def __init__(self, weights: Path, device: str = "cpu") -> None:
        import onnxruntime as ort

        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if device.startswith("cuda")
            else ["CPUExecutionProvider"]
        )
        self._sess = ort.InferenceSession(str(weights), providers=providers)

    def infer(self, person_rgb: np.ndarray) -> Keypoints:
        h, w = person_rgb.shape[:2]
        inp, scale = self._preprocess(person_rgb)
        heatmaps = self._sess.run(None, {self._sess.get_inputs()[0].name: inp})[0]
        return self._decode(heatmaps, scale, (h, w))

    def _preprocess(self, rgb: np.ndarray) -> tuple[np.ndarray, float]:
        target = (256, 192)  # (H, W) — DWPose input
        import cv2

        resized = cv2.resize(rgb, (target[1], target[0]), interpolation=cv2.INTER_LINEAR)
        x = (resized.astype(np.float32) - self._MEAN) / self._STD
        x = x.transpose(2, 0, 1)[None]
        return x.astype(np.float32), target[1] / rgb.shape[1]

    def _decode(self, heatmaps: np.ndarray, scale: float, orig: tuple[int, int]) -> Keypoints:
        hm = heatmaps[0]  # (K, h, w)
        k, hh, ww = hm.shape
        flat = hm.reshape(k, -1)
        idx = flat.argmax(axis=1)
        conf = flat[np.arange(k), idx]
        ys, xs = np.divmod(idx, ww)
        xy = np.stack([xs, ys], axis=1).astype(np.float32)
        xy *= np.array([orig[1] / ww, orig[0] / hh], dtype=np.float32)
        return Keypoints(xy=xy, conf=conf.astype(np.float32), score=float(conf.mean()))