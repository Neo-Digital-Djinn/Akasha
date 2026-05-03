#!/usr/bin/env python3
"""
akasha-domain-combinator
Composes all domain packs into a joint workspace. Ranks domain pairs by
relevance to the pipeline input, then emits overlaps, tensions, and
candidate research questions — most relevant pair first.

Aligned with: REQ-009, Axiom 2 (Discoverability), Axiom 4 (Augmentation),
              Axiom 5 (Traceability), Axiom 6 (Modularity).
"""

from __future__ import annotations

import sys
import yaml
from pathlib import Path
from itertools import combinations


def load_all_domains(root: Path) -> dict[str, dict]:
    domains: dict[str, dict] = {}
    for pack_dir in sorted(root.glob("akasha/akasha-domain-*/packs/*.yaml")):
        domain = pack_dir.parent.parent.name.replace("akasha-domain-", "")
        try:
            data = yaml.safe_load(pack_dir.read_text(encoding="utf-8")) or {}
            domains.setdefault(domain, {})[pack_dir.stem] = data
        except Exception as exc:
            print(f"[combinator] warn: could not load {pack_dir}: {exc}")
    return domains


def flatten_concepts(domain_packs: dict) -> list[str]:
    concepts: list[str] = []
    for pack_data in domain_packs.values():
        for field in ("structures", "examples"):
            concepts.extend(str(v) for v in pack_data.get(field, []) if v)
    return concepts


def token_overlap(a: str, b: str) -> set[str]:
    stops = {"a", "an", "the", "of", "in", "to", "and", "or", "with", "for"}
    ta = set(a.lower().replace("_", " ").split()) - stops
    tb = set(b.lower().replace("_", " ").split()) - stops
    return ta & tb


def domain_seed_score(concepts: list[str], seed_tokens: set[str]) -> int:
    """How many concepts in this domain share tokens with the seed."""
    if not seed_tokens:
        return 0
    stops = {"a", "an", "the", "of", "in", "to", "and", "or", "with", "for"}
    score = 0
    for c in concepts:
        c_tokens = set(c.lower().replace("_", " ").split()) - stops
        if c_tokens & seed_tokens:
            score += 1
    return score


def find_overlaps(d1, c1, d2, c2):
    overlaps = []
    for ca in c1:
        for cb in c2:
            shared = token_overlap(ca, cb)
            if shared:
                overlaps.append({
                    "domain_a": d1, "concept_a": ca,
                    "domain_b": d2, "concept_b": cb,
                    "shared_tokens": sorted(shared),
                    "overlap_score": len(shared),
                })
    overlaps.sort(key=lambda x: x["overlap_score"], reverse=True)
    return overlaps


ROLE_MARKERS = [
    "collapse", "transition", "equilibrium", "emergence", "cascade",
    "propagation", "threshold", "attractor", "instability", "shift",
    "resolution", "modulation", "diffusion", "synchronization", "cycle",
    "flow", "coupling", "dynamics", "field", "critical",
]


def find_tensions(d1, c1, d2, c2):
    tensions = []
    for marker in ROLE_MARKERS:
        in_d1 = [c for c in c1 if marker in c.lower().replace("_", " ")]
        in_d2 = [c for c in c2 if marker in c.lower().replace("_", " ")]
        if in_d1 and in_d2:
            tensions.append({
                "structural_role": marker,
                "domain_a": d1, "instances_a": in_d1,
                "domain_b": d2, "instances_b": in_d2,
            })
    return tensions


def generate_research_questions(d1, d2, overlaps, tensions):
    questions = []
    for ov in overlaps[:3]:
        shared = ", ".join(ov["shared_tokens"])
        questions.append(
            f"Do {d1}::{ov['concept_a']} and {d2}::{ov['concept_b']} share a common "
            f"underlying mechanism? (shared structure: {shared})"
        )
    for t in tensions[:2]:
        role = t["structural_role"]
        ex_a = t["instances_a"][0]
        ex_b = t["instances_b"][0]
        questions.append(
            f"What distinguishes {d1}::{ex_a} from {d2}::{ex_b}? "
            f"Both occupy the '{role}' structural role — domain-specific constraint "
            f"or a deeper structural difference?"
        )
    if not overlaps:
        questions.append(
            f"No structural overlap found between {d1} and {d2}. "
            f"What bridge concept would make them commensurable?"
        )
    return questions


