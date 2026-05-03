# Architecture — akasha-automaton

## System Role

`akasha-automaton` is a **simulation engine** in the Akasha constellation.
It occupies the `simulation` layer — an active experimental instrument that
generates observable emergent phenomena for human analysis and discovery.

## Two Deployments

```
akasha-automaton
├── core/automaton.py        Desktop application (Pygame + NumPy)
└── assets/explorer_v8.html  Browser dashboard (zero dependencies, WebGL)
```

Both deployments share the same conceptual architecture and produce
Akasha-compatible event payloads. They are independently runnable.

---

## Desktop Application Architecture (core/automaton.py)

```
[User Input / AI Prompt]
         │
         ▼
    App (main loop)
         │
    ┌────┴──────────────────────────────┐
    │       Simulation Engines          │
    │  UniverseState   (GoL)            │
    │  ReactionDiffusion (Gray-Scott)   │
    │  BriansBrain                      │
    │  WireWorld                        │
    │  LangtonAnt                       │
    │  CyclicCA                         │
    │  ElementaryCA                     │
    │  ForestFire                       │
    │  SmoothLife                       │
    └────┬──────────────────────────────┘
         │ grid state (numpy array)
         ▼
    Render Pipeline
         │  Classic / Heat / Age / Velocity /
         │  Nebula / Plasma / Aurora / Quantum / 3D ISO
         ▼
    Pygame Display
         │
    ┌────┴──────────────────────────────┐
    │       Analysis Systems            │
    │  Pattern DNA Metrics              │
    │    Sym-H, Sym-V, Stability,       │
    │    Entropy, Complexity, Class,    │
    │    Period, Bounding Box           │
    │  Wolfram Classifier               │
    │  Orbit Hash (Zobrist XOR)         │
    └────┬──────────────────────────────┘
         │
    ┌────┴──────────────────────────────┐
    │       Evolution & History         │
    │  GeneticEvolver (rule discovery)  │
    │  History Buffer (up to 1000 gens) │
    │  Multi-Universe Fork Manager      │
    └────┬──────────────────────────────┘
         │
    ┌────┴──────────────────────────────┐
    │       AI Integration              │
    │  AIClient (async, Claude API)     │
    │  7 analysis modes                 │
    │  Graceful degradation             │
    └────┬──────────────────────────────┘
         │
    [Emergence Event Payloads]
    [PNG Screenshots]
    [.npy Grid Saves]
    [RLE Exports]
```

---

## Simulation Engine Classes

| Class | Engine | Key Data |
|---|---|---|
| `UniverseState` | Conway GoL (configurable B/S) | `grid: np.uint8[H,W]`, `history[]`, metric hists |
| `ReactionDiffusion` | Gray-Scott | `A, B: np.float32[H,W]`, feed/kill params |
| `BriansBrain` | Brian's Brain | `grid: np.uint8` (0=dead, 1=alive, 2=dying) |
| `WireWorld` | WireWorld | `grid: np.uint8` (0=empty,1=conductor,2=head,3=tail) |
| `LangtonAnt` | Langton's Ant | `ants[]`, `grid`, rule strings |
| `CyclicCA` | Cyclic CA | `grid: np.uint8`, state count, threshold |
| `ElementaryCA` | Elementary (1D) | `rule: int (0-255)`, scrolling rows |
| `ForestFire` | Forest Fire | `grid` (empty/tree/burning), p/f params |
| `SmoothLife` | SmoothLife | `field: np.float32`, inner/outer radii |

---

## Render Modes

All render modes operate on a NumPy array and produce a Pygame surface.
Modes are fully vectorized as of v10 (no Python loops in plasma/aurora/crystal).

| Mode | Technique |
|---|---|
| Classic | Direct cell→pixel mapping |
| Heat | Population density heatmap (rolling average) |
| Age | Per-cell age counter → colormap |
| Velocity | Birth+death rate → motion vector overlay |
| Nebula | Gaussian blur + glow |
| Plasma | Vectorized sin/cos field |
| Aurora | Vectorized HSV sweep |
| Quantum | Interference pattern overlay |
| 3D ISO | Isometric projection with depth shading |

---

## Pattern DNA Metrics

Computed every generation from `UniverseState.grid`:

| Metric | Algorithm |
|---|---|
| Sym-H | Compare grid to horizontal flip, count matching cells / total |
| Sym-V | Compare grid to vertical flip |
| Stability | 1 - (population variance / mean) over rolling window |
| Entropy | Edge count (grid[:,:-1] != grid[:,1:]) / total cells |
| Complexity | entropy × (population / total_cells) |
| Class | Rule-based: still=low vel, oscillator=periodic vel, spaceship=moving bbox |
| Period | Orbit hash ring — Zobrist XOR collision-resistant fingerprinting |
| Bounding Box | min/max of nonzero cell coordinates |

---

## Akasha Event Schema

Emergence event payloads conform to `schemas/emergence_event.schema.json`.
Structured for ingestion by `akasha-events`.

Key fields:
- `source`: `"akasha-automaton"`
- `engine`: active simulation engine name
- `generation`: current tick
- `population`: living cell count
- `rule`: B/S rule string (GoL) or engine parameters
- `wolfram_class`: current classification
- `pattern_dna`: full metric snapshot
- `alerts`: active system alerts
- `ai_analysis`: last AI response (if available)

---

## Living README Integration

`core/advance_life.py` + `assets/advance_life.yml`:

```
[GitHub Actions — daily trigger]
         │
         ▼
advance_life.py
  1. Parse LIFE_START/LIFE_END block from README.md
  2. Decode ⬜/⬛ grid to numpy array
  3. Apply one GoL B3/S23 generation step
  4. Encode back to emoji grid
  5. Update generation count and population
  6. Write back to README.md
  7. Commit and push
```

The glider in the README grid travels indefinitely — or until something more
interesting emerges.
