from dataclasses import dataclass, field
from typing import List
from core.config import VOL_EXPANSION_THRESHOLD, DOM_ROTATION_THRESHOLD


@dataclass
class RegimeState:
    regime: str
    flow_state: int
    volatility: float
    btc_dominance: float
    flow_trend: str
    confidence: float
    score_stddev: float | None
    # v3 additions
    score: float = 0.0
    inflow: float = 0.0
    outflow: float = 0.0
    funding: float = 0.0

    def display(self) -> str:
        lines = [
            f"  regime        : {self.regime}",
            f"  flow_state    : {self.flow_state:+d}",
            f"  score         : {self.score:+.4f}",
            f"  inflow        : {self.inflow:+.4f}",
            f"  outflow       : {self.outflow:+.4f}",
            f"  funding       : {self.funding:+.4f}",
            f"  volatility    : {self.volatility:.3f}",
            f"  btc_dominance : {self.btc_dominance:.2f}%",
            f"  flow_trend    : {self.flow_trend}",
            f"  confidence    : {self.confidence:.1%}",
            f"  score_stddev  : {self.score_stddev}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "regime":        self.regime,
            "flow_state":    self.flow_state,
            "score":         round(self.score, 4),
            "inflow":        round(self.inflow, 4),
            "outflow":       round(self.outflow, 4),
            "funding":       round(self.funding, 4),
            "volatility":    round(self.volatility, 3),
            "btc_dominance": round(self.btc_dominance, 2),
            "flow_trend":    self.flow_trend,
            "confidence":    round(self.confidence, 3),
            "score_stddev":  self.score_stddev,
        }


class CapitalCompass:
    """
    Regime classifier — maps CMI state + market context to a named regime.

    Regimes:
      EXPANSION   — positive flow, elevated vol  (capital entering, risk-on)
      ROTATION    — neutral flow, BTC dominant   (rotation from alts to BTC)
      CONTRACTION — negative flow               (capital leaving crypto)
      TRANSITION  — ambiguous / mixed signals
    """

    def __init__(self, flow_engine, data_source):
        self.flow = flow_engine
        self.data = data_source

    def evaluate(self) -> RegimeState:
        flow_state = self.flow.compute()
        volatility = self.data.volatility()
        dominance  = self.data.btc_dominance()
        trend      = self.flow.trend()
        confidence = self.flow.confidence()
        stddev     = self.flow.score_stddev()
        snap       = self.flow.latest_snapshot()

        regime = self._classify(flow_state, volatility, dominance, trend)

        return RegimeState(
            regime        = regime,
            flow_state    = flow_state,
            volatility    = round(volatility, 3),
            btc_dominance = round(dominance, 2),
            flow_trend    = trend,
            confidence    = confidence,
            score_stddev  = stddev,
            score         = round(snap.score, 4)   if snap else 0.0,
            inflow        = round(snap.inflow, 4)  if snap else 0.0,
            outflow       = round(snap.outflow, 4) if snap else 0.0,
            funding       = round(snap.funding, 4) if snap else 0.0,
        )

    def _classify(self, flow_state, vol, dom, trend) -> str:
        if flow_state == 1 and vol > VOL_EXPANSION_THRESHOLD:
            return "EXPANSION"
        if flow_state == 0 and dom > DOM_ROTATION_THRESHOLD:
            return "ROTATION"
        if flow_state == -1:
            return "CONTRACTION"
        return "TRANSITION"
