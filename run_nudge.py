#!/usr/bin/env python3
"""
Launcher Nudge.

Lance le serveur API local, attend qu'il soit prêt, puis ouvre l'interface PyQt6.
Arrête le serveur API à la fermeture de l'application.

Usage :
    python run_nudge.py
"""
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT  = Path(__file__).parent
PYQT6 = ROOT / "PyQt 6"

# Lire host/port depuis .env (sans dépendance externe)
_API_HOST = "127.0.0.1"
_API_PORT = 8000
_env_file = ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        if _line.startswith("NUDGE_API_HOST="):
            _API_HOST = _line.split("=", 1)[1].strip()
        elif _line.startswith("NUDGE_API_PORT="):
            try:
                _API_PORT = int(_line.split("=", 1)[1].strip())
            except ValueError:
                pass

_HEALTH_URL = f"http://{_API_HOST}:{_API_PORT}/health"
_TIMEOUT    = 15  # secondes max pour attendre que l'API soit prête


def _api_ready() -> bool:
    try:
        urllib.request.urlopen(_HEALTH_URL, timeout=2)
        return True
    except Exception:
        return False


def _wait_for_api(timeout: int) -> bool:
    for _ in range(timeout * 2):  # vérifie toutes les 0,5 s
        if _api_ready():
            return True
        time.sleep(0.5)
    return False


def main() -> None:
    api_proc = None

    # ── Démarrer le serveur API ───────────────────────────────────────────────
    if _api_ready():
        print("[Nudge] Serveur API déjà actif — réutilisation.")
    else:
        print(f"[Nudge] Démarrage du serveur API ({_API_HOST}:{_API_PORT})…")
        api_proc = subprocess.Popen(
            [sys.executable, "api_server.py"],
            cwd=str(PYQT6),
        )
        if not _wait_for_api(_TIMEOUT):
            api_proc.terminate()
            print(f"[Nudge] ERREUR : le serveur API n'a pas répondu dans les {_TIMEOUT}s.")
            print("[Nudge] Vérifiez les messages ci-dessus pour plus de détails.")
            sys.exit(1)
        print("[Nudge] Serveur API prêt.")

    # ── Lancer l'interface PyQt6 ──────────────────────────────────────────────
    print("[Nudge] Démarrage de l'interface…")
    try:
        result = subprocess.run(
            [sys.executable, "nudge.py"],
            cwd=str(PYQT6),
        )
    finally:
        if api_proc is not None:
            print("[Nudge] Arrêt du serveur API…")
            api_proc.terminate()
            try:
                api_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_proc.kill()

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
