"""Watch the weights directory and hot-reload on new model packs."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class _Handler(FileSystemEventHandler):
    def __init__(self, on_change: Callable[[Path], None]) -> None:
        self._on_change = on_change

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(str(event.src_path))
        if path.suffix in {".onnx", ".safetensors"}:
            self._on_change(path)


class ModelWatcher:
    def __init__(self, weights_dir: Path, on_change: Callable[[Path], None]) -> None:
        self._dir = weights_dir
        self._observer = Observer()
        self._observer.schedule(_Handler(on_change), str(weights_dir), recursive=False)

    def start(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join(timeout=2.0)