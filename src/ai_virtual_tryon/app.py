"""Qt entrypoint for the try-on studio desktop app.

Boots the Qt application, wires the main window to a PipelineService
running on a background worker pool, and hands control to the event loop.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ai_virtual_tryon.config.loader import load_config
from ai_virtual_tryon.services.pipeline_service import PipelineService
from ai_virtual_tryon.ui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv)
    cfg = load_config(Path("config/default.toml"))

    app = QApplication(argv)
    app.setApplicationName("AI Virtual Try-On Studio")
    app.setOrganizationName("tryon-studio")

    service = PipelineService(cfg)
    service.start()

    window = MainWindow(service=service, config=cfg)
    window.show()

    try:
        return app.exec()
    finally:
        service.stop()


if __name__ == "__main__":
    raise SystemExit(main())