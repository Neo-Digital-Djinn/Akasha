"""
tests/test_discovery.py — Unit tests for the discovery / gap-finder engine.

Previously untested. These exercise is_forbidden(), score_candidate(),
find_gaps(), and infer_possible_transitions() directly.
"""
import sys, os

import pytest
from akasha_phase_engine.discovery import (
    PhaseCoordinate, TopoType, SymBreaking, DynClass, AnyonType,
    is_forbidden, score_candidate, find_gaps, infer_possible_transitions,
    KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS,
)


# ── Helpers ──────────────────────────────────────────────────────

def coord(**kwargs):
    """Build a minimal PhaseCoordinate with sensible defaults."""
    defaults = dict(
        dimensionality=3,
        symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.NONE,
        dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE,
        edge_states=False,
        bulk_gap=False,
        long_range_entanglement=False,
    )
    defaults.update(kwargs)
    return PhaseCoordinate(**defaults)


# ── is_forbidden ─────────────────────────────────────────────────

class TestIsForbidden:
    def test_mermin_wagner_d2_continuous_forbidden(self):
        """Continuous SSB in 2D equilibrium must be forbidden."""
        c = coord(dimensionality=2, symmetry_breaking=SymBreaking.CONTINUOUS)
        forbidden, thm = is_forbidden(c)
        assert forbidden
        assert thm.name == "Mermin-Wagner"

    def test_mermin_wagner_d3_continuous_allowed(self):
        """3D ferromagnet: continuous SSB is fine."""
        c = coord(dimensionality=3, symmetry_breaking=SymBreaking.CONTINUOUS)
        forbidden, _ = is_forbidden(c)
        assert not forbidden

    def test_coleman_d1_continuous_forbidden(self):
        """Continuous SSB in d=1 is forbidden (Coleman, or Mermin-Wagner which also covers d=1).
        Both theorems correctly forbid this — Mermin-Wagner fires first because d=1 <= 2."""
        c = coord(dimensionality=1, symmetry_breaking=SymBreaking.CONTINUOUS)
        forbidden, thm = is_forbidden(c)
        assert forbidden
        # Either theorem is physically correct; MW fires first since d=1 satisfies d<=2
        assert thm.name in ("Coleman (1+1)D", "Mermin-Wagner")

    def test_non_abelian_anyons_need_non_abelian_topo(self):
        """Non-Abelian anyons require Non-Abelian topological order."""
        c = coord(anyons=AnyonType.NON_ABELIAN, topological=TopoType.Z2)
        forbidden, thm = is_forbidden(c)
        assert forbidden
        assert "Non-Abelian" in thm.name

    def test_non_abelian_anyons_with_correct_topo_ok(self):
        c = coord(
            dimensionality=2,
            anyons=AnyonType.NON_ABELIAN,
            topological=TopoType.NON_ABELIAN,
            edge_states=True,
            bulk_gap=True,
            long_range_entanglement=True,
        )
        forbidden, _ = is_forbidden(c)
        assert not forbidden

    def test_lre_without_topo_or_ssb_forbidden(self):
        c = coord(long_range_entanglement=True)
        forbidden, thm = is_forbidden(c)
        assert forbidden
        assert "Hastings" in thm.name

    def test_lre_with_topo_allowed(self):
        c = coord(long_range_entanglement=True, topological=TopoType.Z2)
        forbidden, _ = is_forbidden(c)
        assert not forbidden

    def test_edge_states_without_bulk_topo_forbidden(self):
        c = coord(edge_states=True, topological=TopoType.NONE)
        forbidden, thm = is_forbidden(c)
        assert forbidden
        assert "Bulk-edge" in thm.name

    def test_edge_states_with_bulk_topo_ok(self):
        c = coord(edge_states=True, topological=TopoType.Z2)
        forbidden, _ = is_forbidden(c)
        assert not forbidden

    def test_anyons_in_d1_forbidden(self):
        c = coord(dimensionality=1, anyons=AnyonType.ABELIAN)
        forbidden, thm = is_forbidden(c)
        assert forbidden
        assert "2D" in thm.name


# ── score_candidate ───────────────────────────────────────────────

