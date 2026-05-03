#!/usr/bin/env bash
# install-debian.sh — Debian 13 (Trixie) install for akasha-phase-engine
# Usage: bash install-debian.sh [--with-materials]
set -euo pipefail

WITH_MATERIALS=false
for arg in "$@"; do
  [[ "$arg" == "--with-materials" ]] && WITH_MATERIALS=true
done

echo "==> Checking system..."
python3 --version
pip3 --version

echo "==> Installing akasha-phase-engine..."
if [[ "$WITH_MATERIALS" == "true" ]]; then
  pip3 install -e ".[dev,materials]" --break-system-packages
  echo "==> Materials Project integration installed."
  echo "    Add your MP_API_KEY to .env to use /api/pipeline"
else
  pip3 install -e ".[dev]" --break-system-packages
fi

echo "==> Copying .env..."
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "    Created .env from .env.example — edit it to add MP_API_KEY if needed."
fi

echo ""
echo "==> Done. Quick start:"
echo ""
echo "    akasha-phase-engine            # full demo"
echo "    akasha-phase-engine graph      # graph traversal"
echo "    akasha-phase-engine discovery  # gap finder"
echo "    akasha-phase-engine serve      # dev server on :8000"
echo "    akasha-phase-engine serve --prod  # gunicorn"
echo ""
echo "    python -m pytest tests/ -v     # run tests"
