"""
Akasha Geometry Engine — core.py

Structural geometry over typed graphs.
Nodes carry roles. Edges carry relation types.
All detections are scored and typed, not raw lists.
Lattice-aware: knows what configurations are invalid.
"""

from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# AKASHA TABLE — relation semantics embedded in the engine
# ---------------------------------------------------------------------------

# What each node type expects structurally
NODE_EXPECTATIONS = {
    "state": {
        "expects_incoming": {"transitions_to"},
        "expects_outgoing": {"transitions_to", "tends_toward"},
    },
    "process": {
        "expects_incoming": {"transitions_to"},
        "expects_outgoing": {"transitions_to"},
    },
    "constraint": {
        "expects_outgoing": {"constrains"},
    },
    "attractor": {
        # terminal — no outgoing allowed
        "allows_outgoing": set(),
    },
    "observer": {
        "expects_outgoing": {"observes"},
    },
}

RELATION_ALIASES = {
    "emerges_from": "transitions_to",
    "recovers_to": "transitions_to",
    "transitions_to_instability": "transitions_to",
    "settles_into": "tends_toward",
    "stabilizes": "constrains",
    "destabilizes": "constrains",
}

# Lattice invalidity rules — (phase, attribute, value) combos that are forbidden
LATTICE_INVALID_RULES = [
    {"phase": "attractor", "process": "transform"},
    {"phase": "attractor", "stability": "unstable"},
    {"phase": "attractor", "stability": "dynamic"},
    {"phase": "system",    "stability": "terminal"},
    {"phase": "transition", "process": "none"},
    {"phase": "transition", "stability": "stable"},
    {"phase": "transition", "stability": "terminal"},
    {"process": "converge", "constraint": "none"},
]


# ---------------------------------------------------------------------------
# NODE
# ---------------------------------------------------------------------------

@dataclass
class Edge:
    target: "Node"
    relation: str = "transitions_to"   # canonical relation type

    def canonical_relation(self) -> str:
        return RELATION_ALIASES.get(self.relation, self.relation)


class Node:
    def __init__(
        self,
        id: str,
        node_type: str = "state",
        lattice_attrs: Optional[dict] = None,
    ):
        self.id = id
        self.node_type = node_type          # state | process | constraint | attractor | observer
        self.lattice_attrs = lattice_attrs or {}   # phase, stability, constraint, process
        self._out_edges: list[Edge] = []    # typed directed edges
        self._in_edges: list[Edge] = []     # back-references (populated by graph)

    # convenience: treat node.edges as the set of neighbor nodes (undirected view)
    @property
    def edges(self) -> set["Node"]:
        targets = {e.target for e in self._out_edges}
        sources = {e.target for e in self._in_edges}   # _in_edges store source→self as .target
        return targets | sources

    def out_nodes(self) -> set["Node"]:
        return {e.target for e in self._out_edges}

    def in_nodes(self) -> set["Node"]:
        return {e.target for e in self._in_edges}

    def out_relations(self) -> dict["Node", str]:
        return {e.target: e.canonical_relation() for e in self._out_edges}

    def neighborhood_signature(self) -> tuple:
        """
        Structural fingerprint: sorted tuple of (neighbor_type, relation) pairs.
        Two nodes are structurally symmetric iff their signatures match.
        """
        sig = []
        for e in self._out_edges:
            sig.append((e.target.node_type, e.canonical_relation(), "out"))
        for e in self._in_edges:
            sig.append((e.target.node_type, e.canonical_relation(), "in"))
        return tuple(sorted(sig))

    def __repr__(self):
        return f"Node({self.id!r}, type={self.node_type!r})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id


# ---------------------------------------------------------------------------
# GRAPH BUILDER  (convenience wrapper — engine accepts raw node lists too)
# ---------------------------------------------------------------------------

