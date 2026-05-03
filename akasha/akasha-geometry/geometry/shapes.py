"""
Akasha Geometry Engine — shapes.py

Shape canon. Shapes are not just topological patterns —
each shape carries structural meaning in the Akasha ontology.

Shapes now drive prediction, not just detection.
(Geometry Canon v2, SHAPES.md honored here)
"""

# ---------------------------------------------------------------------------
# SHAPE DEFINITIONS
# Each shape maps to an Akasha structural interpretation.
# ---------------------------------------------------------------------------

SHAPE_CANON = {
    "triangle": {
        "meaning":      "Stability",
        "description":  "Closed triad. Three mutually reachable nodes. "
                        "Indicates structural redundancy and local coherence.",
        "akasha_ref":   "AKASHA_TABLE equilibrium / constraint cluster",
        "discovery":    "Triangles that span different node types suggest cross-domain stability bridges.",
        "prediction":   "If two nodes share two common neighbors, a triangle edge is likely missing.",
    },
    "loop": {
        "meaning":      "Closure / Feedback",
        "description":  "Directed cycle of any length. Short loops = tight coupling. "
                        "Long loops = delayed feedback.",
        "akasha_ref":   "AKASHA_TABLE: process → state → process (iteration)",
        "discovery":    "Loops containing an attractor node are structurally suspect — "
                        "attractors should be terminal.",
        "prediction":   "A near-loop (one edge short of closure) is a high-confidence missing link.",
    },
    "spiral": {
        "meaning":      "Discovery",
        "description":  "An outward novelty path from a seed node. "
                        "Each step expands into maximally unexplored territory.",
        "akasha_ref":   "Axiom 8 (Iteration) + Discovery Doctrine loop",
        "discovery":    "The end of a spiral path is the frontier of current structural knowledge.",
        "prediction":   "Nodes at spiral tips are most likely to connect to undiscovered structure.",
    },
    "symmetry": {
        "meaning":      "Equivalence",
        "description":  "Two or more nodes with identical typed neighborhood signatures. "
                        "True structural equivalence — not just degree matching.",
        "akasha_ref":   "AKASHA_TABLE SYMMETRY primitive / DUALITY CHECK operator",
        "discovery":    "Symmetric nodes in different domains suggest cross-domain analogy candidates.",
        "prediction":   "What is known about one symmetric node likely applies to its partners.",
    },
    "star": {
        "meaning":      "Broadcast / Constraint center",
        "description":  "One hub connected to ≥3 leaf nodes with no edges among leaves. "
                        "Hub dominates local structure.",
        "akasha_ref":   "AKASHA_TABLE: constraint node or SOURCE primitive",
        "discovery":    "Stars whose hub is not typed as 'constraint' may be misclassified.",
        "prediction":   "Leaf nodes of the same star are likely to eventually connect directly.",
    },
    "bridge": {
        "meaning":      "Critical path",
        "description":  "A single edge whose removal disconnects the graph. "
                        "Maximum structural fragility.",
        "akasha_ref":   "AKASHA_TABLE BOUNDARY primitive / single-path flow",
        "discovery":    "Bridges are bottlenecks — the ecosystem needs redundant paths here.",
        "prediction":   "Alternate paths around a bridge are the highest-value missing links.",
    },
    "isolated": {
        "meaning":      "Orphan / Gap",
        "description":  "A node with no edges. Not yet integrated into any structure.",
        "akasha_ref":   "Axiom 2 (Discoverability) — gaps are signals",
        "discovery":    "Isolated nodes are undiscovered candidates, not dead ends.",
        "prediction":   "Match isolated nodes to existing symmetry groups for integration targets.",
    },
}


def describe_shape(shape_name: str) -> dict:
    """Return the full canonical description of a shape."""
    entry = SHAPE_CANON.get(shape_name)
    if not entry:
        return {"error": f"Unknown shape '{shape_name}'"}
    return {"shape": shape_name, **entry}


def prediction_strategy(shape_name: str) -> str:
    """Return what this shape predicts about missing structure."""
    entry = SHAPE_CANON.get(shape_name, {})
    return entry.get("prediction", "No prediction strategy defined for this shape.")


def all_shapes() -> list[dict]:
    return [{"shape": k, **v} for k, v in SHAPE_CANON.items()]