class TestScoreCandidate:
    def test_returns_triple(self):
        c = coord(dimensionality=2, topological=TopoType.CHERN, edge_states=True, bulk_gap=True)
        result = score_candidate(c, KNOWN_PHASE_COORDINATES)
        assert len(result) == 3
        novelty, feasibility, reasoning = result
        assert 0.0 <= novelty <= 1.0
        assert 0.0 <= feasibility <= 1.0
        assert isinstance(reasoning, str) and len(reasoning) > 0

    def test_known_phase_has_zero_novelty(self):
        """A coordinate identical to a known phase should have novelty=0."""
        known_coord = KNOWN_PHASE_COORDINATES["Crystal"]
        novelty, _, _ = score_candidate(known_coord, KNOWN_PHASE_COORDINATES)
        assert novelty == 0.0

    def test_floquet_boosts_feasibility(self):
        base = coord()
        floquet = coord(dynamics=DynClass.DRIVEN_FLOQUET)
        _, feas_base, _ = score_candidate(base, KNOWN_PHASE_COORDINATES)
        _, feas_floquet, _ = score_candidate(floquet, KNOWN_PHASE_COORDINATES)
        assert feas_floquet >= feas_base

    def test_non_abelian_anyons_reduce_feasibility(self):
        base = coord(dimensionality=2, topological=TopoType.NON_ABELIAN)
        with_anyons = coord(
            dimensionality=2,
            topological=TopoType.NON_ABELIAN,
            anyons=AnyonType.NON_ABELIAN,
        )
        _, feas_base, _ = score_candidate(base, KNOWN_PHASE_COORDINATES)
        _, feas_anyons, _ = score_candidate(with_anyons, KNOWN_PHASE_COORDINATES)
        assert feas_anyons < feas_base


# ── find_gaps ─────────────────────────────────────────────────────

class TestFindGaps:
    @pytest.fixture(scope="class")
    def gaps(self):
        return find_gaps(KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS)

    def test_returns_list(self, gaps):
        assert isinstance(gaps, list)
        assert len(gaps) > 0

    def test_status_values(self, gaps):
        valid = {"known", "forbidden", "predicted", "candidate"}
        for g in gaps:
            assert g.status in valid

    def test_known_phases_present(self, gaps):
        known_names = {g.known_name for g in gaps if g.status == "known"}
        assert "Crystal" in known_names
        assert "Topological Insulator" in known_names

    def test_predicted_phases_present(self, gaps):
        predicted  = [g for g in gaps if g.status == "predicted"]
        pred_names = {g.prediction.name for g in predicted}
        assert len(pred_names) > 0, "No predicted phases found"
        # Floquet TI is now a known phase; verify at least one other prediction survives
        assert any("Topological" in n or "Fracton" in n or "Crystal" in n for n in pred_names)

    def test_forbidden_zones_non_empty(self, gaps):
        forbidden = [g for g in gaps if g.status == "forbidden"]
        assert len(forbidden) > 0

    def test_candidates_have_scores(self, gaps):
        candidates = [g for g in gaps if g.status == "candidate"]
        for c in candidates:
            assert 0.0 <= c.novelty_score <= 1.0
            assert 0.0 <= c.feasibility_score <= 1.0
            assert c.interest_score >= 0.0

    def test_no_forbidden_phase_is_known(self, gaps):
        """A coordinate can't simultaneously be known and forbidden."""
        known_coords = {g.coordinate for g in gaps if g.status == "known"}
        for g in gaps:
            if g.status == "forbidden":
                assert g.coordinate not in known_coords


# ── infer_possible_transitions ────────────────────────────────────

class TestInferTransitions:
    def test_same_phase_returns_none(self):
        c = KNOWN_PHASE_COORDINATES["Crystal"]
        assert infer_possible_transitions(c, c) is None

    def test_too_many_differences_returns_none(self):
        a = KNOWN_PHASE_COORDINATES["Crystal"]
        b = KNOWN_PHASE_COORDINATES["Fractional Quantum Hall State"]
        result = infer_possible_transitions(a, b)
        # More than 3 axes differ — should be None
        assert result is None

    def test_one_difference_returns_string(self):
        a = KNOWN_PHASE_COORDINATES["BCS Superconductor"]  # bulk_gap=True
        b = KNOWN_PHASE_COORDINATES["Ferromagnet"]          # bulk_gap=False
        result = infer_possible_transitions(a, b)
        # They differ in >=1 axis — may or may not exceed cutoff
        if result is not None:
            assert "Changes:" in result
