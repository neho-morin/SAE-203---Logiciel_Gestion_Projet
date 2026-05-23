# build_windows.ps1 - Build Nudge pour Windows avec PyInstaller
#
# Usage :
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#   .\build_windows.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== Nudge - Build Windows ===" -ForegroundColor Cyan

# 1. Verification de Python
Write-Host "[1/4] Verification de Python..."
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR : Python introuvable. Ajoutez Python au PATH." -ForegroundColor Red
    exit 1
}

# 2. Installation des dependances
Write-Host "[2/4] Installation des dependances..."
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
python -m pip install --quiet pyinstaller
Write-Host "  Dependances OK"

# 3. Verification syntaxique
Write-Host "[3/4] Verification syntaxique..."
python -m py_compile run_nudge.py
python -m py_compile "PyQt 6\nudge.py"
python -m py_compile "PyQt 6\api_server.py"
Write-Host "  Syntaxe OK"

# 4. Build PyInstaller
Write-Host "[4/4] Build PyInstaller..."
python -m PyInstaller --noconfirm --clean Nudge.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR : Le build a echoue." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Build termine ===" -ForegroundColor Green
Write-Host "Executable : dist\Nudge\Nudge.exe"
Write-Host ""
Write-Host "Pour tester :"
Write-Host "  .\dist\Nudge\Nudge.exe"
