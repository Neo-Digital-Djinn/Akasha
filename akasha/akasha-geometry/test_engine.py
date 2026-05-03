"""
Akasha Geometry Engine — test_engine.py

Smoke test and demonstration. Builds a small typed graph and runs
every engine capability to verify correctness.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from geometry.core import Graph, GeometryEngine
from geometry.fields import Field, FieldComposer
from geometry.metrics import compute_metrics
from geometry.shapes import describe_shape, all_shapes
from integration.hooks import suggest_discoveries, geometry_report


def build_test_graph() -> Graph:
    """
    Small typed graph modeling a simple phase system:
    instability → transition → equilibrium → attractor
    with a constraint node and an observer.
    """
    g = Graph()

    # Nodes with lattice_attrs matching akasha_lattice.yaml
    g.add_node("instability",  "state",      {"phase": "system",     "stability": "unstable",  "constraint": "weak",    "process": "transform"})
    g.add_node("transition",   "process",    {"phase": "transition", "stability": "dynamic",   "constraint": "none",    "process": "transform"})
    g.add_node("equilibrium",  "state",      {"phase": "system",     "stability": "stable",    "constraint": "strong",  "process": "none"})
    g.add_node("attractor",    "attractor",  {"phase": "attractor",  "stability": "terminal",  "constraint": "maximal", "process": "converge"})
    g.add_node("constraint_a", "constraint", {})
    g.add_node("observer_a",   "observer",   {})
    g.add_node("orphan",       "state",      {})  # isolated — no edges

    # Edges
    g.add_edge("instability",  "transition",  "transitions_to")
    g.add_edge("transition",   "equilibrium", "transitions_to")
    g.add_edge("equilibrium",  "attractor",   "tends_toward")
    g.add_edge("constraint_a", "transition",  "constrains")
    g.add_edge("observer_a",   "instability", "observes")
    g.add_edge("instability",  "equilibrium", "transitions_to")  # shortcut — creates triangle

    return g


def run():
    print("=" * 60)
    print("Akasha Geometry Engine — Test Run")
    print("=" * 60)

    g = build_test_graph()
    engine = GeometryEngine(g)

    # --- SHAPES ---
    print("\n[ SHAPES ]")
    shapes = engine.detect_all_shapes()
    for s in shapes:
        print(f"  {s.shape:12s}  score={s.score}  nodes={s.nodes}")
        print(f"             → {s.note}")

    # --- SYMMETRY ---
    print("\n[ SYMMETRY GROUPS ]")
    sym = engine.detect_symmetry()
    if sym:
        for group in sym:
            print(f"  {group.nodes}  (size {group.size})")
    else:
        print("  No symmetry groups detected")

    # --- SPIRAL ---
    print("\n[ SPIRAL from instability ]")
    start = g.get("instability")
    spiral = engine.detect_spirals(start, depth=6)
    print(f"  Path:    {spiral.path}")
    print(f"  Novelty: {spiral.novelty_scores}")
    print(f"  Total:   {spiral.total_novelty}")

    # --- MISSING LINKS ---
    print("\n[ MISSING LINK PREDICTIONS ]")
    links = engine.predict_missing_links()
    for l in links:
        print(f"  {l.from_id} → {l.to_id}  conf={l.confidence}")
        print(f"    reason: {l.reason}")

    # --- LATTICE VIOLATIONS ---
    print("\n[ LATTICE VIOLATIONS ]")
    violations = engine.detect_lattice_violations()
    if violations:
        for v in violations:
            print(f"  {v.node_id}: {v.description}")
    else:
        print("  None — graph is lattice-valid")

    # --- ROLE AUDIT ---
    print("\n[ ROLE AUDIT ]")
    audit = engine.audit_node_roles()
    if audit:
        for node_id, issues in audit.items():
            for issue in issues:
                print(f"  {node_id}: {issue}")
    else:
        print("  All roles fulfilled")

    # --- DISCOVERY FRONTIER ---
    print("\n[ DISCOVERY FRONTIER ]")
    frontier = engine.discovery_frontier()
    for entry in frontier[:5]:
        print(f"  {entry['node_id']:15s} score={entry['frontier_score']}  dist_to_attractor={entry['dist_to_attractor']}")

    # --- FIELDS ---
    print("\n[ FIELDS ]")
    gap = Field("gap_pressure")
    gap.set(g.get("orphan"),       1.0)
    gap.set(g.get("instability"),  0.7)
    gap.set(g.get("transition"),   0.4)
    gap.set(g.get("equilibrium"),  0.2)
    gap.set(g.get("attractor"),    0.0)

    propagated = gap.propagate(steps=2, decay=0.7)
    print(f"  gap_pressure summary: {gap.summary()}")
    tensions = gap.tension_map(engine.graph)
    print(f"  Tension nodes: {[(t.node_id, t.tension) for t in tensions]}")
    conv = gap.convergence_points(engine.graph, threshold=0.3)
    print(f"  Convergence points: {[(c.node_id, c.value) for c in conv]}")

    # --- METRICS ---
    print("\n[ GRAPH METRICS ]")
    m = compute_metrics(engine)
    print(f"  Nodes:           {m.node_count}")
    print(f"  Edges:           {m.edge_count}")
    print(f"  Density:         {m.density}")
    print(f"  Symmetry index:  {m.symmetry_index}")
    print(f"  Triangles:       {m.triangle_count}")
    print(f"  Loops:           {m.loop_count}")
    print(f"  Bridges:         {m.bridge_count}")
    print(f"  Isolated:        {m.isolated_count}")
    print(f"  Violations:      {m.violation_count}")
    print(f"  Role gaps:       {m.role_audit_issues}")
    print(f"  Health score:    {m.health_score}")

    print("\n" + "=" * 60)
    print("Test complete.")


# ============================================================
# REASONER TEST
# ============================================================

def run_reasoner():
    import json
    from geometry.reasoner import GeometryReasoner

    print("\n" + "=" * 60)
    print("Akasha Geometry Reasoner — Test Run")
    print("=" * 60)

    g = build_test_graph()
    engine = GeometryEngine(g)
    reasoner = GeometryReasoner(engine)

    print("\n[ COMPOUND FINDINGS ]")
    findings = reasoner.find_compound_findings()
    for f in findings:
        print(f"\n  [{f.finding_type}]  severity={f.severity}")
        print(f"  Nodes:   {f.involved_nodes}")
        print(f"  Meaning: {f.interpretation[:120]}...")
        print(f"  Predict: {f.prediction[:100]}...")

    print("\n[ HYPOTHESES ]")
    hypotheses = reasoner.generate_hypotheses(findings)
    for h in hypotheses:
        print(f"\n  {h.id} — {h.title}")
        print(f"  Type:       {h.hypothesis_type}  confidence={h.confidence}")
        print(f"  Summary:    {h.summary[:120]}...")
        print(f"  Falsifier:  {h.falsifier[:100]}...")
        print(f"  Action:     {h.suggested_action[:100]}...")

    print("\n[ REQUEST EXPORT (first 2) ]")
    reqs = reasoner.export_as_requests(hypotheses)
    for req in reqs[:2]:
        print(json.dumps(req, indent=2))

    print("\n" + "=" * 60)
    print("Reasoner test complete.")


if __name__ == "__main__":
    run()
    run_reasoner()
