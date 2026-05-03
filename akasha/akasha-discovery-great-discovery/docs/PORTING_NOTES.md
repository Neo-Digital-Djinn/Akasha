# Porting Notes

Source: *The Great Discovery* ver+4, written in Termux on Android
Target: akasha-discovery, canonical Akasha ecosystem member

---

## What Changed

### 1. `driver.py` — Schema column name correction

**Bug:** `driver.py` referenced `edges.source` and `edges.target`.
`core_engine.py` creates columns named `src` and `dst`.

On Android/Termux the database was always initialised fresh, so this mismatch
never triggered. On a persistent install it would fail on resume.

**Fix:** All references in driver.py changed to `src` / `dst`.

---

### 2. `driver.py` — `holes` table schema correction

**Bug:** `detect_holes()` tried to insert `node_id` into the holes table.
The Phase 2 schema in `core_engine.py` has no `node_id` column — it uses
`epoch_found`, `shape_sig`, `demands`, `filled`.

**Fix:** Rewrote `detect_holes()` to use `shape_sig = "isolated:{node_id}"` and
insert via the correct Phase 2 schema.

---

### 3. `driver.py` — `semantic_pressure` table schema correction

**Bug:** `apply_semantic_pressure()` inserted into a `value` column.
The Phase 2 schema uses `structural_compress`, `semantic_compress`, `mismatch`.

**Fix:** Rewrote to compute and insert all three columns correctly.

---

### 4. `driver.py` — NDJSON output for Akasha pipeline

**Addition:** Epoch output changed from `print()` strings to `json.dumps()`
NDJSON records so the driver can be piped into Akasha's pipeline
(e.g. `akasha-anomaly`, `akasha-attractor`).

---

### 5. `driver.py` — `main()` entrypoint

**Addition:** `main()` function added with argparse (`--epochs`, `--db`)
for `pyproject.toml` script registration and CLI use.

---

### 6. Package structure

Wrapped in standard `src/` layout with `pyproject.toml` for pip install.

---

## What Was NOT Changed

All discovery logic is preserved exactly:

- `core_engine.py` — Phase 2 schema (unchanged)
- `pressure_engine.py` — WL-1 motif signatures, 3-force field (unchanged)
- `governance.py` — domain-aware forbidden motifs (unchanged)
- `hole_detector.py` — 3 hole types, precision ranking (unchanged)
- `questioner.py` — question composition, pressure boost feedback (unchanged)
- `explorer.py` — softmax sampling (unchanged)
- `settler.py` — Laplacian energy minimisation (unchanged)
- `convergence.py` — 5-state classifier (unchanged)
- `recursion.py` — depth-threading (unchanged)
- `analogy_engine.py` — 3-pattern analogy detection (unchanged)
- `semantics.py` — 84-concept vocabulary, 10 relation types (unchanged)
- `ceiling_engine.py` — full pipeline wiring (unchanged)
- `kernel/` — Constitution, State, Engine, Loop (unchanged)
- `memory/` — DiscoveryMemory, archive, lineage (unchanged)

---

## Akasha Alignment Additions

- `repo-manifest.yaml` — canonical system declaration
- `README.md` — Akasha-format documentation
- `docs/ARCHITECTURE.md` — system architecture reference
- `docs/PORTING_NOTES.md` — this file
- `docs/AKASHA_ALIGNMENT.md` — axiom-by-axiom alignment record
- `tests/test_smoke.py` — schema and epoch smoke tests
- Constellation patch — `registry.yaml` update
