"""Central registry that resolves backend names to loaded model objects.

Backends are lazy: the registry stores factory callables and instantiates
on first use so the UI boots without loading multi-GB weights.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ai_virtual_tryon.config.schema import StudioConfig


@dataclass
class _Lazy:
    factory: Callable[[], Any]
    _instance: Any | None = field(default=None, init=False)

    def get(self) -> Any:
        if self._instance is None:
            self._instance = self.factory()
        return self._instance


class ModelRegistry:
    def __init__(self, cfg: StudioConfig) -> None:
        self._cfg = cfg
        self._slots: dict[str, _Lazy] = {}
        self._register_defaults()

    def register(self, slot: str, factory: Callable[[], Any]) -> None:
        self._slots[slot] = _Lazy(factory)

    @property
    def pose(self) -> Any:
        return self._slots["pose"].get()

    @property
    def warp(self) -> Any:
        return self._slots["warp"].get()

    @property
    def render(self) -> Any:
        return self._slots["render"].get()

    def _register_defaults(self) -> None:
        # Factories are imported lazily to keep import time low.
        self.register("pose", lambda: _load_pose(self._cfg))
        self.register("warp", lambda: _load_warp(self._cfg))
        self.register("render", lambda: _load_render(self._cfg))


def _load_pose(cfg: StudioConfig) -> Any:
    from ai_virtual_tryon.models.pose_onnx import OnnxPoseEstimator

    return OnnxPoseEstimator(cfg.models.weights_dir / "dwpose.onnx", device=cfg.runtime.device)


def _load_warp(cfg: StudioConfig) -> Any:
    from ai_virtual_tryon.models.warp_viton import VitonWarp

    return VitonWarp(cfg.models.weights_dir / "viton_hd.onnx", device=cfg.runtime.device)


def _load_render(cfg: StudioConfig) -> Any:
    from ai_virtual_tryon.models.render_sd import SDInpaintRenderer

    return SDInpaintRenderer(cfg.models.weights_dir / "sd15_inpaint.onnx", device=cfg.runtime.device)