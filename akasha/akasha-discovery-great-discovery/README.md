# akasha-discovery

The structural discovery engine of the Akasha ecosystem.

Originally written as **The Great Discovery** (ver+4) in Termux on Android.
Ported and aligned with Akashic law for canonical constellation membership.

---

## What It Does

akasha-discovery grows a typed knowledge graph and watches where it experiences
structural pressure. It does not search for answers. It eliminates impossible
structures until only necessary shapes remain.

The core loop:

```
grow graph
    ↓
measure structural pressure (3-force field)
    ↓
detect forbidden motifs (compression spike → governance)
    ↓
find named holes (transitive / co-citation / symmetry gaps)
    ↓
generate questions from hole profiles (bridge / depth / boundary)
    ↓
attempt settling via Laplacian energy minimisation
    ↓
inject question nodes back into topology (recursive layer)
    ↓
repeat
```

Discoveries arise from structural tension — not from retrieval, classification,
or instruction.

---

## Engine Role in the Akasha Ecosystem

```
akasha-axioms        governs principles
akasha-world         defines knowledge structure
akasha-discovery     explores unknown structure  ← this engine
akasha-forge         builds tools from discoveries
akasha-constellation maps the ecosystem
```

akasha-discovery is the organ that **asks what is missing**.

---

## Architecture

| Module | Phase | Responsibility |
|---|---|---|
| `core_engine.py` | 2 | SQLite schema — typed nodes, typed edges, holes, semantic_pressure |
| `semantics.py` | 2 | 84-concept vocabulary across 6 domains; 10 relation types |
| `pressure_engine.py` | 3 | WL-1 motif signatures; compression ratio; Shannon entropy; forbidden detection |
| `governance.py` | 3 | Domain-aware forbidden motifs; domain-specific repulsion field |
| `hole_detector.py` | 3 | Transitive / co-citation / symmetry holes; precision-ranked profiles |
| `questioner.py` | 3 | Question composition from hole profiles; pressure boost feedback |
| `explorer.py` | 4 | 3-force field: pull + void + hole_attraction − forbidden_repulsion; softmax sampling |
| `settler.py` | 4 | Laplacian energy minimisation; recursion-domain handling; hold coordination |
| `convergence.py` | 4 | 5-state classifier: STABLE / DEADLOCKED / EXPANDING / DIVERGENT / OSCILLATORY |
| `recursion.py` | 4 | Depth-0 object questions → depth-1 meta-questions; question-node topology |
| `analogy_engine.py` | — | 3-pattern structural analogy: shared-target / sibling-bridge / symmetry |
| `ceiling_engine.py` | — | Full pipeline wiring: holes → pressure → questions → hypotheses → mutation |
| `driver.py` | — | Epoch runner; seed nodes; graph growth; memory stamping |
| `kernel/` | — | Constitution, State, Engine, Loop — governance validation layer |
| `memory/` | — | DiscoveryMemory, archive, lineage, pattern index |

---

## Quick Start

```bash
pip install numpy networkx
python run_discovery.py --simulate
```

Or with dashboard:
```bash
python run_discovery.py --dashboard
# opens at http://localhost:8080
```

---

## Convergence States

| State | Meaning | Engine Response |
|---|---|---|
| STABLE | Holes filling, pressure stabilising | Continue |
| DEADLOCKED | Compression flat, holes static | Perturbation + raise temperature |
| EXPANDING | Holes growing, compression flat | Slow settling, let holes sharpen |
| DIVERGENT | Pressure increasing | Raise exploration temperature |
| OSCILLATORY | Cycling without direction | Modulate temperature in phase |

---

## Outputs

- **Named hole profiles** — JSON, ranked by precision, suitable for akasha-edge-generator
- **Question log** — NDJSON, human-readable structural questions
- **Convergence state** — feeds akasha-attractor ledger
- **discovery.db** — SQLite, full graph + motif + hole history

---

## Axiom Alignment

| Axiom | How This Engine Embodies It |
|---|---|
| 1 — Coherence | Contradiction detection (forbidden motifs) is the primary signal |
| 2 — Discoverability | Entire engine is built around gap detection as a first-class activity |
| 4 — Augmentation | Recursive layer — the engine becomes its own instrument |
| 5 — Traceability | Every hole carries epoch_found, shape_sig, src/dst nodes |
| 6 — Modularity | Fully decomposable — each phase is a replaceable module |
| 8 — Iteration | The discovery loop is recursively self-applied |
| 9 — Stewardship | Humans approve what holes are acted on; engine proposes, never decides |
| 10 — Continuity | SQLite ledger accumulates; memory does not reset |

---

## Position in Constellation

```
akasha-anomaly  →  akasha-discovery  →  akasha-edge-generator
                         ↓
                   akasha-attractor
                         ↓
                   akasha-suggestion-engine
```

Named hole profiles from this engine are the primary seed for
akasha-edge-generator's cross-domain candidate edges.

---

## Source Lineage

Written as *The Great Discovery* (ver+4) in Termux on Android.
Phase 0–4 completed. Phase 4 (Recursive Discovery) is active.
Ported and aligned with Akashic law for canonical membership.

---

This repository participates in the Akasha ecosystem and is described
by `repo-manifest.yaml`.