class Graph:
    def __init__(self):
        self._nodes: dict[str, Node] = {}

    def add_node(self, id: str, node_type: str = "state", lattice_attrs: dict = None) -> Node:
        n = Node(id, node_type, lattice_attrs)
        self._nodes[id] = n
        return n

    def add_edge(self, from_id: str, to_id: str, relation: str = "transitions_to"):
        src = self._nodes[from_id]
        tgt = self._nodes[to_id]
        e = Edge(tgt, relation)
        src._out_edges.append(e)
        back = Edge(src, relation)    # _in_edges use target field to store the source
        tgt._in_edges.append(back)

    def nodes(self) -> list[Node]:
        return list(self._nodes.values())

    def get(self, id: str) -> Optional[Node]:
        return self._nodes.get(id)


# ---------------------------------------------------------------------------
# RESULT TYPES
# ---------------------------------------------------------------------------

@dataclass
class ShapeResult:
    shape: str          # triangle | loop | star | bridge | isolated
    nodes: list[str]
    score: float        # 0–1, structural significance
    note: str = ""

@dataclass
class SymmetryGroup:
    nodes: list[str]
    signature: tuple
    size: int

@dataclass
class SpiralPath:
    path: list[str]
    novelty_scores: list[float]   # per step
    total_novelty: float

@dataclass
class MissingLinkSuggestion:
    from_id: str
    to_id: str
    reason: str
    confidence: float   # 0–1

@dataclass
class LatticeViolation:
    node_id: str
    rule: dict
    description: str


# ---------------------------------------------------------------------------
# GEOMETRY ENGINE
# ---------------------------------------------------------------------------

