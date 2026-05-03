#!/usr/bin/env python3
"""
Capital Suite v5 — Debian CLI runner

Usage:
  python3 cli/debian.py                              # 5 ticks, BTC
  CS_TICKS=20 python3 cli/debian.py                 # 20 ticks
  CS_ASSETS=multi python3 cli/debian.py             # multi-asset mode
  CS_TICKS=10 CS_JSON=1 python3 cli/debian.py       # JSON export
  CS_BACKTEST=200 python3 cli/debian.py             # backtest + summary
  CS_BACKTEST=200 CS_ASSETS=multi python3 cli/debian.py  # multi-asset backtest
  CS_BACKTEST=500 CS_SEED=42 CS_JSON=1 python3 cli/debian.py
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.flow          import CapitalFlowIndicator
from core.compass       import CapitalCompass
from core.signals       import DivergenceDetector
from core.watchdog      import RegimeWatchdog
from core.forecast      import RegimeForecaster
from core.regime_memory import RegimeMemory
from core.portfolio     import MultiAssetPortfolio
from core.config        import DEFAULT_TICKS, ASSETS
from adapters.api_client import MarketData

TICKS      = int(os.getenv("CS_TICKS",    str(DEFAULT_TICKS)))
JSON_OUT   = os.getenv("CS_JSON",   "0") == "1"
BACKTEST_N = os.getenv("CS_BACKTEST","0")
SEED       = os.getenv("CS_SEED",   None)
MULTI      = os.getenv("CS_ASSETS", "btc").lower() == "multi"

# ── Backtest mode ─────────────────────────────────────────────────────────────
if BACKTEST_N != "0":
    from core.backtest import BacktestEngine
    n    = int(BACKTEST_N)
    seed = int(SEED) if SEED else None
    label = f"{n} ticks{'  seed='+str(seed) if seed else ''}{'  multi-asset' if MULTI else ''}"
    print(f"  Running backtest · {label}…")
    report = BacktestEngine(ticks=n, seed=seed, multi_asset=MULTI).run()
    if JSON_OUT:
        out_path = os.getenv("CS_OUT", "backtest_report_v5.json")
        report.to_json(out_path)
    else:
        print(report.summary())
    sys.exit(0)

# ── Streaming tick mode ────────────────────────────────────────────────────────
data      = MarketData(seed=int(SEED) if SEED else None)
data.for_asset("BTC")
cmi       = CapitalFlowIndicator(data)
compass   = CapitalCompass(cmi, data)
detector  = DivergenceDetector()
watchdog  = RegimeWatchdog()
forecaster= RegimeForecaster()
memory    = RegimeMemory()
portfolio = MultiAssetPortfolio(data) if MULTI else None

if JSON_OUT:
    results = []
    for i in range(TICKS):
        data.for_asset("BTC")
        state  = compass.evaluate()
        data.tick_done()
        divs   = detector.evaluate(state.score, state.inflow, state.outflow,
                                   state.funding, state.volatility, state.btc_dominance)
        alerts = watchdog.evaluate(state.regime, state.confidence,
                                   state.score_stddev, i + 1)
        fc     = forecaster.ingest(state.regime, i + 1)
        memory.ingest(state.regime, i + 1, state.score, len(divs), len(alerts))
        port   = portfolio.evaluate().to_dict() if portfolio else None
        results.append({
            "tick":        i + 1,
            "state":       state.to_dict(),
            "portfolio":   port,
            "divergences": [{"kind": d.kind, "severity": d.severity,
                             "description": d.description} for d in divs],
            "alerts":      [{"level": a.level, "code": a.code,
                             "message": a.message} for a in alerts],
            "forecast":    fc.to_dict() if fc else None,
        })
    print(json.dumps(results, indent=2))
    sys.exit(0)

# ── Pretty terminal output ─────────────────────────────────────────────────────
W = 60
def hr(ch="─"): print(ch * W)
def section(title): print(f"\n{'─'*2} {title} {'─'*(W - len(title) - 4)}")

hr("═")
print(f"  CAPITAL SUITE v5  ·  {'multi-asset' if MULTI else 'BTC'} OU-correlated simulation")
hr("═")

for i in range(TICKS):
    data.for_asset("BTC")
    state  = compass.evaluate()
    data.tick_done()
    divs   = detector.evaluate(state.score, state.inflow, state.outflow,
                               state.funding, state.volatility, state.btc_dominance)
    alerts = watchdog.evaluate(state.regime, state.confidence,
                               state.score_stddev, i + 1)
    fc     = forecaster.ingest(state.regime, i + 1)
    memory.ingest(state.regime, i + 1, state.score, len(divs), len(alerts))

    section(f"tick {i+1}/{TICKS}")
    print(state.display())

    if MULTI and portfolio:
        port = portfolio.evaluate()
        section("PORTFOLIO")
        print(port.display())

    if fc:
        section("FORECAST")
        print(fc.display())

    if divs:
        section("DIVERGENCES")
        for d in divs: print(d.display())

    if alerts:
        section("ALERTS")
        for a in alerts: print(a.display())

print()
hr("═")
summary = cmi.summary()
print(f"  final confidence  : {summary.get('confidence', 0):.1%}")
print(f"  score stddev      : {summary.get('score_stddev', 'n/a')}")
print(f"  window used       : {summary.get('window_used', 0)}/{cmi.window}")
print(f"  total alerts      : {len(watchdog.alerts)}")
print()
print(memory.summary())
hr("═")
print("  tip: CS_BACKTEST=200 CS_ASSETS=multi python3 cli/debian.py")
hr("═")
