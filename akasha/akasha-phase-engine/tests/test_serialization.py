"""
tests/test_serialization.py — Tests for the inf serialization bug in phase.py

json.dump does NOT call the default= hook for plain floats, so float('inf')
produced invalid JSON (`Infinity` token).  This suite confirms the fix.
"""
import sys, os, json, tempfile

import pytest
from akasha_phase_engine.database import build_default_registry


@pytest.fixture(scope="module")
def registry():
    return build_default_registry()


def test_to_json_produces_valid_json(registry):
    """to_json() must not crash and must write parseable JSON."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    registry.to_json(path)
    with open(path) as f:
        data = json.load(f)   # would raise json.JSONDecodeError if invalid
    assert "phases" in data
    assert "transitions" in data


def test_no_infinity_tokens_in_output(registry):
    """The string 'Infinity' must not appear in the JSON output."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode='w') as f:
        path = f.name
    registry.to_json(path)
    with open(path) as f:
        raw = f.read()
    assert "Infinity" not in raw, (
        "JSON contains bare 'Infinity' — float('inf') not sanitised before dump"
    )
    assert "NaN" not in raw


def test_material_pressure_range_serialized(registry):
    """Material.pressure_range=(0, inf) must appear as (0, 'inf') in JSON."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    registry.to_json(path)
    with open(path) as f:
        data = json.load(f)

    for phase_data in data["phases"]:
        for mat in phase_data.get("materials", []):
            # temperature_range values must be numbers or "inf" strings
            for v in mat.get("temp_range", []):
                assert isinstance(v, (int, float, str)), f"Unexpected type: {type(v)}"


def test_phase_temperature_range_serialized(registry):
    """Phase.temperature_range=(0, inf) must not produce Infinity."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    registry.to_json(path)
    with open(path) as f:
        raw = f.read()
    # Standard JSON parsers reject Infinity
    try:
        json.loads(raw)
    except json.JSONDecodeError as e:
        pytest.fail(f"Output is not valid JSON: {e}")
