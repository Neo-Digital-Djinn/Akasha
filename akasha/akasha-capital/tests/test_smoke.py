"""
akasha-capital — smoke test
Validates that the core pipeline runs and produces expected output types.
Aligned with Axiom 5 (Traceability) and Axiom 8 (Iteration).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.api_client import MarketData
from core.flow import CapitalFlowIndicator
from core.compass import CapitalCompass
from core.signals import DivergenceDetector
from core.watchdog import RegimeWatchdog


def test_regime_pipeline_runs():
    data = MarketData(seed=42)
    flow = CapitalFlowIndicator(data)
    compass = CapitalCompass(flow, data)
    detector = DivergenceDetector()
    watchdog = RegimeWatchdog()

    for tick in range(10):
        state = compass.evaluate()
        divergences = detector.evaluate(
            score=state.score,
            inflow=state.inflow,
            outflow=state.outflow,
            funding=state.funding,
            vol=state.volatility,
            dom=state.btc_dominance,
        )
        alerts = watchdog.evaluate(
            regime=state.regime,
            confidence=state.confidence,
            score_stddev=state.score_stddev,
            tick=tick,
        )

        assert state.regime in ("EXPANSION", "ROTATION", "CONTRACTION", "TRANSITION")
        assert 0.0 <= state.confidence <= 1.0
        assert isinstance(divergences, list)
        assert isinstance(alerts, list)

    print("✓ akasha-capital smoke test passed — regime pipeline operational")


def test_manifest_fields_present():
    import yaml
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "repo-manifest.yaml")
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    required = ["repo", "identity", "interfaces", "alignment", "depends_on"]
    for field in required:
        assert field in manifest, f"Missing manifest field: {field}"

    assert manifest["alignment"]["axioms_required"] is True
    assert manifest["ownership"]["steward"] == "human"

    print("✓ akasha-capital manifest validation passed — canonical structure confirmed")


if __name__ == "__main__":
    test_regime_pipeline_runs()
    try:
        test_manifest_fields_present()
    except ImportError:
        print("  (yaml not available — skipping manifest test)")
    print("\nakasha-capital is operational and canon-compliant.")
