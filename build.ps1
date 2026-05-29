# build.ps1 — Script de build Nudge pour Windows
#
# Usage :
#   .\build.ps1
#
# Produit : dist\Nudge.exe (build one-file)
# Nécessite : Python 3 installé et accessible via la commande "python"

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ROOT     = $PSScriptRoot
$PYQT6    = Join-Path $ROOT "PyQt 6"
$SPEC     = Join-Path $ROOT "Cr. .exe for Windows\Nudge.spec"
$DIST_EXE = Join-Path $ROOT "dist\Nudge.exe"

Write-Host ""
Write-Host "=== Build Nudge ===" -ForegroundColor Cyan
Write-Host "Répertoire : $ROOT"
Write-Host ""

# ── Nettoyage ─────────────────────────────────────────────────────────────────
Write-Host "[1/4] Nettoyage des anciens builds..." -ForegroundColor Yellow
foreach ($dir in @("build", "dist")) {
    $full = Join-Path $ROOT $dir
    if (Test-Path $full) {
        Remove-Item -Recurse -Force $full
        Write-Host "  Supprimé : $full"
    }
}

# ── Dépendances ───────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[2/4] Installation des dépendances Python..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install -r (Join-Path $ROOT "requirements.txt") --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR : pip install a échoué." -ForegroundColor Red
    exit 1
}
Write-Host "  Dépendances installées."

# ── PyInstaller ───────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[3/4] Génération du .exe avec PyInstaller..." -ForegroundColor Yellow
Write-Host "  Spec : $SPEC"

# PyInstaller doit être lancé depuis PyQt 6/ car les chemins dans le spec
# (nudge.py, database/, services/, config/, api/) sont relatifs à ce dossier.
Push-Location $PYQT6
try {
    python -m PyInstaller $SPEC --noconfirm --distpath (Join-Path $ROOT "dist") --workpath (Join-Path $ROOT "build")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR : PyInstaller a échoué." -ForegroundColor Red
        exit 1
    }
}
finally {
    Pop-Location
}

# ── Résultat ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[4/4] Vérification du résultat..." -ForegroundColor Yellow
if (Test-Path $DIST_EXE) {
    $size = [math]::Round((Get-Item $DIST_EXE).Length / 1MB, 1)
    Write-Host ""
    Write-Host "Build réussi !" -ForegroundColor Green
    Write-Host "  Fichier : $DIST_EXE"
    Write-Host "  Taille  : ${size} Mo"
    Write-Host ""
    Write-Host "Pour tester :"
    Write-Host "  .\dist\Nudge.exe"
} else {
    Write-Host "ERREUR : $DIST_EXE non trouvé." -ForegroundColor Red
    Write-Host "Consultez les logs PyInstaller ci-dessus."
    exit 1
}
