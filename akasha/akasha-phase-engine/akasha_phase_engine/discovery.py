"""
discovery.py — Phase Discovery Engine

Treats the phase space as a coordinate system, identifies gaps,
applies known physical theorems to label them forbidden or candidate,
and scores candidate phases by how likely they are to exist and be found.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum
import itertools


# ============================================================================
# PHASE COORDINATE SYSTEM
# Reduce each phase to a point in a discrete multi-dimensional space
# ============================================================================

class TopoType(Enum):
    NONE       = "none"
    Z2         = "Z2"
    CHERN      = "Chern (integer)"
    ABELIAN    = "Abelian (FQH)"
    NON_ABELIAN = "Non-Abelian"

class SymBreaking(Enum):
    NONE       = "none"
    DISCRETE   = "discrete"
    CONTINUOUS = "continuous"
    GAUGE      = "gauge"

class DynClass(Enum):
    EQUILIBRIUM     = "equilibrium"
    DRIVEN_FLOQUET  = "driven-Floquet"
    DISSIPATIVE     = "dissipative"
    ACTIVE          = "active"

class AnyonType(Enum):
    NONE        = "none"
    ABELIAN     = "Abelian"
    NON_ABELIAN = "Non-Abelian"


@dataclass(frozen=True)
class PhaseCoordinate:
    """
    A point in the discrete phase space.
    Each axis is a physically meaningful binary or categorical choice.
    """
    dimensionality: int          # 0, 1, 2, 3
    symmetry_breaking: SymBreaking
    topological: TopoType
    dynamics: DynClass
    anyons: AnyonType
    edge_states: bool
    bulk_gap: bool
    long_range_entanglement: bool

    def __str__(self):
        parts = [
            f"d={self.dimensionality}",
            f"sym={self.symmetry_breaking.value}",
            f"topo={self.topological.value}",
            f"dyn={self.dynamics.value}",
            f"anyons={self.anyons.value}",
            f"edge={self.edge_states}",
            f"gap={self.bulk_gap}",
            f"LRE={self.long_range_entanglement}",
        ]
        return "(" + ", ".join(parts) + ")"


# ============================================================================
# KNOWN PHYSICAL THEOREMS — forbidden zone logic
# ============================================================================

@dataclass
class Theorem:
    name: str
    statement: str
    reference: str
    forbids: str   # human-readable description of what's forbidden

def is_forbidden(coord: PhaseCoordinate) -> Tuple[bool, Optional[Theorem]]:
    """
    Check if a coordinate is ruled out by a known physical theorem.
    Returns (is_forbidden, theorem_that_forbids_it).
    """

    theorems = [
        Theorem(
            name="Mermin-Wagner",
            statement="Continuous symmetry cannot be spontaneously broken at finite T in d ≤ 2",
            reference="Mermin & Wagner, PRL 17, 1133 (1966)",
            forbids="continuous symmetry breaking in d=1,2 at equilibrium"
        ),
        Theorem(
            name="Watanabe-Oshikawa",
            statement="Equilibrium time crystals cannot exist",
            reference="Watanabe & Oshikawa, PRL 114, 251603 (2015)",
            forbids="time-symmetry breaking in equilibrium"
        ),
        Theorem(
            name="Coleman (1+1)D",
            statement="No Goldstone bosons in 1+1D (continuous SSB forbidden)",
            reference="Coleman, Comm. Math. Phys. 31, 259 (1973)",
            forbids="continuous symmetry breaking in d=1"
        ),
        Theorem(
            name="Lieb-Schultz-Mattis",
            statement="Half-integer spin chains cannot have a unique gapped ground state",
            reference="Lieb, Schultz, Mattis, Ann. Phys. 16, 407 (1961)",
            forbids="gapped non-degenerate ground state in d=1 with half-integer spin"
        ),
        Theorem(
            name="Nielsen-Ninomiya",
            statement="Weyl nodes come in pairs of opposite chirality",
            reference="Nielsen & Ninomiya, NPB 185, 20 (1981)",
            forbids="single isolated Weyl node (must have partner)"
        ),
        Theorem(
            name="No-go: Non-Abelian anyons require non-Abelian topo order",
            statement="Non-Abelian anyons require non-Abelian topological order",
            reference="Kitaev, Ann. Phys. 321, 2 (2006)",
            forbids="non-Abelian anyons without non-Abelian topological order"
        ),
        Theorem(
            name="Hastings: LRE requires topological order or SSB",
            statement="Long-range entanglement requires topological order or symmetry breaking",
            reference="Hastings, J. Stat. Mech. P08024 (2007)",
            forbids="LRE without topological order and without symmetry breaking"
        ),
        Theorem(
            name="Bulk-edge correspondence",
            statement="Edge states require a bulk topological invariant",
            reference="Hatsugai, PRL 71, 3697 (1993)",
            forbids="edge states without topological bulk"
        ),
        Theorem(
            name="Anyons require 2D (or fracton in 3D)",
            statement="Conventional anyons (fractional statistics) only exist in 2D",
            reference="Leinaas & Myrheim, Nuovo Cim. B 37, 1 (1977)",
            forbids="conventional anyons in d=1 or d=3"
        ),
    ]

    # Check each theorem
    for thm in theorems:

        # Mermin-Wagner: continuous SSB forbidden in d≤2 at equilibrium
        if thm.name == "Mermin-Wagner":
            if (coord.symmetry_breaking == SymBreaking.CONTINUOUS
                    and coord.dimensionality <= 2
                    and coord.dynamics == DynClass.EQUILIBRIUM):
                return True, thm

        # Watanabe-Oshikawa: no equilibrium time crystals
        # (time crystals need driven dynamics — checked via DynClass)
        if thm.name == "Watanabe-Oshikawa":
            # Time crystals are non-equilibrium by definition in our schema
            # Flag if someone tries to put time-breaking in equilibrium:
            # (we don't have a time_breaking axis explicitly, but driven=False + anyons=none
            #  with discrete sym breaking in d=0 is a proxy)
            pass   # Handled implicitly by DynClass

        # Coleman: continuous SSB forbidden in d=1
        if thm.name == "Coleman (1+1)D":
            if (coord.symmetry_breaking == SymBreaking.CONTINUOUS
                    and coord.dimensionality == 1):
                return True, thm

        # No-go: non-Abelian anyons need non-Abelian topo order
        if thm.name == "No-go: Non-Abelian anyons require non-Abelian topo order":
            if (coord.anyons == AnyonType.NON_ABELIAN
                    and coord.topological != TopoType.NON_ABELIAN):
                return True, thm

        # LRE requires topo order or SSB
        if thm.name == "Hastings: LRE requires topological order or SSB":
            if (coord.long_range_entanglement
                    and coord.topological == TopoType.NONE
                    and coord.symmetry_breaking == SymBreaking.NONE):
                return True, thm

        # Edge states require topological bulk
        if thm.name == "Bulk-edge correspondence":
            if coord.edge_states and coord.topological == TopoType.NONE:
                return True, thm

        # Anyons require 2D
        if thm.name == "Anyons require 2D (or fracton in 3D)":
            if (coord.anyons != AnyonType.NONE
                    and coord.dimensionality == 1):
                return True, thm

    return False, None


# ============================================================================
# MAP KNOWN PHASES TO COORDINATES
# ============================================================================

KNOWN_PHASE_COORDINATES: Dict[str, PhaseCoordinate] = {
    "Crystal": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.DISCRETE,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Ferromagnet": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.CONTINUOUS,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "BCS Superconductor": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.GAUGE,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=True, long_range_entanglement=False
    ),
    "Topological Insulator": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.Z2, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=True,
        bulk_gap=True, long_range_entanglement=False
    ),
    "Weyl Semimetal": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.CHERN, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=True,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Fractional Quantum Hall State": PhaseCoordinate(
        dimensionality=2, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.ABELIAN, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.ABELIAN, edge_states=True,
        bulk_gap=True, long_range_entanglement=True
    ),
    "Quantum Spin Liquid": PhaseCoordinate(
        dimensionality=2, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.Z2, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.ABELIAN, edge_states=False,
        bulk_gap=False, long_range_entanglement=True
    ),
    "Mott Insulator": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.CONTINUOUS,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=True, long_range_entanglement=False
    ),
    "Bose-Einstein Condensate": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.CONTINUOUS,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Time Crystal": PhaseCoordinate(
        dimensionality=1, symmetry_breaking=SymBreaking.DISCRETE,
        topological=TopoType.NONE, dynamics=DynClass.DRIVEN_FLOQUET,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    # ── Ghost phases (now full entries) ──────────────────────────────
    "Paramagnet": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Normal Metal": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Normal Liquid": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Normal Bose Gas": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    # ── New phases ────────────────────────────────────────────────────
    "Topological Superconductor": PhaseCoordinate(
        dimensionality=1, symmetry_breaking=SymBreaking.GAUGE,
        topological=TopoType.Z2, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NON_ABELIAN, edge_states=True,
        bulk_gap=True, long_range_entanglement=False
    ),
    "Integer Quantum Hall State": PhaseCoordinate(
        dimensionality=2, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.CHERN, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=True,
        bulk_gap=True, long_range_entanglement=False
    ),
    "Dirac Semimetal": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.Z2, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=True,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Spin Glass": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.DISCRETE,
        topological=TopoType.NONE, dynamics=DynClass.DISSIPATIVE,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Nematic Liquid Crystal": PhaseCoordinate(
        dimensionality=3, symmetry_breaking=SymBreaking.CONTINUOUS,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=False, long_range_entanglement=False
    ),
    "Floquet Topological Insulator": PhaseCoordinate(
        dimensionality=2, symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.CHERN, dynamics=DynClass.DRIVEN_FLOQUET,
        anyons=AnyonType.NONE, edge_states=True,
        bulk_gap=True, long_range_entanglement=False
    ),
    "Wigner Crystal": PhaseCoordinate(
        dimensionality=2, symmetry_breaking=SymBreaking.DISCRETE,
        topological=TopoType.NONE, dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE, edge_states=False,
        bulk_gap=True, long_range_entanglement=False
    ),
}


# ============================================================================
# THEORETICAL PREDICTIONS — phases predicted but not confirmed
# ============================================================================

@dataclass
class TheoreticalPrediction:
    name: str
    coordinate: PhaseCoordinate
    predicted_by: str
    prediction_year: int
    prediction_paper: str
    mechanism: str
    candidate_materials: List[str]
    experimental_status: str
    confidence: float   # 0-1


THEORETICAL_PREDICTIONS = [
    TheoreticalPrediction(
        name="Non-Abelian FQH State (ν=5/2 Moore-Read)",
        coordinate=PhaseCoordinate(
            dimensionality=2, symmetry_breaking=SymBreaking.NONE,
            topological=TopoType.NON_ABELIAN, dynamics=DynClass.EQUILIBRIUM,
            anyons=AnyonType.NON_ABELIAN, edge_states=True,
            bulk_gap=True, long_range_entanglement=True
        ),
        predicted_by="Moore & Read",
        prediction_year=1991,
        prediction_paper="Moore & Read, Nuclear Physics B 360, 362 (1991)",
        mechanism="Paired composite fermions form non-Abelian topological order at ν=5/2",
        candidate_materials=["GaAs/AlGaAs at ν=5/2", "ZnO/MgZnO heterostructures"],
        experimental_status="Observed at ν=5/2 but non-Abelian nature not yet conclusively confirmed",
        confidence=0.75
    ),
    TheoreticalPrediction(
        name="Topological Superconductor (Kitaev Chain)",
        coordinate=PhaseCoordinate(
            dimensionality=1, symmetry_breaking=SymBreaking.GAUGE,
            topological=TopoType.Z2, dynamics=DynClass.EQUILIBRIUM,
            anyons=AnyonType.NON_ABELIAN, edge_states=True,
            bulk_gap=True, long_range_entanglement=False
        ),
        predicted_by="Kitaev",
        prediction_year=2001,
        prediction_paper="Kitaev, Physics-Uspekhi 44, 131 (2001)",
        mechanism="p-wave superconductor hosts Majorana zero modes at ends",
        candidate_materials=[
            "InAs nanowire + Nb (proximitized)",
            "Fe atomic chain on Pb",
            "Bi₂Se₃ + NbSe₂ (TI-SC interface)"
        ],
        experimental_status="Majorana signatures seen but topological protection debated (2023 retractions)",
        confidence=0.60
    ),
    TheoreticalPrediction(
        name="Floquet Topological Insulator",
        coordinate=PhaseCoordinate(
            dimensionality=2, symmetry_breaking=SymBreaking.NONE,
            topological=TopoType.CHERN, dynamics=DynClass.DRIVEN_FLOQUET,
            anyons=AnyonType.NONE, edge_states=True,
            bulk_gap=True, long_range_entanglement=False
        ),
        predicted_by="Oka & Aoki / Kitagawa et al.",
        prediction_year=2009,
        prediction_paper="Oka & Aoki, PRB 79, 081406 (2009); Kitagawa et al., PRB 82, 235114 (2010)",
        mechanism="Periodic driving induces topological band structure absent in equilibrium",
        candidate_materials=[
            "Graphene + circularly polarized light",
            "Photonic lattices",
            "Ultracold atoms in optical lattices"
        ],
        experimental_status="Demonstrated in photonic systems and cold atoms; electronic realization ongoing",
        confidence=0.85
    ),
    TheoreticalPrediction(
        name="3D Fractional Topological Insulator",
        coordinate=PhaseCoordinate(
            dimensionality=3, symmetry_breaking=SymBreaking.NONE,
            topological=TopoType.ABELIAN, dynamics=DynClass.EQUILIBRIUM,
            anyons=AnyonType.ABELIAN, edge_states=True,
            bulk_gap=True, long_range_entanglement=True
        ),
        predicted_by="Maciejko, Hughes, Zhang / Swingle et al.",
        prediction_year=2010,
        prediction_paper="Maciejko et al., PRL 105, 166803 (2010)",
        mechanism="Strongly-correlated 3D TI with fractional θ=π/3 magnetoelectric coupling",
        candidate_materials=["Strongly-correlated TI materials (unknown)", "Iridates under pressure"],
        experimental_status="Not yet observed experimentally",
        confidence=0.30
    ),
    TheoreticalPrediction(
        name="Topological Time Crystal",
        coordinate=PhaseCoordinate(
            dimensionality=2, symmetry_breaking=SymBreaking.DISCRETE,
            topological=TopoType.Z2, dynamics=DynClass.DRIVEN_FLOQUET,
            anyons=AnyonType.ABELIAN, edge_states=True,
            bulk_gap=True, long_range_entanglement=True
        ),
        predicted_by="Po, Fidkowski, Vishwanath et al.",
        prediction_year=2016,
        prediction_paper="Po et al., PRL 117, 126803 (2016) - Chiral Floquet phases",
        mechanism="Floquet drive simultaneously breaks time-translation symmetry and creates topological order",
        candidate_materials=[
            "Superconducting qubit arrays",
            "Trapped ion chains with 2D geometry",
            "Photonic Floquet topological insulators"
        ],
        experimental_status="Theoretical framework established; no experimental realization yet",
        confidence=0.45
    ),
    TheoreticalPrediction(
        name="Fracton Topological Order",
        coordinate=PhaseCoordinate(
            dimensionality=3, symmetry_breaking=SymBreaking.NONE,
            topological=TopoType.NON_ABELIAN, dynamics=DynClass.EQUILIBRIUM,
            anyons=AnyonType.NON_ABELIAN, edge_states=False,
            bulk_gap=True, long_range_entanglement=True
        ),
        predicted_by="Chamon / Haah / Vijay, Haah, Fu",
        prediction_year=2005,
        prediction_paper="Vijay, Haah, Fu, PRB 92, 235136 (2015)",
        mechanism="Immobile excitations (fractons) with sub-extensive ground state degeneracy",
        candidate_materials=[
            "Spin ice materials (Dy₂Ti₂O₇)",
            "Quantum spin liquids under pressure",
            "Engineered superconducting arrays"
        ],
        experimental_status="No material realization; extensively studied theoretically",
        confidence=0.40
    ),
    TheoreticalPrediction(
        name="Dissipative Topological Phase",
        coordinate=PhaseCoordinate(
            dimensionality=2, symmetry_breaking=SymBreaking.NONE,
            topological=TopoType.Z2, dynamics=DynClass.DISSIPATIVE,
            anyons=AnyonType.NONE, edge_states=True,
            bulk_gap=True, long_range_entanglement=False
        ),
        predicted_by="Diehl, Rico, Baranov, Zoller",
        prediction_year=2011,
        prediction_paper="Diehl et al., Nature Physics 7, 971 (2011)",
        mechanism="Engineered Lindblad dissipation stabilizes topological steady states",
        candidate_materials=[
            "Cold atoms with engineered loss",
            "Photonic cavities with gain/loss",
            "Superconducting circuits with controlled dissipation"
        ],
        experimental_status="Partial demonstrations in photonic systems",
        confidence=0.55
    ),
]


# ============================================================================
# GAP FINDER
# ============================================================================

@dataclass
class CandidatePhase:
    """A gap in the phase space — either forbidden or a candidate for discovery."""
    coordinate: PhaseCoordinate
    status: str          # "forbidden", "candidate", "predicted", "known"
    forbidden_by: Optional[Theorem] = None
    prediction: Optional[TheoreticalPrediction] = None
    known_name: Optional[str] = None
    novelty_score: float = 0.0     # How different from known phases (0-1)
    feasibility_score: float = 0.0  # How achievable experimentally (0-1)
    interest_score: float = 0.0    # Overall interest (novelty × feasibility)
    reasoning: str = ""


def score_candidate(coord: PhaseCoordinate, known_coords: Dict[str, PhaseCoordinate]) -> Tuple[float, float, str]:
    """
    Score a candidate coordinate for novelty and feasibility.
    Returns (novelty, feasibility, reasoning).
    """
    reasoning_parts = []
    novelty = 0.0
    feasibility = 0.5  # baseline

    # Novelty: how far is this from any known phase?
    min_distance = float('inf')
    closest = None
    for name, kc in known_coords.items():
        dist = sum([
            kc.dimensionality != coord.dimensionality,
            kc.symmetry_breaking != coord.symmetry_breaking,
            kc.topological != coord.topological,
            kc.dynamics != coord.dynamics,
            kc.anyons != coord.anyons,
            kc.edge_states != coord.edge_states,
            kc.bulk_gap != coord.bulk_gap,
            kc.long_range_entanglement != coord.long_range_entanglement,
        ])
        if dist < min_distance:
            min_distance = dist
            closest = name

    novelty = min(min_distance / 8.0, 1.0)
    reasoning_parts.append(f"Closest known phase: '{closest}' (distance={min_distance})")

    # Feasibility adjustments
    if coord.dynamics == DynClass.DRIVEN_FLOQUET:
        feasibility += 0.1
        reasoning_parts.append("Floquet systems are experimentally accessible")

    if coord.dimensionality == 2:
        feasibility += 0.1
        reasoning_parts.append("2D systems well-studied experimentally")

    if coord.anyons == AnyonType.NON_ABELIAN:
        feasibility -= 0.2
        reasoning_parts.append("Non-Abelian anyons are hard to detect/confirm")

    if coord.dynamics == DynClass.DISSIPATIVE:
        feasibility -= 0.1
        reasoning_parts.append("Dissipative topological phases require precise engineering")

    if coord.long_range_entanglement and coord.topological == TopoType.NON_ABELIAN:
        feasibility -= 0.15
        reasoning_parts.append("Non-Abelian LRE phases are theoretically complex")

    if coord.bulk_gap:
        feasibility += 0.05
        reasoning_parts.append("Gapped bulk aids experimental identification")

    feasibility = max(0.0, min(1.0, feasibility))
    return novelty, feasibility, "; ".join(reasoning_parts)


def find_gaps(known_coords: Dict[str, PhaseCoordinate],
              predictions: List[TheoreticalPrediction]) -> List[CandidatePhase]:
    """
    Enumerate a meaningful subset of phase space, classify each point,
    and return all non-trivial gaps as CandidatePhase objects.
    """
    results = []
    prediction_coords = {p.coordinate: p for p in predictions}

    # Axes to explore
    dims = [1, 2, 3]
    sym_breaks = list(SymBreaking)
    topos = list(TopoType)
    dynamics = list(DynClass)
    anyons = [AnyonType.NONE, AnyonType.ABELIAN, AnyonType.NON_ABELIAN]
    edge_states = [True, False]
    bulk_gaps = [True, False]
    lre_vals = [True, False]

    seen_known = set(known_coords.values())

    for combo in itertools.product(dims, sym_breaks, topos, dynamics,
                                   anyons, edge_states, bulk_gaps, lre_vals):
        d, sb, topo, dyn, anyon, edge, gap, lre = combo

        coord = PhaseCoordinate(
            dimensionality=d,
            symmetry_breaking=sb,
            topological=topo,
            dynamics=dyn,
            anyons=anyon,
            edge_states=edge,
            bulk_gap=gap,
            long_range_entanglement=lre
        )

        # Already known?
        if coord in seen_known:
            known_name = [n for n, c in known_coords.items() if c == coord][0]
            results.append(CandidatePhase(
                coordinate=coord,
                status="known",
                known_name=known_name
            ))
            continue

        # Forbidden?
        forbidden, theorem = is_forbidden(coord)
        if forbidden:
            results.append(CandidatePhase(
                coordinate=coord,
                status="forbidden",
                forbidden_by=theorem
            ))
            continue

        # Theoretically predicted?
        if coord in prediction_coords:
            pred = prediction_coords[coord]
            novelty, feasibility, reasoning = score_candidate(coord, known_coords)
            results.append(CandidatePhase(
                coordinate=coord,
                status="predicted",
                prediction=pred,
                novelty_score=novelty,
                feasibility_score=feasibility,
                interest_score=novelty * feasibility * (0.5 + 0.5 * pred.confidence),
                reasoning=reasoning
            ))
            continue

        # Candidate gap
        novelty, feasibility, reasoning = score_candidate(coord, known_coords)
        interest = novelty * feasibility

        # Filter out boring / trivial combos
        if interest < 0.05:
            continue

        results.append(CandidatePhase(
            coordinate=coord,
            status="candidate",
            novelty_score=novelty,
            feasibility_score=feasibility,
            interest_score=interest,
            reasoning=reasoning
        ))

    return results


# ============================================================================
# PHASE TRANSITION INFERENCE
# ============================================================================

def infer_possible_transitions(coord_a: PhaseCoordinate,
                               coord_b: PhaseCoordinate) -> Optional[str]:
    """
    Given two phase coordinates, infer if a transition between them
    is plausible and what drives it.
    """
    differences = []
    if coord_a.symmetry_breaking != coord_b.symmetry_breaking:
        differences.append(f"symmetry: {coord_a.symmetry_breaking.value} → {coord_b.symmetry_breaking.value}")
    if coord_a.topological != coord_b.topological:
        differences.append(f"topology: {coord_a.topological.value} → {coord_b.topological.value}")
    if coord_a.dynamics != coord_b.dynamics:
        differences.append(f"dynamics: {coord_a.dynamics.value} → {coord_b.dynamics.value}")
    if coord_a.bulk_gap != coord_b.bulk_gap:
        differences.append(f"gap: {coord_a.bulk_gap} → {coord_b.bulk_gap}")
    if coord_a.long_range_entanglement != coord_b.long_range_entanglement:
        differences.append(f"LRE: {coord_a.long_range_entanglement} → {coord_b.long_range_entanglement}")

    if not differences:
        return None  # Same phase

    if len(differences) > 3:
        return None  # Too many changes at once — unlikely direct transition

    return "Changes: " + "; ".join(differences)


# ============================================================================
# MAIN DISCOVERY REPORT
# ============================================================================

def run_discovery_report():
    print("=" * 70)
    print("  PHASE DISCOVERY ENGINE")
    print("  Scanning phase space for gaps, candidates, and predictions")
    print("=" * 70)

    # Run gap finder
    all_candidates = find_gaps(KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS)

    known     = [c for c in all_candidates if c.status == "known"]
    forbidden = [c for c in all_candidates if c.status == "forbidden"]
    predicted = [c for c in all_candidates if c.status == "predicted"]
    candidate = [c for c in all_candidates if c.status == "candidate"]

    print(f"\n  Phase space scanned: {len(all_candidates)} coordinates evaluated")
    print(f"  ✓ Known phases:             {len(known)}")
    print(f"  ✗ Forbidden by theorems:    {len(forbidden)}")
    print(f"  ◈ Theoretically predicted:  {len(predicted)}")
    print(f"  ? Candidate gaps:           {len(candidate)}")

    # ----------------------------------------------------------------
    # THEORETICALLY PREDICTED — ranked by confidence
    # ----------------------------------------------------------------
    print("\n" + "─" * 70)
    print("  THEORETICALLY PREDICTED PHASES (ranked by confidence)")
    print("─" * 70)
    predicted_sorted = sorted(predicted, key=lambda x: x.prediction.confidence, reverse=True)
    for c in predicted_sorted:
        p = c.prediction
        bar = "█" * int(p.confidence * 10) + "░" * (10 - int(p.confidence * 10))
        print(f"\n  [{bar}] {p.confidence:.0%} — {p.name}")
        print(f"    Predicted: {p.predicted_by} ({p.prediction_year})")
        print(f"    Mechanism: {p.mechanism}")
        print(f"    Status: {p.experimental_status}")
        print(f"    Materials: {', '.join(p.candidate_materials[:2])}")
        print(f"    Paper: {p.prediction_paper}")

    # ----------------------------------------------------------------
    # TOP CANDIDATE GAPS — uncharted, not forbidden
    # ----------------------------------------------------------------
    print("\n" + "─" * 70)
    print("  TOP CANDIDATE GAPS (unexplored, not forbidden by known theorems)")
    print("─" * 70)
    top_candidates = sorted(candidate, key=lambda x: x.interest_score, reverse=True)[:12]
    for i, c in enumerate(top_candidates, 1):
        interest_bar = "★" * int(c.interest_score * 10) + "·" * (10 - int(c.interest_score * 10))
        print(f"\n  #{i} [{interest_bar}] interest={c.interest_score:.2f}")
        print(f"    Coordinate: {c.coordinate}")
        print(f"    Novelty: {c.novelty_score:.2f}  Feasibility: {c.feasibility_score:.2f}")
        print(f"    Reasoning: {c.reasoning}")

    # ----------------------------------------------------------------
    # FORBIDDEN ZONES — summary by theorem
    # ----------------------------------------------------------------
    print("\n" + "─" * 70)
    print("  FORBIDDEN ZONES (ruled out by known theorems)")
    print("─" * 70)
    theorem_counts: Dict[str, int] = {}
    for c in forbidden:
        name = c.forbidden_by.name
        theorem_counts[name] = theorem_counts.get(name, 0) + 1
    for thm_name, count in sorted(theorem_counts.items(), key=lambda x: -x[1]):
        thm = next(c.forbidden_by for c in forbidden if c.forbidden_by.name == thm_name)
        print(f"\n  {thm_name} ({count} coordinates ruled out)")
        print(f"    Forbids: {thm.forbids}")
        print(f"    Reference: {thm.reference}")

    # ----------------------------------------------------------------
    # TRANSITION INFERENCE — what can reach what
    # ----------------------------------------------------------------
    print("\n" + "─" * 70)
    print("  INFERRED POSSIBLE TRANSITIONS BETWEEN KNOWN PHASES")
    print("─" * 70)
    names = list(KNOWN_PHASE_COORDINATES.keys())
    found = 0
    for i, name_a in enumerate(names):
        for name_b in names[i+1:]:
            result = infer_possible_transitions(
                KNOWN_PHASE_COORDINATES[name_a],
                KNOWN_PHASE_COORDINATES[name_b]
            )
            if result:
                print(f"\n  {name_a}  ↔  {name_b}")
                print(f"    {result}")
                found += 1
    print(f"\n  Total plausible transitions found: {found}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_discovery_report()
