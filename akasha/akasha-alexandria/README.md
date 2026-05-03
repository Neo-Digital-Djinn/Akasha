# akasha-alexandria

> *"Alexandria does not answer questions. It preserves the conditions under which answers can be trusted."*

**Alexandria Temporal Kernel** — the truth-verification and structured memory engine of the Akasha ecosystem.

Alexandria is a deterministic, auditable **Canonicalization Field** — a system that preserves a
singular historical sequence, enforces invariant-bound state transitions, and guarantees that all
state is derivative of history.

It is not a database. It is not an event bus. It is not a simulation engine. It **remembers** —
and from memory alone, can reconstruct truth.

---

## Akasha Ecosystem Role

```
akasha-axioms        ← governs this system's doctrine
akasha-world         ← provides structural vocabulary
akasha-alexandria    ← verifies hypotheses, maintains immutable ledger   ← YOU ARE HERE
akasha-events        ← receives verified event payloads
akasha-attractor     ← pattern analysis over ledger data
akasha-lens          ← semantic interpretation of outputs
```

See `repo-manifest.yaml` and `AKASHA_ALIGNMENT.md` for full canonical declaration.

---

## Installation (Debian)

```bash
# Requires Python 3.9+
pip install pyyaml

# Install the package in editable mode
pip install -e .

# Or without editable mode
pip install .
```

Optional — for the FastAPI HTTP server:
```bash
pip install "akasha-alexandria[api]"
```

---

## Quickstart

```python
from alexandria import TemporalKernel, Event, Lattice
from alexandria.relations import SumRelation, RatioRelation
from alexandria.invariants import ValueMustBePositive

lattice = (
    Lattice()
    .define("fin", "costs",   {int, float})
    .define("fin", "profit",  {int, float})
    .define("fin", "revenue", {int, float})
    .define("fin", "margin",  {int, float})
    .relate(SumRelation(["costs", "profit"], "revenue"))
    .relate(RatioRelation("profit", "revenue", "margin"))
)

k = TemporalKernel(
    lattice=lattice,
    invariants=[ValueMustBePositive("revenue")]
)

k.apply(Event({"costs": 60.0, "profit": 40.0}, domain="fin"))

print(k.state["revenue"])   # 100.0 — inferred
print(k.state["margin"])    # 0.4   — inferred

for line in k.explain_chain("margin"):
    print(line)
```

---

## CLI

```bash
alexandria                      # version + doctrine banner
alexandria replay ledger.json   # replay and report state
alexandria report ledger.json   # full equilibrium report (JSON)
alexandria verify ledger.json   # verify all event hashes
alexandria schema ledger.json   # infer schema and relation proposals
```

---

## Generator Interface

Run from the project root:

```bash
python run.py --generator symbolic   # deterministic self-test
python run.py --generator manual     # reads input.json
python run.py --generator bridge     # HTTP bridge on localhost:8080
python run.py --generator local      # Ollama local LLM (requires ollama)
python run.py --generator api        # external API (implement in api_adapter.py)
python run.py --verify-ledger        # verify ledger integrity
```

**Note on the HTTP bridge:** On Debian this uses `HTTPBridgeAdapter`, a direct port of the
original Android Tasker bridge. It listens on `127.0.0.1:8080` for a single POST containing
a Hypothesis JSON payload. The `TaskerBridgeAdapter` name is retained as an alias.

---

## Architecture

Five core abstractions:

| Abstraction | Role |
|---|---|
| **Event** | Immutable record with unique ID, timestamp, domain, payload, and cryptographic hash |
| **Ledger** | Append-only ordered event sequence — the source of truth |
| **Lattice** | The coordinate grid — what *could* exist, defined before filling |
| **Relations** | Typed edges: `SumRelation`, `RatioRelation`, `TemporalRelation`, and more |
| **Invariants** | Conservation laws — halt on violation |

Solver: two-phase arc-consistency + energy minimization finds the minimum-tension fixed point.

---

## Design Doctrine

1. **Linear Time is Doctrine.** History is singular.
2. **Holes Are First-Class.** Absence is meaningful.
3. **Invariants Are Conservation Laws.** Admissibility, not correctness.
4. **Domains Are Axes.** No implicit cross-domain mutation.
5. **State Is Derived.** Replay is canonical reconstruction.

See `DOCTRINE.md`, `LAW_STACK/`, and `TRUTH_ENGINE_SPEC.md` for the full constitutional record.

---

## Platform Notes (Debian Port)

This repository was originally developed in **Termux on Android**. The Debian port makes
the following changes:

- `TaskerBridgeAdapter` → replaced with `HTTPBridgeAdapter` (same protocol, no Android dependency)
- `pyproject.toml` updated: package renamed `akasha-alexandria`, `pyyaml` made explicit dependency
- `run.py` hardened: explicit yaml open, proper generator map, clear error messages
- `api/__init__.py` added for correct package discovery under setuptools

All source logic — kernel, ledger, solver, relations, invariants, policies, persistence — is
unchanged from the Termux version.

---

## License

PolyForm (original). See `LICENSE`.
