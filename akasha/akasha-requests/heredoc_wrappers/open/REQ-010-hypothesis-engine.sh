    #!/data/data/com.termux/files/usr/bin/bash
    set -euo pipefail

    DEST_DIR="${HOME}/akasha-requests/requests/open"
    mkdir -p "$DEST_DIR"
    cat > "$DEST_DIR/REQ-010-hypothesis-engine.json" <<'JSON'
    {
  "request_id": "REQ-010",
  "title": "Hypothesis Engine",
  "request_type": "engine",
  "source": "conversation",
  "status": "open",
  "priority": "high",
  "summary": "Turn detected gaps, analogies, and candidate edges into explicit, testable hypotheses that can be handed to simulation and validation layers.",
  "why": "Akasha already has the bones of discovery, but discoveries do not become research objects until they are stated as hypotheses with assumptions, predicted behaviors, and falsifiers.",
  "proposed_repo": "akasha-hypothesis-engine",
  "suggested_family": "discovery_engine",
  "suggested_class": "engine",
  "suggested_role": "hypothesis_materialization",
  "notes": [
    "Outputs should be structured objects, not vague prose.",
    "Each hypothesis should include supporting inputs, expected outcome, and disconfirmation criteria.",
    "Pairs naturally with akasha-gap, akasha-simulation, and akasha-validation."
  ],
  "captured_from": "Akasha.zip deep dive",
  "created_at": "2026-04-06T16:00:00Z"
}
    JSON
    echo "Wrote $DEST_DIR/REQ-010-hypothesis-engine.json"
