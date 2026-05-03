"""
pipeline.py — Materials Project Integration Pipeline

Full discovery loop:
  PhaseCoordinate → requirements → MP API query → topological DB check
  → score specific compounds → ranked experimental predictions

Setup:
  1. pip install pymatgen mp-api python-dotenv
  2. cp .env.example .env
  3. Add your MP_API_KEY to .env
  4. python pipeline.py
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

from dotenv import load_dotenv

# Load API key from .env — never hardcoded
load_dotenv()
MP_API_KEY = os.getenv("MP_API_KEY")
TOPO_DB_PATH = os.getenv("TOPO_DB_PATH", "./data/topological_materials.json")

from akasha_phase_engine.discovery import (
    PhaseCoordinate, TopoType, SymBreaking, DynClass, AnyonType,
    KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS, find_gaps
)
from akasha_phase_engine.materials import extract_requirements


# ============================================================================
# MATERIALS PROJECT QUERY
# ============================================================================

@dataclass
class MPMaterial:
    """A real material from the Materials Project database."""
    mp_id: str                          # e.g. "mp-2815"
    formula: str                        # e.g. "Bi2Se3"
    formula_pretty: str                 # e.g. "Bi₂Se₃"
    crystal_system: str
    space_group: str
    space_group_number: int
    band_gap: float                     # eV, from DFT
    formation_energy: float             # eV/atom
    energy_above_hull: float            # eV/atom — stability
    is_stable: bool
    elements: List[str]
    nsites: int
    volume: float                       # Å³
    density: float                      # g/cm³
    # Topological data (from Topological Materials DB, if available)
    z2_invariant: Optional[int] = None
    chern_number: Optional[int] = None
    topological_class: Optional[str] = None
    # Our scoring
    coordinate_match_score: float = 0.0
    reasoning: str = ""


def query_materials_project(requirements, coord: PhaseCoordinate) -> List[MPMaterial]:
    """
    Query the Materials Project API for materials matching phase requirements.
    Returns list of MPMaterial objects.

    Requires: pip install mp-api pymatgen
    Requires: MP_API_KEY in .env
    """
    if not MP_API_KEY:
        raise EnvironmentError(
            "MP_API_KEY not found. Copy .env.example to .env and add your key.\n"
            "Get a free key at: https://materialsproject.org/api"
        )

    try:
        from mp_api.client import MPRester
    except ImportError:
        raise ImportError(
            "mp-api not installed. Run: pip install mp-api pymatgen python-dotenv"
        )

    # Build query filters from requirements
    required_elements = []
    band_gap_range = None
    crystal_systems = None

    for req in requirements:
        required_elements.extend(req.implies_elements)

        if req.name == "Bulk energy gap":
            band_gap_range = (0.01, 5.0)  # eV — has a gap

        if req.name == "Strong spin-orbit coupling":
            # Heavy elements only
            required_elements.extend(["Bi", "Sb", "Te", "Se", "Ir", "Pt", "W", "Ta", "Pb"])

        if req.name == "2D confinement":
            crystal_systems = ["trigonal", "hexagonal", "tetragonal"]

    # Deduplicate elements
    required_elements = list(set(required_elements))

    results = []

    with MPRester(MP_API_KEY) as mpr:
        # Query by element inclusion + stability + band gap
        query_kwargs = {
            "fields": [
                "material_id", "formula_pretty", "symmetry",
                "band_gap", "formation_energy_per_atom",
                "energy_above_hull", "is_stable",
                "elements", "nsites", "volume", "density"
            ],
            "energy_above_hull": (0, 0.1),   # Stable or nearly stable
        }

        if band_gap_range:
            query_kwargs["band_gap"] = band_gap_range

        if required_elements:
            # Query materials containing ANY of the required heavy elements
            # (intersect with element lists from requirements)
            query_kwargs["elements"] = required_elements[:5]  # MP API limit

        docs = mpr.materials.summary.search(**query_kwargs)

        for doc in docs[:50]:  # Cap at 50 results
            sym = doc.symmetry
            mat = MPMaterial(
                mp_id=doc.material_id,
                formula=str(doc.formula_pretty).replace(" ", ""),
                formula_pretty=doc.formula_pretty,
                crystal_system=sym.crystal_system.value if sym else "unknown",
                space_group=sym.symbol if sym else "unknown",
                space_group_number=sym.number if sym else 0,
                band_gap=doc.band_gap or 0.0,
                formation_energy=doc.formation_energy_per_atom or 0.0,
                energy_above_hull=doc.energy_above_hull or 0.0,
                is_stable=doc.is_stable or False,
                elements=[str(e) for e in (doc.elements or [])],
                nsites=doc.nsites or 0,
                volume=doc.volume or 0.0,
                density=doc.density or 0.0,
            )
            results.append(mat)

    return results


# ============================================================================
# TOPOLOGICAL MATERIALS DATABASE
# ============================================================================

def load_topo_db() -> Dict:
    """
    Load the Topological Materials Database.
    Download from: https://topologicalquantumchemistry.org/#/topomat
    or: https://www.materialscloud.org/discover/topologicalinsulators

    Expected JSON format:
    {
      "Bi2Se3": {"z2": 1, "class": "TI", "gap": 0.3},
      ...
    }
    """
    path = Path(TOPO_DB_PATH)
    if not path.exists():
        print(f"  ⚠ Topological DB not found at {TOPO_DB_PATH}")
        print("    Download from: https://topologicalquantumchemistry.org")
        print("    Save to: ./data/topological_materials.json")
        return {}

    with open(path) as f:
        return json.load(f)


def enrich_with_topology(materials: List[MPMaterial], topo_db: Dict) -> List[MPMaterial]:
    """Cross-reference MP materials with topological classification database."""
    for mat in materials:
        # Try to match by formula (simple version — real version needs structure matching)
        formula_clean = mat.formula.replace("₂", "2").replace("₃", "3")
        if formula_clean in topo_db:
            entry = topo_db[formula_clean]
            mat.z2_invariant = entry.get("z2")
            mat.chern_number = entry.get("chern")
            mat.topological_class = entry.get("class")
    return materials


# ============================================================================
# SCORING
# ============================================================================

def score_material(mat: MPMaterial, coord: PhaseCoordinate) -> float:
    """
    Score a specific material against a target phase coordinate.
    Returns 0-1 score.
    """
    score = 0.0
    reasons = []

    # Stability — prefer thermodynamically stable
    if mat.is_stable:
        score += 0.15
        reasons.append("Thermodynamically stable")
    elif mat.energy_above_hull < 0.05:
        score += 0.08
        reasons.append("Nearly stable (hull < 50 meV)")

    # Band gap match
    if coord.topology != TopoType.NONE and coord.bulk_gap:
        if 0.05 < mat.band_gap < 1.0:
            score += 0.20
            reasons.append(f"Topological gap range: {mat.band_gap:.2f} eV")
        elif mat.band_gap > 1.0:
            score += 0.05

    elif not coord.bulk_gap:
        if mat.band_gap < 0.05:
            score += 0.15
            reasons.append("Semimetallic (no gap, as required)")

    # Topological classification match
    if mat.topological_class:
        if coord.topological == TopoType.Z2 and "TI" in mat.topological_class:
            score += 0.30
            reasons.append(f"Topological DB: {mat.topological_class}")
        elif coord.topological == TopoType.CHERN and "Weyl" in mat.topological_class:
            score += 0.30
            reasons.append(f"Topological DB: {mat.topological_class}")
        elif coord.topological == TopoType.NONE and "trivial" in mat.topological_class.lower():
            score += 0.10

    # Z₂ invariant match
    if mat.z2_invariant is not None:
        if coord.topological == TopoType.Z2 and mat.z2_invariant == 1:
            score += 0.20
            reasons.append("Z₂ = 1 (non-trivial)")
        elif coord.topological == TopoType.NONE and mat.z2_invariant == 0:
            score += 0.05

    # Heavy elements → SOC
    heavy_elements = {"Bi", "Sb", "Te", "Ir", "Pt", "W", "Ta", "Pb", "Hg", "Tl"}
    mat_heavy = set(mat.elements) & heavy_elements
    if coord.topological != TopoType.NONE and mat_heavy:
        score += 0.10 * min(len(mat_heavy), 2)
        reasons.append(f"Heavy elements (SOC): {mat_heavy}")

    # Dimensionality proxy from crystal system
    if coord.dimensionality == 2:
        if mat.crystal_system in ("trigonal", "hexagonal"):
            score += 0.10
            reasons.append("Layered structure (2D candidate)")

    mat.coordinate_match_score = min(score, 1.0)
    mat.reasoning = "; ".join(reasons)
    return mat.coordinate_match_score


# ============================================================================
# EXPERIMENTAL PREDICTION OUTPUT
# ============================================================================

@dataclass
class ExperimentalPrediction:
    """A concrete, actionable experimental prediction."""
    target_coordinate: PhaseCoordinate
    target_label: str
    material: MPMaterial
    prediction: str
    experiment: str
    why_unexplored: str
    estimated_difficulty: str
    estimated_timeline: str
    references_to_read: List[str] = field(default_factory=list)


def generate_predictions(coord: PhaseCoordinate,
                         label: str,
                         materials: List[MPMaterial]) -> List[ExperimentalPrediction]:
    """Turn scored materials into concrete experimental predictions."""
    predictions = []

    for mat in materials:
        if mat.coordinate_match_score < 0.2:
            continue

        # What's the experiment?
        experiments = []
        if coord.topological != TopoType.NONE:
            experiments.append("ARPES to map surface states")
        if coord.bulk_gap:
            experiments.append("Tunneling spectroscopy for gap measurement")
        if coord.dynamics == DynClass.DRIVEN_FLOQUET:
            experiments.append("Pump-probe or Floquet-ARPES with periodic laser drive")
        if coord.anyons != AnyonType.NONE:
            experiments.append("Shot noise or interferometry for fractional charge")

        experiment = "; ".join(experiments) if experiments else "Transport + spectroscopy"

        # Why unexplored?
        if mat.topological_class is None:
            why = "Not yet classified in topological databases — unexplored territory"
        elif coord.dynamics == DynClass.DRIVEN_FLOQUET:
            why = "Equilibrium phase known but driven/Floquet regime not studied"
        else:
            why = f"Coordinate gap: {label} not experimentally confirmed in this material"

        # Difficulty
        if mat.coordinate_match_score > 0.6:
            difficulty = "Moderate — good material candidate, standard techniques"
            timeline = "1-3 years"
        elif mat.coordinate_match_score > 0.4:
            difficulty = "Hard — requires optimization of synthesis and measurement"
            timeline = "3-5 years"
        else:
            difficulty = "Very hard — multiple unsolved problems"
            timeline = "5-10 years"

        predictions.append(ExperimentalPrediction(
            target_coordinate=coord,
            target_label=label,
            material=mat,
            prediction=f"{mat.formula_pretty} (MP: {mat.mp_id}) is a candidate for {label}",
            experiment=experiment,
            why_unexplored=why,
            estimated_difficulty=difficulty,
            estimated_timeline=timeline,
        ))

    return sorted(predictions, key=lambda x: x.material.coordinate_match_score, reverse=True)


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline(target_coords: Optional[List[tuple]] = None):
    """
    Full discovery pipeline.

    Args:
        target_coords: List of (label, PhaseCoordinate) tuples.
                       If None, uses top candidate gaps from discovery.py
    """
    print("=" * 70)
    print("  PHASE DISCOVERY PIPELINE")
    print("  Materials Project + Topological DB Integration")
    print("=" * 70)

    # Check API key
    if not MP_API_KEY:
        print("\n  ⚠  NO API KEY FOUND")
        print("  To activate live Materials Project queries:")
        print("  1. Get free key at: https://materialsproject.org/api")
        print("  2. cp .env.example .env")
        print("  3. Set MP_API_KEY=your_key in .env")
        print("  4. pip install mp-api pymatgen python-dotenv")
        print("\n  Running in DEMO MODE — showing pipeline structure only.")
        print("=" * 70)
        _demo_mode()
        return

    # Load topological database
    print("\n  Loading topological materials database...")
    topo_db = load_topo_db()
    print(f"  Loaded {len(topo_db)} entries from topological DB")

    # Get target coordinates
    if target_coords is None:
        print("\n  Finding top candidate gaps from discovery engine...")
        all_gaps = find_gaps(KNOWN_PHASE_COORDINATES, THEORETICAL_PREDICTIONS)
        candidates = sorted(
            [g for g in all_gaps if g.status in ("candidate", "predicted")],
            key=lambda x: x.interest_score, reverse=True
        )[:5]
        target_coords = [
            (g.prediction.name if g.prediction else f"Candidate gap {i+1}",
             g.coordinate)
            for i, g in enumerate(candidates)
        ]

    all_predictions = []

    for label, coord in target_coords:
        print(f"\n{'─'*70}")
        print(f"  TARGET: {label}")
        print(f"  COORDINATE: {coord}")
        print(f"{'─'*70}")

        # Extract requirements
        reqs = extract_requirements(coord)
        print(f"\n  Requirements: {[r.name for r in reqs]}")

        # Query Materials Project
        print(f"\n  Querying Materials Project API...")
        try:
            materials = query_materials_project(reqs, coord)
            print(f"  Found {len(materials)} candidate materials")
        except Exception as e:
            print(f"  ✗ API query failed: {e}")
            continue

        # Enrich with topology
        print(f"  Cross-referencing topological database...")
        materials = enrich_with_topology(materials, topo_db)

        # Score
        print(f"  Scoring materials against coordinate...")
        for mat in materials:
            score_material(mat, coord)
        materials.sort(key=lambda x: x.coordinate_match_score, reverse=True)

        # Generate predictions
        predictions = generate_predictions(coord, label, materials)
        all_predictions.extend(predictions)

        # Print top results
        print(f"\n  Top material candidates:")
        for i, mat in enumerate(materials[:5], 1):
            score_bar = "★" * int(mat.coordinate_match_score * 10)
            score_bar += "·" * (10 - len(score_bar))
            topo_str = f" [{mat.topological_class}]" if mat.topological_class else ""
            print(f"\n  #{i} [{score_bar}] {mat.formula_pretty}{topo_str}")
            print(f"      MP ID: {mat.mp_id}")
            print(f"      Structure: {mat.crystal_system}, {mat.space_group}")
            print(f"      Band gap: {mat.band_gap:.3f} eV")
            print(f"      Stability: {'✓ stable' if mat.is_stable else f'Δ = {mat.energy_above_hull:.3f} eV/atom'}")
            print(f"      Score: {mat.coordinate_match_score:.2f} — {mat.reasoning}")

    # Final predictions report
    if all_predictions:
        print(f"\n{'═'*70}")
        print(f"  EXPERIMENTAL PREDICTIONS ({len(all_predictions)} generated)")
        print(f"{'═'*70}")
        for i, pred in enumerate(all_predictions[:10], 1):
            print(f"\n  #{i} {pred.prediction}")
            print(f"     Experiment: {pred.experiment}")
            print(f"     Why unexplored: {pred.why_unexplored}")
            print(f"     Difficulty: {pred.estimated_difficulty}")
            print(f"     Timeline: {pred.estimated_timeline}")

    print("\n" + "=" * 70)


def _demo_mode():
    """Show pipeline structure without API key."""
    print("\n  PIPELINE STRUCTURE (demo — no API key)")
    print("─" * 70)

    example_coord = PhaseCoordinate(
        dimensionality=3,
        symmetry_breaking=SymBreaking.NONE,
        topological=TopoType.Z2,
        dynamics=DynClass.EQUILIBRIUM,
        anyons=AnyonType.NONE,
        edge_states=True,
        bulk_gap=True,
        long_range_entanglement=False
    )

    print(f"\n  Example target: Topological Insulator")
    print(f"  Coordinate: {example_coord}")

    reqs = extract_requirements(example_coord)
    print(f"\n  Physical requirements extracted:")
    for r in reqs:
        print(f"    • {r.name}: {', '.join(r.implies_elements[:4]) or 'see conditions'}")

    print(f"\n  With API key, would query Materials Project for:")
    print(f"    elements: {list(set(e for r in reqs for e in r.implies_elements))[:8]}")
    print(f"    band_gap: (0.01, 1.0) eV")
    print(f"    energy_above_hull: (0, 0.1) eV/atom")

    print(f"\n  Would cross-reference with:")
    print(f"    Topological Materials Database (~400,000 classified materials)")
    print(f"    Filter: Z₂ = 1, non-trivial")

    print(f"\n  Would output ranked list like:")
    print(f"    #1 Bi₂Se₃ (mp-541837) — Z₂=1, gap=0.30 eV, stable ★★★★★★★★")
    print(f"    #2 Bi₂Te₃ (mp-19717)  — Z₂=1, gap=0.15 eV, stable ★★★★★★★·")
    print(f"    #3 SnTe   (mp-1883)   — Z₂=0, gap=0.18 eV, TCM   ★★★★★·····")
    print(f"    ...")

    print(f"\n  Add your API key to .env to activate.")


if __name__ == "__main__":
    run_pipeline()
