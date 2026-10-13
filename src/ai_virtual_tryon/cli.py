"""Headless CLI: run a single try-on pass without the Qt shell."""
from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from ai_virtual_tryon.config.loader import load_config
from ai_virtual_tryon.services.pipeline_service import PipelineService

console = Console()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tryon-cli", description="Headless virtual try-on.")
    p.add_argument("--person", required=True, type=Path, help="Path to person photo.")
    p.add_argument("--garment", required=True, type=Path, help="Path to flat-lay garment image.")
    p.add_argument("--out", required=True, type=Path, help="Output PNG path.")
    p.add_argument("--config", type=Path, default=Path("config/default.toml"))
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)
    service = PipelineService(cfg)
    service.start()
    try:
        result = service.run_sync(person=args.person, garment=args.garment, out=args.out)
    finally:
        service.stop()
    console.print(f"[bold green]rendered[/] -> {result.output_path} ({result.ms} ms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())