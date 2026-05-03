"""
app.py — Flask backend for the Akasha Phase Behavior Ontology Engine
"""

import os
import numpy as np
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from akasha_phase_engine.database import build_default_registry
from akasha_phase_engine.graph_engine import PhaseGraph
from akasha_phase_engine.discovery import (
    PhaseCoordinate, TopoType, SymBreaking,
    DynClass, AnyonType,
    KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS, find_gaps,
)
from akasha_phase_engine.materials import extract_requirements, suggest_materials

app      = Flask(__name__)
CORS(app)

registry = build_default_registry()
graph    = PhaseGraph(registry)
_gaps    = find_gaps(KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS)


def _safe_float(v):
    if isinstance(v, float) and not np.isfinite(v):
        return None
    return v


def phase_to_dict(phase, detail=False):
    d = {
        "name":           phase.name,
        "category":       phase.category,
        "dimensionality": phase.dimensionality,
        "topology": {
            "has_topological_order": phase.topology.has_topological_order,
            "topological_order_type": phase.topology.topological_order_type,
            "edge_states":  phase.topology.edge_states,
            "corner_states": phase.topology.corner_states,
            "anyonic_excitations": phase.topology.anyonic_excitations,
            "bulk_gap":     phase.topology.bulk_gap,
            "long_range_entanglement": phase.topology.long_range_entanglement,
        },
        "dynamics": {
            "equilibrium":  phase.dynamics.equilibrium,
            "driven":       phase.dynamics.driven is not None,
            "mbl":          phase.dynamics.time_evolution.many_body_localized,
            "far_from_equilibrium": phase.dynamics.far_from_equilibrium,
        },
        "breaks_symmetry":    phase.symmetry_breaking is not None,
        "prototype_material": phase.prototype_material,
        "applications":       phase.technological_applications,
        "potential_applications": phase.potential_applications,
        "discovery_year":     phase.discovery_year,
    }
    if detail:
        d.update({
            "quantum": {
                "berry_phase":     phase.quantum.berry_phase,
                "berry_curvature": phase.quantum.berry_curvature,
                "superposition":   phase.quantum.superposition,
            },
            "symmetry_breaking": {
                "order_parameter":    phase.symmetry_breaking.order_parameter.name,
                "symbol":             phase.symmetry_breaking.order_parameter.symbol,
                "universality_class": phase.symmetry_breaking.universality_class,
                "critical_temperature": _safe_float(phase.symmetry_breaking.critical_temperature),
                "goldstone_modes":    phase.symmetry_breaking.num_goldstone_modes,
                "defects":            phase.symmetry_breaking.topological_defects,
            } if phase.symmetry_breaking else None,
            "materials": [
                {
                    "formula":             m.formula,
                    "crystal_structure":   m.crystal_structure,
                    "temperature_range": [
                        _safe_float(m.temperature_range[0]),
                        _safe_float(m.temperature_range[1]),
                    ],
                    "band_gap_eV":             m.band_gap,
                    "commercially_available":  m.commercially_available,
                    "cost_per_gram_usd":       m.cost_per_gram,
                }
                for m in phase.materials
            ],
            "open_questions":          phase.open_questions,
            "controversies":           phase.controversies,
            "key_theoretical_papers":  phase.key_theoretical_papers,
            "key_experimental_papers": phase.key_experimental_papers,
            "neighboring_phases":      registry.neighbors(phase.name),
        })
    return d


def coord_from_dict(d):
    try:
        return PhaseCoordinate(
            dimensionality=int(d.get("dimensionality", 3)),
            symmetry_breaking=SymBreaking(d.get("symmetry_breaking", "none")),
            topological=TopoType(d.get("topological", "none")),
            dynamics=DynClass(d.get("dynamics", "equilibrium")),
            anyons=AnyonType(d.get("anyons", "none")),
            edge_states=bool(d.get("edge_states", False)),
            bulk_gap=bool(d.get("bulk_gap", False)),
            long_range_entanglement=bool(d.get("long_range_entanglement", False)),
        )
    except (ValueError, KeyError) as e:
        raise ValueError(str(e))


# ── UI ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")


# ── Phases ──────────────────────────────────────────────────

@app.route("/api/phases")
def get_phases():
    q = registry.all()
    if (v := request.args.get("topological")) is not None:
        q = q.topological() if v == "true" else q.non_topological()
    if (v := request.args.get("equilibrium")) is not None:
        q = q.equilibrium() if v == "true" else q.non_equilibrium()
    if request.args.get("breaks_symmetry") == "true":
        q = q.breaks_symmetry()
    if d := request.args.get("dimensionality"):
        q = q.dimensionality(int(d))
    if cat := request.args.get("category"):
        q = q.category(cat)
    phases = list(q)
    return jsonify({"count": len(phases), "phases": [phase_to_dict(p) for p in phases]})


