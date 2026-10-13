"""TOML config loader with env-var overrides."""
from __future__ import annotations

import os
import tomllib
from pathlib import Path

from pydantic import ValidationError

from ai_virtual_tryon.config.schema import StudioConfig


class ConfigError(RuntimeError):
    """Raised when the config file is malformed or missing."""


def load_config(path: Path) -> StudioConfig:
    if not path.exists():
        raise ConfigError(f"config not found: {path}")
    raw = tomllib.loads(path.read_text(encoding="utf-8"))

    # Env overrides: TRYON_DEVICE, TRYON_WORKERS, TRYON_WEIGHTS_DIR
    runtime = raw.setdefault("runtime", {})
    if dev := os.environ.get("TRYON_DEVICE"):
        runtime["device"] = dev
    if workers := os.environ.get("TRYON_WORKERS"):
        runtime["workers"] = int(workers)
    models = raw.setdefault("models", {})
    if wd := os.environ.get("TRYON_WEIGHTS_DIR"):
        models["weights_dir"] = wd

    try:
        return StudioConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"invalid config at {path}: {exc}") from exc