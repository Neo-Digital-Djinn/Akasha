"""
Akasha Request Pipeline
Manage requests through: open → exploring → approved → forged → archived

Invariant enforcement:
  - Promotion to 'approved' runs lightweight contract validation
  - Forge runs full validation and refuses on failure
  - All rejections are logged permanently (INTEGRATION_CONTRACT requirement)
  - Same validation always produces same result (Determinism, Invariant VI)
"""

import json
import logging
import shutil
import sys
import time
from pathlib import Path

BASE = Path("requests")
REPO_ROOT = Path.home()
STAGES = ["open", "exploring", "approved", "forged", "archived"]
REJECT_LOG = Path("requests") / "REJECTION_LOG.ndjson"

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("akasha.pipeline")


# ---------------------------------------------------------------------------
# Invariant validation (local, minimal — no external deps required)
# Based on INTEGRATION_CONTRACT.md and INVARIANTS.md
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"id", "title", "summary"}
VALID_STATUSES = {"open", "exploring", "approved", "forged", "archived"}
VALID_PROVENANCE = {"observation", "derivation", "simulation", "synthesis", "request"}


def _validate_request(data: dict) -> list[str]:
    """
    Returns a list of error strings. Empty list == PASS.
    Checks: schema, provenance, minimality (gap declaration).
    """
    errors = []

    # I — Structural Integrity: required fields
    for field in REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f"SCHEMA_FAIL: missing required field '{field}'")

    # II — Consistency: id must be a string
    req_id = data.get("id", "")
    if req_id and not isinstance(req_id, str):
        errors.append(f"SCHEMA_FAIL: 'id' must be a string, got {type(req_id).__name__}")

    # IV — Provenance
    prov = data.get("provenance") or data.get("source")
    if not prov:
        errors.append("NO_PROVENANCE: request is missing a provenance or source declaration")
    elif isinstance(prov, str) and prov not in VALID_PROVENANCE:
        errors.append(f"NO_PROVENANCE: provenance '{prov}' not in recognised set {VALID_PROVENANCE}")

    # X — Minimality: must name what gap it solves
    gap = data.get("gap") or data.get("problem") or data.get("purpose") or data.get("summary")
    if not gap:
        errors.append("REDUNDANT: request does not declare a gap, problem, or purpose")

    return errors


def _log_rejection(req_id: str, errors: list[str]) -> None:
    """Append rejection record to the permanent rejection log (Invariant V — immutability)."""
    REJECT_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = json.dumps({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "req_id": req_id,
        "errors": errors,
    })
    with open(REJECT_LOG, "a", encoding="utf-8") as f:
        f.write(record + "\n")
    log.warning("Rejection logged: %s — %d error(s)", req_id, len(errors))


# ---------------------------------------------------------------------------
# Pipeline operations
# ---------------------------------------------------------------------------

def find_request(req_id):
    for stage in STAGES:
        stage_dir = BASE / stage
        matches = sorted(stage_dir.glob(f"{req_id}*.json"))
        if matches:
            return matches[0], stage
    return None, None


def promote(req_id, new_stage, skip_validation=False):
    src, stage = find_request(req_id)

    if not src:
        print("Request not found.")
        return False

    if new_stage not in STAGES:
        print(f"Invalid stage: {new_stage}")
        return False

    # Run invariant checks when promoting to 'approved' (Integration Contract gate)
    if new_stage == "approved" and not skip_validation:
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"SCHEMA_FAIL: {src.name} is not valid JSON — {exc}")
            _log_rejection(req_id, [f"SCHEMA_FAIL: invalid JSON — {exc}"])
            return False

        errors = _validate_request(data)
        if errors:
            for e in errors:
                print(f"  ✗ {e}")
            _log_rejection(req_id, errors)
            print(f"\nPromotion to 'approved' REJECTED — {len(errors)} invariant(s) failed.")
            print(f"Rejection logged to {REJECT_LOG}")
            return False
        print(f"  ✓ Invariant validation passed ({req_id})")

    dest = BASE / new_stage / src.name
    shutil.move(src, dest)
    print(f"{req_id} moved {stage} → {new_stage}")
    return True


