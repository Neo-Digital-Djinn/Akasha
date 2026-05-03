# Architecture

## Discovery Loop

```
seed_nodes()
     ↓
grow_graph(epoch)          — random typed edge added each epoch
     ↓
pressure_engine            — WL-1 motif signatures, compression ratio C, entropy H
     ↓
governance                 — domain-aware forbidden motif detection
     ↓
hole_detector              — transitive / co-citation / symmetry holes; precision ranking
     ↓
questioner                 — bridge / depth / boundary questions; pressure boost feedback
     ↓
settler                    — Laplacian energy minimisation; hold coordination
     ↓
recursion                  — depth-0 questions → depth-1 meta-questions → topology
     ↓
convergence                — STABLE / DEADLOCKED / EXPANDING / DIVERGENT / OSCILLATORY
     ↓
repeat
```

## SQLite Schema (Phase 2+)

### nodes
| column | type | notes |
|---|---|---|
| id | INTEGER PK | |
| concept | TEXT | meaning anchor from 84-concept vocabulary |
| domain | TEXT | physics / mathematics / biology / cognition / systems / information |
| introduced | INTEGER | epoch when node entered graph |

### edges
| column | type | notes |
|---|---|---|
| src | INTEGER | |
| dst | INTEGER | |
| relation_type | TEXT | causes / requires / constrains / amplifies / stabilizes / emerges_from / destabilizes / analogous_to / is_dual_of / related |
| weight | REAL | 0.0–1.0 |

### motifs
| column | type | notes |
|---|---|---|
| signature | TEXT PK | WL-1 isomorphism-invariant canonical string |
| count | INTEGER | times observed |
| last_seen_epoch | INTEGER | |

### forbidden
| column | type | notes |
|---|---|---|
| signature | TEXT PK | |
| spike_score | REAL | magnitude of compression spike |
| domain_set | TEXT | comma-separated sorted domain names at spike time |
| epoch_found | INTEGER | |

### holes
| column | type | notes |
|---|---|---|
| id | INTEGER PK | |
| epoch_found | INTEGER | |
| shape_sig | TEXT | e.g. "hole:3->7", "3-causality-7", "meta:3->7" |
| demands | TEXT | human-readable description of what the hole requires |
| filled | INTEGER | 0 = open, 1 = filled |
| filled_by | TEXT | concept that settled the hole |
| src_id / dst_id | INTEGER | endpoint nodes |
| filled_epoch | INTEGER | |

### semantic_pressure
| column | type | notes |
|---|---|---|
| epoch | INTEGER PK | |
| structural_compress | REAL | S/T motif compression ratio |
| semantic_compress | REAL | semantic coherence proxy |
| mismatch | REAL | gap between structural and semantic compression |

## Three-Force Pressure Field

```
field(v) = pull(v) + void(v) + hole_attraction(v) - forbidden_repulsion(v)
```

- **pull** — degree-based hub gravity: `deg(v) / max_deg`
- **void** — structural underrepresentation: nodes with many implied-but-missing edges
- **hole_attraction** — endpoint nodes of open precise holes drawn in
- **forbidden_repulsion** — domain-aware push from destabilising pattern regions

Sampling uses softmax with temperature T (default 0.4; raised during DIVERGENT/DEADLOCKED).

## Recursion Depth

| Depth | Content |
|---|---|
| 0 | Object-level questions about domain topology |
| 1 | Meta-questions about the pattern of questions |
| 2 | Meta-meta (ceiling; rarely triggered) |

Question node concept = `"{q_type}:{src_domain}:{dst_domain}:{dominant_relation}"`
