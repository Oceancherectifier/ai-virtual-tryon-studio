"""Threaded wrapper around TryOnPipeline.

Owns a small worker pool. Exposes an async `submit` that returns a future
and a synchronous `run_sync` for the CLI. Cancels in-flight jobs on
`stop()` and drains the pool.
"""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from ai_virtual_tryon.config.schema import StudioConfig
from ai_virtual_tryon.core.pipeline import TryOnPipeline, TryOnRequest, TryOnResult
from ai_virtual_tryon.models.registry import ModelRegistry


class PipelineService:
    def __init__(self, cfg: StudioConfig) -> None:
        self._cfg = cfg
        self._registry = ModelRegistry(cfg)
        self._pipeline = TryOnPipeline(cfg, self._registry)
        self._pool: ThreadPoolExecutor | None = None

    def start(self) -> None:
        if self._pool is None:
            self._pool = ThreadPoolExecutor(
                max_workers=self._cfg.runtime.workers,
                thread_name_prefix="tryon",
            )

    def stop(self) -> None:
        if self._pool is not None:
            self._pool.shutdown(wait=True, cancel_futures=True)
            self._pool = None

    def submit(self, req: TryOnRequest) -> Future[TryOnResult]:
        if self._pool is None:
            raise RuntimeError("service not started")
        return self._pool.submit(self._pipeline.run, req)

    def run_sync(self, person: Path, garment: Path, out: Path) -> TryOnResult:
        return self._pipeline.run(TryOnRequest(person_path=person, garment_path=garment, out_path=out))