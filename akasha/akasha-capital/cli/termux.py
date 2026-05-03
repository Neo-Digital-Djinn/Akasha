#!/usr/bin/env python
"""
Capital Suite v4 — Termux CLI runner
Saves last_state.txt + last_alerts.txt for widget/notification use.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.flow     import CapitalFlowIndicator
from core.compass  import CapitalCompass
from core.signals  import DivergenceDetector
from core.watchdog import RegimeWatchdog
from adapters.api_client import MarketData

BASE = os.getenv("APP_DIR", os.getcwd())

data     = MarketData()
cmi      = CapitalFlowIndicator(data)
compass  = CapitalCompass(cmi, data)
detector = DivergenceDetector()
watchdog = RegimeWatchdog()

state   = compass.evaluate()
summary = cmi.summary()
divs    = detector.evaluate(state.score, state.inflow, state.outflow,
                            state.funding, state.volatility, state.btc_dominance)
alerts  = watchdog.evaluate(state.regime, state.confidence, state.score_stddev, 1)

output = f"""CAPITAL SUITE v4
{"="*32}
REGIME     : {state.regime}
FLOW       : {state.flow_state:+d}
SCORE      : {state.score:+.4f}
TREND      : {state.flow_trend}
CONFIDENCE : {state.confidence:.1%}
VOL        : {state.volatility}
DOM        : {state.btc_dominance}%
SCORE_SD   : {state.score_stddev}
DIVS       : {len(divs)}
ALERTS     : {len(alerts)}
"""

print(output)

with open(os.path.join(BASE, "last_state.txt"), "w") as f:
    f.write(output)

if alerts:
    alert_lines = "\n".join(a.display() for a in alerts)
    with open(os.path.join(BASE, "last_alerts.txt"), "w") as f:
        f.write(alert_lines + "\n")
    print("Alerts written to last_alerts.txt")
