"""
Ultra-Detailed Phase Ontology
Maximum depth: symmetries, order parameters, field theories, experiments, materials
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Callable
from enum import Enum
import json
import numpy as np

# ============================================================================
# SYMMETRY GROUPS (Complete)
# ============================================================================

class ContinuousSymmetry(Enum):
    """Continuous Lie groups"""
    SO2 = "SO(2)"           # 2D rotation
    SO3 = "SO(3)"           # 3D rotation
    U1 = "U(1)"             # Phase rotation / gauge
    SU2 = "SU(2)"           # Spin rotation
    SU3 = "SU(3)"           # Color (QCD)
    E8 = "E(8)"             # Exceptional (string theory)

class DiscreteSymmetry(Enum):
    """Discrete groups"""
    Z2 = "Z(2)"             # Ising
    Z3 = "Z(3)"             # 3-state Potts
    ZN = "Z(N)"             # Cyclic
    D4 = "D(4)"             # Square lattice
    D6 = "D(6)"             # Hexagonal lattice
    S3 = "S(3)"             # Permutation
    C4V = "C4v"             # Point group

class SpaceTimeSymmetry(Enum):
    """Spacetime symmetries"""
    TRANSLATION = "Translation"
    ROTATION = "Rotation"
    INVERSION = "Inversion (P)"
    TIME_REVERSAL = "Time Reversal (T)"
    CHARGE_CONJUGATION = "Charge Conjugation (C)"
    PARITY_TIME = "PT"
    CPT = "CPT"
    GALILEAN = "Galilean"
    LORENTZ = "Lorentz"

class GaugeSymmetry(Enum):
    """Gauge symmetries"""
    U1_EM = "U(1)_EM"          # Electromagnetism
    U1_SC = "U(1)_SC"          # Superconductor
    SU2_WEAK = "SU(2)_weak"    # Weak force
    SU3_COLOR = "SU(3)_color"  # Strong force

# ============================================================================
# ORDER PARAMETERS (Detailed)
# ============================================================================

@dataclass
class OrderParameter:
    """Complete description of order parameter"""
    name: str
    symbol: str                         # ψ, M, ρ, etc.
    physical_meaning: str
    units: str

    # Mathematical properties
    symmetry_representation: str = "scalar"  # "scalar", "vector", "spinor", "tensor"
    complex_valued: bool = False
    dimension: int = 1                  # Vector/tensor dimension

    # Field theory
    field_theory: Optional[str] = None  # "φ⁴", "XY model", "Ginzburg-Landau"
    lagrangian: Optional[str] = None
    effective_action: Optional[str] = None

    # Critical behavior
    critical_exponent_beta: Optional[float] = None   # M ~ t^β
    correlation_length_exponent: Optional[float] = None  # ξ ~ t^(-ν)
    universality_class: Optional[str] = None

    # Experimental measurement
    measurement_technique: List[str] = field(default_factory=list)
    typical_value: Optional[float] = None

@dataclass
class SymmetryBreakingPattern:
    """Detailed symmetry breaking description"""

    # Which symmetry breaks
    original_symmetry: Set
    broken_to: Set

    # Order parameter
    order_parameter: OrderParameter

    # Spontaneous vs explicit
    spontaneous: bool = True
    explicit_breaking_term: Optional[str] = None  # h·M for magnets

    # Critical temperature/coupling
    critical_temperature: Optional[float] = None  # Kelvin
    critical_pressure: Optional[float] = None     # GPa
    critical_field: Optional[float] = None        # Tesla

    # Universality class
    universality_class: Optional[str] = None
    spatial_dimension_upper_critical: Optional[int] = None
    spatial_dimension_lower_critical: Optional[int] = None

    # Goldstone modes
    num_goldstone_modes: int = 0
    goldstone_dispersion: Optional[str] = None  # "ω ~ k" or "ω ~ k²"

    # Defects
    topological_defects: List[str] = field(default_factory=list)

# ============================================================================
# TOPOLOGICAL INVARIANTS (Complete)
# ============================================================================

@dataclass
class TopologicalInvariant:
    """Single topological invariant"""
    name: str
    symbol: str                 # C, ν, W, etc.
    value: float
    physical_meaning: str

    # Mathematical origin
    cohomology_group: Optional[str] = None   # H^n(M, Z)
    homotopy_group: Optional[str] = None     # π_n(M)
    k_theory: Optional[str] = None           # K-theory class

    # Physical consequence
    observable_consequence: List[str] = field(default_factory=list)

    # Stability
    protected_by: Set = field(default_factory=set)
    robust_to_disorder: bool = True
    quantization: str = "exact"  # "exact", "approximate", "none"

@dataclass
class TopologicalProperties:
    """Complete topological characterization"""

    has_topological_order: bool = False
    topological_order_type: Optional[str] = None  # "Z2", "Abelian", "Non-Abelian"

    # Invariants by dimension
    invariants_0d: List[TopologicalInvariant] = field(default_factory=list)
    invariants_1d: List[TopologicalInvariant] = field(default_factory=list)
    invariants_2d: List[TopologicalInvariant] = field(default_factory=list)
    invariants_3d: List[TopologicalInvariant] = field(default_factory=list)

    # Bulk-boundary correspondence
    bulk_gap: bool = False
    edge_states: bool = False
    edge_state_dispersion: Optional[str] = None
    corner_states: bool = False   # Higher-order TI
    hinge_states: bool = False

    # Ground state properties
    ground_state_degeneracy: Optional[int] = None
    ground_state_degeneracy_on_torus: Optional[int] = None
    ground_state_degeneracy_depends_on_genus: bool = False

    # Entanglement
    topological_entanglement_entropy: Optional[float] = None  # γ
    long_range_entanglement: bool = False

    # Excitations
    anyonic_excitations: bool = False
    anyon_types: List[str] = field(default_factory=list)
    fusion_rules: Optional[Dict] = None
    braiding_statistics: Optional[str] = None  # "Abelian", "Non-Abelian"

    # Field theory
    topological_field_theory: Optional[str] = None  # "Chern-Simons", "BF theory"
    modular_data: Optional[Dict] = None              # S and T matrices

# ============================================================================
# QUANTUM PROPERTIES (Detailed)
# ============================================================================

@dataclass
class QuantumCoherence:
    """Quantum coherence properties"""
    coherence_length_zero_temp: Optional[float] = None   # meters
    coherence_length_finite_temp: Optional[Callable] = None  # ξ(T)
    decoherence_time: Optional[float] = None             # seconds
    decoherence_mechanism: List[str] = field(default_factory=list)
    phase_coherence_length: Optional[float] = None
    phase_breaking_time: Optional[float] = None

@dataclass
class EntanglementStructure:
    """Many-body entanglement"""
    area_law: bool = False
    volume_law: bool = False
    logarithmic_correction: bool = False
    long_range_entanglement: bool = False
    short_range_entanglement: bool = True
    entanglement_entropy_formula: Optional[str] = None
    entanglement_spectrum: Optional[str] = None
    tensor_network_structure: Optional[str] = None  # "MPS", "PEPS", "MERA"
    bond_dimension: Optional[int] = None

@dataclass
class QuantumProperties:
    """Complete quantum characterization"""
    superposition: bool = False
    quantum_interference: bool = False
    tunneling: bool = False
    coherence: Optional[QuantumCoherence] = None
    entanglement: Optional[EntanglementStructure] = None
    quantum_phase_transition: bool = False
    qpt_critical_point: Optional[float] = None
    qpt_universality_class: Optional[str] = None
    zero_point_energy: Optional[float] = None
    quantum_fluctuations_suppress_order: bool = False
    berry_phase: Optional[float] = None
    berry_curvature: Optional[str] = None
    quantum_critical_point: bool = False
    quantum_critical_fan: Optional[Tuple[float, float]] = None

# ============================================================================
# DYNAMICAL PROPERTIES (Complete)
# ============================================================================

@dataclass
class TimeEvolution:
    """Time evolution characteristics"""
    hamiltonian: Optional[str] = None
    equations_of_motion: Optional[str] = None
    relaxation_time: Optional[float] = None
    thermalization_time: Optional[float] = None
    recurrence_time: Optional[float] = None
    ergodic: bool = True
    many_body_localized: bool = False
    integrable: bool = False
    chaotic: bool = False
    lyapunov_exponent: Optional[float] = None
    quantum_lyapunov: Optional[float] = None

@dataclass
class DrivenDynamics:
    """Driven system properties"""
    floquet_system: bool = False
    drive_frequency: Optional[float] = None   # Hz
    drive_amplitude: Optional[float] = None
    floquet_hamiltonian: Optional[str] = None
    heating_rate: Optional[float] = None
    prethermal_regime: bool = False
    prethermal_timescale: Optional[float] = None
    floquet_topological_invariant: Optional[int] = None
    anomalous_floquet_phase: bool = False

@dataclass
class DissipativeDynamics:
    """Open system dynamics"""
    lindblad_operators: List[str] = field(default_factory=list)
    jump_operators: List[str] = field(default_factory=list)
    steady_state_unique: bool = True
    steady_state_mixed: bool = True
    dissipative_phase_transition: bool = False
    liouvillian_gap: Optional[float] = None

@dataclass
class DynamicalProperties:
    """Complete dynamical characterization"""
    equilibrium: bool = True
    thermal_equilibrium_temperature: Optional[float] = None
    time_evolution: TimeEvolution = field(default_factory=TimeEvolution)
    driven: Optional[DrivenDynamics] = None
    dissipative: Optional[DissipativeDynamics] = None
    active_matter: bool = False
    activity_parameter: Optional[float] = None
    far_from_equilibrium: bool = False
    non_equilibrium_steady_state: bool = False

# ============================================================================
# EXPERIMENTAL CHARACTERIZATION
# ============================================================================

@dataclass
class ExperimentalTechnique:
    """Specific experimental method"""
    name: str
    measures: str
    resolution: Optional[float] = None
    typical_setup: str = ""

@dataclass
class SpectroscopicSignature:
    """Spectroscopic features"""
    technique: str
    energy_range: Tuple[float, float]  # eV
    characteristic_features: List[str] = field(default_factory=list)

@dataclass
class TransportSignature:
    """Transport measurements"""
    conductivity: Optional[str] = None
    resistivity: Optional[str] = None
    hall_coefficient: Optional[str] = None
    thermal_conductivity: Optional[str] = None
    thermopower: Optional[str] = None

@dataclass
class ExperimentalCharacterization:
    """Complete experimental profile"""
    primary_signatures: List[str] = field(default_factory=list)
    spectroscopy: List[SpectroscopicSignature] = field(default_factory=list)
    transport: Optional[TransportSignature] = None
    xray_diffraction_pattern: Optional[str] = None
    neutron_scattering: Optional[str] = None
    raman_spectrum: Optional[str] = None
    stm_tunneling_spectrum: Optional[str] = None
    afm_features: Optional[str] = None
    specific_heat: Optional[str] = None
    magnetic_susceptibility: Optional[str] = None
    optical_conductivity: Optional[str] = None
    reflectivity: Optional[str] = None
    required_techniques: List[ExperimentalTechnique] = field(default_factory=list)
    sample_purity_required: Optional[str] = None
    sample_size_required: Optional[str] = None
    temperature_control: Optional[Tuple[float, float]] = None

# ============================================================================
# MATERIALS REALIZATION
# ============================================================================

@dataclass
class Material:
    """Specific material realizing the phase"""
    formula: str
    crystal_structure: str
    space_group: str
    temperature_range: Tuple[float, float]   # Kelvin
    pressure_range: Tuple[float, float] = (0, float('inf'))  # GPa
    doping_required: Optional[str] = None
    sample_quality: str = "single crystal"
    typical_defect_density: Optional[float] = None
    lattice_constants: Optional[Tuple] = None  # Angstrom
    band_gap: Optional[float] = None           # eV
    carrier_density: Optional[float] = None    # cm^-3
    synthesis_method: List[str] = field(default_factory=list)
    commercially_available: bool = False
    cost_per_gram: Optional[float] = None      # USD
    discovery_paper: Optional[str] = None
    doi: Optional[str] = None

# ============================================================================
# FIELD THEORY DESCRIPTION
# ============================================================================

@dataclass
class FieldTheory:
    """Field theory description"""
    theory_type: str   # "Landau-Ginzburg", "Chern-Simons", "CFT"
    lagrangian: str
    action: str
    fields: List[str] = field(default_factory=list)
    field_dimensions: Dict[str, float] = field(default_factory=dict)
    couplings: Dict[str, float] = field(default_factory=dict)
    marginal_couplings: List[str] = field(default_factory=list)
    relevant_couplings: List[str] = field(default_factory=list)
    irrelevant_couplings: List[str] = field(default_factory=list)
    beta_functions: Dict[str, str] = field(default_factory=dict)
    fixed_points: List[Dict] = field(default_factory=list)
    symmetries: Set = field(default_factory=set)
    exactly_solvable: bool = False
    solution_method: Optional[str] = None

# ============================================================================
# PHASE TRANSITIONS (Detailed)
# ============================================================================

@dataclass
class PhaseTransition:
    """Complete phase transition description"""
    phase_from: str
    phase_to: str
    order: int   # 1 = first order, 2 = second order
    continuous: bool
    control_parameter: str
    critical_value: float
    universality_class: Optional[str] = None
    critical_exponents: Dict[str, float] = field(default_factory=dict)
    latent_heat: Optional[float] = None
    volume_change: Optional[float] = None
    hysteresis: bool = False
    mechanism: str = ""
    order_parameter_changes: str = ""
    symmetry_changes: str = ""
    critical_slowing_down: bool = False
    relaxation_time_divergence: Optional[str] = None
    experimental_signatures: List[str] = field(default_factory=list)
    phase_coexistence: bool = False
    coexistence_region: Optional[Tuple[float, float]] = None

# ============================================================================
# COMPLETE PHASE DESCRIPTION
# ============================================================================

@dataclass
class Phase:
    """Ultra-detailed phase description"""

    # ========== BASIC INFO ==========
    name: str
    category: str
    dimensionality: int  # 0, 1, 2, 3

    # ========== SYMMETRY ==========
    symmetry_breaking: Optional[SymmetryBreakingPattern] = None
    residual_symmetries: Set = field(default_factory=set)
    emergent_symmetries: Set = field(default_factory=set)

    # ========== TOPOLOGY ==========
    topology: TopologicalProperties = field(default_factory=TopologicalProperties)

    # ========== QUANTUM ==========
    quantum: QuantumProperties = field(default_factory=QuantumProperties)

    # ========== DYNAMICS ==========
    dynamics: DynamicalProperties = field(default_factory=DynamicalProperties)

    # ========== FIELD THEORY ==========
    field_theory: Optional[FieldTheory] = None
    effective_field_theory_low_energy: Optional[FieldTheory] = None

    # ========== EXPERIMENT ==========
    experimental: ExperimentalCharacterization = field(default_factory=ExperimentalCharacterization)

    # ========== MATERIALS ==========
    materials: List[Material] = field(default_factory=list)
    prototype_material: Optional[str] = None

    # ========== THERMODYNAMICS ==========
    temperature_range: Tuple[float, float] = (0, float('inf'))
    pressure_range: Tuple[float, float] = (0, float('inf'))
    free_energy: Optional[str] = None
    entropy: Optional[str] = None

    # ========== PHASE SPACE ==========
    phase_diagram_coordinates: List[str] = field(default_factory=list)
    neighboring_phases: List[str] = field(default_factory=list)
    transitions: List[PhaseTransition] = field(default_factory=list)

    # ========== HISTORY ==========
    discovery_year: Optional[int] = None
    discovered_by: Optional[str] = None
    theoretical_prediction_year: Optional[int] = None
    experimental_confirmation_year: Optional[int] = None

    # ========== REFERENCES ==========
    key_theoretical_papers: List[str] = field(default_factory=list)
    key_experimental_papers: List[str] = field(default_factory=list)
    review_papers: List[str] = field(default_factory=list)
    textbook_references: List[str] = field(default_factory=list)

    # ========== APPLICATIONS ==========
    technological_applications: List[str] = field(default_factory=list)
    potential_applications: List[str] = field(default_factory=list)

    # ========== OPEN QUESTIONS ==========
    open_questions: List[str] = field(default_factory=list)
    controversies: List[str] = field(default_factory=list)


# ============================================================================
# QUERY BUILDER — chainable compound queries
# ============================================================================

class PhaseQuery:
    """Chainable query builder for the registry."""

    def __init__(self, phases: List[Phase]):
        self._phases = list(phases)

    def __iter__(self):
        return iter(self._phases)

    def __len__(self):
        return len(self._phases)

    def __repr__(self):
        names = [p.name for p in self._phases]
        return f"PhaseQuery({len(self._phases)} phases: {names})"

    # --- Basic filters ---
    def topological(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.topology.has_topological_order])

    def non_topological(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if not p.topology.has_topological_order])

    def equilibrium(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.dynamics.equilibrium])

    def non_equilibrium(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if not p.dynamics.equilibrium])

    def driven(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.dynamics.driven is not None])

    def breaks_symmetry(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.symmetry_breaking is not None])

    def no_symmetry_breaking(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.symmetry_breaking is None])

    def dimensionality(self, d: int) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.dimensionality == d])

    def category(self, cat: str) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.category == cat])

    def has_edge_states(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.topology.edge_states])

    def has_anyons(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.topology.anyonic_excitations])

    def mbl(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.dynamics.time_evolution.many_body_localized])

    def berry_phase(self, value: float, tol: float = 1e-9) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases
                           if p.quantum.berry_phase is not None
                           and abs(p.quantum.berry_phase - value) < tol])

    def discovered_after(self, year: int) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases
                           if p.discovery_year is not None and p.discovery_year >= year])

    def discovered_before(self, year: int) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases
                           if p.discovery_year is not None and p.discovery_year <= year])

    def has_material(self, formula: str) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases
                           if any(formula.lower() in m.formula.lower() for m in p.materials)])

    def has_application(self, keyword: str) -> "PhaseQuery":
        kw = keyword.lower()
        return PhaseQuery([p for p in self._phases
                           if any(kw in a.lower() for a in p.technological_applications + p.potential_applications)])

    def bulk_gap(self) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.topology.bulk_gap])

    def name(self, n: str) -> "PhaseQuery":
        return PhaseQuery([p for p in self._phases if p.name == n])

    # --- Output helpers ---
    def names(self) -> List[str]:
        return [p.name for p in self._phases]

    def first(self) -> Optional[Phase]:
        return self._phases[0] if self._phases else None

    def summary(self) -> str:
        lines = []
        for p in self._phases:
            topo = "T" if p.topology.has_topological_order else "-"
            eq   = "E" if p.dynamics.equilibrium else "N"
            sb   = "S" if p.symmetry_breaking else "-"
            lines.append(f"  [{topo}{eq}{sb}] {p.name} ({p.category}, {p.dimensionality}D, {p.discovery_year})")
        header = f"{'[T=Topological, E=Equilibrium, S=Symmetry-broken]':}\n"
        return header + "\n".join(lines)


# ============================================================================
# REGISTRY
# ============================================================================

class PhaseRegistry:
    def __init__(self):
        self.phases: List[Phase] = []
        self.transitions: List[PhaseTransition] = []

    def register(self, phase: Phase):
        self.phases.append(phase)

    def register_transition(self, transition: PhaseTransition):
        self.transitions.append(transition)

    # --- Query entry point ---
    def query(self, **kwargs) -> PhaseQuery:
        """
        Start a chainable query. Filters by exact match on top-level Phase fields.
        Example: registry.query(category="Topological").topological().names()
        """
        results = self.phases
        for key, value in kwargs.items():
            results = [p for p in results if getattr(p, key, None) == value]
        return PhaseQuery(results)

    def all(self) -> PhaseQuery:
        """Return all phases as a chainable query."""
        return PhaseQuery(self.phases)

    # --- Convenience shortcuts (kept for backwards compat) ---
    def query_topology(self, has_topological_order: bool) -> List[Phase]:
        return [p for p in self.phases if p.topology.has_topological_order == has_topological_order]

    def query_equilibrium(self, equilibrium: bool) -> List[Phase]:
        return [p for p in self.phases if p.dynamics.equilibrium == equilibrium]

    def query_driven(self) -> List[Phase]:
        return [p for p in self.phases if p.dynamics.driven is not None]

    def query_berry_phase(self, value: float) -> List[Phase]:
        return [p for p in self.phases if p.quantum.berry_phase == value]

    def query_dimensionality(self, d: int) -> List[Phase]:
        return [p for p in self.phases if p.dimensionality == d]

    def query_breaks_symmetry(self) -> List[Phase]:
        return [p for p in self.phases if p.symmetry_breaking is not None]

    # --- Transition graph ---
    def neighbors(self, phase_name: str) -> List[str]:
        """Return names of phases reachable via a transition from phase_name."""
        seen = set()
        result = []
        for name in (
            [t.phase_to   for t in self.transitions if t.phase_from == phase_name] +
            [t.phase_from for t in self.transitions if t.phase_to   == phase_name]
        ):
            if name not in seen:
                seen.add(name)
                result.append(name)
        return result

    def get_transition(self, phase_from: str, phase_to: str) -> Optional[PhaseTransition]:
        for t in self.transitions:
            if (t.phase_from == phase_from and t.phase_to == phase_to) or \
               (t.phase_from == phase_to and t.phase_to == phase_from):
                return t
        return None

    # --- Stats ---
    def stats(self) -> Dict:
        return {
            "total_phases": len(self.phases),
            "total_transitions": len(self.transitions),
            "categories": list({p.category for p in self.phases}),
            "topological": len([p for p in self.phases if p.topology.has_topological_order]),
            "non_equilibrium": len([p for p in self.phases if not p.dynamics.equilibrium]),
            "total_materials": sum(len(p.materials) for p in self.phases),
            "year_range": (
                min(p.discovery_year for p in self.phases if p.discovery_year),
                max(p.discovery_year for p in self.phases if p.discovery_year)
            )
        }

    # --- Persistence ---
    def to_json(self, path: str):
        """Export registry summary to JSON."""
        def serialize(obj):
            """json.dump default= handler for non-standard types."""
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, set):
                return [serialize(i) for i in obj]
            if callable(obj):
                return "<function>"
            raise TypeError(f"Not serializable: {type(obj)}")

        def sanitize(obj):
            """
            Pre-walk the data structure so float('inf') becomes the string
            "inf" before json.dump sees it.  The default= hook never fires
            for plain floats, so this is the only reliable fix.
            """
            if isinstance(obj, float):
                if obj == float('inf'):
                    return "inf"
                if obj == float('-inf'):
                    return "-inf"
                return obj
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [sanitize(v) for v in obj]
            return obj

        data = {
            "phases": [],
            "transitions": []
        }

        for p in self.phases:
            entry = {
                "name": p.name,
                "category": p.category,
                "dimensionality": p.dimensionality,
                "discovery_year": p.discovery_year,
                "theoretical_prediction_year": p.theoretical_prediction_year,
                "experimental_confirmation_year": p.experimental_confirmation_year,
                "discovered_by": p.discovered_by,
                "topology": {
                    "has_topological_order": p.topology.has_topological_order,
                    "topological_order_type": p.topology.topological_order_type,
                    "edge_states": p.topology.edge_states,
                    "anyonic_excitations": p.topology.anyonic_excitations,
                    "invariants": [
                        {"name": i.name, "symbol": i.symbol, "value": i.value,
                         "meaning": i.physical_meaning}
                        for i in (p.topology.invariants_0d + p.topology.invariants_1d +
                                  p.topology.invariants_2d + p.topology.invariants_3d)
                    ]
                },
                "dynamics": {
                    "equilibrium": p.dynamics.equilibrium,
                    "driven": p.dynamics.driven is not None,
                    "mbl": p.dynamics.time_evolution.many_body_localized,
                },
                "symmetry_breaking": {
                    "order_parameter": p.symmetry_breaking.order_parameter.name,
                    "symbol": p.symmetry_breaking.order_parameter.symbol,
                    "universality_class": p.symmetry_breaking.universality_class,
                    "critical_temperature": p.symmetry_breaking.critical_temperature,
                    "goldstone_modes": p.symmetry_breaking.num_goldstone_modes,
                    "defects": p.symmetry_breaking.topological_defects,
                } if p.symmetry_breaking else None,
                "quantum": {
                    "berry_phase": p.quantum.berry_phase,
                    "berry_curvature": p.quantum.berry_curvature,
                },
                "materials": [
                    {"formula": m.formula, "structure": m.crystal_structure,
                     "temp_range": list(m.temperature_range),
                     "band_gap_eV": m.band_gap, "cost_per_gram_usd": m.cost_per_gram,
                     "commercially_available": m.commercially_available}
                    for m in p.materials
                ],
                "technological_applications": p.technological_applications,
                "potential_applications": p.potential_applications,
                "open_questions": p.open_questions,
                "controversies": p.controversies,
                "key_theoretical_papers": p.key_theoretical_papers,
                "key_experimental_papers": p.key_experimental_papers,
                "review_papers": p.review_papers,
                "neighboring_phases": p.neighboring_phases,
            }
            data["phases"].append(entry)

        for t in self.transitions:
            data["transitions"].append({
                "from": t.phase_from,
                "to": t.phase_to,
                "order": t.order,
                "control_parameter": t.control_parameter,
                "critical_value": t.critical_value if t.critical_value != float('inf') else "inf",
                "universality_class": t.universality_class,
                "mechanism": t.mechanism,
            })

        with open(path, "w") as f:
            json.dump(sanitize(data), f, indent=2, default=serialize)
        print(f"Saved {len(self.phases)} phases and {len(self.transitions)} transitions to {path}")
