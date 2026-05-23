"""
Serveur API Nudge — utilisable en script ou importé par run_nudge.py.

Usage direct :
    cd "PyQt 6"
    python api_server.py

Ou depuis run_nudge.py (mode import, sans subprocess) :
    from api_server import start_in_thread
    start_in_thread()
"""
import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from config.settings import API_HOST, API_PORT


def start_in_thread(host: str = API_HOST, port: int = API_PORT) -> None:
    """Lance uvicorn dans un thread daemon — retourne immédiatement."""
    def _run():
        uvicorn.run("api.app:app", host=host, port=port, log_level="warning")

    t = threading.Thread(target=_run, daemon=True, name="nudge-api")
    t.start()


if __name__ == "__main__":
    print(f"[NUDGE API] Démarrage sur http://{API_HOST}:{API_PORT}")
    print(f"[NUDGE API] Documentation : http://{API_HOST}:{API_PORT}/docs")
    uvicorn.run("api.app:app", host=API_HOST, port=API_PORT, reload=False)
