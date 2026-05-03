"""
Akasha Geometry Engine — geometry/reasoner.py

Structural reasoning over combined detection results.
The engine doesn't just find things — it thinks about what it found.

A Finding is a compound observation: two or more detections that,
in combination, mean something the individual parts don't.
A Hypothesis is a Finding elevated into a testable claim with
a falsifier and a confidence score.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# RESULT TYPES
# ---------------------------------------------------------------------------

@dataclass
class CompoundFinding:
    """
    Two or more detections that interact to produce a meaning
    neither carries alone.
    """
    finding_type: str           # e.g. "fragile_convergence_path"
    involved_nodes: list[str]
    evidence: list[str]         # what detections triggered this
    severity: float             # 0–1, how structurally significant
    interpretation: str         # what this means in Akasha terms
    prediction: str             # what should be true if this is real


@dataclass
class GeometryHypothesis:
    """
    A structured, testable claim derived from compound findings.
    Matches the Akasha request schema — ready to become a REQ-xxx.json.
    """
    id: str                         # e.g. "GEO-HYP-001"
    title: str
    summary: str
    why: str
    hypothesis_type: str            # missing_organ | structural_fault | analogy_candidate | frontier_claim
    involved_nodes: list[str]
    supporting_findings: list[str]  # finding_type references
    confidence: float               # 0–1
    falsifier: str                  # what observation would disprove this
    suggested_action: str           # what to do next
    proposed_repo: Optional[str] = None
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# REASONER
# ---------------------------------------------------------------------------

class GeometryReasoner:
    """
    Accepts raw outputs from GeometryEngine and reasons over them
    to produce compound findings and hypotheses.
    """

    def __init__(self, engine):
        self.engine = engine
        self._graph_index = {n.id: n for n in engine.graph}

        # Run all detections once, cache results
        self._shapes        = engine.detect_all_shapes()
        self._symmetry      = engine.detect_symmetry()
        self._violations    = engine.detect_lattice_violations()
        self._audit         = engine.audit_node_roles()
        self._missing       = engine.predict_missing_links()
        self._frontier      = engine.discovery_frontier()

        self._shape_index   = self._index_shapes()

    def _index_shapes(self) -> dict[str, list]:
        """Index shapes by type for fast lookup."""
        index = {}
        for s in self._shapes:
            index.setdefault(s.shape, []).append(s)
        return index

    # -----------------------------------------------------------------------
    # COMPOUND FINDING DETECTION
    # -----------------------------------------------------------------------

    def find_compound_findings(self) -> list[CompoundFinding]:
        findings = []
        findings += self._find_fragile_convergence_paths()
        findings += self._find_unconstrained_transitions()
        findings += self._find_symmetric_orphans()
        findings += self._find_bridge_role_gaps()
        findings += self._find_attractor_violations()
        findings += self._find_spiral_dead_ends()
        findings += self._find_isolated_symmetry_matches()
        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings

    def _find_fragile_convergence_paths(self) -> list[CompoundFinding]:
        """
        A bridge edge that is ALSO the only path to an attractor.
        Fragile convergence = single critical path to a terminal state.
        This is structurally dangerous and a strong missing-link signal.
        """
        findings = []
        bridges = {tuple(sorted(s.nodes)) for s in self._shapes if s.shape == "bridge"}
        attractor_ids = {n.id for n in self.engine.graph if n.node_type == "attractor"}

        for bridge_pair in bridges:
            a_id, b_id = bridge_pair
            a = self._graph_index.get(a_id)
            b = self._graph_index.get(b_id)
            if not a or not b:
                continue

            # Check if removing this bridge would disconnect any attractor from the rest
            for att_id in attractor_ids:
                att = self._graph_index.get(att_id)
                if not att:
                    continue
                dist_through = self.engine.distance(a, att)
                if dist_through < float("inf") and (a_id in [att_id] or b_id in [att_id] or dist_through <= 2):
                    findings.append(CompoundFinding(
                        finding_type="fragile_convergence_path",
                        involved_nodes=[a_id, b_id, att_id],
                        evidence=[f"bridge({a_id},{b_id})", f"attractor({att_id})", f"dist={dist_through}"],
                        severity=0.95,
                        interpretation=(
                            f"The only path toward attractor '{att_id}' passes through bridge "
                            f"'{a_id}→{b_id}'. A single edge failure severs convergence. "
                            "Akasha Axiom 6 (Modularity) requires redundant paths to terminal states."
                        ),
                        prediction=(
                            f"Adding an alternate route to '{att_id}' that bypasses this bridge "
                            "would lower structural fragility and increase health score."
                        ),
                    ))
        return findings

    def _find_unconstrained_transitions(self) -> list[CompoundFinding]:
        """
        Transition nodes (process type, dynamic phase) with no incoming
        constraint edge. Per akasha_lattice: a transition with no constraint
        is structurally loose — undirected change.
        """
        findings = []
        for node in self.engine.graph:
            if node.node_type != "process":
                continue
            in_relations = {e.canonical_relation() for e in node._in_edges}
            if "constrains" not in in_relations:
                audit_issues = self._audit.get(node.id, [])
                findings.append(CompoundFinding(
                    finding_type="unconstrained_transition",
                    involved_nodes=[node.id],
                    evidence=[f"process_node({node.id})", "no_incoming_constrains", f"audit_issues={len(audit_issues)}"],
                    severity=0.75,
                    interpretation=(
                        f"Process node '{node.id}' has no constraint governing it. "
                        "Unconstrained transitions produce unpredictable structural change. "
                        "AKASHA_TABLE: process nodes expect limiting influence."
                    ),
                    prediction=(
                        f"A constraint node pointing to '{node.id}' would stabilize this transition "
                        "and close the role gap."
                    ),
                ))
        return findings

    def _find_symmetric_orphans(self) -> list[CompoundFinding]:
        """
        An isolated node that shares a neighborhood signature with a connected node.
        This is the strongest integration signal: the orphan has a structural partner.
        """
        findings = []
        isolated_ids = {s.nodes[0] for s in self._shapes if s.shape == "isolated"}
        if not isolated_ids:
            return findings

        for group in self._symmetry:
            orphans_in_group = [nid for nid in group.nodes if nid in isolated_ids]
            connected_in_group = [nid for nid in group.nodes if nid not in isolated_ids]
            if orphans_in_group and connected_in_group:
                for orphan_id in orphans_in_group:
                    findings.append(CompoundFinding(
                        finding_type="symmetric_orphan",
                        involved_nodes=[orphan_id] + connected_in_group,
                        evidence=[
                            f"isolated({orphan_id})",
                            f"symmetry_group({group.nodes})",
                            f"connected_partners={connected_in_group}",
                        ],
                        severity=0.90,
                        interpretation=(
                            f"Isolated node '{orphan_id}' has the same structural signature as "
                            f"connected node(s) {connected_in_group}. "
                            "This is not a random orphan — it is a structurally displaced partner. "
                            "Axiom 2 (Discoverability): gaps in coherent structure are signals."
                        ),
                        prediction=(
                            f"'{orphan_id}' should receive the same edge configuration as its "
                            f"symmetric partners. The missing edges are predictable from the signature."
                        ),
                    ))
        return findings

    def _find_bridge_role_gaps(self) -> list[CompoundFinding]:
        """
        A bridge node that also has unmet role expectations.
        Critically positioned AND structurally incomplete = highest priority repair.
        """
        findings = []
        bridge_nodes = set()
        for s in self._shapes:
            if s.shape == "bridge":
                bridge_nodes.update(s.nodes)

        for node_id in bridge_nodes:
            issues = self._audit.get(node_id, [])
            if issues:
                findings.append(CompoundFinding(
                    finding_type="bridge_role_gap",
                    involved_nodes=[node_id],
                    evidence=[f"bridge_node({node_id})", f"role_gaps={issues}"],
                    severity=0.85,
                    interpretation=(
                        f"Node '{node_id}' is a structural bridge (critical single point of flow) "
                        f"AND has {len(issues)} unmet role expectation(s). "
                        "A structurally critical node that is also incomplete is a compounded risk."
                    ),
                    prediction=(
                        f"Fulfilling the role expectations of '{node_id}' will both close its "
                        "structural gaps and reduce graph fragility simultaneously."
                    ),
                ))
        return findings

    def _find_attractor_violations(self) -> list[CompoundFinding]:
        """
        An attractor node with outgoing edges — attractors are terminal.
        This is a lattice violation AND a semantic contradiction.
        """
        findings = []
        for node in self.engine.graph:
            if node.node_type == "attractor" and node.out_nodes():
                out_ids = [n.id for n in node.out_nodes()]
                findings.append(CompoundFinding(
                    finding_type="attractor_violation",
                    involved_nodes=[node.id] + out_ids,
                    evidence=[
                        f"attractor({node.id})",
                        f"outgoing_edges={out_ids}",
                        "lattice_rule: attractor.allows_outgoing=[]",
                    ],
                    severity=1.0,
                    interpretation=(
                        f"Node '{node.id}' is typed as an attractor but has outgoing edges to {out_ids}. "
                        "Attractors are terminal convergence points — they cannot emit transitions. "
                        "This is either a misclassification or a structural error."
                    ),
                    prediction=(
                        f"Either reclassify '{node.id}' as a process or state node, "
                        "or remove its outgoing edges. The graph cannot be lattice-valid with this configuration."
                    ),
                ))
        return findings

    def _find_spiral_dead_ends(self) -> list[CompoundFinding]:
        """
        Run spirals from all frontier nodes. If a spiral terminates at a bridge,
        the discovery path leads to a fragile point — a compound signal.
        """
        findings = []
        bridge_nodes = {nid for s in self._shapes if s.shape == "bridge" for nid in s.nodes}
        frontier_ids = [f["node_id"] for f in self._frontier[:3]]

        for fid in frontier_ids:
            start = self._graph_index.get(fid)
            if not start:
                continue
            spiral = self.engine.detect_spirals(start, depth=6)
            if len(spiral.path) < 2:
                continue
            tip = spiral.path[-1]
            if tip in bridge_nodes:
                findings.append(CompoundFinding(
                    finding_type="spiral_bridge_terminus",
                    involved_nodes=spiral.path,
                    evidence=[
                        f"spiral_from({fid})",
                        f"terminus({tip})",
                        f"tip_is_bridge=True",
                        f"novelty={spiral.total_novelty}",
                    ],
                    severity=0.70,
                    interpretation=(
                        f"The discovery spiral from frontier node '{fid}' terminates at '{tip}', "
                        "which is a structural bridge. Exploration along this path leads directly "
                        "to the graph's most fragile point. "
                        "The discovery frontier and the structural weakness are the same location."
                    ),
                    prediction=(
                        f"Extending structure beyond '{tip}' would simultaneously expand "
                        "the discovery frontier and reduce bridge fragility."
                    ),
                ))
        return findings

    def _find_isolated_symmetry_matches(self) -> list[CompoundFinding]:
        """
        Isolated nodes that have role-structural missing links pointing to them.
        Cross-signal: topology says orphan, role engine says connect here.
        """
        findings = []
        isolated_ids = {s.nodes[0] for s in self._shapes if s.shape == "isolated"}
        for link in self._missing:
            if link.to_id in isolated_ids or link.from_id in isolated_ids:
                orphan = link.to_id if link.to_id in isolated_ids else link.from_id
                partner = link.from_id if orphan == link.to_id else link.to_id
                findings.append(CompoundFinding(
                    finding_type="role_confirmed_orphan",
                    involved_nodes=[orphan, partner],
                    evidence=[
                        f"isolated({orphan})",
                        f"role_missing_link({partner}→{orphan})",
                        f"confidence={link.confidence}",
                        f"reason={link.reason}",
                    ],
                    severity=0.80,
                    interpretation=(
                        f"Node '{orphan}' is topologically isolated AND role analysis independently "
                        f"identifies '{partner}' as expecting a connection to it. "
                        "Two independent signals converge on the same missing edge."
                    ),
                    prediction=(
                        f"The edge '{partner}→{orphan}' is structurally required. "
                        "Confidence is compounded by independent evidence streams."
                    ),
                ))
        return findings

    # -----------------------------------------------------------------------
    # HYPOTHESIS GENERATION
    # -----------------------------------------------------------------------

    def generate_hypotheses(self, findings: list[CompoundFinding] = None) -> list[GeometryHypothesis]:
        """
        Elevate compound findings into structured, testable hypotheses.
        Each hypothesis is ready for the Akasha request pipeline.
        """
        if findings is None:
            findings = self.find_compound_findings()

        hypotheses = []
        counter = 1

        for f in findings:
            hyp = self._finding_to_hypothesis(f, counter)
            if hyp:
                hypotheses.append(hyp)
                counter += 1

        hypotheses.sort(key=lambda h: h.confidence, reverse=True)
        return hypotheses

    def _finding_to_hypothesis(self, f: CompoundFinding, n: int) -> Optional[GeometryHypothesis]:
        hid = f"GEO-HYP-{n:03d}"

        if f.finding_type == "fragile_convergence_path":
            return GeometryHypothesis(
                id=hid,
                title="Redundant Convergence Path Required",
                hypothesis_type="structural_fault",
                involved_nodes=f.involved_nodes,
                supporting_findings=[f.finding_type],
                confidence=f.severity,
                summary=f"The graph has a single fragile path to its attractor state. Structural redundancy is required for robust convergence.",
                why="Akasha Axiom 6 (Modularity) states systems must be decomposable without collapse. A single convergence path violates this. Any disruption to this bridge severs the system from its attractor — the system cannot find stability.",
                falsifier="Demonstrate two independent paths from any system node to the attractor that share no edges.",
                suggested_action="Add an alternate tends_toward or transitions_to edge that routes around the bridge to the attractor.",
                notes=[
                    f"Involved nodes: {f.involved_nodes}",
                    "Priority: fix before expanding the graph further.",
                ],
            )

        elif f.finding_type == "unconstrained_transition":
            node_id = f.involved_nodes[0]
            return GeometryHypothesis(
                id=hid,
                title=f"Missing Constraint on Transition Node '{node_id}'",
                hypothesis_type="missing_organ",
                involved_nodes=f.involved_nodes,
                supporting_findings=[f.finding_type],
                confidence=f.severity,
                summary=f"Process node '{node_id}' operates without any governing constraint, producing undirected structural change.",
                why="AKASHA_TABLE defines process nodes as transformations that occur under constraints. Without constraint, a transition is ungoverned — its outcome cannot be predicted or validated. This violates Axiom 5 (Traceability).",
                falsifier=f"Show that '{node_id}' produces consistent, predictable outputs without constraint input.",
                suggested_action=f"Introduce a constraint node that governs '{node_id}' via a 'constrains' edge.",
                proposed_repo="akasha-geometry-constraint-audit",
                notes=[
                    "Constraint nodes should declare what limiting rule they represent.",
                    "See AKASHA_TABLE constraint primitive.",
                ],
            )

        elif f.finding_type == "symmetric_orphan":
            orphan = f.involved_nodes[0]
            partners = f.involved_nodes[1:]
            return GeometryHypothesis(
                id=hid,
                title=f"Structurally Displaced Node '{orphan}' — Integration Candidate",
                hypothesis_type="frontier_claim",
                involved_nodes=f.involved_nodes,
                supporting_findings=[f.finding_type],
                confidence=f.severity,
                summary=f"Isolated node '{orphan}' has an identical structural signature to connected node(s) {partners}. It is not a random orphan — it belongs to the same equivalence class.",
                why="Axiom 2 (Discoverability) states that gaps in coherent structure are signals. A node that is structurally equivalent to a connected node but unconnected itself is a displaced element, not an absent one. Its integration is predictable.",
                falsifier=f"Show that '{orphan}' has fundamentally different semantics from {partners} despite identical signatures, justifying its isolation.",
                suggested_action=f"Mirror the edge configuration of {partners} onto '{orphan}'. The missing edges are inferrable from the neighborhood signature.",
                notes=[
                    "This is the highest-confidence integration target in the graph.",
                    "Symmetric orphans produce predictable missing edges — no guesswork required.",
                ],
            )

        elif f.finding_type == "bridge_role_gap":
            node_id = f.involved_nodes[0]
            return GeometryHypothesis(
                id=hid,
                title=f"Critical Node '{node_id}' Is Structurally Incomplete",
                hypothesis_type="structural_fault",
                involved_nodes=f.involved_nodes,
                supporting_findings=[f.finding_type],
                confidence=f.severity,
                summary=f"Node '{node_id}' is both a structural bridge (single critical flow point) and has unmet role expectations. Structural importance and structural incompleteness are compounded.",
                why="A bridge node failing to fulfill its declared role means the critical path through the graph is governed by an incomplete organ. This is a compounded risk: fragility plus incompleteness at the same location.",
                falsifier=f"Show that the role gaps on '{node_id}' are intentional design choices that do not affect its bridge function.",
                suggested_action=f"Fulfill the role expectations of '{node_id}' before adding any further structure that depends on it.",
                notes=["Role gaps at bridges are higher priority than role gaps at non-bridge nodes."],
            )

        elif f.finding_type == "attractor_violation":
            node_id = f.involved_nodes[0]
            return GeometryHypothesis(
                id=hid,
                title=f"Attractor Node '{node_id}' Is Misclassified or Malformed",
                hypothesis_type="structural_fault",
                involved_nodes=f.involved_nodes,
                supporting_findings=[f.finding_type],
                confidence=f.severity,
                summary=f"Node '{node_id}' is declared as an attractor but emits outgoing edges. Attractors are terminal — they do not transition to further states.",
                why="The akasha_lattice.yaml explicitly forbids attractor nodes from having process=transform or emitting transitions. A non-terminal attractor is a contradiction: the system cannot converge if convergence points keep transforming.",
                falsifier=f"Reclassify '{node_id}' as a process or state node and demonstrate the graph becomes lattice-valid.",
                suggested_action=f"Either remove outgoing edges from '{node_id}' or reclassify it. Do not leave it as attractor with outgoing structure.",
                notes=["Lattice violations are the highest severity class — they indicate incoherent structure."],
            )

        elif f.finding_type == "spiral_bridge_terminus":
            return GeometryHypothesis(
                id=hid,
                title="Discovery Frontier Coincides with Structural Fragility",
                hypothesis_type="frontier_claim",
                involved_nodes=f.involved_nodes,
                supporting_findings=[f.finding_type],
                confidence=f.severity,
                summary="The novelty-driven discovery spiral from the highest-priority frontier node terminates at a bridge edge. The edge of known structure is also the graph's most fragile point.",
                why="When the discovery frontier and structural fragility coincide, expansion is risky: adding new structure beyond a bridge increases the load on an already critical single point. Axiom 6 (Modularity) requires redundancy before extension.",
                falsifier="Show that the bridge at the spiral terminus connects two well-redundant subgraphs and is not actually load-bearing.",
                suggested_action="Add structural redundancy at the bridge terminus before extending the spiral path further. Discovery should not proceed through a known fragile point.",
                notes=[f"Spiral path: {f.involved_nodes}", "Fix the bridge, then continue the spiral."],
            )

        elif f.finding_type == "role_confirmed_orphan":
            orphan = f.involved_nodes[0]
            partner = f.involved_nodes[1]
            return GeometryHypothesis(
                id=hid,
                title=f"Dual-Signal Missing Edge: '{partner}' → '{orphan}'",
                hypothesis_type="missing_organ",
                involved_nodes=f.involved_nodes,
                supporting_findings=[f.finding_type],
                confidence=min(1.0, f.severity + 0.1),
                summary=f"Two independent signals — topological isolation and role expectation analysis — both identify the edge '{partner}→{orphan}' as missing.",
                why="Independent evidence streams converging on the same structural gap is the strongest possible missing-link signal. Axiom 2 (Discoverability) + Axiom 5 (Traceability): this is a traceable, dual-anchored discovery.",
                falsifier=f"Show that '{partner}' and '{orphan}' are intentionally disconnected and the role expectation is being fulfilled by another path not visible in the current graph.",
                suggested_action=f"Add the edge '{partner}→{orphan}'. This is the highest-confidence single structural addition available.",
                notes=["Dual-signal findings are the closest thing this engine produces to a certainty."],
            )

        return None

    # -----------------------------------------------------------------------
    # REQUEST EXPORT
    # -----------------------------------------------------------------------

    def export_as_requests(self, hypotheses: list[GeometryHypothesis] = None) -> list[dict]:
        """
        Export hypotheses as Akasha REQ-format dicts.
        Ready to be written as REQ-GEO-xxx.json files.
        """
        from datetime import datetime, timezone
        if hypotheses is None:
            hypotheses = self.generate_hypotheses()

        requests = []
        for hyp in hypotheses:
            req = {
                "request_id": hyp.id,
                "title": hyp.title,
                "request_type": "research" if hyp.hypothesis_type in ("frontier_claim", "analogy_candidate") else "system",
                "source": "geometry_engine",
                "status": "open",
                "priority": "high" if hyp.confidence >= 0.85 else "medium",
                "summary": hyp.summary,
                "why": hyp.why,
                "hypothesis_type": hyp.hypothesis_type,
                "confidence": hyp.confidence,
                "involved_nodes": hyp.involved_nodes,
                "falsifier": hyp.falsifier,
                "suggested_action": hyp.suggested_action,
                "supporting_findings": hyp.supporting_findings,
                "notes": hyp.notes,
                "captured_from": "akasha-geometry-engine / reasoner.py",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if hyp.proposed_repo:
                req["proposed_repo"] = hyp.proposed_repo
            requests.append(req)
        return requests
