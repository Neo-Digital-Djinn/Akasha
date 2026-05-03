"""
materials.py — Material Suggestion Engine

Given a target phase coordinate (known, predicted, or candidate gap),
reasons about what physical ingredients are needed and suggests
real or plausible material systems to look in.

Design logic:
  Each axis of PhaseCoordinate implies physical requirements.
  We combine requirements across axes, find material families that
  satisfy them, score by feasibility, and explain the reasoning.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from akasha_phase_engine.discovery import (
    PhaseCoordinate, TopoType, SymBreaking, DynClass, AnyonType,
    KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS, find_gaps
)


# ============================================================================
# MATERIAL INGREDIENT SYSTEM
# Each physical requirement maps to a set of material properties
# ============================================================================

@dataclass
class PhysicalRequirement:
    """A single physical ingredient needed to realize a phase."""
    name: str
    description: str
    difficulty: float       # 0 (easy) to 1 (very hard)
    implies_elements: List[str] = field(default_factory=list)
    implies_structure: List[str] = field(default_factory=list)
    implies_conditions: List[str] = field(default_factory=list)
    implies_techniques: List[str] = field(default_factory=list)


@dataclass
class MaterialCandidate:
    """A suggested material or material class for a given phase coordinate."""
    name: str
    formula_or_class: str
    rationale: str
    requirements_satisfied: List[str]
    requirements_missing: List[str]
    feasibility_score: float     # 0-1
    synthesis_difficulty: float  # 0-1
    detection_difficulty: float  # 0-1
    overall_score: float
    suggested_experiment: str
    estimated_timeline: str      # "months", "years", "decade+"
    prior_work: List[str] = field(default_factory=list)
    warning: Optional[str] = None


# ============================================================================
# REQUIREMENT EXTRACTION
# For each axis value, what does physics require of the material?
# ============================================================================

def extract_requirements(coord: PhaseCoordinate) -> List[PhysicalRequirement]:
    """
    Given a phase coordinate, return the list of physical requirements
    that any material realizing this phase must satisfy.
    """
    reqs = []

    # --- DIMENSIONALITY ---
    if coord.dimensionality == 2:
        reqs.append(PhysicalRequirement(
            name="2D confinement",
            description="Electrons or spins must be confined to 2D",
            difficulty=0.3,
            implies_structure=["Heterostructure", "Monolayer", "2DEG", "Van der Waals"],
            implies_techniques=["MBE", "CVD", "Mechanical exfoliation"],
            implies_conditions=["Low temperature (< 10K typically)"]
        ))
    elif coord.dimensionality == 1:
        reqs.append(PhysicalRequirement(
            name="1D confinement",
            description="System must be quasi-1D: nanowire, chain, or edge",
            difficulty=0.5,
            implies_structure=["Nanowire", "Atomic chain", "Edge state", "Carbon nanotube"],
            implies_techniques=["STM atom manipulation", "Nanowire growth", "Etching"],
            implies_conditions=["Ultra-low temperature (< 1K for quantum effects)"]
        ))

    # --- TOPOLOGY ---
    if coord.topological == TopoType.Z2:
        reqs.append(PhysicalRequirement(
            name="Strong spin-orbit coupling",
            description="SOC must be large enough to invert bands or create Z₂ topology",
            difficulty=0.3,
            implies_elements=["Bi", "Sb", "Te", "Se", "Hg", "Pb", "Ir", "Pt", "W", "Ta"],
            implies_structure=["Heavy element compounds", "Inverted band gap"],
            implies_techniques=["ARPES", "Transport"],
            implies_conditions=["Band inversion at Γ or TRIM points"]
        ))
    elif coord.topological == TopoType.CHERN:
        reqs.append(PhysicalRequirement(
            name="Broken time-reversal + SOC",
            description="Need broken T symmetry (magnetic) + strong SOC for non-zero Chern number",
            difficulty=0.5,
            implies_elements=["Mn", "Cr", "Fe", "Co", "Bi", "Te", "Se"],
            implies_structure=["Magnetic topological insulator", "Anomalous Hall system"],
            implies_techniques=["ARPES", "Anomalous Hall measurement"],
            implies_conditions=["Magnetic order + band inversion simultaneously"]
        ))
    elif coord.topological == TopoType.ABELIAN:
        reqs.append(PhysicalRequirement(
            name="Strong electron correlations in 2D + magnetic field",
            description="Need partially filled Landau levels or flat Chern bands",
            difficulty=0.7,
            implies_elements=["GaAs", "C (graphene)", "Mo", "W"],
            implies_structure=["2DEG", "Moiré superlattice", "High magnetic field setup"],
            implies_techniques=["Ultra-high purity MBE", "Dilution refrigerator", "High B"],
            implies_conditions=["T < 100 mK", "B > 10 T", "Ultra-clean interface"]
        ))
    elif coord.topological == TopoType.NON_ABELIAN:
        reqs.append(PhysicalRequirement(
            name="Non-Abelian topological order",
            description="Need p-wave pairing, ν=5/2 FQH, or Kitaev honeycomb physics",
            difficulty=0.9,
            implies_elements=["In", "As", "Nb", "Ru", "Cl", "Ir"],
            implies_structure=["Proximitized semiconductor", "Kitaev material", "p-wave SC"],
            implies_techniques=["Interference measurement", "Braiding experiment"],
            implies_conditions=["T < 50 mK", "Topological gap > thermal fluctuations"]
        ))

    # --- SYMMETRY BREAKING ---
    if coord.symmetry_breaking == SymBreaking.CONTINUOUS:
        reqs.append(PhysicalRequirement(
            name="Continuous symmetry breaking mechanism",
            description="Need exchange coupling, BEC condensation, or U(1) breaking",
            difficulty=0.2,
            implies_structure=["Magnetic material", "Superfluid", "Ferroelectric"],
            implies_techniques=["Magnetometry", "Neutron scattering", "Specific heat"],
        ))
    elif coord.symmetry_breaking == SymBreaking.GAUGE:
        reqs.append(PhysicalRequirement(
            name="Superconducting pairing",
            description="Cooper pairs or BEC condensate must break U(1) gauge symmetry",
            difficulty=0.3,
            implies_elements=["Nb", "Pb", "Al", "In", "Cu", "Y", "Ba"],
            implies_structure=["Superconductor", "Proximitized material"],
            implies_techniques=["Resistance measurement", "Meissner effect", "Tunneling"],
            implies_conditions=["T < T_c (material dependent)"]
        ))
    elif coord.symmetry_breaking == SymBreaking.DISCRETE:
        reqs.append(PhysicalRequirement(
            name="Discrete symmetry breaking",
            description="Ising, Z₂, or lattice symmetry must be broken",
            difficulty=0.2,
            implies_structure=["Ising magnet", "CDW material", "Crystal"],
            implies_techniques=["X-ray diffraction", "NMR", "Magnetometry"],
        ))

    # --- DYNAMICS ---
    if coord.dynamics == DynClass.DRIVEN_FLOQUET:
        reqs.append(PhysicalRequirement(
            name="Periodic drive",
            description="System must be driven periodically without heating to death",
            difficulty=0.5,
            implies_structure=["MBL material", "Prethermal system", "Photonic lattice"],
            implies_techniques=["Pulsed laser", "Microwave drive", "RF pulses"],
            implies_conditions=["Drive frequency >> system energy scales", "Disorder for MBL"]
        ))
    elif coord.dynamics == DynClass.DISSIPATIVE:
        reqs.append(PhysicalRequirement(
            name="Engineered dissipation",
            description="Lindblad jump operators must be precisely controlled",
            difficulty=0.7,
            implies_structure=["Cavity QED", "Cold atoms with laser cooling",
                               "Superconducting circuit with tunable loss"],
            implies_techniques=["Quantum optics", "Cavity coupling", "Feedback control"],
            implies_conditions=["Ratio of coherent to dissipative rates must be tuned"]
        ))
    elif coord.dynamics == DynClass.ACTIVE:
        reqs.append(PhysicalRequirement(
            name="Self-propulsion or activity",
            description="System must have local energy injection (active matter)",
            difficulty=0.6,
            implies_structure=["Active colloids", "Bacterial suspension", "Driven granular"],
            implies_techniques=["Optical microscopy", "Particle tracking"],
            implies_conditions=["Maintained far from equilibrium by internal motors"]
        ))

    # --- ANYONS ---
    if coord.anyons == AnyonType.ABELIAN:
        reqs.append(PhysicalRequirement(
            name="Fractionalized excitations",
            description="Quasiparticles must carry fractional quantum numbers",
            difficulty=0.6,
            implies_structure=["FQH system", "Z₂ QSL", "Kitaev material"],
            implies_techniques=["Shot noise", "Interferometry", "Tunneling spectroscopy"],
            implies_conditions=["Strong correlations + frustration or strong B field"]
        ))
    elif coord.anyons == AnyonType.NON_ABELIAN:
        reqs.append(PhysicalRequirement(
            name="Non-Abelian anyons",
            description="Braiding must implement non-commuting unitary operations",
            difficulty=0.95,
            implies_structure=["ν=5/2 FQH", "Kitaev honeycomb", "Topological SC"],
            implies_techniques=["Anyon interferometry", "Braiding experiment"],
            implies_conditions=["Exceptionally clean sample", "T < 10 mK typically"]
        ))

    # --- EDGE STATES ---
    if coord.edge_states:
        reqs.append(PhysicalRequirement(
            name="Topological boundary modes",
            description="Sample must have clean edges/surfaces where modes localize",
            difficulty=0.3,
            implies_structure=["Clean cleaved surface", "Etched edge", "Interface"],
            implies_techniques=["ARPES", "STM", "Transport in Hall bar geometry"],
            implies_conditions=["Surface/edge must be free of reconstruction or disorder"]
        ))

    # --- LONG RANGE ENTANGLEMENT ---
    if coord.long_range_entanglement:
        reqs.append(PhysicalRequirement(
            name="Long-range entanglement",
            description="Ground state must have topological entanglement entropy γ > 0",
            difficulty=0.7,
            implies_structure=["Topologically ordered ground state"],
            implies_techniques=["Entanglement spectrum from DMRG", "Topological entropy"],
            implies_conditions=["No spontaneous symmetry breaking that masks topo order"]
        ))

    # --- BULK GAP ---
    if coord.bulk_gap:
        reqs.append(PhysicalRequirement(
            name="Bulk energy gap",
            description="Bulk must be gapped to protect edge states and topological order",
            difficulty=0.3,
            implies_structure=["Insulator or SC with gap"],
            implies_techniques=["Tunneling spectroscopy", "Optical gap measurement", "ARPES"],
            implies_conditions=["Gap >> k_B T for topological protection"]
        ))

    return reqs


# ============================================================================
# MATERIAL DATABASE
# Known material families and their intrinsic properties
# ============================================================================

@dataclass
class MaterialFamily:
    name: str
    example_compounds: List[str]
    intrinsic_properties: List[str]
    typical_synthesis: List[str]
    typical_characterization: List[str]
    dimensionality: List[int]
    known_phases: List[str]
    notes: str


MATERIAL_FAMILIES = [
    MaterialFamily(
        name="Bismuth chalcogenides",
        example_compounds=["Bi₂Se₃", "Bi₂Te₃", "Sb₂Te₃", "BiSbTeSe₂"],
        intrinsic_properties=["Strong SOC", "Band inversion", "Z₂ topology", "Rhombohedral structure"],
        typical_synthesis=["Bridgman", "MBE", "CVD"],
        typical_characterization=["ARPES", "Transport", "STM"],
        dimensionality=[2, 3],
        known_phases=["Topological Insulator"],
        notes="Workhorse TI family. Bulk conductivity problematic. Thin films cleaner."
    ),
    MaterialFamily(
        name="Transition metal dichalcogenides (TMDs)",
        example_compounds=["MoS₂", "WSe₂", "WTe₂", "MoTe₂", "NbSe₂"],
        intrinsic_properties=["2D van der Waals", "Strong SOC (W,Mo)", "Superconductivity (NbSe₂)",
                               "CDW", "Ising SOC in monolayer"],
        typical_synthesis=["MBE", "CVD", "Mechanical exfoliation"],
        typical_characterization=["ARPES", "Transport", "Raman", "STM"],
        dimensionality=[2],
        known_phases=["BCS Superconductor (NbSe₂)", "CDW", "Weyl Semimetal (WTe₂)"],
        notes="Highly tunable via stacking, twisting, gating. Rich phase space."
    ),
    MaterialFamily(
        name="Moiré systems (twisted bilayers)",
        example_compounds=["Twisted bilayer graphene", "Twisted WSe₂", "Twisted MoTe₂",
                           "Graphene/hBN moiré"],
        intrinsic_properties=["Flat bands", "Strong correlations tunable by twist angle",
                               "Superconductivity", "FQH without B field (fractional Chern)"],
        typical_synthesis=["Mechanical assembly with rotation control"],
        typical_characterization=["Transport", "STM/STS", "Optical spectroscopy"],
        dimensionality=[2],
        known_phases=["BCS Superconductor", "Mott Insulator", "Fractional Chern Insulator"],
        notes="Magic angle graphene opened entirely new phase space. High tunability."
    ),
    MaterialFamily(
        name="Kitaev materials (honeycomb iridates / ruthenates)",
        example_compounds=["α-RuCl₃", "Na₂IrO₃", "α-Li₂IrO₃", "H₃LiIr₂O₆"],
        intrinsic_properties=["Kitaev interactions dominant", "Frustrated honeycomb",
                               "Strong SOC (Ir, Ru)", "Possible QSL ground state"],
        typical_synthesis=["CVT", "Hydrothermal", "Bridgman"],
        typical_characterization=["Neutron scattering", "μSR", "Raman", "THz spectroscopy"],
        dimensionality=[2, 3],
        known_phases=["Quantum Spin Liquid (candidate)", "Antiferromagnet"],
        notes="α-RuCl₃ closest to Kitaev QSL. Field-induced QSL phase actively studied."
    ),
    MaterialFamily(
        name="Proximitized semiconductor nanowires",
        example_compounds=["InAs/Nb", "InSb/Al", "InAs/Al", "Ge/Sn nanowire + SC"],
        intrinsic_properties=["Strong Rashba SOC", "Proximitized SC gap",
                               "Tunable by gate voltage", "1D confinement"],
        typical_synthesis=["MBE nanowire growth + SC deposition"],
        typical_characterization=["Tunneling conductance", "Zero-bias peak", "Non-local transport"],
        dimensionality=[1],
        known_phases=["BCS Superconductor (proximitized)", "→ Topological Superconductor (Kitaev chain)"],
        notes="Main platform for Majorana search. Results controversial post-2023 retractions."
    ),
    MaterialFamily(
        name="GaAs/AlGaAs 2DEG",
        example_compounds=["GaAs/Al₀.₃Ga₀.₇As", "GaAs/AlAs"],
        intrinsic_properties=["Ultra-high mobility 2DEG", "Clean Landau levels",
                               "FQH states well-developed"],
        typical_synthesis=["MBE (ultra-high purity, mobility > 10⁷ cm²/Vs)"],
        typical_characterization=["Hall transport", "Shot noise", "Interferometry"],
        dimensionality=[2],
        known_phases=["Integer QHE", "FQH (ν=1/3, 2/5, 5/2, ...)"],
        notes="Gold standard for FQH physics. Expensive, slow growth. ν=5/2 key target."
    ),
    MaterialFamily(
        name="Cuprate superconductors",
        example_compounds=["La₂CuO₄", "YBa₂Cu₃O₇", "Bi₂Sr₂CaCu₂O₈", "HgBa₂CuO₄"],
        intrinsic_properties=["High-T_c SC from doped Mott insulator",
                               "d-wave pairing", "Pseudogap", "Competing orders"],
        typical_synthesis=["Solid-state reaction", "Floating zone", "PLD"],
        typical_characterization=["ARPES", "Neutron scattering", "STM", "Transport"],
        dimensionality=[2, 3],
        known_phases=["Mott Insulator", "BCS Superconductor (high-T_c)"],
        notes="Central unsolved problem in condensed matter. Rich phase diagram."
    ),
    MaterialFamily(
        name="Iridium oxides (iridates)",
        example_compounds=["Sr₂IrO₄", "Na₂IrO₃", "Pr₂Ir₂O₇", "Ba₂IrO₄"],
        intrinsic_properties=["J_eff=1/2 Mott physics", "Strong SOC + correlations",
                               "Anisotropic magnetic interactions", "Topological candidates"],
        typical_synthesis=["Floating zone", "Solid-state reaction"],
        typical_characterization=["ARPES", "Neutron scattering", "X-ray"],
        dimensionality=[2, 3],
        known_phases=["Mott Insulator", "Topological Mott Insulator (predicted)"],
        notes="Jeff=1/2 state makes iridates unique intersection of SOC + Mott physics."
    ),
    MaterialFamily(
        name="Ultracold atoms in optical lattices",
        example_compounds=["⁸⁷Rb in optical lattice", "⁶Li Fermi gas", "⁴⁰K + ⁸⁷Rb mixture"],
        intrinsic_properties=["Perfect tunability of all parameters",
                               "No disorder (unless added)", "Hubbard model realization",
                               "Floquet driving straightforward"],
        typical_synthesis=["Laser cooling + evaporative cooling + optical lattice"],
        typical_characterization=["Absorption imaging", "Quantum gas microscope", "TOF"],
        dimensionality=[1, 2, 3],
        known_phases=["BEC", "Mott Insulator", "Superfluid"],
        notes="Quantum simulator par excellence. Can engineer almost any Hamiltonian."
    ),
    MaterialFamily(
        name="Superconducting qubit arrays",
        example_compounds=["Transmon arrays", "Fluxonium chains", "Google/IBM chips"],
        intrinsic_properties=["Engineered Hamiltonians", "Tunable coupling",
                               "Floquet driving trivial", "Measurement at will"],
        typical_synthesis=["Nanofabrication on Si/sapphire"],
        typical_characterization=["Qubit tomography", "Correlation measurements"],
        dimensionality=[1, 2],
        known_phases=["Time Crystal (demonstrated)", "Floquet phases"],
        notes="Best platform for exotic non-equilibrium phases. Limited by coherence time."
    ),
    MaterialFamily(
        name="Magnetic topological insulators",
        example_compounds=["MnBi₂Te₄", "Cr-doped (Bi,Sb)₂Te₃", "V-doped Bi₂Se₃",
                           "(Bi,Sb)₂Te₃/EuS heterostructure"],
        intrinsic_properties=["TI + magnetic order = Chern insulator",
                               "Quantized anomalous Hall effect",
                               "Axion insulator state"],
        typical_synthesis=["MBE", "Bridgman (MnBi₂Te₄)"],
        typical_characterization=["Transport (QAHE)", "ARPES", "MCD"],
        dimensionality=[2, 3],
        known_phases=["Topological Insulator", "Axion Insulator", "Chern Insulator"],
        notes="MnBi₂Te₄ is intrinsic: no doping needed. Key platform for Chern phases."
    ),
    MaterialFamily(
        name="Frustrated magnets (kagome/pyrochlore)",
        example_compounds=["ZnCu₃(OH)₆Cl₂ (Herbertsmithite)",
                           "Dy₂Ti₂O₇ (spin ice)", "Yb₂Ti₂O₇",
                           "Ca₁₀Cr₇O₂₈"],
        intrinsic_properties=["Geometric frustration", "No ordering to T→0",
                               "Emergent gauge fields", "Spinon/vison excitations"],
        typical_synthesis=["Hydrothermal", "Bridgman", "Floating zone"],
        typical_characterization=["Neutron scattering", "μSR", "Specific heat", "NMR"],
        dimensionality=[2, 3],
        known_phases=["Quantum Spin Liquid (candidate)", "Spin Ice"],
        notes="Herbertsmithite: best kagome QSL candidate. Dy₂Ti₂O₇: classical spin ice."
    ),
]


# ============================================================================
# MATERIAL SUGGESTION ENGINE
# ============================================================================

def suggest_materials(coord: PhaseCoordinate,
                      top_n: int = 5) -> List[MaterialCandidate]:
    """
    Given a phase coordinate, suggest the best material families to search in,
    with reasoning and feasibility scores.
    """
    requirements = extract_requirements(coord)
    req_names = {r.name for r in requirements}

    candidates = []

    for family in MATERIAL_FAMILIES:
        # Score how many requirements this family satisfies
        satisfied = []
        missing = []

        for req in requirements:
            # Check if family's intrinsic properties or known phases hint at this req
            family_text = " ".join(
                family.intrinsic_properties +
                family.known_phases +
                [family.notes]
            ).lower()

            # Match requirement to family properties
            matched = False
            if req.name == "2D confinement" and coord.dimensionality in family.dimensionality:
                if any(kw in family_text for kw in ["2d", "monolayer", "heterostructure", "2deg", "van der waals"]):
                    matched = True
            elif req.name == "1D confinement" and 1 in family.dimensionality:
                matched = True
            elif req.name == "Strong spin-orbit coupling":
                if any(el in " ".join(family.example_compounds) for el in ["Bi", "Sb", "Te", "Ir", "W", "Pt", "Pb"]):
                    matched = True
            elif req.name == "Broken time-reversal + SOC":
                if any(kw in family_text for kw in ["magnetic", "chern", "anomalous hall", "mn", "cr"]):
                    matched = True
            elif req.name == "Strong electron correlations in 2D + magnetic field":
                if any(kw in family_text for kw in ["fqh", "landau", "2deg", "moiré", "flat band"]):
                    matched = True
            elif req.name == "Non-Abelian topological order":
                if any(kw in family_text for kw in ["non-abelian", "kitaev", "majorana", "p-wave", "5/2"]):
                    matched = True
            elif req.name == "Superconducting pairing":
                if any(kw in family_text for kw in ["superconduct", "sc", "cooper", "proximitized"]):
                    matched = True
            elif req.name == "Periodic drive":
                if any(kw in family_text for kw in ["floquet", "driven", "qubit", "laser", "microwave"]):
                    matched = True
            elif req.name == "Engineered dissipation":
                if any(kw in family_text for kw in ["cavity", "cold atom", "qubit", "photonic"]):
                    matched = True
            elif req.name == "Fractionalized excitations":
                if any(kw in family_text for kw in ["spinon", "vison", "anyon", "fqh", "qsl", "fractional"]):
                    matched = True
            elif req.name == "Non-Abelian anyons":
                if any(kw in family_text for kw in ["non-abelian", "majorana", "5/2", "kitaev"]):
                    matched = True
            elif req.name == "Bulk energy gap":
                if any(kw in family_text for kw in ["insulator", "gap", "superconduct"]):
                    matched = True
            elif req.name == "Continuous symmetry breaking mechanism":
                if any(kw in family_text for kw in ["magnetic", "ferromagnet", "bec", "superfluid"]):
                    matched = True
            elif req.name == "Discrete symmetry breaking":
                if any(kw in family_text for kw in ["ising", "cdw", "crystal", "antiferromagnet"]):
                    matched = True
            elif req.name == "Topological boundary modes":
                if any(kw in family_text for kw in ["surface state", "edge state", "arpes", "dirac"]):
                    matched = True
            else:
                # Generic match on requirement elements vs family elements
                if req.implies_elements:
                    if any(el in " ".join(family.example_compounds) for el in req.implies_elements):
                        matched = True

            if matched:
                satisfied.append(req.name)
            else:
                missing.append(req.name)

        if not requirements:
            satisfied = ["No special requirements"]
            missing = []

        fraction = len(satisfied) / max(len(requirements), 1)
        if fraction < 0.1:
            continue  # Skip families with no relevant properties

        # Base feasibility from fraction satisfied
        feasibility = fraction * 0.7

        # Bonus for families known to host nearby phases
        for known in family.known_phases:
            if any(known.lower() in kp.lower() for kp in KNOWN_PHASE_COORDINATES.keys()):
                feasibility += 0.05

        # Synthesis difficulty: average req difficulties
        avg_req_difficulty = sum(r.difficulty for r in requirements) / max(len(requirements), 1)
        synthesis_difficulty = avg_req_difficulty

        # Detection difficulty
        detection_difficulty = 0.3
        if coord.anyons != AnyonType.NONE:
            detection_difficulty += 0.3
        if coord.dynamics == DynClass.DRIVEN_FLOQUET:
            detection_difficulty += 0.1
        if coord.long_range_entanglement:
            detection_difficulty += 0.2

        feasibility = min(feasibility, 0.95)
        overall = feasibility * (1 - 0.3 * detection_difficulty) * (1 - 0.2 * synthesis_difficulty)

        # Build suggested experiment
        all_techniques = []
        for req in requirements:
            all_techniques.extend(req.implies_techniques)
        all_conditions = []
        for req in requirements:
            all_conditions.extend(req.implies_conditions)

        unique_techniques = list(dict.fromkeys(all_techniques))[:4]
        unique_conditions = list(dict.fromkeys(all_conditions))[:3]

        experiment = ""
        if unique_techniques:
            experiment += f"Techniques: {', '.join(unique_techniques)}. "
        if unique_conditions:
            experiment += f"Conditions: {', '.join(unique_conditions)}."

        # Timeline
        if overall > 0.6:
            timeline = "1-3 years"
        elif overall > 0.35:
            timeline = "3-7 years"
        else:
            timeline = "decade+"

        # Warning for hard cases
        warning = None
        if coord.anyons == AnyonType.NON_ABELIAN:
            warning = "Non-Abelian anyons are extremely hard to confirm experimentally. Expect false positives."
        elif coord.dynamics == DynClass.DISSIPATIVE:
            warning = "Dissipative topological phases require very precise engineering of loss rates."
        elif fraction < 0.4:
            warning = "This family only partially satisfies requirements — may need significant engineering."

        candidates.append(MaterialCandidate(
            name=family.name,
            formula_or_class=", ".join(family.example_compounds[:3]),
            rationale=f"Satisfies {len(satisfied)}/{len(requirements)} requirements. "
                      f"Known for: {', '.join(family.intrinsic_properties[:3])}.",
            requirements_satisfied=satisfied,
            requirements_missing=missing,
            feasibility_score=feasibility,
            synthesis_difficulty=synthesis_difficulty,
            detection_difficulty=detection_difficulty,
            overall_score=overall,
            suggested_experiment=experiment,
            estimated_timeline=timeline,
            prior_work=family.known_phases,
            warning=warning
        ))

    candidates.sort(key=lambda x: x.overall_score, reverse=True)
    return candidates[:top_n]


# ============================================================================
# REPORT
# ============================================================================

def material_report(coord: PhaseCoordinate, label: str = ""):
    print("\n" + "=" * 70)
    if label:
        print(f"  TARGET PHASE: {label}")
    print(f"  COORDINATE: {coord}")
    print("=" * 70)

    reqs = extract_requirements(coord)
    print(f"\n  Physical requirements ({len(reqs)}):")
    for r in reqs:
        diff_bar = "▓" * int(r.difficulty * 10) + "░" * (10 - int(r.difficulty * 10))
        print(f"    [{diff_bar}] {r.name}")
        print(f"      {r.description}")
        if r.implies_elements:
            print(f"      Key elements: {', '.join(r.implies_elements[:6])}")
        if r.implies_conditions:
            print(f"      Conditions: {', '.join(r.implies_conditions[:2])}")

    candidates = suggest_materials(coord)
    print(f"\n  Top material candidates ({len(candidates)}):")
    for i, c in enumerate(candidates, 1):
        score_bar = "★" * int(c.overall_score * 10) + "·" * (10 - int(c.overall_score * 10))
        print(f"\n  #{i} [{score_bar}] {c.name}")
        print(f"     Examples: {c.formula_or_class}")
        print(f"     {c.rationale}")
        print(f"     Satisfied: {', '.join(c.requirements_satisfied) or 'none'}")
        if c.requirements_missing:
            print(f"     Missing:   {', '.join(c.requirements_missing)}")
        print(f"     Experiment: {c.suggested_experiment}")
        print(f"     Timeline: {c.estimated_timeline}")
        if c.warning:
            print(f"     ⚠ {c.warning}")

    print()


def run_material_suggestions():
    print("=" * 70)
    print("  MATERIAL SUGGESTION ENGINE")
    print("  For known, predicted, and candidate phases")
    print("=" * 70)

    # --- Known phases ---
    print("\n\n▶ KNOWN PHASES — validating material suggestions")
    for name, coord in list(KNOWN_PHASE_COORDINATES.items())[:3]:
        material_report(coord, label=name)

    # --- Predicted phases ---
    print("\n\n▶ THEORETICALLY PREDICTED PHASES — where to look")
    for pred in THEORETICAL_PREDICTIONS[:3]:
        material_report(pred.coordinate, label=pred.name)

    # --- Top candidate gaps ---
    print("\n\n▶ CANDIDATE GAPS — unexplored coordinates")
    all_gaps = find_gaps(KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS)
    top_candidates = sorted(
        [g for g in all_gaps if g.status == "candidate"],
        key=lambda x: x.interest_score, reverse=True
    )[:3]
    for gap in top_candidates:
        material_report(gap.coordinate, label=f"Candidate gap (interest={gap.interest_score:.2f})")


if __name__ == "__main__":
    run_material_suggestions()
