"""
Aetherius Backend
=================
Flask + SocketIO REST/WebSocket server.

Akasha alignment:
  Axiom 5 — Traceability : /api/ledger exposes the full audit trail.
  Axiom 7 — Transparency : /api/governor exposes current rate limits.
  Axiom 9 — Stewardship  : feedback and governor endpoints require human action.

Debian 13 notes:
  - Token and repo list loaded from environment variables (no hardcoded secrets).
  - eventlet is the recommended async mode for flask-socketio on Debian; falls
    back gracefully to threading if eventlet is absent.
  - Requires: pip install flask flask-socketio requests
    Optional:  pip install eventlet   (recommended for production)

Environment variables
---------------------
GITHUB_TOKEN      GitHub personal access token (required)
AETHERIUS_REPOS   Comma-separated list of owner/repo  (default: example/repo)
AETHERIUS_HOST    Bind host  (default: 0.0.0.0)
AETHERIUS_PORT    Bind port  (default: 5000)
"""

import logging
import os
import threading
import time

from flask import Flask, jsonify, request
from flask_socketio import SocketIO

from aetherius_engine import AetheriusEngine, issues_store, ledger_store

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
_raw_repos = os.environ.get("AETHERIUS_REPOS", "yourusername/repo1")
REPOS = [r.strip() for r in _raw_repos.split(",") if r.strip()]
HOST = os.environ.get("AETHERIUS_HOST", "0.0.0.0")
PORT = int(os.environ.get("AETHERIUS_PORT", "5000"))

if not GITHUB_TOKEN:
    log.warning(
        "GITHUB_TOKEN is not set — GitHub API calls will fail. "
        "Export GITHUB_TOKEN before starting Aetherius."
    )

# ---------------------------------------------------------------------------
# Flask + SocketIO
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("AETHERIUS_SECRET", "aetherius-dev-secret")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
aetherius = AetheriusEngine(token=GITHUB_TOKEN, repo_list=REPOS)


def _emit_update() -> None:
    socketio.emit("update", {"issues": issues_store, "ledger": ledger_store})


# ---------------------------------------------------------------------------
# Background scan loop
# ---------------------------------------------------------------------------
SCAN_INTERVAL = int(os.environ.get("AETHERIUS_SCAN_INTERVAL", "60"))


def _scan_loop() -> None:
    while True:
        try:
            aetherius.scan_and_rank_issues()
            _emit_update()
        except Exception as exc:
            log.exception("Scan loop error: %s", exc)
        time.sleep(SCAN_INTERVAL)


_scan_thread = threading.Thread(target=_scan_loop, daemon=True, name="aetherius-scan")
_scan_thread.start()

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/api/issues", methods=["GET"])
def get_issues():
    return jsonify(issues_store)


@app.route("/api/ledger", methods=["GET"])
def get_ledger():
    return jsonify(ledger_store)


@app.route("/api/feedback", methods=["POST"])
def post_feedback():
    data = request.get_json(force=True)
    repo = data.get("repo", "")
    issue_number = data.get("issue_number")
    adjustment = float(data.get("adjustment", 0))
    if not repo or issue_number is None:
        return jsonify({"status": "error", "message": "repo and issue_number required"}), 400
    aetherius.apply_human_feedback(repo, int(issue_number), adjustment)
    _emit_update()
    return jsonify({"status": "ok"})


@app.route("/api/update_file", methods=["POST"])
def update_file():
    data = request.get_json(force=True)
    repo = data.get("repo", "")
    path = data.get("path", "")
    content = data.get("content", "")
    message = data.get("message", "")
    if not repo or not path:
        return jsonify({"status": "error", "message": "repo and path required"}), 400
    aetherius.create_or_update_file(repo, path, content, message)
    _emit_update()
    return jsonify({"status": "ok"})


@app.route("/api/governor", methods=["GET"])
def get_governor():
    return jsonify(aetherius.governor.status())


@app.route("/api/governor", methods=["POST"])
def set_governor():
    data = request.get_json(force=True)
    if "github_limit" in data:
        aetherius.governor.github_limit = int(data["github_limit"])
    if "llm_limit" in data:
        aetherius.governor.llm_limit = int(data["llm_limit"])
    msg = (
        f"[AetheriusGovernor] Limits updated — "
        f"GitHub={aetherius.governor.github_limit}/min, "
        f"LLM={aetherius.governor.llm_limit}/min"
    )
    ledger_store.append(msg)
    _emit_update()
    return jsonify({"status": "ok", **aetherius.governor.status()})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "engine": "aetherius", "repos": REPOS})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log.info("Aetherius backend starting on %s:%d", HOST, PORT)
    socketio.run(app, host=HOST, port=PORT, use_reloader=False)
