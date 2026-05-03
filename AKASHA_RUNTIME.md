# Akasha Runtime

## Quick Start

```bash
./akasha-core/requirements.sh        # install deps (once)
./akasha-run "your input here"
```

## Pipeline Stages

| #  | Stage      | Engine                                          | Role                                                      |
|----|------------|-------------------------------------------------|-----------------------------------------------------------|
| 1  | ANOMALY    | akasha-anomaly `cli/pipeline.py`                | Stamps input as a time-enriched observation               |
| 2  | ANALOGY    | akasha-analogy-engine `src/main.py`             | Structural analogy seeded by input concept                |
| 3  | EDGE       | akasha-edge-generator `src/main.py`             | Cross-domain candidate edges (discovery)                  |
| 3b | COMBINATOR | akasha-domain-combinator `src/main.py`          | Cross-domain overlap map, tensions, research questions    |
| 4  | ATTRACTOR  | akasha-attractor `cli/pipeline.py`              | Event ledger summary (reads ledger.db)                    |
| 5  | PHASE      | akasha-phase-engine `src/main.py`               | Phase state estimation from physics domain                |
| 6  | ATLAS      | akasha-atlas-engine `src/main.py`               | Knowledge space map and growth frontiers                  |
| 7  | SUGGESTION | akasha-suggestion-engine `src/main.py`          | Ranked next-step suggestions                              |

All stages run in degraded mode on failure — the pipeline never hard-stops mid-run.

## Event Storage

ANOMALY writes to two places:

- `akasha-core/events/ledger.db` — SQLite ledger (ATTRACTOR reads this)
- `akasha-core/events/<uuid>.json` — JSON sidecar per event

## Memory

`akasha-core/memory.ndjson` — one NDJSON record per run:

```json
{"ts": "2026-05-03T12:00:00+00:00", "input": "your input here"}
```

## Logs

`akasha-core/logs/run_<YYYYMMDD_HHMMSS>.log` — full output of each run.

## Installed Python Packages Required

```bash
pip install -e akasha/akasha-time-nexus
pip install -e akasha/akasha-anomaly
pip install -e akasha/akasha-attractor
pip install -e akasha/akasha-apis
pip install PyYAML
```

Or just run `./akasha-core/requirements.sh` which does all of the above.

## Environment Variables

| Variable   | Default | Purpose                                 |
|------------|---------|-----------------------------------------|
| AKASHA_LAT | 0.0     | Latitude for ANOMALY geo-stamping       |
| AKASHA_LON | 0.0     | Longitude for ANOMALY geo-stamping      |
| AKASHA_TZ  | UTC     | Timezone name for ANOMALY clock context |

Example (Ironton, Ohio):

```bash
export AKASHA_LAT=38.5368
export AKASHA_LON=-82.6824
export AKASHA_TZ=America/New_York
```

## Stage Details

### ANALOGY
Picks the domain concept most structurally resonant with your input (using token overlap).
Emits a named structural analogy type (attractor, threshold, resonance, emergence, etc.)
and a natural-language statement. Template is seeded by concept+input for determinism.

### COMBINATOR
Reads all akasha-domain-* packs simultaneously. For every domain pair:
- **overlap map**: concept pairs sharing structural tokens (with overlap score)
- **tension points**: structural roles (collapse, equilibrium, transition…) appearing
  in both domains with different context
- **research questions**: derived from the top overlaps and tensions

### ATTRACTOR
Reads the SQLite ledger and emits human-readable event statistics:
event count, top day, peak hour, season, date span.

### SUGGESTION
Only surfaces genuinely open requests (status=open). Forged engines are silently
excluded. Also surfaces stubs and empty design docs.
