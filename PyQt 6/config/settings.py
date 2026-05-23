import os
from dotenv import load_dotenv
from config.paths import get_env_path, get_db_path

# Charge le .env depuis le bon emplacement (dev ou frozen)
load_dotenv(str(get_env_path()), override=False)

# Base de données
DATABASE_PATH = str(get_db_path())

# SMTP — priorité aux clés NUDGE_SMTP_*, fallback sur SMTP_* pour rétrocompatibilité
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("NUDGE_SMTP_USER") or os.getenv("SMTP_USER", "")
SMTP_PASS     = os.getenv("NUDGE_SMTP_PASS") or os.getenv("SMTP_PASSWORD", "")

# True = simulation (pas d'envoi réel), False = envoi SMTP réel
# priorité à NUDGE_SIMULATE, fallback sur MAIL_SIMULATE
MAIL_SIMULATE = (os.getenv("NUDGE_SIMULATE") or os.getenv("MAIL_SIMULATE", "true")).lower() == "true"

# API locale Nudge (exposée à OpenClaw)
API_TOKEN = os.getenv("NUDGE_API_TOKEN", "")
API_HOST  = os.getenv("NUDGE_API_HOST", "127.0.0.1")
API_PORT  = int(os.getenv("NUDGE_API_PORT", "8000"))

# Client OpenClaw (HTTP OpenAI-compatible)
OPENCLAW_BASE_URL = os.getenv("OPENCLAW_BASE_URL", "")
OPENCLAW_TOKEN    = os.getenv("OPENCLAW_TOKEN", "")
OPENCLAW_MODEL    = os.getenv("OPENCLAW_MODEL", "openclaw/default")
OPENCLAW_TIMEOUT  = int(os.getenv("OPENCLAW_TIMEOUT", "60"))
