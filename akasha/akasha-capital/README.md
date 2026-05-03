# akasha-capital

**Akasha Constellation — Capital Flow & Regime Analysis Engine**

Observational liquidity and market-regime analysis system.
A structured reasoning instrument. Not a trading bot.

---

## Akasha Alignment

This system is part of the Akasha ecosystem and aligns with
`akasha-axioms`, `akasha-world`, and `akasha-constellation`.

| Axiom | Alignment |
|---|---|
| Axiom 1 — Coherence | Regime classifications are internally consistent; contradiction surfaces as a Divergence |
| Axiom 2 — Discoverability | Gaps in regime structure are inferred from signal relationships |
| Axiom 3 — Alignment | Declared, manifest-registered, constellation-placed |
| Axiom 4 — Augmentation | Expands human capacity to observe and reason about capital markets |
| Axiom 5 — Traceability | All outputs traceable to input signals and documented thresholds |
| Axiom 6 — Modularity | Core, adapters, CLI, and schemas are independently replaceable |
| Axiom 7 — Transparency | All classification logic is explicit and human-readable |
| Axiom 8 — Iteration | Regime memory accumulates; Markov matrix updates each spell |
| Axiom 9 — Stewardship | Human steward required; approval_required: true |
| Axiom 10 — Continuity | Regime memory and spell journals compound across runs |

**Constellation role:** `engine` | **Layer:** `analysis`

---

## What It Does

`akasha-capital` ingests market signals and classifies capital flow regimes:

| Regime | Meaning |
|---|---|
| `EXPANSION` | Positive flow + elevated vol — capital entering, risk-on |
| `ROTATION` | Neutral flow + BTC dominant — rotation from alts to BTC |
| `CONTRACTION` | Negative flow — capital leaving crypto |
| `TRANSITION` | Ambiguous / mixed signals |

### Components

```
core/
  config.py         — centralized thresholds + asset loadings
  flow.py           — CapitalFlowIndicator (CMI, rolling window, confidence)
  compass.py        — CapitalCompass (regime classifier → RegimeState)
  signals.py        — DivergenceDetector (4 divergence types)
  watchdog.py       — RegimeWatchdog (structured alerts)
  backtest.py       — BacktestEngine + BacktestReport
  portfolio.py      — MultiAssetPortfolio (BTC/ETH/SOL/BNB)
  forecast.py       — RegimeForecaster (Markov transition matrix)
  regime_memory.py  — RegimeMemory (persistent spell journal)
adapters/
  api_client.py     — MarketData (multi-asset OU correlated simulator)
cli/
  main.py           — multi-tick runner, multi-asset, backtest, event export
  termux.py         — single-tick runner
capital_dashboard.html  — full browser dashboard (v5)
```

---

## Run

```bash
# BTC only — 5 ticks
python3 cli/main.py

# Multi-asset — 10 ticks
CS_ASSETS=multi CS_TICKS=10 python3 cli/main.py

# JSON export (Akasha event-compatible)
CS_TICKS=10 CS_JSON=1 python3 cli/main.py

# Backtest — BTC, 200 ticks
CS_BACKTEST=200 python3 cli/main.py

# Backtest — multi-asset, seeded
CS_BACKTEST=500 CS_ASSETS=multi CS_SEED=42 python3 cli/main.py
```

## Dashboard

Open `capital_dashboard.html` in a browser.

| Key | Action |
|---|---|
| `space` | Pause / resume |
| `r` | Reset simulation |
| `a` | Trigger AI analysis |
| `t` | Toggle light/dark theme |
| `b` | Run in-dashboard backtest (100 ticks) |
| `e` | Export session JSON |
| `m` | Toggle multi-asset panel |

---

## Akasha Event Emission

When run with `CS_JSON=1`, outputs are structured as Akasha-compatible
event payloads, consumable by `akasha-events` for persistence in the
canonical ledger.

Event schema keys:
- `regime` — current RegimeState classification
- `score` — CMI score
- `confidence` — rolling window confidence
- `divergences` — list of active Divergence objects
- `alerts` — list of active Alert objects
- `forecast` — next-regime probabilities (after 20 spells)
- `memory_summary` — regime spell statistics

---

## Constellation Placement

```yaml
akasha-capital:
  role: engine
  layer: analysis
  description: Capital flow and market-regime analysis engine. Classifies
    market regimes from stablecoin flow, BTC dominance, volatility, and
    funding signals. Produces regime snapshots, divergence reports, alerts,
    Markov forecasts, and regime memory summaries.
```

See `repo-manifest.yaml` for full declaration.

---

## Lineage

`capital-suite-v5` → canonicalized as `akasha-capital` (v1.0.0)

Source architecture unchanged. Canonical wrapping added:
- `repo-manifest.yaml` (identity + alignment declaration)
- `README.md` (this file)
- `docs/ARCHITECTURE.md` (Akasha structural documentation)
- `docs/AKASHA_ALIGNMENT.md` (axiom-by-axiom alignment record)
- `schemas/regime_event.schema.json` (Akasha event schema)
- `CONSTELLATION_ENTRY.md` (registry patch for akasha-constellation)
- `CHANGELOG.md` (lineage record)
