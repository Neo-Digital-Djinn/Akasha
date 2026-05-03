"""
Capital Suite v5 — Central configuration
Adjust thresholds here without touching core logic.
"""

# ── CMI / Flow thresholds ───────────────────────────────────────────────────
SIGNAL_THRESHOLD   = 0.20
TREND_THRESHOLD    = 0.30
WINDOW_SIZE        = 24

# ── Regime classification ───────────────────────────────────────────────────
VOL_EXPANSION_THRESHOLD  = 0.60
DOM_ROTATION_THRESHOLD   = 50.0

# ── Divergence detection ────────────────────────────────────────────────────
DIVERGENCE_FUNDING_FLIP_THRESHOLD = 0.25
DIVERGENCE_DOM_SPIKE_THRESHOLD    = 5.0
DIVERGENCE_VOL_DROP_WHILE_INFLOW  = 0.25

# ── Watchdog alert thresholds ───────────────────────────────────────────────
ALERT_CONFIDENCE_LOW     = 0.35
ALERT_STDDEV_HIGH        = 0.40
ALERT_TRANSITION_STREAK  = 3

# ── CLI ─────────────────────────────────────────────────────────────────────
DEFAULT_TICKS = 5

# ── v5: Multi-asset ─────────────────────────────────────────────────────────
ASSETS = ["BTC", "ETH", "SOL", "BNB"]

ASSET_RISK_LOADING = {
    "BTC": 1.00,
    "ETH": 0.88,
    "SOL": 0.72,
    "BNB": 0.65,
}

ASSET_IDIO_SIGMA = {
    "BTC": 0.10,
    "ETH": 0.18,
    "SOL": 0.28,
    "BNB": 0.22,
}

# ── v5: Regime forecast ─────────────────────────────────────────────────────
FORECAST_MIN_SAMPLES = 20
FORECAST_HORIZON     = 5
REGIME_ORDER = ["EXPANSION", "ROTATION", "CONTRACTION", "TRANSITION"]
