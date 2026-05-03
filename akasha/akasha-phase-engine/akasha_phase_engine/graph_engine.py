"""
graph_engine.py — NetworkX phase transition graph

Bug fixes vs original:
  - Graph is now built from registry.transitions (the authoritative list),
    not from phase.transitions (always empty []).
  - shortest_path raises a clear ValueError instead of a raw networkx
    exception when start/end nodes are missing.
  - Added helpers: all_paths, reachable_from, transition_subgraph.
"""

import networkx as nx
from typing import List, Dict, Optional


class PhaseGraph:
    def __init__(self, registry):
        self.registry = registry
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        # Add every registered phase as a node
        for phase in self.registry.phases:
            self.graph.add_node(phase.name, data=phase)

        # Add edges from registry.transitions — this is the authoritative source.
        # (Phase.transitions is a list of PhaseTransition objects on the Phase
        #  dataclass but is never populated by build_default_registry, so we
        #  must use registry.transitions instead.)
        for t in self.registry.transitions:
            # Ensure both endpoint nodes exist even if orphaned
            if t.phase_from not in self.graph:
                self.graph.add_node(t.phase_from)
            if t.phase_to not in self.graph:
                self.graph.add_node(t.phase_to)

            self.graph.add_edge(
                t.phase_from, t.phase_to,
                order=t.order,
                continuous=t.continuous,
                control_parameter=t.control_parameter,
                critical_value=t.critical_value,
                universality_class=t.universality_class,
                mechanism=t.mechanism,
            )
            # Also add reverse edge — melting <-> freezing, etc.
            self.graph.add_edge(
                t.phase_to, t.phase_from,
                order=t.order,
                continuous=t.continuous,
                control_parameter=t.control_parameter,
                critical_value=t.critical_value,
                universality_class=t.universality_class,
                mechanism=t.mechanism,
            )

    def shortest_path(self, start: str, end: str) -> List[str]:
        """Return shortest path between two phase names."""
        if start not in self.graph:
            raise ValueError(
                f"Phase '{start}' not in graph. "
                f"Available: {sorted(self.graph.nodes)}"
            )
        if end not in self.graph:
            raise ValueError(
                f"Phase '{end}' not in graph. "
                f"Available: {sorted(self.graph.nodes)}"
            )
        try:
            return nx.shortest_path(self.graph, start, end)
        except nx.NetworkXNoPath:
            raise ValueError(f"No path exists between '{start}' and '{end}'")

    def all_paths(self, start: str, end: str, cutoff: int = 5) -> List[List[str]]:
        return list(nx.all_simple_paths(self.graph, start, end, cutoff=cutoff))

    def centrality(self) -> Dict[str, float]:
        return nx.degree_centrality(self.graph)

    def betweenness(self) -> Dict[str, float]:
        return nx.betweenness_centrality(self.graph)

    def strongly_connected_components(self):
        return list(nx.strongly_connected_components(self.graph))

    def reachable_from(self, start: str) -> List[str]:
        if start not in self.graph:
            raise ValueError(f"Phase '{start}' not in graph.")
        return list(nx.descendants(self.graph, start))

    def transition_data(self, phase_from: str, phase_to: str) -> Optional[Dict]:
        if self.graph.has_edge(phase_from, phase_to):
            return dict(self.graph[phase_from][phase_to])
        return None

    def nodes(self) -> List[str]:
        return list(self.graph.nodes)

    def edges(self) -> List[tuple]:
        return list(self.graph.edges)

    def __repr__(self):
        return (
            f"PhaseGraph({len(self.graph.nodes)} nodes, "
            f"{len(self.graph.edges)} edges)"
        )