class GeometryEngine:
    def __init__(self, graph: list[Node] | Graph):
        if isinstance(graph, Graph):
            self.graph: list[Node] = graph.nodes()
        else:
            self.graph = graph
        self._node_index: dict[str, Node] = {n.id: n for n in self.graph}

    # -----------------------------------------------------------------------
    # DISTANCE  (BFS, directed-aware)
    # -----------------------------------------------------------------------

    def distance(self, start: Node, end: Node, directed: bool = False) -> int:
        visited = set()
        queue = deque([(start, 0)])
        while queue:
            node, dist = queue.popleft()
            if node == end:
                return dist
            if node in visited:
                continue
            visited.add(node)
            neighbors = node.out_nodes() if directed else node.edges
            for n in neighbors:
                queue.append((n, dist + 1))
        return float("inf")

    def all_distances(self, start: Node, directed: bool = False) -> dict[str, int]:
        """BFS from start — returns distance to every reachable node."""
        visited = {}
        queue = deque([(start, 0)])
        while queue:
            node, dist = queue.popleft()
            if node.id in visited:
                continue
            visited[node.id] = dist
            neighbors = node.out_nodes() if directed else node.edges
            for n in neighbors:
                if n.id not in visited:
                    queue.append((n, dist + 1))
        return visited

    # -----------------------------------------------------------------------
    # CURVATURE  (local connectivity richness)
    # -----------------------------------------------------------------------

    def curvature(self, node: Node) -> float:
        """
        Extended curvature: degree normalized by graph average.
        >1.0 means this node is a hub. <1.0 means sparse.
        """
        deg = len(node.edges)
        avg = sum(len(n.edges) for n in self.graph) / max(len(self.graph), 1)
        return deg / avg if avg > 0 else 0.0

    # -----------------------------------------------------------------------
    # SHAPE DETECTION
    # -----------------------------------------------------------------------

    def detect_triangles(self) -> list[ShapeResult]:
        seen = set()
        results = []
        for a in self.graph:
            for b in a.out_nodes():
                for c in b.out_nodes():
                    if a in c.out_nodes():
                        key = tuple(sorted([a.id, b.id, c.id]))
                        if key not in seen:
                            seen.add(key)
                            # score: triangles involving attractors or constraints are more significant
                            types = {a.node_type, b.node_type, c.node_type}
                            sig_bonus = 0.2 if "attractor" in types or "constraint" in types else 0.0
                            results.append(ShapeResult(
                                shape="triangle",
                                nodes=[a.id, b.id, c.id],
                                score=round(0.6 + sig_bonus, 2),
                                note="Closed triad — structural stability indicator",
                            ))
        return results

    def detect_loops(self, max_length: int = 8) -> list[ShapeResult]:
        """
        Detect directed cycles of length 2–max_length.
        Short loops = tight coupling. Long loops = feedback potential.
        """
        results = []
        seen = set()

        def dfs(start: Node, current: Node, path: list, depth: int):
            if depth > max_length:
                return
            for nxt in current.out_nodes():
                if nxt == start and len(path) >= 2:
                    key = tuple(sorted(path))
                    if key not in seen:
                        seen.add(key)
                        length = len(path)
                        score = round(1.0 - (length - 2) / max_length, 2)
                        results.append(ShapeResult(
                            shape="loop",
                            nodes=list(path),
                            score=score,
                            note=f"Directed cycle length {length} — feedback / closure",
                        ))
                elif nxt.id not in path:
                    dfs(start, nxt, path + [nxt.id], depth + 1)

        for node in self.graph:
            dfs(node, node, [node.id], 1)
        return results

    def detect_stars(self) -> list[ShapeResult]:
        """
        Star: one hub node connected to ≥3 leaves with no edges among leaves.
        Stars often mark constraint nodes or broadcast points.
        """
        results = []
        for node in self.graph:
            neighbors = list(node.edges)
            if len(neighbors) < 3:
                continue
            leaves = [n for n in neighbors if not (n.edges - {node})]
            if len(leaves) >= 3:
                score = min(1.0, round(len(leaves) / len(self.graph), 2) + 0.4)
                results.append(ShapeResult(
                    shape="star",
                    nodes=[node.id] + [l.id for l in leaves],
                    score=score,
                    note=f"Hub with {len(leaves)} leaf nodes — broadcast or constraint center",
                ))
        return results

    def detect_bridges(self) -> list[ShapeResult]:
        """
        Bridge: an edge whose removal disconnects the graph.
        Bridges are structurally critical — single points of flow.
        """
        results = []
        base_components = self._count_components()

        for a in self.graph:
            for b in list(a.out_nodes()):
                # temporarily remove edge both directions
                a._out_edges = [e for e in a._out_edges if e.target != b]
                b._in_edges  = [e for e in b._in_edges  if e.target != a]
                new_components = self._count_components()
                if new_components > base_components:
                    results.append(ShapeResult(
                        shape="bridge",
                        nodes=[a.id, b.id],
                        score=1.0,
                        note="Critical bridge — removal disconnects graph",
                    ))
                # restore
                a._out_edges.append(Edge(b))
                b._in_edges.append(Edge(a))

        return results

    def detect_isolated(self) -> list[ShapeResult]:
        return [
            ShapeResult(
                shape="isolated",
                nodes=[n.id],
                score=0.1,
                note="No edges — structural orphan",
            )
            for n in self.graph if not n.edges
        ]

    def detect_all_shapes(self, include_loops: bool = True, max_loop_length: int = 8) -> list[ShapeResult]:
        shapes = []
        shapes += self.detect_triangles()
        if include_loops:
            shapes += self.detect_loops(max_loop_length)
        shapes += self.detect_stars()
        shapes += self.detect_bridges()
        shapes += self.detect_isolated()
        shapes.sort(key=lambda s: s.score, reverse=True)
        return shapes

    # -----------------------------------------------------------------------
    # SYMMETRY  (neighborhood-signature based, not degree-based)
    # -----------------------------------------------------------------------

    def detect_symmetry(self) -> list[SymmetryGroup]:
        """
        Group nodes by structural neighborhood signature.
        Two nodes are symmetric iff their typed relation neighborhoods are identical.
        This is actual structural equivalence, not just degree matching.
        """
        groups: dict[tuple, list[str]] = defaultdict(list)
        for node in self.graph:
            sig = node.neighborhood_signature()
            groups[sig].append(node.id)

        result = []
        for sig, node_ids in groups.items():
            if len(node_ids) > 1:
                result.append(SymmetryGroup(
                    nodes=node_ids,
                    signature=sig,
                    size=len(node_ids),
                ))
        result.sort(key=lambda g: g.size, reverse=True)
        return result

    # -----------------------------------------------------------------------
    # SPIRALS  (novelty-driven, not greedy-degree)
    # -----------------------------------------------------------------------

    def detect_spirals(self, start: Node, depth: int = 8) -> SpiralPath:
        """
        Novelty-driven spiral: at each step, move to the neighbor that
        maximizes unexplored structural territory (neighbors not yet seen),
        not just the highest-degree hub.

        Novelty score per step = fraction of that neighbor's neighbors
        that are outside the already-visited frontier.
        """
        visited_ids = {start.id}
        path = [start.id]
        novelty_scores = []
        current = start

        for _ in range(depth):
            candidates = list(current.edges - {self._node_index.get(p) for p in path if self._node_index.get(p)})
            candidates = [c for c in candidates if c.id not in visited_ids]
            if not candidates:
                break

            def novelty(node: Node) -> float:
                frontier = node.edges
                new = [n for n in frontier if n.id not in visited_ids]
                return len(new) / max(len(frontier), 1)

            next_node = max(candidates, key=novelty)
            score = novelty(next_node)
            novelty_scores.append(round(score, 3))
            path.append(next_node.id)
            visited_ids.add(next_node.id)
            current = next_node

        total = round(sum(novelty_scores) / max(len(novelty_scores), 1), 3)
        return SpiralPath(path=path, novelty_scores=novelty_scores, total_novelty=total)

    # -----------------------------------------------------------------------
    # MISSING LINK PREDICTION  (role-aware + topological)
    # -----------------------------------------------------------------------

    def predict_missing_links(self) -> list[MissingLinkSuggestion]:
        """
        Two sources of missing link suggestions:

        1. TOPOLOGICAL — nodes with ≥2 common neighbors that aren't connected.
           (original logic, kept and scored)

        2. ROLE-STRUCTURAL — a node's type has `expects_outgoing` relations
           that don't appear anywhere in its actual edges.
           For each unfulfilled expectation, find the most natural target.
        """
        suggestions = []
        seen = set()

        # 1. Topological
        for a in self.graph:
            for b in self.graph:
                if a == b or b in a.out_nodes():
                    continue
                common = len(a.edges.intersection(b.edges))
                if common >= 2:
                    key = (a.id, b.id)
                    if key not in seen:
                        seen.add(key)
                        confidence = min(1.0, round(common / max(len(a.edges), 1), 2))
                        suggestions.append(MissingLinkSuggestion(
                            from_id=a.id,
                            to_id=b.id,
                            reason=f"{common} common neighbors suggest structural proximity",
                            confidence=confidence,
                        ))

        # 2. Role-structural
        for node in self.graph:
            expectations = NODE_EXPECTATIONS.get(node.node_type, {})
            expected_out = expectations.get("expects_outgoing", set())
            actual_out = set(node.out_relations().values())

            missing_relations = expected_out - actual_out
            for rel in missing_relations:
                # find best candidate target: a node that would accept this relation
                for candidate in self.graph:
                    if candidate == node or candidate in node.out_nodes():
                        continue
                    cand_exp = NODE_EXPECTATIONS.get(candidate.node_type, {})
                    expected_in = cand_exp.get("expects_incoming", set())
                    if rel in expected_in:
                        key = (node.id, candidate.id)
                        if key not in seen:
                            seen.add(key)
                            suggestions.append(MissingLinkSuggestion(
                                from_id=node.id,
                                to_id=candidate.id,
                                reason=f"Role '{node.node_type}' expects outgoing '{rel}' — '{candidate.node_type}' accepts it",
                                confidence=0.75,
                            ))

        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        return suggestions

    # -----------------------------------------------------------------------
    # LATTICE VIOLATION DETECTION
    # -----------------------------------------------------------------------

    def detect_lattice_violations(self) -> list[LatticeViolation]:
        """
        Check every node's lattice_attrs against the invalid rule set
        from akasha_lattice.yaml.
        A violation means this node is in a structurally forbidden configuration.
        """
        violations = []
        for node in self.graph:
            attrs = node.lattice_attrs
            if not attrs:
                continue
            for rule in LATTICE_INVALID_RULES:
                if all(attrs.get(k) == v for k, v in rule.items()):
                    desc_parts = [f"{k}={v}" for k, v in rule.items()]
                    violations.append(LatticeViolation(
                        node_id=node.id,
                        rule=rule,
                        description=f"Invalid lattice combination: {', '.join(desc_parts)}",
                    ))
        return violations

    # -----------------------------------------------------------------------
    # STRUCTURAL ROLE AUDIT
    # -----------------------------------------------------------------------

    def audit_node_roles(self) -> dict[str, list[str]]:
        """
        For each node, check whether its actual edges fulfill its declared
        role expectations. Returns a dict of node_id → list of unmet expectations.
        """
        audit = {}
        for node in self.graph:
            issues = []
            expectations = NODE_EXPECTATIONS.get(node.node_type, {})

            # attractor should have no outgoing edges
            if node.node_type == "attractor" and node.out_nodes():
                issues.append("Attractor has outgoing edges — attractors are terminal")

            # check expected outgoing relations
            expected_out = expectations.get("expects_outgoing", set())
            actual_out = set(node.out_relations().values())
            for rel in expected_out:
                if rel not in actual_out:
                    issues.append(f"Missing expected outgoing relation: '{rel}'")

            # check expected incoming relations
            in_rels = {e.canonical_relation() for e in node._in_edges}
            expected_in = expectations.get("expects_incoming", set())
            for rel in expected_in:
                if rel not in in_rels:
                    issues.append(f"Missing expected incoming relation: '{rel}'")

            if issues:
                audit[node.id] = issues
        return audit

    # -----------------------------------------------------------------------
    # DISCOVERY FRONTIER
    # -----------------------------------------------------------------------

    def discovery_frontier(self) -> list[dict]:
        """
        Nodes at the structural edge of the known graph:
        - low in-degree (few things point to them)
        - high out-degree relative to in-degree
        - or structurally isolated from any attractor

        These are the best candidates for further exploration.
        """
        frontier = []
        attractor_ids = {n.id for n in self.graph if n.node_type == "attractor"}

        for node in self.graph:
            in_deg = len(node.in_nodes())
            out_deg = len(node.out_nodes())
            total = in_deg + out_deg
            if total == 0:
                continue

            # distance to nearest attractor
            dist_to_attractor = float("inf")
            for aid in attractor_ids:
                anode = self._node_index.get(aid)
                if anode:
                    d = self.distance(node, anode)
                    dist_to_attractor = min(dist_to_attractor, d)

            frontier_score = round(
                (out_deg / max(total, 1)) * 0.5
                + (1 / max(in_deg + 1, 1)) * 0.3
                + (1 / max(dist_to_attractor, 1)) * 0.2,
                3,
            )
            if frontier_score > 0.3:
                frontier.append({
                    "node_id": node.id,
                    "node_type": node.node_type,
                    "frontier_score": frontier_score,
                    "in_degree": in_deg,
                    "out_degree": out_deg,
                    "dist_to_attractor": dist_to_attractor,
                })

        frontier.sort(key=lambda x: x["frontier_score"], reverse=True)
        return frontier

    # -----------------------------------------------------------------------
    # INTERNAL HELPERS
    # -----------------------------------------------------------------------

    def _count_components(self) -> int:
        visited = set()
        count = 0
        for node in self.graph:
            if node.id not in visited:
                count += 1
                queue = deque([node])
                while queue:
                    n = queue.popleft()
                    if n.id in visited:
                        continue
                    visited.add(n.id)
                    for nb in n.edges:
                        queue.append(nb)
        return count
