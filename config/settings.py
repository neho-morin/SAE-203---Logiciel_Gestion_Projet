import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_PATH = os.path.join(BASE_DIR, "nudge.db")

APP_NAME    = "Nudge"
APP_VERSION = "0.1.0"

# ── Mode envoi ────────────────────────────────────────────────────────────────
# True  → simulation console uniquement (aucun mail réel)
# False → envoi SMTP réel (nécessite les paramètres ci-dessous)
MAIL_SIMULATE = os.getenv("NUDGE_SIMULATE", "true").lower() == "true"

# ── Paramètres SMTP ───────────────────────────────────────────────────────────
# Ne jamais écrire les credentials en dur ici — utiliser des variables d'env.
# Exemples de configuration :
#   export NUDGE_SMTP_HOST=smtp.gmail.com
#   export NUDGE_SMTP_PORT=587
#   export NUDGE_SMTP_USER=votre.adresse@gmail.com
#   export NUDGE_SMTP_PASS=xxxx xxxx xxxx xxxx   ← mot de passe d'application Gmail
#   export NUDGE_SIMULATE=false
SMTP_HOST = os.getenv("NUDGE_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("NUDGE_SMTP_PORT", "587"))
SMTP_USER = os.getenv("NUDGE_SMTP_USER", "")
SMTP_PASS = os.getenv("NUDGE_SMTP_PASS", "")
