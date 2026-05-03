#!/usr/bin/env python3
"""
akasha-analogy-engine
Reads ALL domain packs and emits a structurally grounded analogy anchored
to the concept most resonant with the pipeline input.
Aligned with: REQ-007, Axiom 2 (Discoverability), Axiom 5 (Traceability).
"""

from __future__ import annotations

import sys
import random
import yaml
from pathlib import Path


ANALOGY_TEMPLATES = [
    ("{concept} exhibits a phase transition — a boundary where continuous change produces discontinuous behavior.",
     "threshold → discontinuity"),
    ("{concept} acts as an attractor — dynamics of surrounding structure tend toward it under sufficient constraint.",
     "attractor → convergence"),
    ("{concept} functions as a signal propagating through a medium, carrying structured difference across a boundary.",
     "signal → propagation"),
    ("{concept} shows emergence — higher-order coherence arising from lower-level interactions without central control.",
     "emergence → self-organization"),
    ("{concept} is a coupling node — changes here propagate bidirectionally, creating mutual dependency.",
     "coupling → bilateral influence"),
    ("{concept} behaves as a constraint — it limits the space of possible states without prescribing which is reached.",
     "constraint → boundary-shaping"),
    ("{concept} resembles resonance — its response amplifies when driving frequency aligns with intrinsic structure.",
     "resonance → selective amplification"),
    ("{concept} operates as a gradient — the difference it embodies drives directional flow toward equilibrium.",
     "gradient → directed flow"),
    ("{concept} exhibits hysteresis — history of traversal determines which attractor is reached, not current state alone.",
     "hysteresis → path-dependence"),
    ("{concept} is a symmetry-breaking event — before it, outcomes are equivalent; after, structure becomes specific.",
     "symmetry-breaking → differentiation"),
]


def load_all_domains(root: Path) -> dict[str, list[str]]:
    """Load all concepts from all akasha-domain-* packs under root."""
    domain_concepts: dict[str, list[str]] = {}
    for pack_dir in sorted(root.glob("akasha/akasha-domain-*/packs/*.yaml")):
        domain = pack_dir.parent.parent.name.replace("akasha-domain-", "")
        try:
            data = yaml.safe_load(pack_dir.read_text(encoding="utf-8")) or {}
            concepts = data.get("examples", []) + data.get("structures", [])
            domain_concepts.setdefault(domain, []).extend(c for c in concepts if c)
        except Exception:
            pass
    return domain_concepts


def load_single_domain(domain_path: Path) -> list[str]:
    concepts: list[str] = []
    for pack in domain_path.glob("packs/*.yaml"):
        try:
            data = yaml.safe_load(pack.read_text(encoding="utf-8")) or {}
            concepts.extend(data.get("examples", []) + data.get("structures", []))
        except Exception:
            pass
    return [c for c in concepts if c]


def pick_best_concept(domain_concepts: dict[str, list[str]], seed: str) -> tuple[str, str]:
    """
    Score every concept across all domains by token overlap with seed.
    Return (best_concept, its_domain). Falls back to first concept in first domain.
    """
    if not seed:
        # No seed — pick first concept from first domain
        for domain, concepts in domain_concepts.items():
            if concepts:
                return concepts[0], domain
        return "unknown", "unknown"

    seed_tokens = set(seed.lower().replace("_", " ").split())
    stops = {"a", "an", "the", "of", "in", "to", "and", "or", "with", "for"}
    seed_tokens -= stops

    best_concept, best_domain, best_score = "", "", -1
    for domain, concepts in domain_concepts.items():
        for c in concepts:
            c_tokens = set(c.lower().replace("_", " ").split()) - stops
            score = len(c_tokens & seed_tokens)
            if score > best_score:
                best_score, best_concept, best_domain = score, c, domain

    if best_score == 0:
        # No token match — pick deterministically from the domain with most concepts
        biggest = max(domain_concepts, key=lambda d: len(domain_concepts[d]))
        return domain_concepts[biggest][0], biggest

    return best_concept, best_domain


def pick_template(concept: str, seed: str) -> tuple[str, str]:
    rng = random.Random(concept + seed)
    template, label = rng.choice(ANALOGY_TEMPLATES)
    return template.format(concept=concept), label


def run(root: Path, seed: str = "") -> None:
    print("[analogy] akasha-analogy-engine starting")

    domain_concepts = load_all_domains(root)
    total = sum(len(v) for v in domain_concepts.values())

    if not domain_concepts or total == 0:
        print("[analogy] ERROR: no concepts found in any domain pack")
        sys.exit(1)

    concept, domain = pick_best_concept(domain_concepts, seed)
    analogy_text, structural_label = pick_template(concept, seed)

    print(f"[analogy] domains scanned:  {len(domain_concepts)} ({total} concepts total)")
    if seed:
        print(f"[analogy] seed concept:     {seed}")
    print(f"[analogy] anchor domain:    {domain}")
    print(f"[analogy] anchor concept:   {concept}")
    print(f"[analogy] structural type:  {structural_label}")
    print(f"[analogy] analogy:")
    print(f"           {analogy_text}")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    # When called standalone, root is 3 levels up from src/
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent.parent
    seed = sys.argv[2] if len(sys.argv) > 2 else ""

    if not root.exists():
        print(f"[analogy] ERROR: root not found: {root}")
        sys.exit(1)

    run(root, seed=seed)
