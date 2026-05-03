# tests/test_pipeline.py

from esce.pipeline import Pipeline


def test_xor_pipeline_transforms():
    pipeline = Pipeline(["xor"])
    data = b"hello"
    result = pipeline.process(data)
    assert result != data, "XOR must transform data"


def test_xor_is_self_inverse():
    pipeline = Pipeline(["xor"])
    data = b"hello akasha"
    encoded = pipeline.process(data)
    decoded = pipeline.process(encoded)
    assert decoded == data, "XOR decode must recover original (self-inverse)"


def test_pipeline_ordering():
    """Axiom 1: execution order must be explicit and deterministic."""
    p1 = Pipeline(["hash"])
    p2 = Pipeline(["hash"])
    assert p1.process(b"test") == p2.process(b"test"), "Pipeline must be deterministic"


def test_empty_pipeline():
    """A pipeline with no plugins is valid and returns data unchanged."""
    from esce.plugin_loader import load_plugins
    from esce.pipeline import Pipeline
    p = Pipeline.__new__(Pipeline)
    p.plugin_order = []
    p.plugins = []
    assert p.process(b"unchanged") == b"unchanged"
