"""
Serveur API Nudge (optionnel) — à lancer séparément de nudge.py.

Usage :
    cd "PyQt 6"
    python api_server.py

L'API écoute sur http://127.0.0.1:8000 par défaut.
Configurez NUDGE_API_HOST / NUDGE_API_PORT dans .env pour changer.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from config.settings import API_HOST, API_PORT

if __name__ == "__main__":
    print(f"[NUDGE API] Démarrage sur http://{API_HOST}:{API_PORT}")
    print(f"[NUDGE API] Documentation : http://{API_HOST}:{API_PORT}/docs")
    uvicorn.run("api.app:app", host=API_HOST, port=API_PORT, reload=False)
