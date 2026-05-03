# Changelog — akasha-capital

## v1.0.0 — Canonicalization (2026-05-02)

**Source:** `capital-suite-v5`

Canonicalization into the Akasha ecosystem. No core logic was altered.
All changes are additive — canonical wrapping only.

### Added

- `repo-manifest.yaml` — full identity, role, layer, interface, and alignment declaration
- `README.md` — Akasha-aligned documentation with axiom alignment table
- `docs/AKASHA_ALIGNMENT.md` — axiom-by-axiom formal alignment record
- `docs/ARCHITECTURE.md` — structural documentation for constellation context
- `schemas/regime_event.schema.json` — Akasha event schema for akasha-events ingestion
- `CONSTELLATION_ENTRY.md` — registry patch for akasha-constellation admission
- `CHANGELOG.md` — this file

### Preserved (unchanged from capital-suite-v5)

- `core/config.py`
- `core/flow.py` (CapitalFlowIndicator / CMI)
- `core/compass.py` (CapitalCompass / RegimeState)
- `core/signals.py` (DivergenceDetector)
- `core/watchdog.py` (RegimeWatchdog)
- `core/backtest.py` (BacktestEngine)
- `core/portfolio.py` (MultiAssetPortfolio)
- `core/forecast.py` (RegimeForecaster)
- `core/regime_memory.py` (RegimeMemory)
- `adapters/api_client.py` (MarketData simulator)
- `cli/main.py` (multi-tick runner)
- `cli/termux.py` (single-tick runner)
- `capital_dashboard.html` (browser dashboard)

---

## capital-suite-v5 — Pre-Canonicalization History

### v5 (pre-canonical)
- MultiAssetPortfolio (BTC/ETH/SOL/BNB) with shared latent risk axis
- RegimeForecaster with online Markov transition matrix
- RegimeMemory persistent spell journal
- Multi-asset OU correlated market data simulator
- Full v5 browser dashboard with multi-asset panel, forecast panel, memory panel

### v4 (pre-canonical)
- BacktestEngine + BacktestReport
- OU simulation with correlation matrix

### v3 (pre-canonical)
- DivergenceDetector (4 divergence types)
- RegimeWatchdog (structured alerts)
- Dashboard heatmap, sparklines

### v2 (pre-canonical)
- Live dashboard + Claude AI analysis integration

### v1 (pre-canonical)
- Core architecture: CMI, CapitalCompass, RegimeState
