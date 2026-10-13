"""End-to-end try-on pipeline: ingest -> pose -> warp -> render -> composite.

Stages are pure functions over numpy arrays so they can be unit-tested
without a GPU. The pipeline itself is synchronous; callers (services)
own concurrency.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ai_virtual_tryon.config.schema import StudioConfig
from ai_virtual_tryon.models.registry import ModelRegistry


@dataclass(frozen=True)
class TryOnRequest:
    person_path: Path
    garment_path: Path
    out_path: Path
    seed: int | None = None


@dataclass(frozen=True)
class TryOnResult:
    output_path: Path
    ms: int
    stage_timings: dict[str, int]


class TryOnPipeline:
    def __init__(self, cfg: StudioConfig, registry: ModelRegistry) -> None:
        self._cfg = cfg
        self._registry = registry

    def run(self, req: TryOnRequest) -> TryOnResult:
        t0 = time.perf_counter()
        timings: dict[str, int] = {}

        person = self._ingest(req.person_path)
        garment = self._ingest(req.garment_path)
        timings["ingest"] = _ms(t0)

        t = time.perf_counter()
        keypoints = self._registry.pose.infer(person)
        timings["pose"] = _ms(t)

        t = time.perf_counter()
        warped, mask = self._registry.warp.warp(garment, keypoints, self._cfg.render.resolution)
        timings["warp"] = _ms(t)

        t = time.perf_counter()
        rendered = self._registry.render.inpaint(
            person=person,
            warped=warped,
            mask=mask,
            steps=self._cfg.render.steps,
            guidance=self._cfg.render.guidance,
            seed=req.seed if req.seed is not None else self._cfg.render.seed,
        )
        timings["render"] = _ms(t)

        t = time.perf_counter()
        composed = self._composite(person, rendered, mask)
        timings["composite"] = _ms(t)

        _write_png(req.out_path, composed)
        return TryOnResult(output_path=req.out_path, ms=_ms(t0), stage_timings=timings)

    @staticmethod
    def _ingest(path: Path) -> np.ndarray:
        import cv2

        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"unreadable image: {path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def _composite(person: np.ndarray, rendered: np.ndarray, mask: np.ndarray) -> np.ndarray:
        alpha = (mask.astype(np.float32) / 255.0)[..., None]
        out = rendered.astype(np.float32) * alpha + person.astype(np.float32) * (1.0 - alpha)
        return np.clip(out, 0, 255).astype(np.uint8)


def _ms(since: float) -> int:
    return int((time.perf_counter() - since) * 1000)


def _write_png(path: Path, rgb: np.ndarray) -> None:
    import cv2

    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))