# Changelog — akasha-alexandria

## v9.1.0 — Debian Port + Akasha Canon Alignment (2026-05-02)

### Platform
- **Ported from Termux (Android) to Debian Linux**
- Replaced `TaskerBridgeAdapter` (Android Tasker HTTP bridge) with `HTTPBridgeAdapter`
  — functionally equivalent, binds to `127.0.0.1:8080` by default, no Android dependency
- `TaskerBridgeAdapter` retained as alias for backward compatibility
- `pyproject.toml` updated: renamed package `akasha-alexandria`, added `pyyaml` as explicit dep,
  added optional `[api]` extras for FastAPI server usage

### Akasha Alignment
- Added `repo-manifest.yaml` declaring canonical membership, role, layer, inputs, outputs,
  dependencies, and alignment with all 10 Akasha axioms
- Added `AKASHA_ALIGNMENT.md` documenting structural fit analysis
- Added entry in `akasha-constellation/registry.yaml` (see constellation patch)

### Fixes
- `run.py` rewritten for clarity: clean argparse, explicit generator map, proper yaml open
- `api/__init__.py` added so the `api` package installs correctly under setuptools

---

## v9.0.0 — Alexandria Temporal Kernel (Original, Termux)

Original release. See `TRUTH_ENGINE_SPEC.md` and `README.md` for full doctrine.
