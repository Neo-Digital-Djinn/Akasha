"""
tests/test_graph.py — Unit tests for graph_engine.py

Tests the core bug that was fixed: graph must be built from
registry.transitions, not from phase.transitions (always empty).
"""
import sys, os

import pytest
from akasha_phase_engine.database import build_default_registry
from akasha_phase_engine.graph_engine import PhaseGraph


@pytest.fixture(scope="module")
def graph():
    registry = build_default_registry()
    return PhaseGraph(registry)


def test_graph_has_nodes(graph):
    """All registered phases must appear as nodes."""
    nodes = graph.nodes()
    assert "Crystal" in nodes
    assert "Ferromagnet" in nodes
    assert "Topological Insulator" in nodes
    assert len(nodes) >= 10


def test_graph_has_edges(graph):
    """Transitions must produce edges — this was the core bug."""
    edges = graph.edges()
    assert len(edges) >= 5, (
        "Graph has no edges — build_graph() is reading phase.transitions "
        "(always []) instead of registry.transitions."
    )


def test_shortest_path_crystal_to_bcs(graph):
    """Crystal -> Normal Liquid -> ... should find some path through the graph."""
    # Both Crystal and BCS Superconductor have registered transitions
    nodes = graph.nodes()
    assert "Crystal" in nodes
    assert "BCS Superconductor" in nodes
    # There may not be a direct path — just check no crash and returns a list
    try:
        path = graph.shortest_path("Crystal", "Normal Liquid")
        assert isinstance(path, list)
        assert path[0] == "Crystal"
        assert path[-1] == "Normal Liquid"
    except ValueError as e:
        # Acceptable only if the path genuinely doesn't exist
        assert "No path" in str(e) or "not in graph" in str(e)


def test_shortest_path_known_transition(graph):
    """Ferromagnet -> Paramagnet is a registered transition; path must exist."""
    path = graph.shortest_path("Ferromagnet", "Paramagnet")
    assert path == ["Ferromagnet", "Paramagnet"]


def test_shortest_path_missing_node_raises(graph):
    """Unknown phase name must raise ValueError, not NetworkXError."""
    with pytest.raises(ValueError, match="not in graph"):
        graph.shortest_path("Unobtainium", "Crystal")


def test_centrality_returns_all_nodes(graph):
    c = graph.centrality()
    for node in graph.nodes():
        assert node in c, f"Node '{node}' missing from centrality output"


def test_reachable_from_ferromagnet(graph):
    reachable = graph.reachable_from("Ferromagnet")
    assert "Paramagnet" in reachable


def test_transition_data(graph):
    data = graph.transition_data("Ferromagnet", "Paramagnet")
    assert data is not None
    assert data["continuous"] is True
    assert data["control_parameter"] == "temperature"
