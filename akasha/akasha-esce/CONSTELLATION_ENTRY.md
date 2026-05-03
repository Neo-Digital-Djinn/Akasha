# CONSTELLATION ENTRY — akasha-esce

**Status:** Canonical  
**Layer:** Transformation  
**Admitted:** 2026-05-02  
**Steward:** Akasha Forge  
**Source Lineage:** ESCE Stage 10 (Termux/Android) → Debian 13 port

---

## Role

`akasha-esce` is the Akasha Constellation's **byte-transformation organ**.  
It provides a modular, deterministic, plugin-driven pipeline for encoding,
hashing, and transforming arbitrary binary data. Its plugin interface makes
it a platform for building new transformation tools without modifying the
core engine.

---

## Axiom Alignment Summary

| Axiom | How ESCE Satisfies It |
|---|---|
| 1 Coherence | Explicit plugin order; failures are named errors, never silent |
| 2 Discoverability | Dynamic plugin loader — missing capability is visible, not hidden |
| 3 Alignment | Declared role, layer, inputs, outputs, and constellation position |
| 4 Augmentation | Plugin interface is a tool-for-building-tools |
| 5 Traceability | Plugin loads traceable; pipeline order inspectable at runtime |
| 6 Modularity | Each layer (C core, encoder, pipeline, loader, CLI) independently replaceable |
| 7 Transparency | Human-readable Python and minimal annotated C; no hidden state |
| 8 Iteration | Termux Stage 10 → Debian v1.1.0; evolution tracked in CHANGELOG |
| 9 Stewardship | Human steward approval required; security notice maintained |
| 10 Continuity | Termux lineage preserved; porting decisions documented |

---

## Constellation Position

```
[akasha-axioms]
      │
      ▼
[akasha-esce]  ←── transformation layer
      │
      ├──► akasha-events     (potential: emit transform traces)
      ├──► akasha-anomaly    (potential: feed encoded streams)
      │
      peers: akasha-cantus, akasha-cipher-lab
```

---

## Porting Notes (Termux → Debian 13)

| Issue | Resolution |
|---|---|
| C extension build | `sudo apt install python3-dev build-essential` before `pip install .` |
| `PY_SSIZE_T_CLEAN` missing | Added macro to `esce_core.c` (required Python 3.10+) |
| `setup.py` path | `extra_compile_args=["-O2", "-Wall"]` added; explicit source path |
| CI target | Updated from ubuntu-latest/py3.11 to matrix py3.11+3.12 |
| `hmac.new` → `hmac.new` | No change needed; stdlib compat confirmed for Python 3.11+ |
| Console script | Added `esce` entry point via pyproject.toml `[project.scripts]` |
