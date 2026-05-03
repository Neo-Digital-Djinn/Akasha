# akasha-cantus — Constellation Entry

## Admission Summary

| Field | Value |
|---|---|
| Repo Name | akasha-cantus |
| Role | engine |
| Layer | simulation |
| Canonical Status | canonical |
| Maturity | stable |
| Source Lineage | Cantus v2.0 (Termux/Android) |
| Ported To | Debian 13 Linux |

---

## Admission Test (per SYSTEM_REQUIREMENTS.md)

| Question | Answer |
|---|---|
| Does it align with the axioms? | Yes — see `repo-manifest.yaml` axiom_alignment |
| Does it have a declared role? | Yes — `engine` |
| Does it declare inputs and outputs? | Yes — DSL files, audio, MIDI → stack results, bytecode, halt traces |
| Can it be placed in the constellation? | Yes — simulation layer, peers: automaton, cipher-lab |
| Can its purpose be explained clearly? | Yes — acoustic/musical computation engine |

**Verdict: ADMITTED as canonical.**

---

## Constellation Position

### Layer
`simulation` — sits alongside `akasha-automaton`

### Upstream dependencies
- `akasha-axioms` — governing principles
- `akasha-domain-music` — domain context for musical opcode semantics

### Downstream
- `akasha-events` — future: emit execution traces as Akasha-compatible events

### Peers
- `akasha-automaton` — emergent systems simulation
- `akasha-cipher-lab` — symbolic / cryptographic transformation

---

## What It Brings to the Constellation

Cantus fills a previously absent role: **a simulation engine whose instruction
stream can be encoded in a continuous physical signal (sound)**.

It demonstrates that:
1. Computation is substrate-independent (text, audio, MIDI all valid)
2. Cross-domain structural transfer works in practice (music → code)
3. Self-modification (POKE) is a tractable, documented capability

These properties align directly with Akasha's core hypothesis that structural
patterns transfer across domains.

---

## Porting Lineage

```
Cantus v1.0 (text DSL)
    → Cantus v2.0 (+ MIDI bridge + POKE) [Termux/Android]
        → akasha-cantus v2.1.0 [Debian 13, Akasha canonical]
```

Bugs fixed during porting (all traced, per Axiom 5):
1. `parse_cantus` missing from `dsl.py` → ImportError in `repl.py`
2. `OVER` opcode missing from `vm.py` → factorial.cantus failed silently
3. `JNZ` missing from `vm.py` → spec gap
4. Division-by-zero silently continued → now explicit HALT + halt_reason
5. Stack underflow silently continued → now explicit HALT + halt_reason
