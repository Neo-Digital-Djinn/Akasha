"""
Aetherius smoke tests
Axiom 5 — Traceability: every engine action must be ledger-visible.
Axiom 7 — Transparency: governor state must be readable at any time.
"""

import time
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ─── Governor ──────────────────────────────────────────────────────────────

def test_governor_allows_under_limit():
    from aetherius_governor import AetheriusGovernor
    g = AetheriusGovernor(github_limit_per_min=5, llm_limit_per_min=5)
    for _ in range(5):
        assert g.allow_github() is True


def test_governor_throttles_over_limit():
    from aetherius_governor import AetheriusGovernor
    g = AetheriusGovernor(github_limit_per_min=3, llm_limit_per_min=3)
    for _ in range(3):
        g.allow_github()
    assert g.allow_github() is False


def test_governor_status_keys():
    from aetherius_governor import AetheriusGovernor
    g = AetheriusGovernor()
    s = g.status()
    assert {"github_limit", "github_used", "llm_limit", "llm_used"} <= s.keys()


def test_governor_llm_throttle():
    from aetherius_governor import AetheriusGovernor
    g = AetheriusGovernor(llm_limit_per_min=2)
    assert g.allow_llm() is True
    assert g.allow_llm() is True
    assert g.allow_llm() is False


# ─── Engine ────────────────────────────────────────────────────────────────

def test_engine_compute_score_bug_label():
    from aetherius_engine import AetheriusEngine
    e = AetheriusEngine(token="fake", repo_list=["x/y"])
    issue = {"body": "short", "labels": [{"name": "bug"}]}
    assert e.compute_score(issue) > 50


def test_engine_compute_score_no_labels():
    from aetherius_engine import AetheriusEngine
    e = AetheriusEngine(token="fake", repo_list=["x/y"])
    issue = {"body": "x" * 100, "labels": []}
    assert e.compute_score(issue) == 10.0


def test_engine_feedback_not_found_logs():
    from aetherius_engine import AetheriusEngine, ledger_store
    ledger_store.clear()
    e = AetheriusEngine(token="fake", repo_list=["x/y"])
    e.apply_human_feedback("x/y", 999, 10)
    assert any("WARNING" in msg for msg in ledger_store)


def test_engine_llm_throttled():
    from aetherius_engine import AetheriusEngine, ledger_store
    ledger_store.clear()
    e = AetheriusEngine(token="fake", repo_list=[])
    e.governor.llm_limit = 0   # force throttle
    result = e.generate_llm_code("test prompt")
    assert "Throttled" in result
    assert any("throttled" in m.lower() for m in ledger_store)


def test_engine_feedback_adjusts_priority():
    from aetherius_engine import AetheriusEngine, issues_store
    issues_store.clear()
    issues_store.append({"repo": "x/y", "number": 1, "priority": 10.0})
    e = AetheriusEngine(token="fake", repo_list=["x/y"])
    e.apply_human_feedback("x/y", 1, 5.0)
    assert issues_store[0]["priority"] == 15.0
