# akasha-cantus

**Akasha Constellation — Acoustic Transition Virtual Machine**

*"Programs encoded as sound. Computation encoded as music."*

Cantus is a stack-based virtual machine and domain-specific language in which
programs may be written as text **or** as ordered acoustic state transitions in
audio signals. A MIDI bridge maps musical note sequences to opcodes. The
self-modifying `POKE` instruction constitutes the "dangerous" half.

---

## Akasha Alignment

This system is part of the Akasha ecosystem and aligns with
`akasha-axioms`, `akasha-world`, and `akasha-constellation`.

| Axiom | Alignment |
|---|---|
| Axiom 1 — Coherence | Halt conditions are explicit and named; contradiction surfaces as `halt_reason`, not silence |
| Axiom 2 — Discoverability | Acoustic tokenizer infers program structure from pitch transitions; gaps become NOOPs |
| Axiom 3 — Alignment | Declared, manifest-registered, constellation-placed |
| Axiom 4 — Augmentation | Encodes computation in acoustic and musical domains; POKE enables recursive self-modification |
| Axiom 5 — Traceability | All halts traced to `halt_reason`; tokenizer fallback paths documented |
| Axiom 6 — Modularity | VM, DSL, tokenizer, MIDI bridge, compiler independently replaceable |
| Axiom 7 — Transparency | All opcode semantics explicit in `vm.py`; ATVM spec in `docs/` |
| Axiom 8 — Iteration | v1 → v2 evolution recorded in `CHANGELOG.md`; spec versions in `spec/` |
| Axiom 9 — Stewardship | Human steward required; POKE is intentional and documented |
| Axiom 10 — Continuity | Termux origin preserved; all porting decisions documented |

**Constellation role:** `engine` | **Layer:** `simulation`

---

## What It Does

Cantus is a **dual-mode** computation engine:

### Mode 1 — Text DSL
Write programs in `.cantus` files using a stack-based assembly language:

```cantus
# Factorial of 5
PUSH 5
PUSH 1
LABEL loop
DUP
JZ end
SWAP
OVER
MUL
SWAP
PUSH 1
SUB
JMP loop
LABEL end
POP
PRINT
HALT
```

### Mode 2 — Acoustic (ATVM)
Feed an audio file. The tokenizer extracts pitch transitions and maps them to opcodes using the Acoustic Transition Virtual Machine spec. No text required.

### Mode 3 — MIDI
Pass a sequence of MIDI note numbers. Musical notes become instructions.

---

## Instruction Set

| Opcode | Stack Effect | Notes |
|---|---|---|
| `PUSH n` | `-- n` | Push integer |
| `POP` | `a --` | Discard top |
| `DUP` | `a -- a a` | Copy top |
| `SWAP` | `a b -- b a` | Swap top two |
| `OVER` | `a b -- a b a` | Copy second |
| `ROT` | `a b c -- b c a` | Rotate top three |
| `ADD` | `a b -- a+b` | |
| `SUB` | `a b -- a-b` | |
| `MUL` | `a b -- a*b` | |
| `DIV` | `a b -- a//b` | Halts on zero |
| `MOD` | `a b -- a%b` | Halts on zero |
| `STORE` | `addr val --` | Write to memory |
| `LOAD` | `addr -- val` | Read from memory |
| `LABEL name` | — | Define jump target |
| `JMP name` | — | Unconditional jump |
| `JZ name` | `a --` | Jump if zero |
| `JNZ name` | `a --` | Jump if non-zero |
| `PRINT` | — | Print top (non-destructive) |
| `HALT` | — | Stop execution |
| `POKE` | `addr val --` | **Dangerous**: rewrite instruction at `addr` |

---

## Run

### Install (Debian 13)

```bash
pip install -e .                    # core (no audio)
pip install -e ".[audio]"          # with librosa for acoustic mode
pip install -e ".[dev]"            # with pytest
```

### Run a program

```bash
cantus examples/factorial.cantus
cantus examples/music.cantus
cantus examples/danger.cantus
```

Or via module:

```bash
python -m cantus.cli examples/factorial.cantus
```

### Acoustic mode

```bash
cantus --audio recording.wav
```

### REPL

```bash
cantus --repl
```

### Show bytecode

```bash
cantus --bytecode examples/music.cantus
```

---

## Architecture

```
cantus/
  vm.py         — CantusVM: stack, memory, all opcodes, halt_reason
  dsl.py        — Text parser: .cantus source → token list
  tokenizer.py  — ATVM frontend: audio → token list (librosa, optional)
  midi.py       — MIDI bridge: note sequence → token list
  compiler.py   — Token list → flat integer bytecode
  cli.py        — Unified CLI entry point
  repl.py       — Interactive REPL

spec/
  CANTUS_SPEC_v1.md   — v1 opcode reference
  SPEC_v2.md          — v2 additions (MIDI, POKE, bytecode)

docs/
  SPEC.md             — ATVM specification
  INVARIANTS.md       — Execution invariants
  REFERENCE_ANALYZER.md — Acoustic analyzer reference implementation

examples/
  music.cantus        — Musical aesthetic demo
  factorial.cantus    — Factorial of 5
  danger.cantus       — Self-modifying POKE demo

tests/
  test_cantus.py      — Full test suite
```

---

## ATVM Specification (Summary)

The Acoustic Transition Virtual Machine maps acoustic state changes to opcodes:

- **State** = `{f_c, A, H, N, Δt}` (frequency centroid, amplitude, harmonicity, noise, duration)
- **Transition** = difference between consecutive states
- **Instruction** = transition exceeding a threshold
- **Determinism** guaranteed: same audio → same program
- **Analyzer** and **VM** are strictly separate (Axiom 6)

See `docs/SPEC.md` and `docs/INVARIANTS.md` for full specification.

---

## Origin and Porting

Cantus was originally developed and run on **Termux (Android)**.

This is the canonical **Debian 13** port, entering the Akasha Constellation as an official engine.

**Porting changes:**
- `parse_cantus` alias added to `dsl.py` (was missing, broke `repl.py` import)
- `OVER`, `JNZ`, `MOD`, `ROT` opcodes added to `vm.py` (referenced in spec/tests, absent from original)
- Division-by-zero now explicit `HALT` with `halt_reason` (was silent `continue`)
- Stack underflow now explicit `HALT` (was `IndexError` caught silently)
- `librosa` import made fully optional with clear install instructions
- `soundfile` backend preferred over `audioread` for Debian compatibility
- `pyproject.toml` replaces ad-hoc Termux install steps
- `cantus` console script entry point added

---

## COLLABORATION.md

> *This project is a proof of capability. A piece of conceptual art. A technical artifact.*
> *A human imagined direction. An AI extended structure. Iteration refined intent.*
> *CANTUS is not just executable music. It is executable cooperation.*

---

## Position in Constellation

```
akasha-domain-music  ──→  akasha-cantus  ──→  akasha-events
                              ↑
                    akasha-axioms / akasha-world
```

**Peers:** `akasha-automaton` (simulation engine), `akasha-cipher-lab` (symbolic transformation)

---

This repository participates in the Akasha ecosystem and is described by `repo-manifest.yaml`.
