# akasha-phase-engine

A computational "periodic table of behaviors" for phases of matter —
an Akasha constellation member, class `domain-graph`.

21 phases encoded by symmetry, topology, quantum properties, dynamics,
field theory, experimental signatures, materials, and transition graph.
Includes a phase-space gap-finder, material suggestion engine, and REST API.

---

## Install (Debian 13 / Trixie)

```bash
git clone https://github.com/akasha/akasha-phase-engine
cd akasha-phase-engine
bash install-debian.sh
```

With Materials Project integration:

```bash
bash install-debian.sh --with-materials
# then add MP_API_KEY to .env
```

Or manually:

```bash
pip3 install -e ".[dev]" --break-system-packages
cp .env.example .env
```

---

## Quick Start

```bash
akasha-phase-engine              # full query demo + JSON export
akasha-phase-engine graph        # graph traversal, centrality
akasha-phase-engine discovery    # gap-finder report
akasha-phase-engine serve        # dev server on :8000
akasha-phase-engine serve --prod # gunicorn (production)

python -m pytest tests/ -v       # run tests (73 tests)
```

---

## Python API

```python
from akasha_phase_engine import build_default_registry, PhaseGraph, find_gaps
import numpy as np

registry = build_default_registry()

# Chainable queries
registry.all().topological().equilibrium().names()
registry.all().has_anyons().names()
registry.all().berry_phase(np.pi).names()
registry.all().discovered_after(1990).names()
registry.all().has_application("quantum computing").names()
registry.all().topological().has_anyons().dimensionality(2).names()

# Graph
graph = PhaseGraph(registry)
graph.shortest_path("Spin Glass", "BCS Superconductor")
# → ['Spin Glass', 'Normal Metal', 'BCS Superconductor']

graph.reachable_from("Normal Metal")
graph.centrality()
graph.betweenness()

# Gap finder
from akasha_phase_engine import KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS
gaps = find_gaps(KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS)
candidates = sorted([g for g in gaps if g.status == "candidate"],
                    key=lambda g: g.interest_score, reverse=True)

# Export
registry.to_json("phases.json")
```

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| GET | `/api/stats` | Registry statistics |
| GET | `/api/phases` | All phases (filterable) |
| GET | `/api/phases/<name>` | Phase detail |
| GET | `/api/transitions` | All transitions |
| GET | `/api/neighbors/<name>` | Phase neighbors |
| GET | `/api/graph/path?from=X&to=Y` | Shortest path |
| GET | `/api/gaps` | Gap finder report |
| POST | `/api/materials` | Material suggestions |
| GET | `/api/enum_options` | Valid enum values for UI |
| POST | `/api/pipeline` | MP API integration (requires key) |

Filter params for `/api/phases`:
`topological=true|false`, `equilibrium=true|false`,
`breaks_symmetry=true`, `dimensionality=0|1|2|3`, `category=<str>`

---

## Phases in Registry (21)

| Phase | Category | Dim | Year |
|-------|----------|-----|------|
| Crystal | Symmetry-Broken | 3D | 1912 |
| Ferromagnet | Symmetry-Broken | 3D | 1895 |
| BCS Superconductor | Symmetry-Broken | 3D | 1911 |
| Bose-Einstein Condensate | Symmetry-Broken | 3D | 1995 |
| Nematic Liquid Crystal | Symmetry-Broken | 3D | 1888 |
| Paramagnet | Symmetry-Broken | 3D | 1895 |
| Normal Metal | Symmetry-Broken | 3D | 1900 |
| Normal Liquid | Symmetry-Broken | 3D | 1687 |
| Normal Bose Gas | Symmetry-Broken | 3D | 1924 |
| Mott Insulator | Strongly-Correlated | 3D | 1937 |
| Spin Glass | Strongly-Correlated | 3D | 1972 |
| Wigner Crystal | Strongly-Correlated | 2D | 1934 |
| Topological Insulator | Topological | 3D | 2007 |
| Weyl Semimetal | Topological | 3D | 2015 |
| Dirac Semimetal | Topological | 3D | 2014 |
| Topological Superconductor | Topological | 1D | 2012 |
| Integer Quantum Hall State | Topological | 2D | 1980 |
| Fractional Quantum Hall State | Topological | 2D | 1982 |
| Quantum Spin Liquid | Topological | 2D | 1973 |
| Floquet Topological Insulator | Topological | 2D | 2013 |
| Time Crystal | Non-Equilibrium | 1D | 2016 |

---

## Extend

Add new phases in `database.py` with a matching entry in
`discovery.py:KNOWN_PHASE_COORDINATES`.
The gap-finder will automatically reclassify it from candidate to known.

Good next candidates: Anderson Insulator, Kitaev Honeycomb,
ν=5/2 Moore-Read, Chern Insulator (zero-field), Haldane Phase, Polar Metal.

---

## Akasha Alignment

See [docs/AKASHA_ALIGNMENT.md](docs/AKASHA_ALIGNMENT.md) for a full
per-axiom alignment analysis.

This repository participates in the Akasha ecosystem and is described
by `repo-manifest.yaml`.
