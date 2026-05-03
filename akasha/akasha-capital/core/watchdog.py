"""
Capital Suite v3 — watchdog.py
RegimeWatchdog: fires structured alerts when anomalous conditions persist.
Designed to be lightweight — no external deps, pure Python.
"""

from dataclasses import dataclass, field
from collections import deque
from typing import List, Optional
from core.config import (
    ALERT_CONFIDENCE_LOW,
    ALERT_STDDEV_HIGH,
    ALERT_TRANSITION_STREAK,
)


@dataclass
class Alert:
    level: str          # 'INFO' | 'WARN' | 'CRITICAL'
    code: str           # machine-readable identifier
    message: str
    tick: int

    def display(self) -> str:
        icons = {"INFO": "ℹ", "WARN": "⚠", "CRITICAL": "✖"}
        return f"  {icons.get(self.level,'?')} [{self.level:<8}] {self.code:<28} {self.message}  (t:{self.tick})"


class RegimeWatchdog:
    """
    Monitors regime state across ticks and emits alerts when:
      - Confidence drops below threshold
      - Score standard deviation is too high (noisy/unstable market)
      - Regime stays TRANSITION for too long (indecision streak)
      - A CONTRACTION begins (capital-leaving event)
      - An EXPANSION begins (capital-entering event)
    """

    def __init__(self):
        self._tick              = 0
        self._alerts: List[Alert] = []
        self._regime_history: deque = deque(maxlen=20)
        self._prev_regime: Optional[str] = None
        self._transition_streak = 0
        self._notified_contraction = False
        self._notified_expansion   = False

    @property
    def alerts(self) -> List[Alert]:
        return list(self._alerts)

    def recent_alerts(self, n: int = 5) -> List[Alert]:
        return self._alerts[-n:]

    def evaluate(
        self,
        regime: str,
        confidence: float,
        score_stddev: Optional[float],
        tick: int,
    ) -> List[Alert]:
        self._tick = tick
        new_alerts: List[Alert] = []

        self._regime_history.append(regime)

        # ── transition streak ──────────────────────────────────────────────
        if regime == "TRANSITION":
            self._transition_streak += 1
        else:
            self._transition_streak = 0

        if self._transition_streak >= ALERT_TRANSITION_STREAK:
            new_alerts.append(Alert(
                level="WARN",
                code="PROLONGED_TRANSITION",
                message=f"{self._transition_streak} consecutive TRANSITION ticks — indecision",
                tick=tick,
            ))

        # ── low confidence ─────────────────────────────────────────────────
        if confidence < ALERT_CONFIDENCE_LOW:
            new_alerts.append(Alert(
                level="INFO",
                code="LOW_CONVICTION",
                message=f"confidence={confidence:.1%} — regime signal unreliable",
                tick=tick,
            ))

        # ── noisy score ────────────────────────────────────────────────────
        if score_stddev is not None and score_stddev > ALERT_STDDEV_HIGH:
            new_alerts.append(Alert(
                level="WARN",
                code="HIGH_VOLATILITY_SIGNAL",
                message=f"score_stddev={score_stddev:.4f} — erratic flow environment",
                tick=tick,
            ))

        # ── regime transition events ───────────────────────────────────────
        if regime != self._prev_regime:
            if regime == "CONTRACTION":
                new_alerts.append(Alert(
                    level="CRITICAL",
                    code="CONTRACTION_ENTRY",
                    message=f"Capital outflow regime began (was {self._prev_regime})",
                    tick=tick,
                ))
            elif regime == "EXPANSION":
                new_alerts.append(Alert(
                    level="INFO",
                    code="EXPANSION_ENTRY",
                    message=f"Capital inflow regime began (was {self._prev_regime})",
                    tick=tick,
                ))
            elif regime == "ROTATION":
                new_alerts.append(Alert(
                    level="INFO",
                    code="ROTATION_ENTRY",
                    message=f"Alt→BTC rotation regime detected (was {self._prev_regime})",
                    tick=tick,
                ))

        self._prev_regime = regime
        self._alerts.extend(new_alerts)
        # keep bounded
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]
        return new_alerts
