#!/usr/bin/env python3
"""
akasha-atlas-engine
Maps the Akasha knowledge space from repo manifests and domain packs.
Emits: domain list, engine list, stub organs, and growth frontiers.
Aligned with: REQ-012, Axiom 2 (Discoverability), Axiom 5 (Traceability).
"""

from __future__ import annotations

import sys
import yaml
from pathlib import Path


def load_manifests(root: Path) -> list[dict]:
    manifests = []
    for path in sorted(root.glob("akasha/*/repo-manifest.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            data["_source"] = path.parent.name
            manifests.append(data)
        except Exception:
            pass
    return manifests


def load_domain_packs(root: Path) -> dict[str, list[str]]:
    domains: dict[str, list[str]] = {}
    for pack_dir in sorted(root.glob("akasha/akasha-domain-*/packs/*.yaml")):
        domain = pack_dir.parent.parent.name.replace("akasha-domain-", "")
        try:
            data = yaml.safe_load(pack_dir.read_text(encoding="utf-8")) or {}
            structures = data.get("structures", []) + data.get("examples", [])
            domains.setdefault(domain, []).extend(structures)
        except Exception:
            pass
    return domains


def classify_engine(manifest: dict) -> str:
    name = manifest.get("_source", "")
    role = manifest.get("role") or (manifest.get("engine") or {}).get("role", "")
    # Detect stubs: main.py only prints "organ initialized"
    return str(role) or "unknown"


def find_stubs(root: Path) -> list[str]:
    stubs = []
    for path in sorted(root.glob("akasha/*/src/main.py")):
        try:
            src = path.read_text(encoding="utf-8")
            if "organ initialized" in src and len(src.strip().splitlines()) < 12:
                stubs.append(path.parent.parent.name)
        except Exception:
            pass
    return stubs


def run(root: Path) -> None:
    print("[atlas] akasha-atlas-engine starting")
    print(f"[atlas] scanning: {root}")

    manifests  = load_manifests(root)
    domains    = load_domain_packs(root)
    stubs      = find_stubs(root)

    engines    = [m["_source"] for m in manifests]
    domain_names = sorted(domains.keys())

    # Count structures per domain
    domain_summary = {d: len(s) for d, s in domains.items()}

    # Growth frontiers — stubs are the first frontier
    frontiers = stubs[:]

    print()
    print(f"[atlas] repos mapped:      {len(manifests)}")
    print(f"[atlas] domains indexed:   {len(domain_names)}")
    print(f"[atlas] stub organs:       {len(stubs)}")
    print()

    if domain_names:
        print("[atlas] domain knowledge:")
        for d in domain_names:
            print(f"         {d:20s} — {domain_summary[d]} structures")

    if stubs:
        print()
        print("[atlas] growth frontiers (stubs to implement):")
        for s in stubs:
            print(f"         → {s}")

    print()
    print("[atlas] map complete")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent.parent
    if not root.exists():
        print(f"[atlas] ERROR: root not found: {root}")
        sys.exit(1)
    run(root)
