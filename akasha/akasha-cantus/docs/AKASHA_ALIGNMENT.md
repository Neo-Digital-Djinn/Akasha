# akasha-cantus — Akasha Alignment

This system is part of the Akasha ecosystem and aligns with
`akasha-axioms`, `akasha-world`, and `akasha-constellation`.

---

## Axiom 1 — Coherence

*Reality is assumed to be internally consistent. Apparent contradiction
indicates incomplete observation, incomplete models, or invalid structure.*

**Alignment:** Every halt condition in the VM is named and recorded in
`halt_reason`. A VM that silently swallows errors (as the original Termux
version did on division-by-zero and stack underflow) violates coherence —
the system appeared to continue but its internal state was undefined.
The ported version surfaces these as explicit, traceable halts.

---

## Axiom 2 — Discoverability

*Unknown structure may be inferred from the patterned relationships of
known structure. Gaps are not voids alone; they are signals.*

**Alignment:** The Acoustic Transition Virtual Machine (ATVM) is a direct
implementation of this axiom. Pitch transitions in audio signal are
structural differences; the tokenizer infers computational instructions
from those differences. Silence → NOOP. Repeated motif → LOOP.
The program is discovered from the pattern, not written symbolically.

---

## Axiom 3 — Alignment

*Systems belong to Akasha only if they can align with the axioms, the
world layer, and the constellation registry.*

**Alignment:** Declared via `repo-manifest.yaml`. Registered in
`akasha-constellation/registry.yaml`. Admission test passed and
recorded in `CONSTELLATION_ENTRY.md`.

---

## Axiom 4 — Augmentation

*Tools exist to expand the capacity to observe, reason, create, simulate,
explain, and distribute knowledge. Tools that enable the creation of better
tools are of special value.*

**Alignment:** Cantus expands the capacity to encode and execute computation
in non-symbolic domains (acoustic, musical). The `POKE` instruction — the
self-modifying opcode — is a literal implementation of tools-that-create-tools:
a running program can rewrite its own instruction stream, creating new
computation mid-execution.

---

## Axiom 5 — Traceability

*Claims, models, discoveries, and outputs must be traceable to observation,
reasoning, experiment, simulation, or declared synthesis.*

**Alignment:**
- `halt_reason` records every abnormal termination
- Acoustic tokenizer fallback is documented and deterministic
- All bug fixes during porting are enumerated in `CHANGELOG.md` and `CONSTELLATION_ENTRY.md`
- Bytecode compiler produces an inspectable integer sequence for every program
- ATVM spec defines determinism guarantees: same audio = same program

---

## Axiom 6 — Modularity

*Systems should be decomposable, composable, and replaceable without
collapse of the whole. Interoperability is preferred over entanglement.*

**Alignment:** Five independent modules with clean interfaces:
- `vm.py` — execution only; knows nothing about audio or MIDI
- `dsl.py` — text parsing only; knows nothing about the VM internals
- `tokenizer.py` — acoustic analysis only; MUST NOT emit instructions directly (per ATVM spec)
- `midi.py` — MIDI mapping only
- `compiler.py` — bytecode serialization only

Any module can be replaced without touching the others.

---

## Axiom 7 — Transparency

*Processes should remain inspectable and understandable by humans
wherever practical.*

**Alignment:**
- All opcode semantics are plain Python in `vm.py` — no hidden dispatch tables
- ATVM specification in `docs/SPEC.md` defines every instruction in prose
- Invariants enumerated in `docs/INVARIANTS.md`
- `NOTE_TO_OP` mapping in `tokenizer.py` is a visible, editable dictionary
- `--bytecode` CLI flag exposes the compiled integer sequence for any program

---

## Axiom 8 — Iteration

*Knowledge advances through cycles of observation, model-building, experiment,
critique, revision, and reintegration. Akasha is recursive by design.*

**Alignment:** The version history embodies iteration:
- v1 → text DSL and basic VM
- v2 → MIDI bridge (musical encoding) + POKE (self-modification) + ATVM spec
- v2.1 → Debian port, bug fixes, Akasha canonical integration

The `POKE` opcode makes iteration recursive at the execution level: a program
can revise itself while running.

---

## Axiom 9 — Stewardship

*Humans remain responsible for governance, ethical boundaries, maintenance,
and final accountability. Machines may participate deeply, but stewardship
is not abdicated.*

**Alignment:** The `POKE` instruction is the clearest test of this axiom.
It is intentionally "dangerous" (per `COLLABORATION.md` and the spec).
It is documented, bounded (address range checked), and permitted — but the
human steward decides whether programs that use it are safe to run.
Cantus does not restrict POKE; it makes it visible and traceable.

---

## Axiom 10 — Continuity

*Knowledge, tools, context, and lineage should accumulate rather than reset.
Progress should compound.*

**Alignment:**
- Complete source lineage from Termux origin is preserved
- All porting decisions and bug fixes are documented, not hidden
- Spec versions are preserved in `spec/` alongside the docs
- `COLLABORATION.md` (the original exhibition statement) is preserved verbatim
- The v2.1 port adds to Cantus; it does not erase what came before
