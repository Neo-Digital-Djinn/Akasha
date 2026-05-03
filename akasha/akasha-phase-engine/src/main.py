#!/usr/bin/env python3
"""
akasha-phase-engine  (pipeline adapter)
========================================
Reads a domain pack directory, estimates the current phase state
of the knowledge in that domain, and emits structured diagnostics.

Aligned with: REQ-013, Axiom 2 (Discoverability), Axiom 5 (Traceability).

Usage:
    python3 src/main.py <domain_path>

    domain_path — path to an akasha-domain-* repo root
                  (must contain a packs/ subdirectory with *.yaml files)
"""

from __future__ import annotations

import sys
import yaml
from pathlib import Path

PHASES = ["seed", "formation", "expansion", "complexity", "criticality", "renewal"]


def load_domain(domain_path: Path) -> dict:
    """Load all YAML packs from domain_path/packs/."""
    packs = {}
    for pack_file in sorted(domain_path.glob("packs/*.yaml")):
        try:
            data = yaml.safe_load(pack_file.read_text(encoding="utf-8")) or {}
            packs[pack_file.stem] = data
        except Exception as exc:
            print(f"[phase] warn: could not load {pack_file.name}: {exc}")
    return packs


def extract_concepts(packs: dict) -> list[str]:
    """Flatten all list-valued fields from all packs into a concept list."""
    concepts: list[str] = []
    for pack_data in packs.values():
        for value in pack_data.values():
            if isinstance(value, list):
                concepts.extend(str(v) for v in value if v)
    return concepts


def score_domain(concepts: list[str]) -> tuple[int, int]:
    """
    Heuristic phase scoring.
    entropy   — proxy for conceptual complexity (0–100)
    stability — inverse proxy, bounded away from 0
    """
    n = len(concepts)
    entropy = min(100, n * 3)
    stability = max(5, 100 - entropy // 2)
    return entropy, stability


def current_phase(concepts: list[str]) -> tuple[str, str]:
    """Map concept count to a phase index and return current + likely-next."""
    idx = min(len(PHASES) - 1, len(concepts) // 10)
    current = PHASES[idx]
    next_phase = PHASES[min(len(PHASES) - 1, idx + 1)]
    return current, next_phase


def run(domain_path: Path) -> None:
    print("[phase] akasha-phase-engine starting")
    print(f"[phase] loading domain: {domain_path.name}")

    if not domain_path.exists():
        print(f"[phase] ERROR: domain path not found: {domain_path}")
        sys.exit(1)

    packs = load_domain(domain_path)
    if not packs:
        print(f"[phase] ERROR: no packs found in {domain_path}/packs/")
        sys.exit(1)

    concepts = extract_concepts(packs)
    if not concepts:
        print("[phase] ERROR: no concepts extracted from packs")
        sys.exit(1)

    entropy, stability = score_domain(concepts)
    cur, nxt = current_phase(concepts)

    print(f"[phase] domain:        {domain_path.name}")
    print(f"[phase] packs loaded:  {len(packs)}")
    print(f"[phase] concepts:      {len(concepts)}")
    print(f"[phase] current phase: {cur}")
    print(f"[phase] likely next:   {nxt}")
    print(f"[phase] entropy:       {entropy}")
    print(f"[phase] stability:     {stability}")
    print(f"[phase] sample:        {concepts[0]}")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    domain_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else here.parent.parent.parent / "akasha-domain-physics"
    )
    run(domain_path)
