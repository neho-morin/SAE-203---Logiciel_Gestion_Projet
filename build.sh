#!/usr/bin/env bash
# build.sh — Script de build Nudge (Linux / Git Bash Windows)
#
# Usage :
#   chmod +x build.sh
#   ./build.sh
#
# Produit : dist/Nudge  (Linux)  ou  dist/Nudge.exe  (Git Bash Windows)
# Nécessite : Python 3 installé (python, python3 ou py)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SPEC="$ROOT/Cr. .exe for Windows/Nudge.spec"
DIST_BIN="$ROOT/dist/Nudge"

echo ""
echo "=== Build Nudge ==="
echo "Répertoire racine : $ROOT"
echo "Spec              : $SPEC"
echo ""

# ── Détection de l'interpréteur Python ───────────────────────────────────────
PYTHON_CMD=""
for candidate in python python3 py; do
    if command -v "$candidate" &>/dev/null; then
        # Vérifier que c'est bien Python 3 (pas le stub Microsoft Store)
        version=$("$candidate" --version 2>&1)
        if echo "$version" | grep -q "^Python 3"; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERREUR : aucun interpréteur Python 3 trouvé."
    echo "  Essayés : python, python3, py"
    echo "  Installez Python 3 et assurez-vous qu'il est dans votre PATH."
    exit 1
fi

echo "  Python détecté : $PYTHON_CMD ($("$PYTHON_CMD" --version 2>&1))"
echo ""

# ── 1. Nettoyage ──────────────────────────────────────────────────────────────
echo "[1/4] Nettoyage des anciens builds..."
for dir in build dist; do
    full="$ROOT/$dir"
    if [ -d "$full" ]; then
        rm -rf "$full"
        echo "  Supprimé : $full"
    fi
done

# ── 2. Dépendances Python ─────────────────────────────────────────────────────
echo ""
echo "[2/4] Installation des dépendances Python..."

"$PYTHON_CMD" -m pip install --upgrade pip --quiet
"$PYTHON_CMD" -m pip install -r "$ROOT/requirements.txt" --quiet

# Installer PyInstaller s'il n'est pas présent
if ! "$PYTHON_CMD" -m PyInstaller --version &>/dev/null; then
    echo "  PyInstaller absent, installation..."
    "$PYTHON_CMD" -m pip install pyinstaller --quiet
fi

echo "  Dépendances OK."

# ── 3. Build PyInstaller ──────────────────────────────────────────────────────
echo ""
echo "[3/4] Génération du binaire avec PyInstaller..."

"$PYTHON_CMD" -m PyInstaller "$SPEC" \
    --noconfirm \
    --distpath "$ROOT/dist" \
    --workpath "$ROOT/build"

# ── 4. Vérification du résultat ───────────────────────────────────────────────
echo ""
echo "[4/4] Vérification du résultat..."

if [ -f "$DIST_BIN" ]; then
    chmod +x "$DIST_BIN"
    SIZE=$(du -sh "$DIST_BIN" | cut -f1)

    # Créer un .env minimal dans dist/ s'il n'en existe pas déjà
    DIST_ENV="$ROOT/dist/.env"
    if [ ! -f "$DIST_ENV" ]; then
        cat > "$DIST_ENV" << 'EOF'
# Configuration Nudge - personnalisez selon vos besoins
# Ce fichier est lu par Nudge au démarrage

# Authentification (true = connexion requise, false = accès direct admin)
NUDGE_AUTH_ENABLED=true

# Serveur SMTP (pour l'envoi réel de mails)
# NUDGE_SMTP_USER=votre@email.com
# NUDGE_SMTP_PASS=motdepasse
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# NUDGE_SIMULATE=true
EOF
        echo "  Créé : $DIST_ENV  (personnalisez-le si nécessaire)"
    fi

    echo ""
    echo "Build réussi !"
    echo "  Fichier : $DIST_BIN"
    echo "  Taille  : $SIZE"
    echo ""
    echo "Pour tester le binaire :"
    echo "  ./dist/Nudge"
else
    echo ""
    echo "ERREUR : $DIST_BIN introuvable après le build."
    echo "Consultez les logs PyInstaller ci-dessus."
    exit 1
fi