def forge(req_id):
    path, stage = find_request(req_id)

    if not path:
        print("Request not found.")
        return

    if stage != "approved":
        print("Request must be approved before forging.")
        return

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"SCHEMA_FAIL: {path.name} is not valid JSON — {exc}")
        _log_rejection(req_id, [f"SCHEMA_FAIL: invalid JSON — {exc}"])
        return

    # Full re-validation at forge time (Post-integration check, Invariant IX)
    errors = _validate_request(data)
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        _log_rejection(req_id, errors)
        print(f"\nForge REJECTED — {len(errors)} invariant(s) failed. No repo created.")
        return

    repo = data.get("proposed_repo")
    title = data.get("title", repo or "Akasha Request")
    summary = data.get("summary", "Forged from akasha-requests.")
    req_type = data.get("type", data.get("request_type", "unknown"))
    role = data.get("role", data.get("suggested_role", "unspecified"))
    family = data.get("family", data.get("suggested_family", "unspecified"))

    if not repo:
        print("No proposed_repo defined in request.")
        return

    repo_path = REPO_ROOT / repo

    if repo_path.exists():
        print(f"Refusing to forge: repo already exists at {repo_path}")
        return

    repo_path.mkdir(parents=True, exist_ok=False)

    (repo_path / "src").mkdir()
    (repo_path / "docs").mkdir()
    (repo_path / "tests").mkdir()

    readme = repo_path / "README.md"
    manifest = repo_path / "repo-manifest.yaml"

    readme.write_text(
        f"# {title}\n\n{summary}\n",
        encoding="utf-8"
    )

    manifest.write_text(
        "\n".join([
            f"repo: {repo}",
            f"type: {req_type}",
            f"family: {family}",
            f"role: {role}",
            "status: forged",
            f"forged_from: {req_id}",
        ]) + "\n",
        encoding="utf-8"
    )

    promote(req_id, "forged", skip_validation=True)
    print(f"Repo created: {repo_path}")


def validate_cmd(req_id):
    """Standalone validation — prints result without moving anything."""
    path, stage = find_request(req_id)
    if not path:
        print("Request not found.")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"SCHEMA_FAIL: invalid JSON — {exc}")
        return

    errors = _validate_request(data)
    if errors:
        print(f"FAIL — {len(errors)} invariant(s) violated:")
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print(f"PASS — {req_id} passes all invariants. Eligible for promotion to 'approved'.")


def status():
    print("=== Akasha Request Pipeline Status ===")
    for stage in STAGES:
        count = len(list((BASE / stage).glob("*.json")))
        print(f"{stage.upper():10} {count}")
    rejected = 0
    if REJECT_LOG.exists():
        with open(REJECT_LOG) as f:
            rejected = sum(1 for _ in f)
    print(f"{'REJECTED':10} {rejected}  (see {REJECT_LOG})")
    print("======================================")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/pipeline.py status")
        print("  python scripts/pipeline.py validate REQ-001")
        print("  python scripts/pipeline.py promote REQ-001 exploring")
        print("  python scripts/pipeline.py forge REQ-001")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        status()

    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Usage: python scripts/pipeline.py validate REQ-001")
            sys.exit(1)
        validate_cmd(sys.argv[2])

    elif cmd == "promote":
        if len(sys.argv) < 4:
            print("Usage: python scripts/pipeline.py promote REQ-001 exploring")
            sys.exit(1)
        promote(sys.argv[2], sys.argv[3])

    elif cmd == "forge":
        if len(sys.argv) < 3:
            print("Usage: python scripts/pipeline.py forge REQ-001")
            sys.exit(1)
        forge(sys.argv[2])

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
