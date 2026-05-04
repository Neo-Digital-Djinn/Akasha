    #!/data/data/com.termux/files/usr/bin/bash
    set -euo pipefail

    DEST_DIR="${HOME}/akasha-requests/requests/open"
    mkdir -p "$DEST_DIR"
    cat > "$DEST_DIR/REQ-011-suggestion-engine.json" <<'JSON'
    {
  "request_id": "REQ-011",
  "title": "Suggestion Engine",
  "request_type": "engine",
  "source": "conversation",
  "status": "open",
  "priority": "medium",
  "summary": "Produce ranked next-step suggestions for repos, experiments, repairs, and research actions based on Akasha state and request pressure.",
  "why": "The constellation is already large enough to need a planner that says what to build next instead of leaving every branch as a forever-maybe.",
  "proposed_repo": "akasha-suggestion-engine",
  "suggested_family": "orchestration_engine",
  "suggested_class": "engine",
  "suggested_role": "action_recommendation",
  "notes": [
    "Could rank suggestions by coherence, leverage, effort, and dependency readiness.",
    "Should be downstream of requests, gap analysis, and discovery outputs.",
    "This is the practical antidote to constellation sprawl."
  ],
  "captured_from": "Akasha.zip deep dive",
  "created_at": "2026-04-06T16:00:00Z"
}
    JSON
    echo "Wrote $DEST_DIR/REQ-011-suggestion-engine.json"
