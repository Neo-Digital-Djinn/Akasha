"""
Capital Suite v5 — forecast.py
RegimeForecaster: learns a Markov transition matrix from observed regime
spells and emits next-regime probabilities + expected spell duration.

The forecaster is stateful — it ingests one regime per tick and updates
its internal matrix online. After FORECAST_MIN_SAMPLES spells, the matrix
is considered reliable enough to report.

Usage:
    forecaster = RegimeForecaster()
    for tick_regime in regime_stream:
        result = forecaster.ingest(tick_regime, tick)
        if result:
            print(result.display())
"""

import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.config import FORECAST_MIN_SAMPLES, FORECAST_HORIZON, REGIME_ORDER


@dataclass
class ForecastResult:
    current_regime: str
    tick: int
    next_probs: Dict[str, float]          # P(next regime | current)
    most_likely_next: str
    most_likely_prob: float
    expected_remaining_ticks: float       # E[spell length] - ticks_in_current_spell
    spell_count: int                      # how many complete spells observed
    matrix_reliable: bool                 # True when spell_count >= MIN_SAMPLES

    def display(self) -> str:
        reliability = "✓ reliable" if self.matrix_reliable else f"⚠ warming up ({self.spell_count}/{FORECAST_MIN_SAMPLES} spells)"
        lines = [
            f"  forecast          : {reliability}",
            f"  current           : {self.current_regime}",
            f"  next most likely  : {self.most_likely_next}  ({self.most_likely_prob:.1%})",
            f"  spell remaining   : ~{self.expected_remaining_ticks:.1f} ticks",
            "",
            "  TRANSITION PROBABILITIES",
        ]
        for r in REGIME_ORDER:
            p = self.next_probs.get(r, 0.0)
            bar = "█" * int(p * 20) + "░" * (20 - int(p * 20))
            lines.append(f"    → {r:<14} {bar}  {p:.1%}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "current_regime":           self.current_regime,
            "tick":                     self.tick,
            "next_probs":               self.next_probs,
            "most_likely_next":         self.most_likely_next,
            "most_likely_prob":         round(self.most_likely_prob, 3),
            "expected_remaining_ticks": round(self.expected_remaining_ticks, 2),
            "spell_count":              self.spell_count,
            "matrix_reliable":          self.matrix_reliable,
        }


class RegimeForecaster:
    """
    Online Markov transition matrix + spell duration model.
    Updates incrementally — no batch needed.
    """

    def __init__(self):
        # transition_counts[from][to] = N observed transitions
        self._transitions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # spell_lengths[regime] = list of observed lengths
        self._spell_lengths: Dict[str, List[int]] = defaultdict(list)

        self._prev_regime: Optional[str] = None
        self._spell_start_tick: int = 1
        self._current_spell_len: int = 0
        self._complete_spells: int = 0

    def ingest(self, regime: str, tick: int) -> Optional[ForecastResult]:
        """
        Feed one tick's regime. Returns ForecastResult after the first
        complete spell is observed (i.e., after first regime change).
        """
        if self._prev_regime is None:
            self._prev_regime = regime
            self._spell_start_tick = tick
            self._current_spell_len = 1
            return None

        if regime == self._prev_regime:
            self._current_spell_len += 1
        else:
            # Spell ended — record it
            self._spell_lengths[self._prev_regime].append(self._current_spell_len)
            self._transitions[self._prev_regime][regime] += 1
            self._complete_spells += 1
            self._prev_regime = regime
            self._spell_start_tick = tick
            self._current_spell_len = 1

        if self._complete_spells < 1:
            return None

        return self._build_result(regime, tick)

    def _build_result(self, regime: str, tick: int) -> ForecastResult:
        # Transition probabilities from current regime
        counts = self._transitions.get(regime, {})
        total  = sum(counts.values())
        if total > 0:
            raw_probs = {r: counts.get(r, 0) / total for r in REGIME_ORDER}
        else:
            # No data yet for this regime — uniform over others
            others = [r for r in REGIME_ORDER if r != regime]
            raw_probs = {r: (1 / len(others) if r != regime else 0.0) for r in REGIME_ORDER}

        # Expected remaining ticks in current spell
        observed_lengths = self._spell_lengths.get(regime, [])
        if observed_lengths:
            mean_len = statistics.mean(observed_lengths)
        else:
            mean_len = 5.0  # prior
        remaining = max(0.0, mean_len - self._current_spell_len)

        most_likely = max(raw_probs, key=lambda r: raw_probs[r])

        return ForecastResult(
            current_regime=regime,
            tick=tick,
            next_probs={r: round(raw_probs[r], 3) for r in REGIME_ORDER},
            most_likely_next=most_likely,
            most_likely_prob=round(raw_probs[most_likely], 3),
            expected_remaining_ticks=round(remaining, 2),
            spell_count=self._complete_spells,
            matrix_reliable=self._complete_spells >= FORECAST_MIN_SAMPLES,
        )

    def transition_matrix(self) -> Dict[str, Dict[str, float]]:
        """Return full normalized transition matrix."""
        matrix = {}
        for from_r in REGIME_ORDER:
            counts = self._transitions.get(from_r, {})
            total  = sum(counts.values())
            if total > 0:
                matrix[from_r] = {to_r: round(counts.get(to_r, 0) / total, 3)
                                  for to_r in REGIME_ORDER}
            else:
                matrix[from_r] = {to_r: 0.0 for to_r in REGIME_ORDER}
        return matrix

    def mean_spell_lengths(self) -> Dict[str, float]:
        return {
            r: round(statistics.mean(v), 2) if v else 0.0
            for r, v in self._spell_lengths.items()
        }
