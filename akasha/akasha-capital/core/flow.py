from collections import deque
from dataclasses import dataclass, field
from typing import Optional
import statistics

from core.config import SIGNAL_THRESHOLD, TREND_THRESHOLD, WINDOW_SIZE


@dataclass
class FlowSnapshot:
    tick: int
    inflow: float
    outflow: float
    funding: float
    score: float
    signal: int
    trend: str


class CapitalFlowIndicator:
    """
    CMI — Capital Market Indicator
    Tracks stablecoin flow balance, funding bias, and rolling trend.
    Produces a signal (-1, 0, +1), trend classification, and confidence.
    """

    def __init__(self, data_source, window: int = WINDOW_SIZE):
        self.data    = data_source
        self.window  = window
        self.history: deque = deque(maxlen=window)
        self._tick   = 0

    def compute(self) -> int:
        self._tick += 1
        inflow  = self.data.stablecoin_inflow()
        outflow = self.data.stablecoin_outflow()
        funding = self.data.funding_bias()
        score   = self._score(inflow, outflow, funding)
        signal  = self._signal(score)
        snap    = FlowSnapshot(
            tick=self._tick,
            inflow=inflow, outflow=outflow, funding=funding,
            score=score, signal=signal, trend=self._trend_from_scores()
        )
        self.history.append(snap)
        return signal

    def latest_snapshot(self) -> Optional[FlowSnapshot]:
        return self.history[-1] if self.history else None

    def trend(self) -> str:
        return self._trend_from_scores()

    def confidence(self) -> float:
        if len(self.history) < 3:
            return 0.0
        latest_signal = self.history[-1].signal
        agreements = sum(1 for s in self.history if s.signal == latest_signal)
        return round(agreements / len(self.history), 3)

    def score_stddev(self) -> Optional[float]:
        scores = [s.score for s in self.history]
        if len(scores) < 2:
            return None
        return round(statistics.stdev(scores), 4)

    def score_series(self) -> list:
        return [round(s.score, 4) for s in self.history]

    def inflow_series(self) -> list:
        return [round(s.inflow, 4) for s in self.history]

    def outflow_series(self) -> list:
        return [round(s.outflow, 4) for s in self.history]

    def summary(self) -> dict:
        if not self.history:
            return {}
        latest = self.history[-1]
        return {
            "tick":         latest.tick,
            "signal":       latest.signal,
            "score":        round(latest.score, 4),
            "inflow":       round(latest.inflow, 4),
            "outflow":      round(latest.outflow, 4),
            "funding":      round(latest.funding, 4),
            "trend":        latest.trend,
            "confidence":   self.confidence(),
            "score_stddev": self.score_stddev(),
            "window_used":  len(self.history),
        }

    def _score(self, inflow, outflow, funding):
        return round((inflow - outflow) * 0.5 + funding * 0.5, 6)

    def _signal(self, x):
        if x > SIGNAL_THRESHOLD:  return  1
        if x < -SIGNAL_THRESHOLD: return -1
        return 0

    def _trend_from_scores(self):
        scores = [s.score for s in self.history]
        if len(scores) < 3:
            return "INSUFFICIENT_DATA"
        delta = scores[-1] - scores[0]
        if delta > TREND_THRESHOLD:  return "ACCELERATING_INFLOW"
        if delta < -TREND_THRESHOLD: return "ACCELERATING_OUTFLOW"
        return "STABLE"
