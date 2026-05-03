"""
Capital Suite v5 — portfolio.py
MultiAssetPortfolio: runs the full CMI/Compass pipeline for each asset
simultaneously and produces a composite market-wide regime score.

New in v5:
  - Per-asset RegimeState
  - Composite score = weighted average of individual scores (by risk loading)
  - Portfolio-level regime derived from composite + BTC anchor
  - Dispersion metric: how far assets deviate from each other
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.config import ASSETS, ASSET_RISK_LOADING, REGIME_ORDER
from core.flow    import CapitalFlowIndicator
from core.compass import CapitalCompass, RegimeState


@dataclass
class AssetSnapshot:
    symbol: str
    state: RegimeState
    weight: float   # risk loading weight used in composite


@dataclass
class PortfolioState:
    tick: int
    assets: Dict[str, AssetSnapshot]
    composite_score: float
    composite_regime: str
    dispersion: float          # std of asset scores — 0 = perfect co-movement
    dominant_regime: str       # most common regime across assets
    regime_consensus: float    # fraction of assets in dominant_regime

    def display(self) -> str:
        lines = [
            f"  composite_score   : {self.composite_score:+.4f}",
            f"  composite_regime  : {self.composite_regime}",
            f"  dominant_regime   : {self.dominant_regime}  ({self.regime_consensus:.0%} consensus)",
            f"  score_dispersion  : {self.dispersion:.4f}",
            "",
            "  PER-ASSET",
        ]
        for sym, snap in self.assets.items():
            bar_w = int(abs(snap.state.score) * 10)
            bar = ("+" if snap.state.score >= 0 else "-") + "█" * bar_w + "░" * (10 - bar_w)
            lines.append(
                f"    {sym:<4}  {bar}  score={snap.state.score:+.3f}"
                f"  {snap.state.regime:<12}  conf={snap.state.confidence:.0%}"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "tick":             self.tick,
            "composite_score":  round(self.composite_score, 4),
            "composite_regime": self.composite_regime,
            "dispersion":       round(self.dispersion, 4),
            "dominant_regime":  self.dominant_regime,
            "regime_consensus": round(self.regime_consensus, 3),
            "assets": {
                sym: {
                    "score":      snap.state.score,
                    "regime":     snap.state.regime,
                    "confidence": snap.state.confidence,
                    "inflow":     snap.state.inflow,
                    "outflow":    snap.state.outflow,
                    "funding":    snap.state.funding,
                    "volatility": snap.state.volatility,
                }
                for sym, snap in self.assets.items()
            },
        }


class MultiAssetPortfolio:
    """
    Runs the full pipeline for each asset and aggregates into a
    PortfolioState with composite scoring and consensus metrics.
    """

    def __init__(self, data_source):
        self.data = data_source
        self._tick = 0

        # Build per-asset CMI + Compass pairs
        self._engines: Dict[str, tuple] = {}
        for sym in ASSETS:
            data_source.for_asset(sym)
            cmi     = CapitalFlowIndicator(data_source)
            compass = CapitalCompass(cmi, data_source)
            self._engines[sym] = (cmi, compass)

    def evaluate(self) -> PortfolioState:
        self._tick += 1

        snapshots: Dict[str, AssetSnapshot] = {}
        scores: List[float] = []
        weights: List[float] = []

        for sym in ASSETS:
            self.data.for_asset(sym)
            cmi, compass = self._engines[sym]
            state  = compass.evaluate()
            weight = ASSET_RISK_LOADING[sym]
            snapshots[sym] = AssetSnapshot(symbol=sym, state=state, weight=weight)
            scores.append(state.score)
            weights.append(weight)

        self.data.tick_done()

        # Composite score: loading-weighted average
        total_w = sum(weights)
        composite = sum(s * w for s, w in zip(scores, weights)) / total_w

        # Score dispersion (population std)
        mean_s = sum(scores) / len(scores)
        dispersion = (sum((s - mean_s) ** 2 for s in scores) / len(scores)) ** 0.5

        # Composite regime
        composite_regime = self._classify_composite(composite, snapshots)

        # Consensus
        regime_list = [snap.state.regime for snap in snapshots.values()]
        from collections import Counter
        most_common, count = Counter(regime_list).most_common(1)[0]
        consensus = count / len(regime_list)

        return PortfolioState(
            tick=self._tick,
            assets=snapshots,
            composite_score=round(composite, 4),
            composite_regime=composite_regime,
            dispersion=round(dispersion, 4),
            dominant_regime=most_common,
            regime_consensus=round(consensus, 3),
        )

    def _classify_composite(self, score: float, snaps: Dict[str, AssetSnapshot]) -> str:
        """
        Composite regime follows BTC anchor but is overridden by unanimous signals.
        """
        btc_regime = snaps["BTC"].state.regime if "BTC" in snaps else None
        if score > 0.20:
            vol = snaps["BTC"].state.volatility if "BTC" in snaps else 0.5
            return "EXPANSION" if vol > 0.60 else "TRANSITION"
        if score < -0.20:
            return "CONTRACTION"
        dom = snaps["BTC"].state.btc_dominance if "BTC" in snaps else 50.0
        if abs(score) <= 0.20 and dom > 50.0:
            return "ROTATION"
        return btc_regime or "TRANSITION"
