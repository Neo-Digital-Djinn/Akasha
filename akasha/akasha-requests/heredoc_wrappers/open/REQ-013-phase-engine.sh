    #!/data/data/com.termux/files/usr/bin/bash
    set -euo pipefail

    DEST_DIR="${HOME}/akasha-requests/requests/open"
    mkdir -p "$DEST_DIR"
    cat > "$DEST_DIR/REQ-013-phase-engine.json" <<'JSON'
    {
  "request_id": "REQ-013",
  "title": "Phase Engine",
  "request_type": "engine",
  "source": "conversation",
  "status": "open",
  "priority": "high",
  "summary": "Generalize the uploaded Phase_Behavior_Ontology_Engine into a constellation-native phase engine that models entities, states, transitions, and tipping behavior across domains.",
  "why": "The snapshot already contains a specialized phase-behavior engine. Formalizing that pattern as a reusable Akasha organ turns one strong local engine into a reusable system primitive.",
  "proposed_repo": "akasha-phase-engine",
  "suggested_family": "core_engine",
  "suggested_class": "engine",
  "suggested_role": "phase_state_transition_modeling",
  "notes": [
    "This should complement, not replace, akasha-phase-transition-engine.",
    "Think general phase/state modeling upstream; tipping-point analysis downstream.",
    "Could eventually absorb shared pieces from the standalone phase behavior ontology prototype."
  ],
  "captured_from": "Akasha.zip deep dive",
  "created_at": "2026-04-06T16:00:00Z"
}
    JSON
    echo "Wrote $DEST_DIR/REQ-013-phase-engine.json"
