# Cantus Changelog

## v2.1.0 — Debian 13 / Akasha Canonical Port (2026-05-02)

**Platform:** Debian 13 Linux (ported from Termux/Android)
**Status:** Canonical Akasha engine

### Bug Fixes
- `parse_cantus` alias added to `dsl.py` — `repl.py` imported this name but it
  didn't exist, causing `ImportError` on any REPL usage
- `OVER` opcode implemented in `vm.py` — was referenced in `factorial.cantus`
  and `test_basic.py` but missing from the VM switch
- `JNZ` opcode implemented in `vm.py` — present in CANTUS_SPEC_v1 but omitted
- Division-by-zero now triggers explicit `HALT` with `halt_reason` (was silently
  caught and continued — violated Axiom 1 Coherence and Axiom 5 Traceability)
- Stack underflow now triggers explicit `HALT` with `halt_reason` (same issue)

### New Features
- `halt_reason` attribute on `CantusVM` — records why execution stopped
- `MOD` and `ROT` opcodes added to complete the standard stack language set
- `--repl`, `--audio`, `--bytecode` flags added to CLI
- REPL now supports `run` / `reset` / `stack` commands (multi-line session)
- `pyproject.toml` with `[audio]` and `[dev]` optional dependency groups
- `cantus` console script entry point
- `soundfile` preferred over `audioread` for librosa backend (Debian compat)
- Mono downmix enforced in tokenizer (per REFERENCE_ANALYZER §2)
- Full test suite `tests/test_cantus.py` covering all fixed bugs

### Akasha Integration
- `repo-manifest.yaml` added — full canonical declaration
- `CONSTELLATION_ENTRY.md` added — admission record
- `AKASHA_ALIGNMENT.md` added — axiom-by-axiom alignment
- Registered in `akasha-constellation/registry.yaml`

---

## v2.0.0 — "Dangerous & Beautiful" (Termux/Android)

- MIDI bridge: musical note sequences → opcodes
- `POKE` instruction: self-modifying bytecode
- Bytecode compilation layer (`compiler.py`)
- ATVM specification (`docs/SPEC.md`, `docs/INVARIANTS.md`)
- Acoustic tokenizer via `librosa.pyin`

---

## v1.0.0 — Initial (Termux/Android)

- Stack-based VM with integer arithmetic
- Text DSL parser (`.cantus` files)
- Core opcodes: PUSH POP DUP SWAP ADD SUB MUL DIV STORE LOAD JMP JZ LABEL PRINT HALT
- REPL
- Examples: music, factorial, danger