def pair_relevance_score(
    d1: str, c1: list[str], d2: str, c2: list[str], seed_tokens: set[str]
) -> int:
    """Score a domain pair by combined seed relevance + overlap richness."""
    seed_score = domain_seed_score(c1, seed_tokens) + domain_seed_score(c2, seed_tokens)
    overlap_count = len(find_overlaps(d1, c1, d2, c2))
    return seed_score * 10 + overlap_count


def run(root: Path, selected_domains: list[str] | None = None, seed: str = "") -> None:
    print("[combinator] akasha-domain-combinator starting")

    all_domains = load_all_domains(root)
    if not all_domains:
        print("[combinator] ERROR: no domain packs found")
        sys.exit(1)

    if selected_domains:
        missing = [d for d in selected_domains if d not in all_domains]
        if missing:
            print(f"[combinator] ERROR: domains not found: {missing}")
            sys.exit(1)
        work_domains = {d: all_domains[d] for d in selected_domains}
    else:
        work_domains = all_domains

    domain_concepts: dict[str, list[str]] = {
        d: flatten_concepts(packs) for d, packs in work_domains.items()
    }

    stops = {"a", "an", "the", "of", "in", "to", "and", "or", "with", "for"}
    seed_tokens = set(seed.lower().replace("_", " ").split()) - stops if seed else set()

    print(f"[combinator] domains: {sorted(work_domains.keys())}")
    for d, concepts in domain_concepts.items():
        print(f"[combinator]   {d:20s} — {len(concepts)} concepts")
    if seed:
        print(f"[combinator] seed: {seed}")
    print()

    # Rank pairs by relevance to seed (or by overlap richness if no seed)
    pairs = list(combinations(sorted(work_domains.keys()), 2))
    ranked_pairs = sorted(
        pairs,
        key=lambda p: pair_relevance_score(
            p[0], domain_concepts[p[0]], p[1], domain_concepts[p[1]], seed_tokens
        ),
        reverse=True,
    )

    for d1, d2 in ranked_pairs:
        c1, c2 = domain_concepts[d1], domain_concepts[d2]
        overlaps = find_overlaps(d1, c1, d2, c2)
        tensions = find_tensions(d1, c1, d2, c2)
        questions = generate_research_questions(d1, d2, overlaps, tensions)

        print(f"[combinator] ── pair: {d1} × {d2} ──")

        if overlaps:
            print(f"[combinator] overlaps ({len(overlaps)} found):")
            for ov in overlaps[:5]:
                shared = ", ".join(ov["shared_tokens"])
                print(f"  {ov['domain_a']}::{ov['concept_a']}")
                print(f"    ↔ {ov['domain_b']}::{ov['concept_b']}")
                print(f"    shared: [{shared}]  score={ov['overlap_score']}")
        else:
            print("[combinator] overlaps: none (structurally orthogonal)")

        if tensions:
            print(f"[combinator] tension points ({len(tensions)} structural roles shared):")
            for t in tensions[:4]:
                print(f"  role '{t['structural_role']}':")
                print(f"    {d1}: {t['instances_a']}")
                print(f"    {d2}: {t['instances_b']}")
        else:
            print("[combinator] tension points: none detected")

        print(f"[combinator] candidate research questions:")
        for i, q in enumerate(questions, 1):
            print(f"  Q{i}: {q}")
        print()

    print(f"[combinator] {len(ranked_pairs)} domain pair(s) processed")
    print("[combinator] done")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent.parent
    seed = sys.argv[2] if len(sys.argv) > 2 else ""
    if not root.exists():
        print(f"[combinator] ERROR: root not found: {root}")
        sys.exit(1)
    run(root, seed=seed)
