# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['nudge.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database', 'database'),
        ('services', 'services'),
        ('config', 'config'),
        ('api', 'api'),
    ],
    hiddenimports=[
        # uvicorn et ses sous-modules (non détectés automatiquement)
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.middleware',
        'uvicorn.middleware.proxy_headers',
        # fastapi / starlette
        'fastapi',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.staticfiles',
        # pydantic
        'pydantic',
        'pydantic.deprecated.class_validators',
        'pydantic_core',
        # anyio (requis par uvicorn)
        'anyio',
        'anyio._backends._asyncio',
        # httpx (utilisé par openclaw_service)
        'httpx',
        # python-dotenv
        'dotenv',
        'dotenv.main',
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
    name='Nudge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # True = fenêtre console visible (utile pour voir les erreurs)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
