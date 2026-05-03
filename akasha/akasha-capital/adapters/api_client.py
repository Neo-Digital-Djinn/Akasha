"""
Capital Suite v5 — MarketData adapter (multi-asset upgrade)

Phase 5: Multi-asset correlated OU simulation.

Each asset shares a latent risk axis but has its own idiosyncratic noise,
producing realistic co-movement with divergence in high-volatility assets.

Phase 3 target: replace each asset's methods with live API calls.
"""

import random
from core.config import ASSETS, ASSET_RISK_LOADING, ASSET_IDIO_SIGMA


def _ou(x, theta, sigma, mean=0.0):
    return x + theta * (mean - x) + sigma * random.gauss(0, 1)


class _SharedMarketState:
    """
    Latent state shared across all assets.
    Drives systematic (market-wide) co-movement.
    """
    def __init__(self):
        self.risk      = 0.0   # market-wide risk axis [-1, +1]
        self.dom_axis  = 0.0   # BTC dominance axis
        self.vol_level = 0.5   # baseline volatility
        self.funding   = 0.0   # baseline funding

    def advance(self):
        self.risk      = _ou(self.risk,      0.12, 0.30)
        self.dom_axis  = _ou(self.dom_axis,  0.08, 0.20)
        self.vol_level = _ou(self.vol_level, 0.10, 0.18, mean=0.5 + 0.3 * abs(self.risk))
        self.funding   = _ou(self.funding,   0.15, 0.25, mean=0.4 * self.risk)

        self.risk      = max(-1.0, min(1.0, self.risk))
        self.dom_axis  = max(-1.0, min(1.0, self.dom_axis))
        self.vol_level = max(0.0,  min(1.0, self.vol_level))
        self.funding   = max(-1.0, min(1.0, self.funding))


class _AssetState:
    """Per-asset idiosyncratic state layered on top of shared risk."""
    def __init__(self, symbol: str):
        self.symbol      = symbol
        self.loading     = ASSET_RISK_LOADING.get(symbol, 0.8)
        self.idio_sigma  = ASSET_IDIO_SIGMA.get(symbol, 0.20)
        self.idio_drift  = 0.0   # asset-specific residual

    def advance(self, shared: _SharedMarketState):
        self.idio_drift = _ou(self.idio_drift, 0.20, self.idio_sigma)

    def effective_risk(self, shared: _SharedMarketState) -> float:
        combined = self.loading * shared.risk + (1 - self.loading) * self.idio_drift
        return max(-1.0, min(1.0, combined))

    def inflow(self, shared: _SharedMarketState) -> float:
        r = self.effective_risk(shared)
        return max(-1.0, min(1.0, 0.5 * r + 0.5 + random.gauss(0, 0.20)))

    def outflow(self, shared: _SharedMarketState) -> float:
        r = self.effective_risk(shared)
        return max(-1.0, min(1.0, -0.4 * r + 0.5 + random.gauss(0, 0.20)))

    def funding(self, shared: _SharedMarketState) -> float:
        r = self.effective_risk(shared)
        f = self.loading * shared.funding + (1 - self.loading) * 0.4 * r
        return max(-1.0, min(1.0, f + random.gauss(0, 0.08)))

    def volatility(self, shared: _SharedMarketState) -> float:
        base = shared.vol_level + 0.15 * (1 - self.loading)  # higher idio → more vol
        return max(0.0, min(1.0, base + random.gauss(0, 0.05)))

    def btc_dominance(self, shared: _SharedMarketState) -> float:
        """BTC dominance is global — driven by shared dom_axis only."""
        return max(30.0, min(70.0, 50.0 + 10.0 * shared.dom_axis + random.gauss(0, 1.0)))


class MarketData:
    """
    v5 multi-asset adapter.
    Default asset = BTC (backwards-compatible with v4 single-asset pipeline).
    Use `.for_asset(symbol)` or `.snapshot_all()` for multi-asset reads.
    """

    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)
        self._shared = _SharedMarketState()
        self._assets = {sym: _AssetState(sym) for sym in ASSETS}
        self._tick_advanced = False
        self._active = "BTC"   # default asset for single-asset calls

    def for_asset(self, symbol: str) -> "MarketData":
        """Switch default asset for single-asset pipeline calls."""
        assert symbol in self._assets, f"Unknown asset: {symbol}"
        self._active = symbol
        return self

    def _maybe_advance(self):
        if not self._tick_advanced:
            self._shared.advance()
            for a in self._assets.values():
                a.advance(self._shared)
            self._tick_advanced = True

    def tick_done(self):
        self._tick_advanced = False

    # ── Single-asset interface (backwards-compatible) ──────────────────────

    def stablecoin_inflow(self) -> float:
        self._maybe_advance()
        return round(self._assets[self._active].inflow(self._shared), 4)

    def stablecoin_outflow(self) -> float:
        return round(self._assets[self._active].outflow(self._shared), 4)

    def funding_bias(self) -> float:
        return round(self._assets[self._active].funding(self._shared), 4)

    def volatility(self) -> float:
        return round(self._assets[self._active].volatility(self._shared), 4)

    def btc_dominance(self) -> float:
        return round(self._assets[self._active].btc_dominance(self._shared), 4)

    # ── Multi-asset snapshot ───────────────────────────────────────────────

    def snapshot_all(self) -> dict:
        """
        Returns one dict per asset with all observables.
        Advances shared state exactly once per call.
        """
        self._maybe_advance()
        out = {}
        for sym, a in self._assets.items():
            out[sym] = {
                "inflow":     round(a.inflow(self._shared), 4),
                "outflow":    round(a.outflow(self._shared), 4),
                "funding":    round(a.funding(self._shared), 4),
                "volatility": round(a.volatility(self._shared), 4),
                "dominance":  round(a.btc_dominance(self._shared), 4),
            }
        return out

    # ── Phase 3 live hooks (stubs) ─────────────────────────────────────────

    @staticmethod
    def from_binance():
        raise NotImplementedError("Phase 3 — Binance adapter not yet implemented")

    @staticmethod
    def from_glassnode(api_key: str):
        raise NotImplementedError("Phase 3 — Glassnode adapter not yet implemented")
