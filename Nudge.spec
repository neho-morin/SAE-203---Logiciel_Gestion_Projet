# -*- mode: python ; coding: utf-8 -*-
"""
Nudge — Fichier spec PyInstaller.

Build Windows  : pyinstaller --noconfirm --clean Nudge.spec
Build Linux    : pyinstaller --noconfirm --clean Nudge.spec
"""
import sys
from pathlib import Path

ROOT  = Path(SPECPATH)          # dossier contenant ce .spec (racine du projet)
PYQT6 = ROOT / "PyQt 6"

block_cipher = None

# ── Données statiques à embarquer ────────────────────────────────────────────
datas = []

# Icône de l'application
_icon = PYQT6 / "icon.ico"
if _icon.exists():
    datas.append((str(_icon), "."))

# ── Imports cachés (uvicorn, apscheduler, fastapi) ───────────────────────────
hidden_imports = [
    # API FastAPI / uvicorn
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    # Routes de l'API Nudge (importées dynamiquement par uvicorn)
    "api.app",
    "api.auth",
    "api.schemas",
    # Services
    "services.project_service",
    "services.task_service",
    "services.user_service",
    "services.relance_service",
    "services.mail_service",
    "services.scheduler_service",
    "services.chat_history_service",
    "services.relance_config_service",
    "services.openclaw_service",
    "services.context_service",
    "services.auth_service",
    # Config
    "config.settings",
    "config.paths",
    "config.permissions",
    # Database
    "database.db",
    "database.models",
    # APScheduler
    "apscheduler",
    "apscheduler.schedulers.background",
    "apscheduler.executors.pool",
    "apscheduler.jobstores.memory",
    # Autres
    "email.mime.text",
    "email.mime.multipart",
]

# uvloop : seulement sur Linux/macOS
if sys.platform != "win32":
    hidden_imports.append("uvloop")

# ── Analyse ───────────────────────────────────────────────────────────────────
a = Analysis(
    [str(ROOT / "run_nudge.py")],
    pathex=[str(PYQT6)],        # PyInstaller cherche les modules ici
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "PIL"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Exécutable ────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Nudge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # pas de console (windowed)
    icon=str(_icon) if _icon.exists() else None,
)

# ── Dossier de distribution ───────────────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Nudge",
)
