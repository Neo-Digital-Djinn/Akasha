# Porting Notes

Source: *Cantus v2.0*, written in Termux on Android  
Target: akasha-cantus, canonical Akasha ecosystem member

---

## Bugs Fixed

### 1. `dsl.py` — `OVER` opcode missing

`OVER` is listed in the v1 spec and used in `factorial.cantus`, but was absent
from the recognised opcode set in `dsl.py`. Parsing any program with `OVER`
raised `ValueError: Unknown opcode OVER`.

**Fix:** Added `OVER` to `_NO_ARG` opcodes in `dsl.py`.

---

### 2. `vm.py` — `OVER` opcode not implemented

Even if parsed, `OVER` had no handler in `vm.py`.

**Fix:** Added `OVER` handler: copies second-from-top onto stack top `( a b → a b a )`.

---

### 3. `dsl.py` — `JNZ` opcode missing

`JNZ` is listed in the v1 spec but absent from `dsl.py` and `vm.py`.

**Fix:** Added `JNZ` to `_LABEL_ARG` in `dsl.py` and added handler in `vm.py`.

---

### 4. `dsl.py` — `MOD` opcode missing

`MOD` is listed in the v1 spec but absent from `dsl.py`, `vm.py`, and `compiler.py`.

**Fix:** Added to all three.

---

### 5. `dsl.py` — `parse_cantus` alias missing

`repl.py` and `tests/test_basic.py` both import `parse_cantus` from `cantus.dsl`.
The function was only named `parse()` — this caused `ImportError` on every REPL
launch and every test run.

**Fix:** Added `parse_cantus = parse` alias at module level in `dsl.py`.

---

### 6. `vm.py` — unguarded stack operations

Stack operations (`DUP`, `SWAP`, `OVER`, arithmetic) raised unhandled `IndexError`
on underflow. The bare `except: continue` in the original silently ate the error
and kept running, but left the VM in an undefined state.

Per ATVM Invariant V.2: *stack underflow HALTS*.

**Fix:** Added `_pop()` helper that sets `self.running = False` before raising,
and checks `len(self.stack)` before multi-element operations.

---

### 7. `vm.py` — division by zero continued execution

Original `DIV` returned 0 on division by zero and continued. Per ATVM Invariant V.3:
*division by zero HALTS*.

**Fix:** `DIV` and `MOD` now set `self.running = False` and break on zero divisor.

---

### 8. `compiler.py` — `MOD`, `OVER`, `JNZ` missing opcodes

These were absent from the `OPCODES` dict.

**Fix:** Added as opcodes 16, 17, 18.

---

### 9. `examples/factorial.cantus` — algorithmic bug

The original factorial example produced `5` instead of `120`. The algorithm
used `OVER` correctly but the stack convention resulted in checking and
decrementing `acc` (which starts at 1) rather than `n` (which starts at 5).
The loop terminated immediately after one iteration.

**Fix:** Corrected stack ordering so `n` is on top and `acc` is below.
Algorithm now correctly computes `5! = 120`. A `HALT` was also added
(original was missing it).

---

## What Was NOT Changed

- `vm.py` — all original opcode semantics preserved
- `dsl.py` — parse logic unchanged; only additions made
- `compiler.py` — compile() output format unchanged
- `tokenizer.py` — audio tokenizer unchanged
- `midi.py` — MIDI bridge unchanged
- `cli.py` — CLI unchanged
- All spec documents preserved verbatim

---

## Akasha Additions

- `repo-manifest.yaml`
- `README.md` (Akasha-format)
- `docs/PORTING_NOTES.md` (this file)
- `docs/CONSTELLATION_PATCH.yaml`
- `pyproject.toml`
- `tests/test_smoke.py` (comprehensive; all passing)
