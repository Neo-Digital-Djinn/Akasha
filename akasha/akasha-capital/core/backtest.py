"""
Capital Suite v5 — backtest.py
Extends v4 BacktestEngine with:
  - Multi-asset portfolio sweep
  - Per-asset regime distribution
  - Forecast matrix snapshot at end
  - RegimeMemory statistics in report
"""

import json
import statistics
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict

from core.flow          import CapitalFlowIndicator
from core.compass       import CapitalCompass
from core.signals       import DivergenceDetector
from core.watchdog      import RegimeWatchdog
from core.portfolio     import MultiAssetPortfolio
from core.forecast      import RegimeForecaster
from core.regime_memory import RegimeMemory
from adapters.api_client import MarketData
from core.config        import ASSETS


@dataclass
class TickRecord:
    tick: int
    state: dict
    portfolio: Optional[dict]
    divergences: List[dict]
    alerts: List[dict]
    forecast: Optional[dict]


@dataclass
class RegimeSpell:
    regime: str
    start_tick: int
    end_tick: int

    @property
    def length(self) -> int:
        return self.end_tick - self.start_tick + 1


@dataclass
class BacktestReport:
    ticks: int
    multi_asset: bool = False
    records: List[TickRecord] = field(default_factory=list)

    # BTC / primary asset stats
    regime_counts: Dict[str, int]         = field(default_factory=dict)
    regime_pct:    Dict[str, float]       = field(default_factory=dict)
    avg_confidence: float                 = 0.0
    pct_low_conviction: float             = 0.0
    confidence_min: float                 = 0.0
    confidence_max: float                 = 0.0
    total_divergences: int                = 0
    divergence_breakdown: Dict[str, int]  = field(default_factory=dict)
    total_alerts: int                     = 0
    alert_breakdown: Dict[str, int]       = field(default_factory=dict)
    regime_spells: List[RegimeSpell]      = field(default_factory=list)
    avg_spell_length: float               = 0.0
    longest_spell: Optional[RegimeSpell]  = None
    score_mean: float                     = 0.0
    score_stddev: float                   = 0.0
    score_min: float                      = 0.0
    score_max: float                      = 0.0
    transition_rate: float                = 0.0

    # v5 additions
    asset_regime_pct: Dict[str, Dict[str, float]] = field(default_factory=dict)
    forecast_matrix: Dict[str, Dict[str, float]]  = field(default_factory=dict)
    mean_spell_lengths: Dict[str, float]           = field(default_factory=dict)
    memory_summary: dict                           = field(default_factory=dict)
    contraction_to_expansion_lag: Optional[float]  = None

    def finalize(self, forecaster: RegimeForecaster, memory: RegimeMemory,
                 asset_regime_streams: Dict[str, List[str]]):
        if not self.records:
            return

        regimes    = [r.state["regime"]    for r in self.records]
        confs      = [r.state["confidence"] for r in self.records]
        scores     = [r.state["score"]      for r in self.records]
        all_divs   = [d for r in self.records for d in r.divergences]
        all_alerts = [a for r in self.records for a in r.alerts]

        self.regime_counts = dict(Counter(regimes))
        self.regime_pct    = {k: round(v / self.ticks, 3)
                              for k, v in self.regime_counts.items()}
        self.avg_confidence    = round(statistics.mean(confs), 3)
        self.pct_low_conviction= round(sum(1 for c in confs if c < 0.35) / self.ticks, 3)
        self.confidence_min    = round(min(confs), 3)
        self.confidence_max    = round(max(confs), 3)
        self.total_divergences = len(all_divs)
        self.divergence_breakdown = dict(Counter(d["kind"] for d in all_divs))
        self.total_alerts      = len(all_alerts)
        self.alert_breakdown   = dict(Counter(a["code"] for a in all_alerts))
        self.score_mean   = round(statistics.mean(scores), 4)
        self.score_stddev = round(statistics.stdev(scores) if len(scores) > 1 else 0, 4)
        self.score_min    = round(min(scores), 4)
        self.score_max    = round(max(scores), 4)

        spells: List[RegimeSpell] = []
        cur = regimes[0]; start = 1
        for i, r in enumerate(regimes[1:], start=2):
            if r != cur:
                spells.append(RegimeSpell(cur, start, i - 1)); cur = r; start = i
        spells.append(RegimeSpell(cur, start, self.ticks))
        self.regime_spells    = spells
        self.avg_spell_length = round(statistics.mean(s.length for s in spells), 2)
        self.longest_spell    = max(spells, key=lambda s: s.length)
        regime_changes        = sum(1 for a in all_alerts if a["code"].endswith("_ENTRY"))
        self.transition_rate  = round(regime_changes / self.ticks, 4)

        # v5 extras
        self.forecast_matrix   = forecaster.transition_matrix()
        self.mean_spell_lengths= forecaster.mean_spell_lengths()
        self.memory_summary    = memory.to_dict()
        self.contraction_to_expansion_lag = memory.contraction_to_expansion_lag()

        for sym, stream in asset_regime_streams.items():
            counts = Counter(stream)
            self.asset_regime_pct[sym] = {k: round(v / self.ticks, 3)
                                           for k, v in counts.items()}

    def summary(self) -> str:
        lines = [
            f"═══ CAPITAL SUITE v5 BACKTEST ({'%d ticks' % self.ticks}"
            + (" · multi-asset" if self.multi_asset else "") + ") ═══",
            "",
            "BTC REGIME DISTRIBUTION",
        ]
        for r, pct in sorted(self.regime_pct.items(), key=lambda x: -x[1]):
            bar = "█" * int(pct * 20)
            lines.append(f"  {r:<14} {pct:5.1%}  {bar}")

        if self.asset_regime_pct:
            lines += ["", "PER-ASSET DOMINANT REGIME"]
            for sym, dist in self.asset_regime_pct.items():
                top = max(dist, key=dist.get) if dist else "—"
                pct = dist.get(top, 0)
                lines.append(f"  {sym:<4}  {top:<14}  {pct:.0%}")

        lines += [
            "",
            "FLOW SCORE (BTC)",
            f"  mean    : {self.score_mean:+.4f}",
            f"  stddev  : {self.score_stddev:.4f}",
            f"  range   : [{self.score_min:+.4f}, {self.score_max:+.4f}]",
            "",
            "CONFIDENCE",
            f"  avg     : {self.avg_confidence:.1%}",
            f"  min/max : {self.confidence_min:.1%} / {self.confidence_max:.1%}",
            f"  low-conv: {self.pct_low_conviction:.1%} of ticks",
            "",
            "TRANSITIONS",
            f"  rate    : {self.transition_rate:.4f} / tick",
            f"  avg spell length: {self.avg_spell_length:.1f} ticks",
        ]
        if self.longest_spell:
            ls = self.longest_spell
            lines.append(f"  longest : {ls.regime} · {ls.length} ticks (t{ls.start_tick}→t{ls.end_tick})")

        if self.contraction_to_expansion_lag is not None:
            lines.append(f"  contraction→expansion lag: ~{self.contraction_to_expansion_lag:.1f} ticks")

        lines += ["", f"DIVERGENCES ({self.total_divergences} total)"]
        for kind, cnt in sorted(self.divergence_breakdown.items(), key=lambda x: -x[1]):
            lines.append(f"  {kind:<22} {cnt:>4}")

        lines += ["", f"ALERTS ({self.total_alerts} total)"]
        for code, cnt in sorted(self.alert_breakdown.items(), key=lambda x: -x[1]):
            lines.append(f"  {code:<28} {cnt:>4}")

        if self.forecast_matrix:
            lines += ["", "LEARNED TRANSITION MATRIX (→ next regime)"]
            from core.config import REGIME_ORDER
            header = "  FROM\\TO        " + "  ".join(f"{r[:6]:>6}" for r in REGIME_ORDER)
            lines.append(header)
            for fr in REGIME_ORDER:
                row = self.forecast_matrix.get(fr, {})
                vals = "  ".join(f"{row.get(to, 0):>6.1%}" for to in REGIME_ORDER)
                lines.append(f"  {fr:<14}  {vals}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "ticks":                self.ticks,
            "multi_asset":          self.multi_asset,
            "regime_counts":        self.regime_counts,
            "regime_pct":           self.regime_pct,
            "asset_regime_pct":     self.asset_regime_pct,
            "avg_confidence":       self.avg_confidence,
            "confidence_min":       self.confidence_min,
            "confidence_max":       self.confidence_max,
            "pct_low_conviction":   self.pct_low_conviction,
            "score_mean":           self.score_mean,
            "score_stddev":         self.score_stddev,
            "score_min":            self.score_min,
            "score_max":            self.score_max,
            "total_divergences":    self.total_divergences,
            "divergence_breakdown": self.divergence_breakdown,
            "total_alerts":         self.total_alerts,
            "alert_breakdown":      self.alert_breakdown,
            "avg_spell_length":     self.avg_spell_length,
            "transition_rate":      self.transition_rate,
            "contraction_to_expansion_lag": self.contraction_to_expansion_lag,
            "forecast_matrix":      self.forecast_matrix,
            "mean_spell_lengths":   self.mean_spell_lengths,
            "memory_summary":       self.memory_summary,
            "longest_spell": {
                "regime":     self.longest_spell.regime,
                "start_tick": self.longest_spell.start_tick,
                "end_tick":   self.longest_spell.end_tick,
                "length":     self.longest_spell.length,
            } if self.longest_spell else None,
            "records": [
                {
                    "tick":        r.tick,
                    "state":       r.state,
                    "portfolio":   r.portfolio,
                    "divergences": r.divergences,
                    "alerts":      r.alerts,
                    "forecast":    r.forecast,
                }
                for r in self.records
            ],
        }

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Saved backtest to {path}")


