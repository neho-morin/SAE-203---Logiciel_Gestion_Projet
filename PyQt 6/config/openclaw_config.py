"""
Gestion de la configuration OpenClaw.

Stockée dans ~/.nudge_openclaw.json (jamais versionné dans Git).
Fallback sur les variables .env pour rétrocompatibilité.

Usage :
    from config.openclaw_config import load, save, mask_token
    cfg = load()
    cfg["gateway_url"] = "http://127.0.0.1:3000"
    save(cfg)
"""
import json
import os
from pathlib import Path

_CONFIG_FILE = Path(os.path.expanduser("~")) / ".nudge_openclaw.json"

DEFAULTS: dict = {
    "enabled": True,
    "gateway_url": "",
    "endpoint": "/chat/completions",
    "api_token": "",
    "bot_name": "nudge-bot",
    "timeout_seconds": 30,
    "retries": 2,
    "debug": False,
}


def load() -> dict:
    """
    Charge la config depuis ~/.nudge_openclaw.json.
    Si absent, tente un fallback sur les variables d'environnement (.env).
    """
    cfg = dict(DEFAULTS)

    if _CONFIG_FILE.exists():
        try:
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            # On ne prend que les clés connues pour éviter des données parasites
            for k in DEFAULTS:
                if k in data:
                    cfg[k] = data[k]
            return cfg
        except (json.JSONDecodeError, OSError):
            pass

    # Fallback rétrocompat : lire depuis les variables d'environnement
    try:
        from config.settings import (
            OPENCLAW_BASE_URL, OPENCLAW_TOKEN, OPENCLAW_MODEL, OPENCLAW_TIMEOUT
        )
        if OPENCLAW_BASE_URL:
            cfg["gateway_url"] = OPENCLAW_BASE_URL
        if OPENCLAW_TOKEN:
            cfg["api_token"] = OPENCLAW_TOKEN
        if OPENCLAW_TIMEOUT:
            cfg["timeout_seconds"] = int(OPENCLAW_TIMEOUT)
        if OPENCLAW_MODEL and OPENCLAW_MODEL != "openclaw/default":
            cfg["bot_name"] = OPENCLAW_MODEL
    except Exception:
        pass

    return cfg


def save(cfg: dict) -> None:
    """Sauvegarde la config dans ~/.nudge_openclaw.json."""
    to_save = {k: cfg.get(k, v) for k, v in DEFAULTS.items()}
    _CONFIG_FILE.write_text(
        json.dumps(to_save, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def mask_token(token: str) -> str:
    """
    Masque un token pour l'affichage sécurisé.
    Ex : "sk-abcdefghijklmnopqrstuvwxyz1234"  →  "sk-a**************************1234"
    """
    if not token:
        return "(non configuré)"
    n = len(token)
    if n <= 8:
        return "*" * n
    visible = min(4, n // 6)
    return f"{token[:visible]}{'*' * (n - visible * 2)}{token[-visible:]}"


def config_file_path() -> Path:
    """Retourne le chemin du fichier de configuration OpenClaw."""
    return _CONFIG_FILE
