#!/bin/bash
# Bouwt RenamerPro.app — voer uit vanuit de projectmap.
set -e
cd "$(dirname "$0")"

source venv/bin/activate

echo "→ PyInstaller installeren..."
pip install pyinstaller --quiet

echo "→ RenamerPro.app bouwen (dit duurt een minuutje)..."
pyinstaller RenamerPro.spec --noconfirm --clean

echo ""
echo "✓ Klaar! De app staat in:  dist/RenamerPro.app"
echo ""
echo "  Sleep de app naar /Applications om hem te installeren,"
echo "  of zip de map 'dist/RenamerPro.app' om te delen met collega's."
