#!/usr/bin/env bash
# Alexandria Temporal Kernel — Debian Setup Script
# Run from the akasha-alexandria/ directory

set -e

echo "=== akasha-alexandria Debian installer ==="
echo

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3,9), 'Python 3.9+ required'" || {
    echo "ERROR: Python 3.9+ is required."
    exit 1
}

echo "Python OK: $(python3 --version)"

# Install
pip install --break-system-packages pyyaml
pip install --break-system-packages -e .

echo
echo "=== Installation complete ==="
echo
echo "Test with:"
echo "  python run.py --generator symbolic"
echo "  alexandria --version"
echo
echo "See README.md for full usage."
