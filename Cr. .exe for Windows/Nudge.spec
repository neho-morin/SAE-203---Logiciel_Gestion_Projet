# -*- mode: python ; coding: utf-8 -*-
#
# Nudge.spec — Build PyInstaller Windows
#
# Point d'entrée  : PyQt 6/nudge.py
#   (nudge.py démarre l'API uvicorn en thread interne — pas besoin de run_nudge.py)
#
# Usage depuis la racine du projet :
#   python -m PyInstaller "Cr. .exe for Windows\Nudge.spec" --noconfirm
#
# SPECPATH est fourni automatiquement par PyInstaller :
#   il contient le dossier de CE fichier .spec.

from pathlib import Path

SPEC_DIR  = Path(SPECPATH)           # …/Cr. .exe for Windows/
ROOT      = SPEC_DIR.parent          # racine du projet
PYQT6_DIR = ROOT / "PyQt 6"         # dossier principal de l'application


a = Analysis(
    [str(PYQT6_DIR / "nudge.py")],
    pathex=[
        str(ROOT),
        str(PYQT6_DIR),
    ],
    binaries=[],
    datas=[
        (str(PYQT6_DIR / "database"), "database"),
        (str(PYQT6_DIR / "services"), "services"),
        (str(PYQT6_DIR / "config"),   "config"),
        (str(PYQT6_DIR / "api"),      "api"),
    ],
    hiddenimports=[
        # uvicorn et ses sous-modules (non détectés automatiquement par PyInstaller)
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.middleware",
        "uvicorn.middleware.proxy_headers",
        # fastapi / starlette
        "fastapi",
        "fastapi.middleware",
        "fastapi.middleware.cors",
        "starlette",
        "starlette.routing",
        "starlette.middleware",
        "starlette.staticfiles",
        # pydantic
        "pydantic",
        "pydantic.deprecated.class_validators",
        "pydantic_core",
        # anyio (requis par uvicorn)
        "anyio",
        "anyio._backends._asyncio",
        # httpx (utilisé par openclaw_service)
        "httpx",
        # python-dotenv
        "dotenv",
        "dotenv.main",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Nudge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # True = console visible, pratique pour voir les erreurs de démarrage
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(PYQT6_DIR / "icon.ico")],
)
