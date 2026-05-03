# Akasha Alignment — akasha-phase-engine

This document records how akasha-phase-engine aligns with each Akasha axiom
and the world layer.

---

## Axiom Alignment

### Axiom 1 — Coherence
Every phase is encoded with internally consistent properties.
The discovery engine explicitly encodes forbidden state combinations
(e.g., anyons in d=1, attractors that transform) as `Theorem` objects
and excludes them from candidate gaps. The registry will never surface
a physically self-contradictory phase.

### Axiom 2 — Discoverability
The gap-finder (`discovery.py`) scans ~5,700 discrete coordinates in
a multi-axis phase space. Gaps are not voids — they are labeled known,
forbidden (by theorem), predicted (by theory), or candidate. Each
candidate is scored by physical interest. This is the core mechanism
of the engine.

### Axiom 3 — Alignment
This repository registers as class `domain-graph` in `repo-manifest.yaml`.
It aligns with the akasha-world lattice schema: phases map to nodes,
transitions map to edges, and the coordinate system maps to the lattice axes
(phase, stability, constraint, process).

### Axiom 4 — Augmentation
The engine exposes a REST API (`/api/*`) enabling any Akasha engine to query
the phase registry, retrieve material suggestions, or request path-finding
across the transition graph. akasha-discovery can ingest gap reports.
akasha-alexandria can use the JSON export as a provenance-tracked document.

### Axiom 5 — Traceability
Every phase carries:
- `discovery_year`, `discovered_by`
- `theoretical_prediction_year`, `experimental_confirmation_year`
- `key_theoretical_papers`, `key_experimental_papers`, `review_papers`
- `textbook_references`

No phase is asserted without a traceable origin.

### Axiom 6 — Modularity
The engine is decomposed into independent, importable modules:
- `phase` — schema only (no dependencies on other modules)
- `database` — registry builder (depends on phase)
- `graph_engine` — NetworkX graph (depends on database)
- `discovery` — gap finder (self-contained)
- `materials` — suggestion engine (depends on discovery)
- `app` — Flask API (depends on all above)
- `cli` — entry point (depends on all above)
- `pipeline` — MP integration (optional extra, gated import)

### Axiom 7 — Transparency
All modules are plain Python with no obfuscation.
The gap-finder labels each coordinate with its classification reason.
The API exposes enum options so UIs can present valid choices.
The CLI prints human-readable output for every command.

### Axiom 8 — Iteration
The registry is designed for extension. New phases are added in `database.py`
with a matching coordinate entry in `discovery.py`. The gap-finder will
automatically reclassify previously candidate coordinates to `known` when
they are added. This is recursive knowledge accumulation.

### Axiom 9 — Stewardship
The Materials Project pipeline (`pipeline.py`) requires an explicit API key
and does not cache or store any materials data without user action.
All promotion of candidate phases to canonical status requires human review
(see akasha-world knowledge states: candidate → canonical).

### Axiom 10 — Continuity
The JSON export (`/api/gaps`, `registry.to_json()`) produces stable,
versionable artifacts that accumulate over runs. The event schema is
compatible with akasha-events for longitudinal logging.

---

## World Layer Mapping

| World concept        | This engine                            |
|----------------------|----------------------------------------|
| canonical knowledge  | PhaseRegistry entries                  |
| candidate knowledge  | find_gaps() → candidate status         |
| archived knowledge   | forbidden by theorem                   |
| domain-graph class   | PhaseGraph (NetworkX DiGraph)          |
| lattice axes         | PhaseCoordinate (dimensionality, topo, |
|                      | symmetry, dynamics, anyons, edge, gap, |
|                      | long-range entanglement)               |
| node types           | Phase (state), PhaseTransition (edge)  |

---

## Constellation Dependencies

None required. This engine is self-contained.
Recommended integrations:
- akasha-anomaly: pipe CLI output for time-enriched logging
- akasha-attractor: summarize phase query sessions from ledger
- akasha-alexandria: use JSON export as provenance-tracked document
- akasha-discovery: ingest gap report as candidate proposals
