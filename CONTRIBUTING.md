# Contributing to ai-virtual-tryon-studio

Thanks for wanting to help build the 2026 virtual try-on stack.

## Dev setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m ai_virtual_tryon.app --config config/default.toml
```

Optional GPU extras (CUDA 12.x):

```powershell
pip install -e ".[gpu]"
```

## Branch model

- `main` — always runnable. CI green required.
- `feat/<area>-<short>` — one feature per branch (e.g. `feat/pose-estimator-onnx`).
- `fix/<area>-<short>` — bugfix branches.

## Commit style

Conventional commits. Scope = subpackage name.

```
feat(pose): add DWPose ONNX backend
fix(compositor): clamp alpha at garment hem to avoid halo
perf(renderer): batch VITON-HD passes at 4x on A100
```

## Adding a model backend

1. Drop the ONNX/TorchScript weights into `models/weights/` (gitignored).
2. Register a loader in `src/ai_virtual_tryon/models/registry.py`.
3. Add a smoke test in `tests/test_pipeline_smoke.py` that runs on a 256x384 dummy.

## Code style

- `ruff format` + `ruff check`. Line length 100.
- Type hints on all public functions. `mypy --strict` on `src/ai_virtual_tryon/core`.
- No blocking I/O on the Qt main thread — dispatch to the worker pool.

## Pull requests

Keep diffs focused. Screenshots of rendered try-ons for any renderer change. Run `pytest -q` before pushing.