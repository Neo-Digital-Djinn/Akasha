#!/usr/bin/env bash
# akasha-core/requirements.sh
# Validates environment and installs required Python packages.
# Run once before first ./akasha-run, and after any updates.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

# ── system dependencies ───────────────────────────────────────────────────────

echo "[check] system dependencies..."
for cmd in bash python3 pip3 jq; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  [ok]   $cmd"
  else
    echo "  [FAIL] $cmd — not found"
    FAIL=1
  fi
done

# Require Python 3.10+
PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [[ $PY_MAJOR -lt 3 ]] || [[ $PY_MAJOR -eq 3 && $PY_MINOR -lt 10 ]]; then
  echo "  [FAIL] Python $PY_VERSION — need 3.10+"
  FAIL=1
else
  echo "  [ok]   Python $PY_VERSION"
fi

[[ $FAIL -eq 1 ]] && { echo "[FAIL] Fix system dependencies first."; exit 1; }

# ── python packages ───────────────────────────────────────────────────────────

echo ""
echo "[check] Python packages..."

PIP_FLAGS="--quiet --break-system-packages"

install_pkg() {
  local label="$1"
  local path="$2"
  echo "  [pip]  $label"
  pip3 install $PIP_FLAGS -e "$path"
}

install_pkg "akasha-time-nexus"  "$ROOT/akasha/akasha-time-nexus"
install_pkg "akasha-anomaly"     "$ROOT/akasha/akasha-anomaly"
install_pkg "akasha-attractor"   "$ROOT/akasha/akasha-attractor"
install_pkg "akasha-apis"        "$ROOT/akasha/akasha-apis"

# Standalone script deps (PyYAML used by analogy/edge/phase/atlas/suggestion mains)
echo "  [pip]  PyYAML"
pip3 install $PIP_FLAGS PyYAML

echo ""
echo "[ok] Environment ready."
echo ""
echo "Tip: set your location for richer context:"
echo "  export AKASHA_LAT=38.5  AKASHA_LON=-82.6  AKASHA_TZ=America/New_York"
