"""
tests/test_smoke.py
akasha-discovery

Verifies:
  1. DB initialises without error
  2. Epoch runner completes without error
  3. Schema columns match what driver.py expects (src/dst not source/target)
  4. Holes table uses Phase 2 schema
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from great_discovery.core_engine import init_db
from great_discovery.driver import run_epoch


def test_db_init():
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "test.db")
        conn = init_db(db_path)

        cur = conn.cursor()
        cur.execute("PRAGMA table_info(edges)")
        columns = {row[1] for row in cur.fetchall()}
        assert "src" in columns, f"edges.src missing — got {columns}"
        assert "dst" in columns, f"edges.dst missing — got {columns}"

        cur.execute("PRAGMA table_info(holes)")
        hole_cols = {row[1] for row in cur.fetchall()}
        assert "epoch_found" in hole_cols
        assert "shape_sig"   in hole_cols
        conn.close()


def test_epoch_runs():
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "epoch_test.db")
        result = run_epoch(0, db_path=db_path)
        assert result is not None
        assert "nodes" in result
        assert "edges" in result
        assert "open_holes" in result


def test_multiple_epochs():
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "multi.db")
        for i in range(5):
            r = run_epoch(i, db_path=db_path)
            assert r is not None, f"Epoch {i} returned None"
        assert r["nodes"] >= 7   # seeds never shrink
        assert r["edges"] >= 5   # 5 edges added


if __name__ == "__main__":
    test_db_init()
    test_epoch_runs()
    test_multiple_epochs()
    print("All smoke tests passed.")
