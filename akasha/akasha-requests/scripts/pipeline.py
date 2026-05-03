import json
import shutil
import sys
from pathlib import Path

BASE = Path("requests")
REPO_ROOT = Path.home()
STAGES = ["open", "exploring", "approved", "forged", "archived"]


def find_request(req_id):
    for stage in STAGES:
        stage_dir = BASE / stage
        matches = sorted(stage_dir.glob(f"{req_id}*.json"))
        if matches:
            return matches[0], stage
    return None, None


def promote(req_id, new_stage):
    src, stage = find_request(req_id)

    if not src:
        print("Request not found.")
        return

    if new_stage not in STAGES:
        print(f"Invalid stage: {new_stage}")
        return

    dest = BASE / new_stage / src.name
    shutil.move(src, dest)
    print(f"{req_id} moved {stage} → {new_stage}")


def forge(req_id):
    path, stage = find_request(req_id)

    if not path:
        print("Request not found.")
        return

    if stage != "approved":
        print("Request must be approved before forging.")
        return

    data = json.loads(path.read_text(encoding="utf-8"))

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

    promote(req_id, "forged")
    print(f"Repo created: {repo_path}")


def status():
    print("=== Akasha Request Pipeline Status ===")
    for stage in STAGES:
        count = len(list((BASE / stage).glob("*.json")))
        print(f"{stage.upper():10} {count}")
    print("======================================")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/pipeline.py status")
        print("  python scripts/pipeline.py promote REQ-001 exploring")
        print("  python scripts/pipeline.py forge REQ-001")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        status()

    elif cmd == "promote":
        if len(sys.argv) < 4:
            print("Usage: python scripts/pipeline.py promote REQ-001 exploring")
            sys.exit(1)
        req = sys.argv[2]
        stage = sys.argv[3]
        promote(req, stage)

    elif cmd == "forge":
        if len(sys.argv) < 3:
            print("Usage: python scripts/pipeline.py forge REQ-001")
            sys.exit(1)
        req = sys.argv[2]
        forge(req)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
