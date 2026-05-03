# Geometry Canon v3

The geometry engine is a structural analysis layer over typed graphs.
Nodes carry roles. Edges carry relation types. All outputs are scored.

---

## Typed Graph Model

Nodes declare a `node_type` from the Akasha Table:
`state | process | constraint | attractor | observer`

Edges declare a `relation` type:
`transitions_to | tends_toward | constrains | observes`
(plus canonical aliases defined in AKASHA_TABLE)

This is not an anonymous topology — structure carries meaning.

---

## Shapes

### Triangle
Three mutually reachable nodes. Structural stability indicator.

### Loop
Directed cycle of any length. Feedback and closure signal.

### Spiral
Novelty-driven outward path from a seed node.
Moves toward maximally unexplored structure — not just highest-degree hubs.

### Symmetry
Nodes with identical typed neighborhood signatures.
True structural equivalence, not degree matching.

### Star
Hub connected to ≥3 leaf nodes with no inter-leaf edges.
Constraint or broadcast center.

### Bridge
Single edge whose removal disconnects the graph.
Maximum structural fragility — missing redundancy signal.

### Isolated
Node with no edges. Undiscovered candidate, not a dead end.

---

## Fields

Named semantic fields grounded in AKASHA_TABLE primitives:

- `gap_pressure` — structural incompleteness
- `attractor_potential` — pull toward terminal states
- `constraint_strength` — limiting influence from constraint nodes
- `discovery_priority` — composite exploration signal
- `flow_density` — directed flow through a node

Fields support:
- propagation (spread with decay over N steps)
- gradient (scalar and directional)
- tension mapping (boundary detection)
- convergence point detection (structural sinks)
- normalization
- composition via FieldComposer

---

## Detection

- `detect_all_shapes()` — triangles, loops, stars, bridges, isolated; all scored
- `detect_symmetry()` — signature-based symmetry groups
- `detect_spirals(start, depth)` — novelty-scored spiral paths
- `predict_missing_links()` — topological + role-structural suggestions
- `detect_lattice_violations()` — nodes in forbidden lattice configurations
- `audit_node_roles()` — unmet structural expectations per node
- `discovery_frontier()` — ranked frontier nodes for exploration

---

## Metrics

`compute_metrics(engine)` returns a `GraphMetrics` dataclass:

- node/edge count, density
- symmetry index
- shape counts
- violation and role-gap counts
- frontier size
- composite health score (0–1)

---

## Integration

`suggest_discoveries(engine)` — ranked, typed discovery suggestions  
`geometry_report(engine)` — full structured report for logging or display  
`inject_geometry(discovery, geometry)` — attach to discovery pipeline
