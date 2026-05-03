#!/usr/bin/env bash
# akasha-core/orchestrator.sh
# The Akasha runtime pipeline.
# Stages: ANOMALY → ANALOGY → EDGE → ATTRACTOR → PHASE → ATLAS → SUGGESTION
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT="${*:-demo input}"

LOGDIR="$ROOT/akasha-core/logs"
mkdir -p "$LOGDIR"

TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOGDIR/run_$TS.log"
MEM="$ROOT/akasha-core/memory.ndjson"
touch "$MEM"

# ── helpers ──────────────────────────────────────────────────────────────────

log() { printf "%s\n" "$*" | tee -a "$LOG"; }
sep() { log ""; log "────────────────────────────────────────"; }

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

# safe_run NAME [cmd args...]
# Runs a pipeline stage. On failure prints the error and continues (degraded mode).
safe_run() {
  local name="$1"; shift
  sep
  log "[AKASHA:$name] starting"
  local out rc
  out=$("$@" 2>&1) && rc=0 || rc=$?
  if [[ $rc -eq 0 ]]; then
    log "[AKASHA:$name] ok"
  else
    log "[AKASHA:$name] degraded (exit $rc)"
  fi
  if [[ -n "$out" ]]; then
    printf "%s\n" "$out" | tee -a "$LOG"
  fi
}

# ── record run ───────────────────────────────────────────────────────────────

printf '{"ts":"%s","input":%s}\n' \
  "$(date -Iseconds)" \
  "$(printf "%s" "$INPUT" | json_escape)" >> "$MEM"

sep
log "[AKASHA] pipeline starting"
log "[AKASHA] input: $INPUT"

# ── stage 1: ANOMALY — stamp observation, write ledger ───────────────────────
safe_run ANOMALY \
  python3 "$ROOT/akasha/akasha-anomaly/akasha_anomaly/cli/pipeline.py" \
  "$INPUT" \
  "$ROOT/akasha-core/events"

# ── stage 2: ANALOGY — structural analogy anchored to input concept ──────────
safe_run ANALOGY \
  python3 "$ROOT/akasha/akasha-analogy-engine/src/main.py" \
  "$ROOT" \
  "$INPUT"

# ── stage 3: EDGE — cross-domain candidate edges ─────────────────────────────
safe_run EDGE \
  python3 "$ROOT/akasha/akasha-edge-generator/src/main.py" \
  "$ROOT" \
  "$INPUT"

# ── stage 3b: COMBINATOR — cross-domain overlap and tension map ──────────────
safe_run COMBINATOR \
  python3 "$ROOT/akasha/akasha-domain-combinator/src/main.py" \
  "$ROOT" \
  "$INPUT"

# ── stage 4: ATTRACTOR — event ledger summary ────────────────────────────────
DB="$ROOT/akasha-core/events/ledger.db"
if [[ -f "$DB" ]]; then
  safe_run ATTRACTOR \
    python3 -m akasha_attractor.cli.pipeline \
    "$DB"
else
  log "[AKASHA:ATTRACTOR] skipped — ledger.db not found (run ANOMALY first)"
fi

# ── stage 5: PHASE — phase state estimation across all domains ───────────────
safe_run PHASE \
  python3 "$ROOT/akasha/akasha-phase-engine/src/main.py" \
  "$ROOT/akasha/akasha-domain-physics"

# ── stage 6: ATLAS — knowledge space map and growth frontiers ────────────────
safe_run ATLAS \
  python3 "$ROOT/akasha/akasha-atlas-engine/src/main.py" \
  "$ROOT"

# ── stage 7: SUGGESTION — ranked next-step suggestions ───────────────────────
safe_run SUGGESTION \
  python3 "$ROOT/akasha/akasha-suggestion-engine/src/main.py" \
  "$ROOT" \
  "$INPUT"

sep
log "[AKASHA] pipeline complete"
log "[AKASHA] log: $LOG"
