#!/usr/bin/env bash
# install-debian.sh — Aetherius bootstrap for Debian 13 (Trixie)
# Run once as a user with sudo access.
set -euo pipefail

echo "==> Installing system dependencies"
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    nodejs npm \
    git curl ca-certificates

echo "==> Creating Python virtual environment"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing Python packages"
pip install --upgrade pip
pip install -e ".[prod]"

echo "==> Installing frontend dependencies"
cd frontend
npm install
cd ..

echo ""
echo "✓ Installation complete."
echo ""
echo "To start Aetherius:"
echo "  1. export GITHUB_TOKEN='your_token_here'"
echo "  2. export AETHERIUS_REPOS='owner/repo1,owner/repo2'"
echo "  3. source .venv/bin/activate"
echo "  4. python backend/aetherius_backend.py   (in one terminal)"
echo "  5. cd frontend && npm run dev             (in another terminal)"
echo "  6. Open http://localhost:3000"
