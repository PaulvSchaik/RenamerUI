#!/bin/bash

# RenamerPro Launcher
# Dit script start de RenamerPro PDF renamer automatisch in de juiste omgeving.

# Bepaal de map waar dit script staat
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Controleer of de virtuele omgeving bestaat
if [ ! -d "venv" ]; then
    echo "Fout: Virtuele omgeving (venv) niet gevonden in $DIR"
    echo "Zorg dat je eerst de installatie-stappen uit de README hebt gevolgd."
    exit 1
fi

# Controleer of .env bestaat
if [ ! -f ".env" ]; then
    echo "Fout: .env bestand niet gevonden."
    echo "Kopieer .env.example naar .env en vul je API key in."
    exit 1
fi

# Help functie
function show_help {
    echo "Gebruik: ./run_renamer.sh [opties]"
    echo ""
    echo "Opties:"
    echo "  --watch [map]    Houdt een map in de gaten voor nieuwe PDF's (standaard)"
    echo "  --once [map]     Scan een map éénmalig en stop daarna"
    echo "  --dry-run        Test de namen zonder de bestanden echt te hernoemen"
    echo ""
    echo "Voorbeeld:"
    echo "  ./run_renamer.sh --watch ~/Downloads"
}

# Als er geen argumenten zijn, toon help
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Start het programma in de venv
echo "[*] RenamerPro wordt gestart..."
source venv/bin/activate
python3 renamer.py "$@"
