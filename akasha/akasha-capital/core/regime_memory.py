"""
Capital Suite v5 — regime_memory.py
RegimeMemory: persistent spell journal with statistical summaries.

Records every completed regime spell with its duration, entry/exit scores,
and the divergences/alerts that bracketed it. Provides:
  - Full spell history
  - Per-regime duration statistics
  - Mean-reversion timing estimate: how long after contraction does expansion follow?
  - Spell correlation: do high-divergence entries lead to shorter spells?
"""

import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SpellRecord:
    regime: str
    start_tick: int
    end_tick: int
    entry_score: float
    exit_score: float
    peak_divergences: int     # max divs seen in any single tick during spell
    total_alerts: int
    preceded_by: Optional[str]   # previous regime

    @property
    def length(self) -> int:
        return self.end_tick - self.start_tick + 1

    def to_dict(self) -> dict:
        return {
            "regime":          self.regime,
            "start_tick":      self.start_tick,
            "end_tick":        self.end_tick,
            "length":          self.length,
            "entry_score":     round(self.entry_score, 4),
            "exit_score":      round(self.exit_score, 4),
            "peak_divergences":self.peak_divergences,
            "total_alerts":    self.total_alerts,
            "preceded_by":     self.preceded_by,
        }


@dataclass
class RegimeStats:
    regime: str
    spell_count: int
    mean_length: float
    median_length: float
    min_length: int
    max_length: int
    mean_entry_score: float
    mean_exit_score: float

    def display(self) -> str:
        return (
            f"  {self.regime:<14} spells={self.spell_count:>3}"
            f"  len: μ={self.mean_length:.1f} med={self.median_length:.1f}"
            f"  [{self.min_length}–{self.max_length}]"
            f"  entry_score={self.mean_entry_score:+.3f}"
        )


class RegimeMemory:
    """
    Records and analyzes regime spell history.
    Call .open_spell() when a new regime begins and .close_spell() when it ends.
    """

    def __init__(self):
        self._journal: List[SpellRecord] = []
        # in-progress spell tracking
        self._open_regime: Optional[str] = None
        self._open_start: int = 0
        self._open_entry_score: float = 0.0
        self._open_peak_divs: int = 0
        self._open_alerts: int = 0
        self._prev_regime: Optional[str] = None

    def open_spell(self, regime: str, tick: int, score: float):
        if self._open_regime is not None and self._open_regime != regime:
            # auto-close previous
            self._do_close(tick - 1, score, 0)
        self._open_regime = regime
        self._open_start  = tick
        self._open_entry_score = score
        self._open_peak_divs   = 0
        self._open_alerts      = 0

    def update_tick(self, tick: int, score: float, n_divs: int, n_alerts: int):
        """Call each tick while a spell is open."""
        if self._open_regime is None:
            return
        if n_divs > self._open_peak_divs:
            self._open_peak_divs = n_divs
        self._open_alerts += n_alerts

    def close_spell(self, end_tick: int, exit_score: float):
        """Explicitly close the current spell."""
        if self._open_regime is None:
            return
        self._do_close(end_tick, exit_score, 0)

    def ingest(self, regime: str, tick: int, score: float, n_divs: int, n_alerts: int):
        """
        Convenience: call once per tick — auto-opens/closes spells.
        """
        if self._open_regime != regime:
            if self._open_regime is not None:
                self._do_close(tick - 1, score, 0)
            self.open_spell(regime, tick, score)
        self.update_tick(tick, score, n_divs, n_alerts)

    def _do_close(self, end_tick: int, exit_score: float, _unused: int):
        rec = SpellRecord(
            regime=self._open_regime,
            start_tick=self._open_start,
            end_tick=end_tick,
            entry_score=self._open_entry_score,
            exit_score=exit_score,
            peak_divergences=self._open_peak_divs,
            total_alerts=self._open_alerts,
            preceded_by=self._prev_regime,
        )
        self._journal.append(rec)
        self._prev_regime = self._open_regime
        self._open_regime = None

    @property
    def journal(self) -> List[SpellRecord]:
        return list(self._journal)

    def stats_by_regime(self) -> Dict[str, RegimeStats]:
        by_regime: Dict[str, List[SpellRecord]] = {}
        for rec in self._journal:
            by_regime.setdefault(rec.regime, []).append(rec)

        out = {}
        for regime, spells in by_regime.items():
            lengths      = [s.length for s in spells]
            entry_scores = [s.entry_score for s in spells]
            exit_scores  = [s.exit_score  for s in spells]
            out[regime]  = RegimeStats(
                regime=regime,
                spell_count=len(spells),
                mean_length=round(statistics.mean(lengths), 2),
                median_length=round(statistics.median(lengths), 2),
                min_length=min(lengths),
                max_length=max(lengths),
                mean_entry_score=round(statistics.mean(entry_scores), 4),
                mean_exit_score=round(statistics.mean(exit_scores), 4),
            )
        return out

    def contraction_to_expansion_lag(self) -> Optional[float]:
        """
        Mean ticks between end of CONTRACTION spell and start of next EXPANSION.
        Returns None if insufficient data.
        """
        lags = []
        prev: Optional[SpellRecord] = None
        for rec in self._journal:
            if prev is not None and prev.regime == "CONTRACTION" and rec.regime == "EXPANSION":
                gap = rec.start_tick - prev.end_tick
                lags.append(gap)
            prev = rec
        return round(statistics.mean(lags), 2) if len(lags) >= 2 else None

    def high_divergence_spell_length(self) -> Tuple[float, float]:
        """
        Returns (mean_length_high_div, mean_length_low_div).
        High = spells with peak_divergences >= 2.
        """
        high = [r.length for r in self._journal if r.peak_divergences >= 2]
        low  = [r.length for r in self._journal if r.peak_divergences < 2]
        h = round(statistics.mean(high), 2) if high else 0.0
        l = round(statistics.mean(low),  2) if low  else 0.0
        return h, l

    def to_dict(self) -> dict:
        stats = self.stats_by_regime()
        c2e   = self.contraction_to_expansion_lag()
        h, l  = self.high_divergence_spell_length()
        return {
            "total_spells": len(self._journal),
            "stats_by_regime": {r: {
                "spell_count": s.spell_count,
                "mean_length": s.mean_length,
                "median_length": s.median_length,
                "min_length": s.min_length,
                "max_length": s.max_length,
                "mean_entry_score": s.mean_entry_score,
                "mean_exit_score": s.mean_exit_score,
            } for r, s in stats.items()},
            "contraction_to_expansion_lag": c2e,
            "high_div_mean_spell_len": h,
            "low_div_mean_spell_len": l,
            "journal": [r.to_dict() for r in self._journal],
        }

    def summary(self) -> str:
        lines = ["  REGIME MEMORY — SPELL STATISTICS"]
        for r, s in sorted(self.stats_by_regime().items()):
            lines.append(s.display())
        c2e = self.contraction_to_expansion_lag()
        if c2e is not None:
            lines.append(f"\n  contraction→expansion lag : ~{c2e:.1f} ticks")
        h, l = self.high_divergence_spell_length()
        if h or l:
            lines.append(f"  high-div spell length     : {h:.1f} ticks")
            lines.append(f"  low-div  spell length     : {l:.1f} ticks")
        return "\n".join(lines)
