import os
from dotenv import load_dotenv

load_dotenv()

# Base de données
DATABASE_PATH = os.path.join(os.path.expanduser("~"), "nudge.db")

# SMTP
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASS     = os.getenv("SMTP_PASSWORD", "")

# True = simulation (pas d'envoi réel), False = envoi SMTP réel
MAIL_SIMULATE = os.getenv("MAIL_SIMULATE", "true").lower() == "true"

# API locale OpenClaw
API_TOKEN = os.getenv("NUDGE_API_TOKEN", "")
API_HOST  = os.getenv("NUDGE_API_HOST", "127.0.0.1")
API_PORT  = int(os.getenv("NUDGE_API_PORT", "8000"))
