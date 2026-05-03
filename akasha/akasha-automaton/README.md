# akasha-automaton

**Akasha Constellation — Emergent Systems Simulation Engine**

*"The universe is a cellular automaton. We're just trying to figure out the rules."*

A professional-grade computational laboratory for exploring emergent systems.
Eight simulation engines. Nine render modes. Genetic evolution. AI-powered discovery.
Time travel. A living README grid.

---

## Akasha Alignment

This system is part of the Akasha ecosystem and aligns with
`akasha-axioms`, `akasha-world`, and `akasha-constellation`.

| Axiom | Alignment |
|---|---|
| Axiom 1 — Coherence | Apparent contradiction in pattern behavior surfaces as Wolfram class reassignment, not suppression |
| Axiom 2 — Discoverability | Genetic evolution engine infers unknown rule sets from patterned fitness signals |
| Axiom 3 — Alignment | Declared, manifest-registered, constellation-placed |
| Axiom 4 — Augmentation | Expands human capacity to observe and reason about emergent, self-organizing systems |
| Axiom 5 — Traceability | All simulation outputs traceable to declared rules, initial state, and generation counter |
| Axiom 6 — Modularity | Eight engines, nine renderers, CLI and browser dashboard are independently replaceable |
| Axiom 7 — Transparency | All classification logic (Wolfram class, Pattern DNA, B/S rules) is explicit and human-readable |
| Axiom 8 — Iteration | Time-travel history buffer and genetic algorithm embody the observe→model→experiment→revise loop |
| Axiom 9 — Stewardship | Human steward required; AI features augment but do not replace human interpretation |
| Axiom 10 — Continuity | Regime history, spell journals, and evolved rule sets accumulate across runs |

**Constellation role:** `engine` | **Layer:** `simulation`

---

## Eight Simulation Engines

| Engine | Description |
|---|---|
| **Game of Life** | Classic B3/S23 CA. Turing-complete. Full B/S rule configurability. |
| **Reaction-Diffusion** | Gray-Scott model. Presets for spots, stripes, coral, maze, cells, spiral. |
| **Lenia** | Continuous CA producing lifelike organisms. Tunable kernel, growth function μ/σ. |
| **Brian's Brain** | Three-state automaton (alive → dying → dead). Moving spark streams. |
| **WireWorld** | Electronic circuit simulator. Build logic gates and computers on the grid. |
| **Langton's Ant** | Turing-complete ant automaton. Up to 20 simultaneous ants. Multiple rule strings. |
| **Cyclic CA** | Multi-state cyclic automaton. Configurable state count (2–16) and neighbor threshold. |
| **SmoothLife** | Continuous generalization of Life. Floating-point fields, tunable radii. |

---

## Nine Render Modes

`Classic` · `Heat` · `Age` · `Velocity` · `Nebula` · `Plasma` · `Aurora` · `Quantum` · `3D ISO`

Switch modes live without stopping simulation.

---

## Run

### Desktop (Pygame)

```bash
pip install pygame numpy anthropic
python3 core/automaton.py
```

### Browser (zero dependencies)

```bash
open assets/explorer_v8.html
```

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Space` | Play / Pause |
| `→` | Step one generation |
| `C` | Clear grid |
| `I` | Invert grid |
| `R` | Random 30% |
| `M` | Cycle render mode |
| `G` | Toggle grid lines |
| `T` | Toggle trails |
| `Ctrl+S` | Save grid (.npy) |
| `Ctrl+O` | Load grid (.npy) |
| `Ctrl+P` | Screenshot (PNG) |
| `+` / `-` | Zoom |

---

## AI Features (Claude-Powered)

Seven AI modes via the Anthropic API:

- **Design Rules from Description** — Plain English → B/S rules
- **Predict Next 100 Gens** — Population trajectory, extinction risk, oscillation detection
- **Find Peak Moment** — Fast-forward 200 gens, find most interesting frame
- **Name This Pattern** — AI names whatever is on the grid
- **Tell the Story** — Narrative of the pattern's behavior and history
- **Describe as Music** — Translate dynamics into musical terms
- **Classify Behavior** — Wolfram class assignment with reasoning

Gracefully degrades when the `anthropic` package is unavailable.

---

## Evolutionary Engine

Genetic algorithm for rule discovery. Configure from the Evolve tab:

- Fitness goals: Stability, Growth, Oscillation, Complexity, Longevity, Glider-like movement, Spatial Diversity
- Population size: 4–24 candidate rule sets
- Test generations: 10–300 per candidate
- One-click to apply winning rule to active universe

---

## Pattern DNA Metrics

| Metric | Measures |
|---|---|
| Sym-H / Sym-V | Horizontal and vertical mirror symmetry (0–100%) |
| Stability | Inverse of population variance |
| Entropy | Edge density — structural complexity |
| Complexity | Combined entropy × stability score |
| Class | Wolfram class: Still Life, Oscillator, Spaceship, Chaotic |
| Period | Detected oscillation period |
| Bounding Box | Spatial extent of living cells |

---

## Akasha Event Emission

When run with `--json` or `CS_JSON=1`, outputs are structured as Akasha-compatible
event payloads, consumable by `akasha-events` for persistence in the canonical ledger.

Event schema: `schemas/emergence_event.schema.json`

---

## Constellation Placement

```yaml
akasha-automaton:
  role: engine
  layer: simulation
  description: Emergent-systems simulation and observation engine. Eight cellular
    automaton engines, nine render modes, genetic rule evolution, multi-universe
    forking, time-travel history, AI pattern analysis, and Pattern DNA metrics.
    Produces grid snapshots, Wolfram classifications, evolved rule sets, and
    Akasha-compatible emergence event payloads.
```

See `repo-manifest.yaml` for full declaration.

---

## Living README Grid

The grid below is a real Conway's Game of Life simulation.
A GitHub Action (`assets/advance_life.yml`) runs daily, computes the next
generation via `core/advance_life.py`, and commits it back.

```
<!-- LIFE_START -->
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬜⬜⬜⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬜⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬜⬜⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
<!-- LIFE_END -->
Generation: 0 · Population: 5 · Rule: B3/S23
```

---

## Lineage

`Cellular_Automation_Explorer` (ULTRAVERSE v10 / v8) → canonicalized as `akasha-automaton` (v1.0.0)

Source code unchanged. Canonical wrapping added:
- `repo-manifest.yaml`
- `README.md`
- `docs/AKASHA_ALIGNMENT.md`
- `docs/ARCHITECTURE.md`
- `schemas/emergence_event.schema.json`
- `CONSTELLATION_ENTRY.md`
- `CHANGELOG.md`
