"""Input validation helpers."""
from __future__ import annotations

from pathlib import Path

_ALLOWED = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
_MAX_BYTES = 25 * 1024 * 1024


def validate_image_path(path: Path, role: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"{role} image not found: {path}")
    if path.suffix.lower() not in _ALLOWED:
        raise ValueError(f"{role} has unsupported extension: {path.suffix}")
    if path.stat().st_size > _MAX_BYTES:
        raise ValueError(f"{role} exceeds 25 MB: {path}")
    return path