"""
tests/test_registry.py — Tests for PhaseRegistry query system and stats.
"""
import sys, os

import pytest
import numpy as np
from akasha_phase_engine.database import build_default_registry


@pytest.fixture(scope="module")
def registry():
    return build_default_registry()


class TestStats:
    def test_phase_count(self, registry):
        assert registry.stats()["total_phases"] >= 10

    def test_transition_count(self, registry):
        assert registry.stats()["total_transitions"] >= 5

    def test_material_count(self, registry):
        assert registry.stats()["total_materials"] >= 20

    def test_year_range_sensible(self, registry):
        lo, hi = registry.stats()["year_range"]
        assert lo >= 1600  # Normal Liquid (Newton/Hooke era, ~1687)
        assert hi <= 2030
        assert lo < hi

    def test_categories_present(self, registry):
        cats = set(registry.stats()["categories"])
        assert "Topological" in cats
        assert "Symmetry-Broken" in cats


class TestChainableQueries:
    def test_topological_phases(self, registry):
        results = registry.all().topological().names()
        assert "Topological Insulator" in results
        assert "Weyl Semimetal" in results
        # Non-topological must not appear
        assert "Crystal" not in results
        assert "Ferromagnet" not in results

    def test_equilibrium_filter(self, registry):
        eq = registry.all().equilibrium().names()
        neq = registry.all().non_equilibrium().names()
        assert "Time Crystal" in neq
        assert "Time Crystal" not in eq

    def test_breaks_symmetry(self, registry):
        sb = registry.all().breaks_symmetry().names()
        assert "Crystal" in sb
        assert "Ferromagnet" in sb
        # TI breaks no symmetry
        assert "Topological Insulator" not in sb

    def test_has_anyons(self, registry):
        a = registry.all().has_anyons().names()
        assert "Fractional Quantum Hall State" in a
        assert "Quantum Spin Liquid" in a
        assert "Crystal" not in a

    def test_dimensionality_2d(self, registry):
        twod = registry.all().dimensionality(2).names()
        assert "Fractional Quantum Hall State" in twod
        assert "Quantum Spin Liquid" in twod
        assert "Crystal" not in twod

    def test_discovered_after_2000(self, registry):
        recent = registry.all().discovered_after(2000).names()
        assert "Weyl Semimetal" in recent
        assert "Time Crystal" in recent
        assert "Crystal" not in recent

    def test_has_edge_states(self, registry):
        edge = registry.all().has_edge_states().names()
        assert "Topological Insulator" in edge
        assert "Weyl Semimetal" in edge
        assert "Ferromagnet" not in edge

    def test_berry_phase_pi(self, registry):
        bp = registry.all().berry_phase(np.pi).names()
        assert "Ferromagnet" in bp

    def test_compound_query_topo_2d(self, registry):
        result = registry.all().topological().dimensionality(2).names()
        assert "Fractional Quantum Hall State" in result
        # All results must be 2D AND topological
        for name in result:
            p = registry.query(name=name).first()
            assert p.dimensionality == 2
            assert p.topology.has_topological_order

    def test_has_application(self, registry):
        qc = registry.all().has_application("quantum computing").names()
        assert len(qc) >= 1

    def test_query_by_name(self, registry):
        p = registry.query(name="Ferromagnet").first()
        assert p is not None
        assert p.name == "Ferromagnet"


class TestNeighbors:
    def test_ferromagnet_neighbors(self, registry):
        neighbors = registry.neighbors("Ferromagnet")
        assert "Paramagnet" in neighbors

    def test_bcs_neighbors(self, registry):
        neighbors = registry.neighbors("BCS Superconductor")
        assert "Normal Metal" in neighbors or "Mott Insulator" in neighbors

    def test_unknown_phase_returns_empty(self, registry):
        assert registry.neighbors("Unobtainium") == []


class TestGetTransition:
    def test_known_transition(self, registry):
        t = registry.get_transition("Ferromagnet", "Paramagnet")
        assert t is not None
        assert t.continuous is True

    def test_reverse_lookup(self, registry):
        """get_transition must work regardless of argument order."""
        t1 = registry.get_transition("Ferromagnet", "Paramagnet")
        t2 = registry.get_transition("Paramagnet", "Ferromagnet")
        assert t1 is not None
        assert t2 is not None
        assert t1.phase_from == t2.phase_from

    def test_missing_transition_returns_none(self, registry):
        assert registry.get_transition("Crystal", "Topological Insulator") is None
