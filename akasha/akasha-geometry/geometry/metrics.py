"""
Akasha Geometry Engine — metrics.py

Graph-level structural health scores.
Gives a single-pass summary of the whole graph's geometry.
"""

from dataclasses import dataclass


@dataclass
class GraphMetrics:
    node_count: int
    edge_count: int
    density: float              # actual edges / possible edges
    symmetry_index: float       # fraction of nodes that belong to a symmetry group
    triangle_count: int
    loop_count: int
    bridge_count: int
    isolated_count: int
    violation_count: int        # lattice violations
    frontier_size: int          # nodes at discovery frontier
    role_audit_issues: int      # total unmet role expectations
    health_score: float         # 0–1 composite


def compute_metrics(engine) -> GraphMetrics:
    """
    Run a full geometric audit of the graph.
    All detections are called once and aggregated.
    """
    from geometry.core import GeometryEngine

    g = engine.graph
    n = len(g)
    e = sum(len(node.out_nodes()) for node in g)
    possible = n * (n - 1)
    density = round(e / possible, 4) if possible > 0 else 0.0

    sym_groups = engine.detect_symmetry()
    nodes_in_sym = set()
    for group in sym_groups:
        for nid in group.nodes:
            nodes_in_sym.add(nid)
    symmetry_index = round(len(nodes_in_sym) / max(n, 1), 4)

    triangles = engine.detect_triangles()
    loops = engine.detect_loops()
    bridges = engine.detect_bridges()
    isolated = engine.detect_isolated()
    violations = engine.detect_lattice_violations()
    frontier = engine.discovery_frontier()
    audit = engine.audit_node_roles()
    total_issues = sum(len(v) for v in audit.values())

    # health score: penalize violations, isolation, missing roles; reward symmetry and density
    health = 1.0
    health -= min(0.3, len(violations) * 0.05)
    health -= min(0.2, len(isolated) * 0.04)
    health -= min(0.2, total_issues * 0.02)
    health += min(0.1, symmetry_index * 0.1)
    health += min(0.1, density * 0.1)
    health = round(max(0.0, min(1.0, health)), 3)

    return GraphMetrics(
        node_count=n,
        edge_count=e,
        density=density,
        symmetry_index=symmetry_index,
        triangle_count=len(triangles),
        loop_count=len(loops),
        bridge_count=len(bridges),
        isolated_count=len(isolated),
        violation_count=len(violations),
        frontier_size=len(frontier),
        role_audit_issues=total_issues,
        health_score=health,
    )
