"""Export a rendered try-on to PNG/JPEG/WebP with quality controls."""
from __future__ import annotations

from pathlib import Path

from PIL import Image


class ExportHandler:
    _FORMATS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}

    def export(self, src: Path, dst: Path, quality: int = 92) -> Path:
        fmt = self._FORMATS.get(dst.suffix.lower())
        if fmt is None:
            raise ValueError(f"unsupported export format: {dst.suffix}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im.save(dst, format=fmt, quality=quality)
        return dst