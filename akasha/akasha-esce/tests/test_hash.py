# tests/test_hash.py

from esce.pipeline import Pipeline


def test_hash_length():
    pipeline = Pipeline(["hash"])
    result = pipeline.process(b"abc")
    assert len(result) == 32, "SHA-256 digest must be 32 bytes"


def test_hash_deterministic():
    pipeline = Pipeline(["hash"])
    r1 = pipeline.process(b"akasha")
    r2 = pipeline.process(b"akasha")
    assert r1 == r2, "Hash must be deterministic (Axiom 1)"


def test_hash_distinct():
    pipeline = Pipeline(["hash"])
    r1 = pipeline.process(b"alpha")
    r2 = pipeline.process(b"beta")
    assert r1 != r2, "Different inputs must produce different hashes"
