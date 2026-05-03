"""
Akasha Geometry Engine — integration/hooks.py

Hooks for connecting the geometry engine to the Akasha discovery pipeline.
Geometry produces typed, scored suggestions — not raw lists.
"""

from geometry.core import GeometryEngine
from geometry.fields import Field, FieldComposer
from geometry.metrics import compute_metrics


def inject_geometry(discovery_engine, geometry_engine: GeometryEngine):
    """Attach a geometry engine instance to a discovery engine."""
    discovery_engine.geometry = geometry_engine


def suggest_discoveries(geometry_engine: GeometryEngine) -> list[dict]:
    """
    Full discovery suggestion pass.
    Returns a ranked list of suggestions with type, confidence, and reason.
    Each entry is ready for consumption by akasha-requests or akasha-forge.
    """
    suggestions = []

    # Missing links (topological + role-structural)
    for link in geometry_engine.predict_missing_links():
        suggestions.append({
            "type": "missing_link",
            "from": link.from_id,
            "to": link.to_id,
            "confidence": link.confidence,
            "reason": link.reason,
        })

    # Lattice violations (invalid structural configs)
    for v in geometry_engine.detect_lattice_violations():
        suggestions.append({
            "type": "lattice_violation",
            "node": v.node_id,
            "confidence": 1.0,
            "reason": v.description,
        })

    # Role audit issues (unmet structural expectations)
    for node_id, issues in geometry_engine.audit_node_roles().items():
        for issue in issues:
            suggestions.append({
                "type": "role_gap",
                "node": node_id,
                "confidence": 0.85,
                "reason": issue,
            })

    # Discovery frontier nodes
    for entry in geometry_engine.discovery_frontier():
        suggestions.append({
            "type": "frontier_node",
            "node": entry["node_id"],
            "confidence": round(entry["frontier_score"], 3),
            "reason": f"Frontier node — dist_to_attractor={entry['dist_to_attractor']}, out_degree={entry['out_degree']}",
        })

    suggestions.sort(key=lambda s: s["confidence"], reverse=True)
    return suggestions


def geometry_report(geometry_engine: GeometryEngine) -> dict:
    """
    Full structured report of a graph's geometry.
    Suitable for logging to akasha-events or display in akasha-console.
    """
    metrics = compute_metrics(geometry_engine)
    shapes = geometry_engine.detect_all_shapes()
    symmetry = geometry_engine.detect_symmetry()
    violations = geometry_engine.detect_lattice_violations()
    audit = geometry_engine.audit_node_roles()

    return {
        "metrics": {
            "nodes": metrics.node_count,
            "edges": metrics.edge_count,
            "density": metrics.density,
            "symmetry_index": metrics.symmetry_index,
            "health_score": metrics.health_score,
            "shapes": {
                "triangles": metrics.triangle_count,
                "loops": metrics.loop_count,
                "bridges": metrics.bridge_count,
                "isolated": metrics.isolated_count,
            },
            "issues": {
                "lattice_violations": metrics.violation_count,
                "role_gaps": metrics.role_audit_issues,
            },
        },
        "symmetry_groups": [
            {"nodes": g.nodes, "size": g.size}
            for g in symmetry
        ],
        "top_shapes": [
            {"shape": s.shape, "nodes": s.nodes, "score": s.score, "note": s.note}
            for s in shapes[:10]
        ],
        "violations": [
            {"node": v.node_id, "description": v.description}
            for v in violations
        ],
        "role_audit": audit,
        "discovery_suggestions": suggest_discoveries(geometry_engine)[:10],
    }
