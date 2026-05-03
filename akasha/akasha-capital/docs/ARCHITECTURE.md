# Architecture — akasha-capital

## System Role

`akasha-capital` is an **analysis engine** in the Akasha constellation.
It occupies the `analysis` layer — downstream of raw data ingestion,
upstream of interpretation, forecasting, and event storage.

## Data Flow

```
[Market Signals]
       │
       ▼
adapters/api_client.py (MarketData)
       │  stablecoin_inflow / outflow
       │  funding_bias
       │  btc_dominance
       │  volatility
       ▼
core/flow.py (CapitalFlowIndicator / CMI)
       │  signal: -1 / 0 / +1
       │  trend, confidence, score_stddev
       ▼
core/compass.py (CapitalCompass)
       │  RegimeState
       │    regime: EXPANSION | ROTATION | CONTRACTION | TRANSITION
       │    score, inflow, outflow, funding, volatility, dominance
       ▼
core/signals.py (DivergenceDetector)
       │  Divergence[]
       │    FUNDING_FLIP | DOM_SPIKE | VOL_COMPRESSION | SCORE_INVERSION
       ▼
core/watchdog.py (RegimeWatchdog)
       │  Alert[]
       │    LOW_CONVICTION | HIGH_VOLATILITY_SIGNAL | PROLONGED_TRANSITION
       │    CONTRACTION_ENTRY | EXPANSION_ENTRY | ROTATION_ENTRY
       ▼
core/portfolio.py (MultiAssetPortfolio)      [optional, CS_ASSETS=multi]
       │  composite_score, regime_consensus, dispersion
       ▼
core/forecast.py (RegimeForecaster)          [after 20 spells]
       │  MarkovTransitionMatrix
       │  next_regime_probabilities
       │  expected_duration_remaining
       ▼
core/regime_memory.py (RegimeMemory)
       │  spell_journal
       │  per_regime_statistics
       │  contraction_expansion_lag
       ▼
[Outputs]
  cli/main.py       → human-readable terminal output
  CS_JSON=1         → JSON event payloads (Akasha-compatible)
  capital_dashboard.html → browser dashboard
```

## Module Responsibilities

| Module | Class | Responsibility |
|---|---|---|
| `config.py` | — | All thresholds and constants. Single source of truth. |
| `flow.py` | `CapitalFlowIndicator` | CMI computation. Rolling window. Signal, trend, confidence. |
| `compass.py` | `CapitalCompass` | Regime classification from CMI + market context. |
| `signals.py` | `DivergenceDetector` | Structural inconsistency detection across sub-indicators. |
| `watchdog.py` | `RegimeWatchdog` | Persistent alert monitoring across ticks. |
| `backtest.py` | `BacktestEngine` | Deterministic replay for regime behavior analysis. |
| `portfolio.py` | `MultiAssetPortfolio` | Shared latent risk axis across BTC/ETH/SOL/BNB. |
| `forecast.py` | `RegimeForecaster` | Online Markov transition matrix from observed spells. |
| `regime_memory.py` | `RegimeMemory` | Persistent spell journal with statistical summaries. |
| `api_client.py` | `MarketData` | Data adapter. Currently: multi-asset OU correlated simulator. |

## Adapter Contract

`api_client.py` implements the `MarketData` interface:

```python
data.stablecoin_inflow() -> float
data.stablecoin_outflow() -> float
data.funding_bias() -> float
data.btc_dominance() -> float
data.volatility() -> float
```

To connect real data: implement a class satisfying this interface and
pass it to `CapitalFlowIndicator` and `CapitalCompass`. No core changes required.

## Akasha Event Schema

When `CS_JSON=1`, emitted payloads conform to `schemas/regime_event.schema.json`.
These payloads are structured for ingestion by `akasha-events`.