@app.route("/api/phases/<path:name>")
def get_phase(name):
    phase = registry.all().name(name).first()
    if not phase:
        abort(404, f"Phase '{name}' not found")
    return jsonify(phase_to_dict(phase, detail=True))


@app.route("/api/stats")
def get_stats():
    stats = registry.stats()
    stats["categories"] = sorted(stats["categories"])
    return jsonify(stats)


# ── Transitions & Graph ──────────────────────────────────────

@app.route("/api/transitions")
def get_transitions():
    return jsonify({
        "count": len(registry.transitions),
        "transitions": [
            {
                "from":              t.phase_from,
                "to":                t.phase_to,
                "order":             t.order,
                "continuous":        t.continuous,
                "control_parameter": t.control_parameter,
                "critical_value":    None if t.critical_value == float("inf") else t.critical_value,
                "universality_class": t.universality_class,
                "mechanism":         t.mechanism,
            }
            for t in registry.transitions
        ],
    })


@app.route("/api/neighbors/<path:phase_name>")
def get_neighbors(phase_name):
    if not registry.all().name(phase_name).first():
        abort(404, f"Phase '{phase_name}' not found")
    neighbors = registry.neighbors(phase_name)
    return jsonify({"phase": phase_name, "neighbors": neighbors, "count": len(neighbors)})


@app.route("/api/graph/path")
def get_graph_path():
    start = request.args.get("from")
    end   = request.args.get("to")
    if not start or not end:
        abort(400, "Query params 'from' and 'to' are required")
    try:
        path = graph.shortest_path(start, end)
        return jsonify({"path": path, "length": len(path) - 1})
    except ValueError as e:
        abort(404, str(e))


# ── Discovery ────────────────────────────────────────────────

@app.route("/api/gaps")
def get_gaps():
    known     = [g for g in _gaps if g.status == "known"]
    forbidden = [g for g in _gaps if g.status == "forbidden"]
    predicted = [g for g in _gaps if g.status == "predicted"]
    candidate = [g for g in _gaps if g.status == "candidate"]
    return jsonify({
        "summary": {
            "total_evaluated": len(_gaps),
            "known":           len(known),
            "forbidden":       len(forbidden),
            "predicted":       len(predicted),
            "candidate_gaps":  len(candidate),
        },
        "predictions": [
            {"name": g.prediction.name, "coordinate": str(g.coordinate)}
            for g in predicted
        ],
        "forbidden_zones": [
            {"coordinate": str(g.coordinate), "theorem": getattr(g, "theorem_name", "theorem")}
            for g in forbidden[:20]
        ],
        "top_candidates": sorted(
            [{"coordinate": str(g.coordinate), "interest": round(g.interest_score, 3)} for g in candidate],
            key=lambda x: x["interest"], reverse=True
        )[:20],
    })


# ── Materials ────────────────────────────────────────────────

@app.route("/api/materials", methods=["POST"])
def get_materials():
    data = request.get_json()
    if not data:
        abort(400, "JSON body required")
    try:
        coord = coord_from_dict(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    reqs       = extract_requirements(coord)
    candidates = suggest_materials(coord, top_n=5)
    return jsonify({
        "coordinate":   str(coord),
        "requirements": [r.name for r in reqs],
        "candidates": [
            {"name": c.name, "score": round(c.overall_score, 3), "rationale": c.rationale}
            for c in candidates
        ],
    })


# ── Enum options ─────────────────────────────────────────────

@app.route("/api/enum_options")
def enum_options():
    return jsonify({
        "dimensionality":    [0, 1, 2, 3],
        "symmetry_breaking": [e.value for e in SymBreaking],
        "topological":       [e.value for e in TopoType],
        "dynamics":          [e.value for e in DynClass],
        "anyons":            [e.value for e in AnyonType],
    })


# ── Pipeline (MP API) ────────────────────────────────────────

@app.route("/api/pipeline", methods=["POST"])
def run_pipeline():
    if not os.getenv("MP_API_KEY"):
        return jsonify({"error": "MP_API_KEY not configured"}), 400
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    try:
        coord = coord_from_dict(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    try:
        from akasha_phase_engine.pipeline import run_pipeline as _run
    except ImportError:
        return jsonify({"error": "Install akasha-phase-engine[materials] for pipeline support"}), 501
    return jsonify(_run(coord, os.getenv("MP_API_KEY")))


# ── Boot ─────────────────────────────────────────────────────

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 8000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
