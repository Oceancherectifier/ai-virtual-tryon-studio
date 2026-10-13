"""Pydantic schema for studio configuration."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RenderConfig(BaseModel):
    resolution: tuple[int, int] = (768, 1024)
    steps: int = Field(default=28, ge=8, le=80)
    guidance: float = Field(default=4.5, ge=1.0, le=12.0)
    seed: int = -1
    preserve_face: bool = True


class ModelConfig(BaseModel):
    pose_backend: str = "dwpose-onnx"
    warp_backend: str = "viton-hd"
    render_backend: str = "sd15-inpaint"
    weights_dir: Path = Path("models/weights")


class RuntimeConfig(BaseModel):
    device: str = "cuda:0"
    workers: int = Field(default=2, ge=1, le=8)
    max_vram_gb: float = 8.0


class StudioConfig(BaseModel):
    render: RenderConfig = RenderConfig()
    models: ModelConfig = ModelConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    plugin_dirs: list[Path] = [Path("plugins")]