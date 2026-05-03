#!/usr/bin/env python3
"""
akasha-suggestion-engine
Reads open requests, stub organs, and domain gaps.
Emits ranked next-step suggestions.
Aligned with: REQ-011, Axiom 4 (Augmentation), Axiom 6 (Modularity).
"""

from __future__ import annotations

import json
import sys
import yaml
from pathlib import Path


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def load_open_requests(root: Path) -> list[dict]:
    reqs = []
    for path in sorted(root.glob("akasha/akasha-requests/requests/approved/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("status") in ("open", None):
                reqs.append(data)
        except Exception:
            pass
    return reqs


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


def find_empty_design_docs(root: Path) -> list[str]:
    empty = []
    for path in sorted(root.glob("akasha/*/docs/design.md")):
        try:
            content = path.read_text(encoding="utf-8").strip()
            if content in ("# Design\n\nDescribe system.", "# Design\n\nDescribe system.", ""):
                empty.append(path.parent.parent.name)
        except Exception:
            pass
    return empty


def score_request(req: dict) -> int:
    priority = req.get("priority", "low")
    return PRIORITY_ORDER.get(priority, 9)


def run(root: Path, input_text: str = "") -> None:
    print("[suggestion] akasha-suggestion-engine starting")

    open_reqs   = load_open_requests(root)
    stubs       = find_stubs(root)
    empty_docs  = find_empty_design_docs(root)

    suggestions: list[tuple[int, str, str]] = []

    # Rank open requests by priority
    for req in sorted(open_reqs, key=score_request):
        rid    = req.get("request_id", "?")
        title  = req.get("title", "?")
        summary = req.get("summary", "")
        priority = req.get("priority", "?")
        suggestions.append((score_request(req), f"[{rid}] {title} [{priority}]", summary))

    # Stubs with no matching open request
    req_repos = {r.get("proposed_repo", "") for r in open_reqs}
    for stub in stubs:
        if stub not in req_repos:
            suggestions.append((5, f"[stub] {stub}", "Implement or document this stub organ."))

    # Docs that need writing
    for repo in empty_docs:
        suggestions.append((6, f"[doc] {repo}/docs/design.md", "Fill design doc per Axiom 5 (Traceability)."))

    print()
    print(f"[suggestion] {len(suggestions)} suggestions ranked:")
    print()
    for i, (_, label, summary) in enumerate(sorted(suggestions, key=lambda x: x[0]), 1):
        print(f"  {i:2d}. {label}")
        if summary:
            # Wrap summary neatly
            words = summary.split()
            line = "      "
            for w in words:
                if len(line) + len(w) > 78:
                    print(line)
                    line = "      " + w + " "
                else:
                    line += w + " "
            if line.strip():
                print(line)
        print()

    print("[suggestion] done")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent.parent
    input_text = sys.argv[2] if len(sys.argv) > 2 else ""
    if not root.exists():
        print(f"[suggestion] ERROR: root not found: {root}")
        sys.exit(1)
    run(root, input_text)
