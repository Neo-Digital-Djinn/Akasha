#!/usr/bin/env python3
"""
akasha-edge-generator
Generates candidate edges between concepts across domain packs.
For each pair of structures from different domains, proposes a relation
from the Akasha Table relation classes, with confidence and rationale.
Aligned with: REQ-008, Axiom 2 (Discoverability), Axiom 5 (Traceability).
"""

from __future__ import annotations

import sys
import random
import yaml
from pathlib import Path


# Relation classes from the Akasha Table (AKASHA_TABLE.md)
RELATION_CLASSES = [
    ("couples_to",        "Mutual linkage — both structures influence each other's state."),
    ("transitions_to",    "State change pathway — one structure shifts into the other under pressure."),
    ("resonates_with",    "Amplified response due to structural or temporal alignment."),
    ("constrains",        "Limiting influence — one structure sets a boundary on the other."),
    ("emerges_from",      "Higher-order structure arising from the lower-level one."),
    ("tends_toward",      "Asymptotic movement — dynamics of one pull toward the other."),
    ("signals",           "Transmissible difference — one structure carries information to the other."),
    ("propagates_through","One structure acts as substrate or medium for the other."),
]

# Confidence scoring heuristics
DOMAIN_AFFINITY: dict[tuple[str, str], float] = {
    ("economics", "physics"):      0.72,
    ("physics",   "economics"):    0.72,
    ("economics", "ecology"):      0.68,
    ("ecology",   "economics"):    0.68,
    ("physics",   "neuroscience"): 0.65,
    ("neuroscience", "physics"):   0.65,
    ("neuroscience", "music"):     0.61,
    ("music",     "neuroscience"): 0.61,
    ("music",     "physics"):      0.58,
    ("physics",   "music"):        0.58,
    ("ecology",   "neuroscience"): 0.55,
}


def load_domain_packs(root: Path) -> dict[str, list[str]]:
    domains: dict[str, list[str]] = {}
    for pack_dir in sorted(root.glob("akasha/akasha-domain-*/packs/*.yaml")):
        domain = pack_dir.parent.parent.name.replace("akasha-domain-", "")
        try:
            data = yaml.safe_load(pack_dir.read_text(encoding="utf-8")) or {}
            structures = data.get("structures", []) + data.get("examples", [])
            domains.setdefault(domain, []).extend(s for s in structures if s)
        except Exception:
            pass
    return domains


def generate_edges(domains: dict[str, list[str]], seed_concept: str = "", n: int = 5) -> list[dict]:
    domain_names = sorted(domains.keys())
    if len(domain_names) < 2:
        return []

    edges = []
    rng = random.Random(seed_concept or 42)

    # If a seed concept is given, try to anchor one side of edges to relevant structures
    candidate_pairs: list[tuple[str, str, str, str]] = []
    for i, d1 in enumerate(domain_names):
        for d2 in domain_names[i + 1:]:
            for s1 in domains[d1]:
                for s2 in domains[d2]:
                    candidate_pairs.append((d1, s1, d2, s2))

    if seed_concept:
        # Prefer pairs where a structure shares tokens with the seed
        seed_tokens = set(seed_concept.lower().replace("_", " ").split())
        def relevance(pair):
            tokens = set((pair[1] + " " + pair[3]).lower().replace("_", " ").split())
            return len(tokens & seed_tokens)
        candidate_pairs.sort(key=relevance, reverse=True)

    # Sample deterministically
    sampled = candidate_pairs[:max(n * 8, 40)]
    rng.shuffle(sampled)
    selected = sampled[:n]

    for d1, s1, d2, s2 in selected:
        relation, rationale = rng.choice(RELATION_CLASSES)
        affinity = DOMAIN_AFFINITY.get((d1, d2), DOMAIN_AFFINITY.get((d2, d1), 0.50))
        # Small jitter so identical relations have distinct confidences
        confidence = round(affinity + rng.uniform(-0.06, 0.06), 2)
        confidence = max(0.1, min(0.99, confidence))

        edges.append({
            "source":     {"domain": d1, "structure": s1},
            "relation":   relation,
            "target":     {"domain": d2, "structure": s2},
            "confidence": confidence,
            "rationale":  rationale,
            "provenance":  "akasha-edge-generator:structural-affinity",
        })

    edges.sort(key=lambda e: e["confidence"], reverse=True)
    return edges


def run(root: Path, seed_concept: str = "", n: int = 5) -> None:
    print("[edge] akasha-edge-generator starting")

    domains = load_domain_packs(root)
    if len(domains) < 2:
        print("[edge] ERROR: need at least 2 domain packs to generate edges")
        sys.exit(1)

    print(f"[edge] domains loaded: {', '.join(sorted(domains.keys()))}")
    if seed_concept:
        print(f"[edge] seed concept:   {seed_concept}")

    edges = generate_edges(domains, seed_concept=seed_concept, n=n)

    print()
    for e in edges:
        src = f"{e['source']['domain']}::{e['source']['structure']}"
        tgt = f"{e['target']['domain']}::{e['target']['structure']}"
        rel = e["relation"]
        conf = e["confidence"]
        print(f"  [{conf:.2f}] {src}")
        print(f"         {rel}")
        print(f"         {tgt}")
        print(f"         ↳ {e['rationale']}")
        print()

    print(f"[edge] {len(edges)} candidate edges emitted")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent.parent
    seed = sys.argv[2] if len(sys.argv) > 2 else ""
    if not root.exists():
        print(f"[edge] ERROR: root not found: {root}")
        sys.exit(1)
    run(root, seed_concept=seed)
