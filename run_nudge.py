#!/usr/bin/env python3
"""
Launcher Nudge — compatible développement et exécutable PyInstaller.

Usage :
    python run_nudge.py          # dev
    ./dist/Nudge/Nudge           # frozen Linux
    dist\\Nudge\\Nudge.exe        # frozen Windows
"""
import sys
import time
import urllib.request
from pathlib import Path

# ── Détection du mode frozen ──────────────────────────────────────────────────
IS_FROZEN: bool = getattr(sys, "frozen", False)

# ── Chemins ───────────────────────────────────────────────────────────────────
if IS_FROZEN:
    # En mode frozen, tout est dans sys._MEIPASS (déjà dans sys.path)
    BUNDLE_ROOT = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
else:
    # En dev, les modules sont dans "PyQt 6/"
    ROOT  = Path(__file__).resolve().parent
    PYQT6 = ROOT / "PyQt 6"
    if str(PYQT6) not in sys.path:
        sys.path.insert(0, str(PYQT6))

# ── Lecture du host/port (avant import de settings pour éviter la circularité) ─
_API_HOST = "127.0.0.1"
_API_PORT = 8000

# Lecture directe du .env sans dépendance externe
def _read_env_var(key: str, default: str) -> str:
    from config.paths import get_env_path
    env_file = get_env_path()
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    return default

_API_HOST = _read_env_var("NUDGE_API_HOST", _API_HOST)
try:
    _API_PORT = int(_read_env_var("NUDGE_API_PORT", str(_API_PORT)))
except ValueError:
    pass

_HEALTH_URL = f"http://{_API_HOST}:{_API_PORT}/health"
_TIMEOUT    = 15  # secondes max


def _api_ready() -> bool:
    try:
        urllib.request.urlopen(_HEALTH_URL, timeout=2)
        return True
    except Exception:
        return False


def _wait_for_api(timeout: int) -> bool:
    for _ in range(timeout * 2):
        if _api_ready():
            return True
        time.sleep(0.5)
    return False


def main() -> None:
    # ── Démarrer l'API en thread (pas de subprocess) ──────────────────────────
    if _api_ready():
        print("[Nudge] Serveur API déjà actif — réutilisation.")
    else:
        print(f"[Nudge] Démarrage du serveur API ({_API_HOST}:{_API_PORT})…")
        from api_server import start_in_thread
        start_in_thread(_API_HOST, _API_PORT)

        if not _wait_for_api(_TIMEOUT):
            print(f"[Nudge] ERREUR : le serveur API n'a pas répondu dans les {_TIMEOUT}s.")
            sys.exit(1)
        print("[Nudge] Serveur API prêt.")

    # ── Lancer l'interface PyQt6 (import direct, pas de subprocess) ───────────
    print("[Nudge] Démarrage de l'interface…")
    from nudge import main as start_ui
    start_ui()


if __name__ == "__main__":
    main()
