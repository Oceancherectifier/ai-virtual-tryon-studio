"""Main Qt window for the studio."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ai_virtual_tryon.config.schema import StudioConfig
from ai_virtual_tryon.handlers.tryon_handler import TryOnHandler
from ai_virtual_tryon.services.pipeline_service import PipelineService


class MainWindow(QMainWindow):
    def __init__(self, service: PipelineService, config: StudioConfig) -> None:
        super().__init__()
        self._config = config
        self._handler = TryOnHandler(service)
        self._person: Path | None = None
        self._garment: Path | None = None

        self.setWindowTitle("AI Virtual Try-On Studio")
        self.resize(118