class BacktestEngine:
    def __init__(self, ticks: int = 100, seed: Optional[int] = None,
                 multi_asset: bool = False):
        import random
        if seed is not None:
            random.seed(seed)
        self.ticks       = ticks
        self.multi_asset = multi_asset

    def run(self) -> BacktestReport:
        data      = MarketData()
        cmi       = CapitalFlowIndicator(data)
        compass   = CapitalCompass(cmi, data)
        detector  = DivergenceDetector()
        watchdog  = RegimeWatchdog()
        forecaster= RegimeForecaster()
        memory    = RegimeMemory()

        portfolio = MultiAssetPortfolio(data) if self.multi_asset else None

        report = BacktestReport(ticks=self.ticks, multi_asset=self.multi_asset)
        asset_regime_streams: Dict[str, List[str]] = {sym: [] for sym in ASSETS}

        for i in range(self.ticks):
            # BTC primary pipeline
            data.for_asset("BTC")
            state  = compass.evaluate()
            data.tick_done()
            divs   = detector.evaluate(
                state.score, state.inflow, state.outflow,
                state.funding, state.volatility, state.btc_dominance,
            )
            alerts = watchdog.evaluate(
                state.regime, state.confidence, state.score_stddev, i + 1,
            )
            forecast_result = forecaster.ingest(state.regime, i + 1)
            memory.ingest(state.regime, i + 1, state.score, len(divs), len(alerts))

            port_dict = None
            if self.multi_asset and portfolio:
                port_state = portfolio.evaluate()
                port_dict  = port_state.to_dict()
                for sym in ASSETS:
                    asset_regime_streams[sym].append(
                        port_state.assets[sym].state.regime
                    )

            report.records.append(TickRecord(
                tick        = i + 1,
                state       = state.to_dict(),
                portfolio   = port_dict,
                divergences = [{"kind": d.kind, "severity": d.severity,
                                "description": d.description} for d in divs],
                alerts      = [{"level": a.level, "code": a.code,
                                "message": a.message} for a in alerts],
                forecast    = forecast_result.to_dict() if forecast_result else None,
            ))

        report.finalize(forecaster, memory, asset_regime_streams)
        return report
