#!/bin/bash

# RenamerUI Personal Launcher (Paul) - ONE-SHOT
# Dit script scant de OneDrive inbox ÉÉN keer en stopt daarna.
# Dit bestand is alleen voor lokaal gebruik en wordt niet naar GitHub gepusht.

# Project map
PROJECT_DIR="/Users/paul/github/RenamerUI"
cd "$PROJECT_DIR"

# De doelmap (Inbox)
INBOX_DIR="/Users/paul/Library/CloudStorage/OneDrive-vanderHamOptometristen/Paul Privé/General/- INBOX -/"

# Controleer of de venv bestaat
if [ ! -d "venv" ]; then
    echo "Fout: Virtuele omgeving niet gevonden in $PROJECT_DIR"
    exit 1
fi

# Controleer of de inbox map bestaat
if [ ! -d "$INBOX_DIR" ]; then
    echo "Fout: Doelmap niet gevonden: $INBOX_DIR"
    exit 1
fi

echo "[*] Starten van RenamerUI (Eenmalige scan) voor de OneDrive Inbox..."
echo "[*] Map: $INBOX_DIR"

# Activeer de venv en start de scan
source venv/bin/activate
python3 renamer.py --once "$INBOX_DIR"
