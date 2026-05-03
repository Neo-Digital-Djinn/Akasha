# Constellation Entry — akasha-capital

This file contains the registry patch to formally admit `akasha-capital`
into the Akasha Constellation.

## Patch: akasha-constellation/registry.yaml

Add the following entry under the `repos:` key:

```yaml
  akasha-capital:
    role: engine
    layer: analysis
    description: >
      Capital flow and market-regime analysis engine. Classifies market regimes
      (EXPANSION, ROTATION, CONTRACTION, TRANSITION) from stablecoin flow,
      BTC dominance, funding bias, and volatility signals. Provides multi-asset
      portfolio analysis, Markov regime forecasting, and persistent regime memory.
      Emits Akasha-compatible event payloads for ingestion by akasha-events.
      Not a trading system — a structured observation and reasoning instrument.
    depends_on:
      - akasha-events
      - akasha-apis
    inputs:
      - stablecoin_inflow_signals
      - stablecoin_outflow_signals
      - funding_bias_readings
      - btc_dominance_readings
      - volatility_readings
    outputs:
      - regime_state_snapshots
      - divergence_reports
      - watchdog_alerts
      - markov_regime_forecasts
      - regime_memory_summaries
      - akasha_event_payloads
    canonical_status: canonical
    maturity: stable
    source_lineage: capital-suite-v5
```

## Admission Checklist

- [x] Axiom alignment documented in `docs/AKASHA_ALIGNMENT.md`
- [x] `repo-manifest.yaml` complete with all required fields
- [x] Role declared: `engine`
- [x] Layer declared: `analysis`
- [x] Inputs declared
- [x] Outputs declared
- [x] Dependencies declared
- [x] Canonical status: `canonical`
- [x] Human steward declared
- [x] Alignment statement present
- [x] Admission test passed (see `docs/AKASHA_ALIGNMENT.md`)

## System Organ Type

`akasha-capital` is a **system organ** — a canonical, active member of the
Akasha constellation with declared role, layer, interfaces, and alignment.

It is not a lab, not an experiment, not a stub.
It is a working analysis instrument, fully integrated.
