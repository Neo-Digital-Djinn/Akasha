#!/data/data/com.termux/files/usr/bin/bash
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

echo "=================================="
echo " Installing Akasha CLI Suite"
echo "=================================="

SUITE_ROOT="${AKASHA_SUITE_HOME:-$HOME/akasha}"
BIN_DIR="$SUITE_ROOT/bin"

mkdir -p "$BIN_DIR"
cp -f "$SCRIPT_DIR"/bin/* "$BIN_DIR"/
chmod +x "$BIN_DIR"/*

if ! grep -q 'akasha/bin' "$HOME/.bashrc" 2>/dev/null; then
  echo '' >> "$HOME/.bashrc"
  echo '# Akasha CLI' >> "$HOME/.bashrc"
  echo 'export PATH=$HOME/akasha/bin:$PATH' >> "$HOME/.bashrc"
fi

echo
echo "Installed to: $BIN_DIR"
echo "Run: source ~/.bashrc"
echo "Then try: akasha-console"
