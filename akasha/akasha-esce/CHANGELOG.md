# CHANGELOG — akasha-esce

## v1.1.0 — 2026-05-02 — Akasha Constellation Admission

### Ported: Termux/Android → Debian 13 Linux

**C Extension fixes:**
- Added `#define PY_SSIZE_T_CLEAN` (required Python 3.10+)
- Added `extra_compile_args=["-O2", "-Wall"]` to `setup.py`
- Explicit source path in `Extension()` for out-of-tree builds
- Debian install: `sudo apt install python3-dev build-essential`

**Python fixes:**
- `plugin_loader.py`: clear `ImportError` message on missing plugin
- `cli.py`: replaced bare `sys.argv` parsing with structured dispatch + error handling
- `pipeline.py`: type hints updated to Python 3.11 (`list[str] | None`)
- `__init__.py`: exports `Pipeline`, declares `__version__`

**Akasha alignment:**
- Added `repo-manifest.yaml` with full axiom alignment table
- Added `CONSTELLATION_ENTRY.md` — formal constellation registration
- Added `CHANGELOG.md` (this file)
- Registered in `akasha-constellation/registry.yaml`

**Tests expanded:**
- `test_hash.py`: added determinism and distinctness tests
- `test_pipeline.py`: added self-inverse, ordering, and empty pipeline tests

**CI:**
- Updated to `actions/checkout@v4`, `actions/setup-python@v5`
- Matrix: Python 3.11 and 3.12
- Added `build-essential` install step

---

## v1.0.0 — 2026-02-14 — ESCE Stage 10 (Termux/Android)

- Initial production-ready architecture milestone
- Plugin system: XOR (C), hash (SHA-256), HMAC-SHA256
- Streaming file support (1 MiB chunks)
- CLI: encode-text, hash-text, encode-file
- CI via GitHub Actions
