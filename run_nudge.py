#!/usr/bin/env python3
"""
Launcher Nudge.

Lance le serveur API local (optionnel), attend qu'il soit prêt, puis ouvre
l'interface PyQt6. Si l'API ne démarre pas, l'interface se lance quand même
en mode dégradé (fonctions IA désactivées, reste fonctionnel).

Usage :
    python run_nudge.py
"""
import subprocess
import sys
import time
import socket
import threading
import urllib.request
from pathlib import Path

ROOT  = Path(__file__).parent
PYQT6 = ROOT / "PyQt 6"

# ── Lire host/port depuis .env (sans dépendance externe) ─────────────────────
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


def _port_in_use() -> bool:
    """Vérifie si le port est déjà occupé par un autre processus."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((_API_HOST, _API_PORT)) == 0


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


def _stream_subprocess_output(proc: subprocess.Popen, log_lines: list) -> None:
    """Lit stdout+stderr du sous-processus en arrière-plan et affiche chaque ligne."""
    try:
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip()
            print(f"  [API] {line}")
            log_lines.append(line)
    except Exception:
        pass


def _start_api_subprocess() -> tuple[subprocess.Popen | None, list[str]]:
    """
    Lance api_server.py comme sous-processus.
    Retourne (proc, log_lines) ou (None, [message_erreur]) si le lancement échoue.
    """
    log_lines: list[str] = []

    if _api_ready():
        print("[Nudge] Serveur API déjà actif — réutilisation.")
        return None, log_lines

    if _port_in_use():
        msg = (
            f"[Nudge] AVERTISSEMENT : le port {_API_PORT} est occupé "
            "mais l'API Nudge ne répond pas.\n"
            "[Nudge] Un autre programme utilise peut-être ce port.\n"
            "[Nudge] Lancement de l'interface sans API dédiée."
        )
        print(msg)
        log_lines.append(msg)
        return None, log_lines

    print(f"[Nudge] Démarrage du serveur API ({_API_HOST}:{_API_PORT})…")

    api_script = PYQT6 / "api_server.py"
    if not api_script.exists():
        msg = f"[Nudge] ERREUR : api_server.py introuvable dans {PYQT6}"
        print(msg)
        log_lines.append(msg)
        return None, log_lines

    try:
        proc = subprocess.Popen(
            [sys.executable, "api_server.py"],
            cwd=str(PYQT6),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # redirige stderr vers stdout pour tout capturer
        )
    except Exception as exc:
        msg = f"[Nudge] ERREUR : impossible de lancer api_server.py : {exc}"
        print(msg)
        log_lines.append(msg)
        return None, log_lines

    # Démarrer la lecture en arrière-plan pour éviter que le buffer se bloque
    t = threading.Thread(target=_stream_subprocess_output, args=(proc, log_lines), daemon=True)
    t.start()

    # Attendre un peu pour détecter un crash immédiat
    time.sleep(0.8)
    if proc.poll() is not None:
        # Le processus a déjà quitté — il a crashé
        time.sleep(0.2)  # laisser le thread de lecture finir
        last = "\n".join(f"  {l}" for l in log_lines[-15:]) if log_lines else "  (aucun message capturé)"
        print(
            "\n[Nudge] ERREUR : le serveur API a crashé immédiatement au démarrage.\n"
            f"[Nudge] Cause probable : dépendance manquante ou erreur de configuration.\n"
            f"[Nudge] Dernier message :\n{last}\n"
            "[Nudge] Lancement de l'interface sans API (mode dégradé)."
        )
        return None, log_lines

    return proc, log_lines


def main() -> None:
    api_proc = None

    # ── Démarrer le serveur API (optionnel) ───────────────────────────────────
    if not _api_ready():
        api_proc, api_logs = _start_api_subprocess()

        if api_proc is not None:
            if _wait_for_api(_TIMEOUT):
                print("[Nudge] Serveur API prêt.")
            else:
                last = "\n".join(f"  {l}" for l in api_logs[-15:]) if api_logs else "  (aucun message capturé)"
                print(
                    f"\n[Nudge] ERREUR : le serveur API n'a pas répondu dans les {_TIMEOUT}s.\n"
                    f"[Nudge] Dernier message :\n{last}\n"
                    "[Nudge] Lancement de l'interface sans API (mode dégradé)."
                )
                api_proc.terminate()
                try:
                    api_proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    api_proc.kill()
                api_proc = None
    else:
        print("[Nudge] Serveur API déjà actif — réutilisation.")

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
