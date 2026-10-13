"""UI-facing handler: translates a button click into a pipeline job."""
from __future__ import annotations

from pathlib import Path

from ai_virtual_tryon.core.pipeline import TryOnRequest
from ai_virtual_tryon.services.pipeline_service import PipelineService
from ai_virtual_tryon.utils.validation import validate_image_path


class TryOnHandler:
    def __init__(self, service: PipelineService) -> None:
        self._service = service

    def handle(
        self,
        person: Path,
        garment: Path,
        out_dir: Path,
        seed: int | None = None,
    ) -> str:
        validate_image_path(person, role="person")
        validate_image_path(garment, role="garment")
        out = out_dir / f"tryon_{person.stem}_{garment.stem}.png"
        req = TryOnRequest(person_path=person, garment_path=garment, out_path=out, seed=seed)
        future = self._service.submit(req)
        return future.result().output_path.as_posix()