# ─────────────────────────────────────────────────────────────────────────────
# build_windows.ps1 — Build Nudge pour Windows avec PyInstaller
# ─────────────────────────────────────────────────────────────────────────────
# Exécution :
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#   .\build_windows.ps1
# ─────────────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== Nudge — Build Windows ===" -ForegroundColor Cyan

# 1. Vérifier / activer le venv
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[1/4] Création du venv…"
    python -m venv venv
}

& "venv\Scripts\Activate.ps1"
Write-Host "[1/4] Venv actif : $(& python -c 'import sys; print(sys.executable)')"

# 2. Installer les dépendances
Write-Host "[2/4] Installation des dépendances…"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
python -m pip install --quiet pyinstaller

# 3. Vérification syntaxique
Write-Host "[3/4] Vérification syntaxique…"
python -m py_compile run_nudge.py
python -m py_compile "PyQt 6\nudge.py"
python -m py_compile "PyQt 6\api_server.py"
Write-Host "  → Syntaxe OK"

# 4. Build
Write-Host "[4/4] Build PyInstaller…"
pyinstaller --noconfirm --clean Nudge.spec

Write-Host ""
Write-Host "=== Build terminé ===" -ForegroundColor Green
Write-Host "Exécutable : dist\Nudge\Nudge.exe"
Write-Host ""
Write-Host "Test rapide :"
Write-Host "  .\dist\Nudge\Nudge.exe"
