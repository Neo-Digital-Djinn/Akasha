"""
Akasha Geometry Engine — fields.py

Scalar fields over typed graphs.
Fields are named and semantically grounded — not arbitrary floats.
Supports propagation, convergence detection, and tension mapping.
"""

from dataclasses import dataclass
from collections import deque


# ---------------------------------------------------------------------------
# CANONICAL FIELD NAMES
# Grounded in AKASHA_TABLE primitives (gradient, attractor, constraint, gap)
# ---------------------------------------------------------------------------

FIELD_TYPES = {
    "gap_pressure":         "Structural incompleteness signal — how many expected connections are missing",
    "attractor_potential":  "Pull toward terminal convergence states",
    "constraint_strength":  "Limiting or shaping influence emanating from constraint nodes",
    "discovery_priority":   "Combined signal for where exploration should go next",
    "flow_density":         "How much directed flow passes through this node",
}


# ---------------------------------------------------------------------------
# RESULT TYPES
# ---------------------------------------------------------------------------

@dataclass
class FieldTension:
    node_id: str
    field_name: str
    tension: float      # how much this node's value differs from its neighbors
    note: str = ""

@dataclass
class ConvergencePoint:
    node_id: str
    field_name: str
    value: float
    basin_size: int     # how many nodes flow toward this point
    note: str = ""


# ---------------------------------------------------------------------------
# FIELD
# ---------------------------------------------------------------------------

class Field:
    def __init__(self, name: str = "unnamed"):
        if name not in FIELD_TYPES and name != "unnamed":
            raise ValueError(
                f"Unknown field type '{name}'. "
                f"Canonical fields: {list(FIELD_TYPES.keys())}"
            )
        self.name = name
        self.description = FIELD_TYPES.get(name, "")
        self._values: dict = {}    # node → float

    def set(self, node, value: float):
        self._values[node] = float(value)

    def get(self, node) -> float:
        return self._values.get(node, 0.0)

    def gradient(self, node) -> float:
        """Mean neighbor value — this node's value (scalar gradient magnitude)."""
        neighbors = list(node.edges)
        if not neighbors:
            return 0.0
        neighbor_mean = sum(self.get(n) for n in neighbors) / len(neighbors)
        return neighbor_mean - self.get(node)

    def directional_gradient(self, node) -> dict[str, float]:
        """Per-neighbor signed gradient: positive = field rises toward that neighbor."""
        return {
            n.id: round(self.get(n) - self.get(node), 4)
            for n in node.edges
        }

    def propagate(self, steps: int = 3, decay: float = 0.8) -> "Field":
        """
        Spread field values outward from seed nodes over N steps.
        At each step, each node receives the weighted average of its
        neighbors' values from the previous step, decayed by `decay`.

        Returns a NEW Field with propagated values (original unchanged).
        """
        result = Field(self.name)
        current = dict(self._values)

        for _ in range(steps):
            next_vals = dict(current)
            for node, value in current.items():
                for neighbor in node.edges:
                    spread = value * decay
                    if next_vals.get(neighbor, 0.0) < spread:
                        next_vals[neighbor] = spread
            current = next_vals

        for node, val in current.items():
            result.set(node, round(val, 4))
        return result

    def tension_map(self, graph: list) -> list[FieldTension]:
        """
        For each node, compute how much its field value differs
        from its neighborhood mean. High tension = structural boundary.
        Tension nodes are candidates for phase transitions or constraint locations.
        """
        tensions = []
        for node in graph:
            neighbors = list(node.edges)
            if not neighbors:
                continue
            my_val = self.get(node)
            neighbor_mean = sum(self.get(n) for n in neighbors) / len(neighbors)
            tension = abs(my_val - neighbor_mean)
            if tension > 0.05:
                tensions.append(FieldTension(
                    node_id=node.id,
                    field_name=self.name,
                    tension=round(tension, 4),
                    note="High field tension — possible boundary or transition point",
                ))
        tensions.sort(key=lambda t: t.tension, reverse=True)
        return tensions

    def convergence_points(self, graph: list, threshold: float = 0.5) -> list[ConvergencePoint]:
        """
        Find nodes where the field pools — value above threshold AND
        gradient points inward from all neighbors (local maximum).
        These are structural sinks or attractor candidates.
        """
        points = []
        for node in graph:
            val = self.get(node)
            if val < threshold:
                continue
            neighbors = list(node.edges)
            if not neighbors:
                continue
            # all neighbors have lower value → local maximum
            if all(self.get(n) <= val for n in neighbors):
                basin = self._basin_size(node, graph)
                points.append(ConvergencePoint(
                    node_id=node.id,
                    field_name=self.name,
                    value=round(val, 4),
                    basin_size=basin,
                    note=f"Field peak — {basin} nodes drain toward this point",
                ))
        points.sort(key=lambda p: p.value, reverse=True)
        return points

    def _basin_size(self, sink: object, graph: list) -> int:
        """Count nodes from which gradient flows toward `sink`."""
        count = 0
        for node in graph:
            if node == sink:
                continue
            my_val = self.get(node)
            sink_val = self.get(sink)
            dist_neighbors = [n for n in node.edges if self.get(n) > my_val]
            if not dist_neighbors and sink_val > my_val:
                count += 1
        return count

    def normalize(self) -> "Field":
        """Return a new field with all values scaled to [0, 1]."""
        result = Field(self.name)
        if not self._values:
            return result
        min_v = min(self._values.values())
        max_v = max(self._values.values())
        span = max_v - min_v
        for node, val in self._values.items():
            result.set(node, round((val - min_v) / span, 4) if span > 0 else 0.5)
        return result

    def summary(self) -> dict:
        if not self._values:
            return {"name": self.name, "nodes": 0}
        vals = list(self._values.values())
        return {
            "name": self.name,
            "description": self.description,
            "nodes": len(vals),
            "min": round(min(vals), 4),
            "max": round(max(vals), 4),
            "mean": round(sum(vals) / len(vals), 4),
        }


# ---------------------------------------------------------------------------
# FIELD COMPOSER — combine multiple fields into discovery_priority
# ---------------------------------------------------------------------------

class FieldComposer:
    """
    Combine named fields into a composite discovery priority signal.
    Weights should sum to 1.0.
    """

    DEFAULT_WEIGHTS = {
        "gap_pressure":        0.4,
        "attractor_potential": 0.3,
        "constraint_strength": 0.2,
        "flow_density":        0.1,
    }

    def compose(self, fields: dict[str, "Field"], graph: list, weights: dict = None) -> "Field":
        w = weights or self.DEFAULT_WEIGHTS
        result = Field("discovery_priority")
        for node in graph:
            score = sum(
                fields[fname].get(node) * weight
                for fname, weight in w.items()
                if fname in fields
            )
            result.set(node, round(score, 4))
        return result
