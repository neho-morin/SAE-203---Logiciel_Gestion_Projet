#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build_linux.sh — Build Nudge pour Linux avec PyInstaller
# ─────────────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Nudge — Build Linux ==="

# 1. Vérifier que le venv est actif (ou en créer un)
if [ ! -f "venv/bin/python" ]; then
    echo "[1/4] Création du venv…"
    python3 -m venv venv
fi

source venv/bin/activate
echo "[1/4] Venv actif : $(which python)"

# 2. Installer / mettre à jour les dépendances
echo "[2/4] Installation des dépendances…"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet pyinstaller

# 3. Vérification syntaxique rapide
echo "[3/4] Vérification syntaxique…"
python -m py_compile run_nudge.py
python -m py_compile "PyQt 6/nudge.py"
python -m py_compile "PyQt 6/api_server.py"
echo "  → Syntaxe OK"

# 4. Build
echo "[4/4] Build PyInstaller…"
pyinstaller --noconfirm --clean Nudge.spec

echo ""
echo "=== Build terminé ==="
echo "Exécutable : dist/Nudge/Nudge"
echo ""
echo "Test rapide :"
echo "  ./dist/Nudge/Nudge"
