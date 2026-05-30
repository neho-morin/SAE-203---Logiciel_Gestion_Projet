# build.ps1 — Script de build Nudge pour Windows
#
# Usage :
#   .\build.ps1
#
# Produit : dist\Nudge.exe (build one-file)
# Necessite : Python 3 installe et accessible via "python"

# Forcer UTF-8 pour eviter les caracteres corrompus dans le terminal
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ROOT     = $PSScriptRoot
$SPEC     = Join-Path $ROOT "Cr. .exe for Windows\Nudge.spec"
$DIST_EXE = Join-Path $ROOT "dist\Nudge.exe"

Write-Host ""
Write-Host "=== Build Nudge ===" -ForegroundColor Cyan
Write-Host "Repertoire racine : $ROOT"
Write-Host "Spec              : $SPEC"
Write-Host ""

# ── 1. Nettoyage ──────────────────────────────────────────────────────────────
Write-Host "[1/4] Nettoyage des anciens builds..." -ForegroundColor Yellow
foreach ($dir in @("build", "dist")) {
    $full = Join-Path $ROOT $dir
    if (Test-Path $full) {
        Remove-Item -Recurse -Force $full
        Write-Host "  Supprime : $full"
    }
}

# ── 2. Dependances Python ─────────────────────────────────────────────────────
Write-Host ""
Write-Host "[2/4] Installation des dependances Python..." -ForegroundColor Yellow

python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR : pip upgrade a echoue." -ForegroundColor Red
    exit 1
}

python -m pip install -r (Join-Path $ROOT "requirements.txt") --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR : pip install requirements a echoue." -ForegroundColor Red
    exit 1
}

# Installer PyInstaller s'il n'est pas present
$piExists = python -m PyInstaller --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  PyInstaller absent, installation..." -ForegroundColor Yellow
    python -m pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR : installation de PyInstaller echouee." -ForegroundColor Red
        exit 1
    }
}

Write-Host "  Dependances OK."

# ── 3. Build PyInstaller ──────────────────────────────────────────────────────
Write-Host ""
Write-Host "[3/4] Generation du .exe avec PyInstaller..." -ForegroundColor Yellow

# PyInstaller est lance depuis la RACINE du projet.
# Les chemins dans Nudge.spec utilisent SPECPATH (chemin absolu calcule dans le .spec)
# donc le repertoire courant n'a pas d'importance.
python -m PyInstaller $SPEC `
    --noconfirm `
    --distpath (Join-Path $ROOT "dist") `
    --workpath (Join-Path $ROOT "build")

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERREUR : PyInstaller a echoue." -ForegroundColor Red
    Write-Host "Consultez les logs ci-dessus pour identifier la cause."
    exit 1
}

# ── 4. Verification du resultat ───────────────────────────────────────────────
Write-Host ""
Write-Host "[4/4] Verification du resultat..." -ForegroundColor Yellow

if (Test-Path $DIST_EXE) {
    $size = [math]::Round((Get-Item $DIST_EXE).Length / 1MB, 1)

    # Creer un .env minimal dans dist/ s'il n'en existe pas deja
    # (permet a l'utilisateur de configurer l'app sans toucher au .env source)
    $distEnv = Join-Path $ROOT "dist\.env"
    if (-not (Test-Path $distEnv)) {
        @"
# Configuration Nudge - personnalisez selon vos besoins
# Ce fichier est lu par Nudge.exe au demarrage

# Authentification (true = connexion requise, false = acces direct admin)
NUDGE_AUTH_ENABLED=true

# Serveur SMTP (pour l'envoi reel de mails)
# NUDGE_SMTP_USER=votre@email.com
# NUDGE_SMTP_PASS=motdepasse
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# NUDGE_SIMULATE=true
"@ | Set-Content $distEnv -Encoding UTF8
        Write-Host "  Cree : $distEnv  (personnalisez-le si necessaire)"
    }

    Write-Host ""
    Write-Host "Build reussi !" -ForegroundColor Green
    Write-Host "  Fichier : $DIST_EXE"
    Write-Host "  Taille  : ${size} Mo"
    Write-Host ""
    Write-Host "Pour tester l'executable :"
    Write-Host "  .\dist\Nudge.exe"
} else {
    Write-Host ""
    Write-Host "ERREUR : $DIST_EXE introuvable apres le build." -ForegroundColor Red
    Write-Host "Consultez les logs PyInstaller ci-dessus."
    exit 1
}
