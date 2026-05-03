"""
cli.py — Command-line interface for akasha-phase-engine

Usage:
    akasha-phase-engine              # Full query demo + JSON export
    akasha-phase-engine query        # Same as above
    akasha-phase-engine graph        # Graph traversal demo
    akasha-phase-engine discovery    # Gap-finder report
    akasha-phase-engine serve        # Start Flask dev server
    akasha-phase-engine serve --prod # Start gunicorn (production)
"""

import sys
import os
import numpy as np


def separator(title=""):
    if title:
        print(f"\n{'═'*60}")
        print(f"  {title}")
        print(f"{'═'*60}")
    else:
        print(f"{'─'*60}")


def cmd_query():
    from akasha_phase_engine.database import build_default_registry

    registry = build_default_registry()

    separator("PHASE BEHAVIOR ONTOLOGY ENGINE")
    stats = registry.stats()
    print(f"  Phases:      {stats['total_phases']}")
    print(f"  Transitions: {stats['total_transitions']}")
    print(f"  Materials:   {stats['total_materials']}")
    print(f"  Categories:  {', '.join(sorted(stats['categories']))}")
    print(f"  Year range:  {stats['year_range'][0]} – {stats['year_range'][1]}")
    print(f"  Topological: {stats['topological']}")
    print(f"  Non-equil.:  {stats['non_equilibrium']}")

    separator("ALL PHASES")
    print(registry.all().summary())

    separator("COMPOUND QUERIES")

    print("\n  Topological + equilibrium:")
    print(f"  → {registry.all().topological().equilibrium().names()}")

    print("\n  Breaks symmetry + 3D:")
    print(f"  → {registry.all().breaks_symmetry().dimensionality(3).names()}")

    print("\n  Has edge states:")
    print(f"  → {registry.all().has_edge_states().names()}")

    print("\n  Has anyons:")
    print(f"  → {registry.all().has_anyons().names()}")

    print("\n  Berry phase = π:")
    print(f"  → {registry.all().berry_phase(np.pi).names()}")

    print("\n  Discovered after 1990:")
    print(f"  → {registry.all().discovered_after(1990).names()}")

    print("\n  Quantum computing applications:")
    print(f"  → {registry.all().has_application('quantum computing').names()}")

    separator("PHASE TRANSITION GRAPH")
    for t in registry.transitions:
        order_str = "continuous" if t.continuous else "first-order"
        print(f"\n  {t.phase_from}  →  {t.phase_to}")
        print(f"    Control: {t.control_parameter} at {t.critical_value}")
        print(f"    Type: {order_str}, universality: {t.universality_class or 'unknown'}")
        print(f"    Mechanism: {t.mechanism}")

    separator("MATERIALS SURVEY")
    print(f"  {'Formula':<20} {'Phase':<30} {'T range (K)':<20} {'Cost $/g'}")
    print(f"  {'─'*18} {'─'*28} {'─'*18} {'─'*10}")
    for phase in registry.phases:
        for mat in phase.materials:
            t_lo, t_hi = mat.temperature_range
            t_hi_str = f"{t_hi:.2e}" if t_hi < 1 else str(int(t_hi))
            cost = f"${mat.cost_per_gram}" if mat.cost_per_gram else "N/A"
            print(f"  {mat.formula:<20} {phase.name:<30} {t_lo}-{t_hi_str:<17} {cost}")

    separator("OPEN QUESTIONS BY PHASE")
    for phase in registry.phases:
        n = len(phase.open_questions)
        bar = "■" * n
        print(f"  {phase.name:<35} {bar} ({n})")

    separator("EXPORT")
    out = "/tmp/akasha-phases.json"
    registry.to_json(out)
    print(f"  JSON saved to {out}")
    separator()


def cmd_graph():
    from akasha_phase_engine.database import build_default_registry
    from akasha_phase_engine.graph_engine import PhaseGraph

    registry = build_default_registry()
    graph = PhaseGraph(registry)

    separator("PHASE TRANSITION GRAPH ENGINE")
    print(f"  {graph}")

    separator("SHORTEST PATHS")
    pairs = [
        ("Spin Glass", "BCS Superconductor"),
        ("Normal Metal", "Fractional Quantum Hall State"),
        ("Crystal", "Topological Insulator"),
    ]
    for a, b in pairs:
        try:
            path = graph.shortest_path(a, b)
            print(f"\n  {a} → {b}:")
            print(f"  → {' → '.join(path)}")
        except ValueError as e:
            print(f"\n  {a} → {b}: {e}")

    separator("CENTRALITY (top 5)")
    centrality = graph.centrality()
    top5 = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    for name, score in top5:
        print(f"  {name:<40} {score:.4f}")

    separator("BETWEENNESS (top 5)")
    betweenness = graph.betweenness()
    top5b = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
    for name, score in top5b:
        print(f"  {name:<40} {score:.4f}")

    separator("REACHABLE FROM Normal Metal")
    reachable = graph.reachable_from("Normal Metal")
    for r in sorted(reachable):
        print(f"  • {r}")
    separator()


def cmd_discovery():
    from akasha_phase_engine.discovery import (
        KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS, find_gaps
    )

    separator("PHASE SPACE GAP FINDER")
    gaps = find_gaps(KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS)

    known      = [g for g in gaps if g.status == "known"]
    forbidden  = [g for g in gaps if g.status == "forbidden"]
    predicted  = [g for g in gaps if g.status == "predicted"]
    candidates = [g for g in gaps if g.status == "candidate"]

    print(f"  Total coordinates scanned: {len(gaps)}")
    print(f"  Known:     {len(known)}")
    print(f"  Forbidden: {len(forbidden)}")
    print(f"  Predicted: {len(predicted)}")
    print(f"  Candidate: {len(candidates)}")

    separator("TOP 10 CANDIDATE GAPS (by interest score)")
    top = sorted(candidates, key=lambda g: g.interest_score, reverse=True)[:10]
    for g in top:
        print(f"\n  Score {g.interest_score:.3f}: {g.coordinate}")
        if hasattr(g, "notes") and g.notes:
            print(f"    Note: {g.notes}")
    separator()


def cmd_serve(prod=False):
    if prod:
        import subprocess
        subprocess.run([
            "gunicorn",
            "--bind", "0.0.0.0:8000",
            "--workers", "2",
            "--timeout", "120",
            "akasha_phase_engine.app:app",
        ])
    else:
        from akasha_phase_engine.app import app
        port = int(os.getenv("PORT", 8000))
        app.run(host="0.0.0.0", port=port, debug=True)


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "query"

    dispatch = {
        "query":     cmd_query,
        "graph":     cmd_graph,
        "discovery": cmd_discovery,
    }

    if cmd == "serve":
        cmd_serve(prod="--prod" in args)
    elif cmd in dispatch:
        dispatch[cmd]()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
