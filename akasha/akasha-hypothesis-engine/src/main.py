#!/usr/bin/env python3
"""
akasha-hypothesis-engine
Execution-first. Reads a domain pack, emits one hypothesis.

Domain contract (minimum readable shape):
  Rule 1: domain must have at least one .yaml file under packs/
  Rule 2: at least one pack must contain at least one non-empty list
"""

import sys
import yaml
from pathlib import Path


def validate_domain(domain_path: Path) -> None:
    packs = list(domain_path.glob("packs/*.yaml"))
    if not packs:
        raise ValueError(f"[contract] FAIL rule 1: no .yaml files in {domain_path}/packs/")

    has_list = False
    for pack in packs:
        content = yaml.safe_load(pack.read_text(encoding="utf-8")) or {}
        if any(isinstance(v, list) and len(v) > 0 for v in content.values()):
            has_list = True
            break

    if not has_list:
        raise ValueError(f"[contract] FAIL rule 2: no iterable list found in {domain_path}/packs/")

    print("[engine] domain contract: OK")


def load_domain(domain_path: Path) -> dict:
    data = {}
    for pack in domain_path.glob("packs/*.yaml"):
        content = yaml.safe_load(pack.read_text(encoding="utf-8")) or {}
        data[pack.stem] = content
    return data


def run(domain_path: Path) -> None:
    print("[engine] akasha-hypothesis-engine starting")
    print(f"[engine] loading domain: {domain_path.name}")

    validate_domain(domain_path)
    domain = load_domain(domain_path)

    concepts = []
    for pack_data in domain.values():
        for v in pack_data.values():
            if isinstance(v, list):
                concepts.extend(v)

    if not concepts:
        print("[engine] ERROR: no concepts found in domain")
        sys.exit(1)

    concept = concepts[0]
    print(f"[engine] loaded domain: {domain_path.name}")
    print(f"[engine] hypothesis: \"{concept} exhibits a transition between qualitatively distinct states under changing constraints\"")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    domain_path = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent.parent / "akasha-domain-physics"

    if not domain_path.exists():
        print(f"[engine] ERROR: domain path not found: {domain_path}")
        sys.exit(1)

    try:
        run(domain_path)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
