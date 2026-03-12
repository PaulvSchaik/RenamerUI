#!/bin/bash
# Bouwt RenamerUI.app — voer uit vanuit de projectmap.
set -e
cd "$(dirname "$0")"

source venv/bin/activate

echo "→ PyInstaller installeren..."
pip install pyinstaller --quiet

echo "→ RenamerUI.app bouwen (dit duurt een minuutje)..."
pyinstaller RenamerUI.spec --noconfirm --clean

echo ""
echo "✓ Klaar! De app staat in:  dist/RenamerUI.app"
echo ""
echo "  Sleep de app naar /Applications om hem te installeren,"
echo "  of zip de map 'dist/RenamerUI.app' om te delen met collega's."
