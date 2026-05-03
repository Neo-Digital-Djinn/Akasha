# Akasha Alignment Record — akasha-capital

This document records the formal alignment of `akasha-capital` with the
governing principles of the Akasha ecosystem as defined in `akasha-axioms`.

---

## Alignment Statement

> This system is part of the Akasha ecosystem and aligns with
> akasha-axioms, akasha-world, and akasha-constellation.

---

## Axiom-by-Axiom Record

### Axiom 1 — Coherence
*Reality is assumed to be internally consistent. Apparent contradiction indicates
incomplete observation, incomplete models, or invalid structure.*

**Alignment:** The `DivergenceDetector` (signals.py) is the direct embodiment of
this axiom. When sub-indicators contradict each other — funding flipping against
net flow, score inverting, vol compressing during inflow — the system surfaces a
`Divergence` object rather than suppressing the contradiction. Contradiction is
signal, not noise.

---

### Axiom 2 — Discoverability
*Unknown structure may be inferred from the patterned relationships of known structure.
Gaps are not voids alone; they are signals.*

**Alignment:** The `RegimeForecaster` (forecast.py) builds a Markov transition matrix
from observed regime spells. Unobserved transitions are not assumed impossible — they
are inferred as low-probability until evidence accumulates. The TRANSITION regime itself
functions as a discoverable gap state.

---

### Axiom 3 — Alignment
*Systems belong to Akasha only if they can align with the axioms, the world layer,
and the constellation registry. Unaligned systems may exist as experiments, but not
as canonical members.*

**Alignment:** `akasha-capital` was previously `capital-suite-v5` — a capable but
unregistered instrument. This canonicalization process is the alignment act:
manifest declared, role assigned, constellation entry prepared, axiom alignment
documented. It was a lab; it is now a canonical organ.

---

### Axiom 4 — Augmentation
*Tools exist to expand the capacity to observe, reason, create, simulate, explain,
and distribute knowledge.*

**Alignment:** This is the primary purpose of `akasha-capital`. It takes raw market
signals and produces structured, human-readable regime state. The dashboard,
divergence reports, watchdog alerts, and Markov forecasts are all augmentations of
the human observer's capacity to understand capital flow dynamics.

---

### Axiom 5 — Traceability
*Claims, models, discoveries, and outputs must be traceable to observation,
reasoning, experiment, simulation, or declared synthesis.*

**Alignment:** Every output of `akasha-capital` is traceable:
- Regime classifications → traceable to `config.py` thresholds (VOL_EXPANSION_THRESHOLD,
  DOM_ROTATION_THRESHOLD, SIGNAL_THRESHOLD)
- Divergence flags → traceable to specific signal comparisons
- Markov forecasts → traceable to observed spell counts in the transition matrix
- Alerts → traceable to specific tick and threshold values
- The adapter layer is explicitly labeled as a simulator until replaced by real data

---

### Axiom 6 — Modularity
*Systems should be decomposable, composable, and replaceable without collapse of the whole.*

**Alignment:** The architecture enforces this structurally:
- `adapters/api_client.py` is replaceable with a real data adapter without touching core
- `core/config.py` centralizes all thresholds — behavior adjustable without logic changes
- `core/flow.py`, `compass.py`, `signals.py`, `watchdog.py` are independently testable units
- `cli/` is a thin wrapper — the core runs without it
- The dashboard is entirely independent of the Python runtime

---

### Axiom 7 — Transparency
*Processes should remain inspectable and understandable by humans wherever practical.*

**Alignment:** The classification logic in `compass.py._classify()` is four explicit
if-conditions, not a black box. Every alert in `watchdog.py` has a human-readable
`message` and a machine-readable `code`. Divergences display a Unicode progress bar
alongside severity and description. The Markov matrix prints as a labeled table.

---

### Axiom 8 — Iteration
*Knowledge advances through cycles of observation, model-building, experiment,
critique, revision, and reintegration. Akasha is recursive by design.*

**Alignment:** `RegimeMemory` (regime_memory.py) accumulates spell statistics across
runs. `RegimeForecaster` updates its Markov matrix with each new spell. The backtest
engine (`backtest.py`) enables systematic critique of classification behavior under
controlled conditions. Version history (v1 → v5 → akasha-capital) embodies iteration.

---

### Axiom 9 — Stewardship
*Humans remain responsible for governance, ethical boundaries, maintenance,
and final accountability. Machines may participate deeply, but stewardship is not abdicated.*

**Alignment:** `repo-manifest.yaml` declares `steward: human` and
`approval_required: true`. The README explicitly states "Not a trading bot."
The system observes and reasons; all action decisions remain with the human steward.
No automated execution. No position-taking.

---

### Axiom 10 — Continuity
*Knowledge, tools, context, and lineage should accumulate rather than reset.
Progress should compound.*

**Alignment:** Regime memory persists across sessions (spell journal). The Markov
matrix grows more reliable with each observed transition. The `CHANGELOG.md` records
the full lineage from `capital-suite` to `akasha-capital`. This document itself is
a continuity artifact.

---

## Conclusion

`akasha-capital` passes the canonical admission test:

1. ✅ Does it align with the axioms? — Yes, documented above
2. ✅ Does it have a declared role? — `engine`, layer `analysis`
3. ✅ Does it declare inputs and outputs? — Yes, in `repo-manifest.yaml`
4. ✅ Can it be placed in the constellation? — Yes, see `CONSTELLATION_ENTRY.md`
5. ✅ Can its purpose be explained clearly? — Capital flow and regime analysis instrument
