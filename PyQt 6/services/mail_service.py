import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

from config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_SIMULATE

_SUBJECTS = {
    "j-2":         "⏰ Rappel : tâche à rendre dans 2 jours",
    "jour-j":      "🔔 Aujourd'hui : échéance de votre tâche",
    "depassement": "🚨 Retard : tâche en dépassement",
    "manuel":      "📧 Relance manuelle",
}


def build_message(task: dict, type_: str) -> tuple[str, str]:
    """Retourne (sujet, corps) selon le type de relance."""
    subject     = _SUBJECTS.get(type_, "Relance Nudge")
    titre       = task["titre"]
    echeance    = task.get("echeance", "—")
    responsable = task.get("responsable") or "Responsable"

    if type_ == "j-2":
        body = (
            f"Bonjour {responsable},\n\n"
            f"La tâche suivante arrive à échéance dans 2 jours :\n"
            f"  ▸ {titre}\n"
            f"  ▸ Échéance : {echeance}\n\n"
            f"Merci de veiller à la finaliser avant la date limite.\n\n"
            f"Cordialement,\nNudge"
        )
    elif type_ == "jour-j":
        body = (
            f"Bonjour {responsable},\n\n"
            f"La tâche suivante est due aujourd'hui ({date.today().isoformat()}) :\n"
            f"  ▸ {titre}\n\n"
            f"Merci de la compléter dès que possible.\n\n"
            f"Cordialement,\nNudge"
        )
    else:  # depassement ou manuel
        body = (
            f"Bonjour {responsable},\n\n"
            f"La tâche suivante est en retard :\n"
            f"  ▸ {titre}\n"
            f"  ▸ Échéance initiale : {echeance}\n\n"
            f"Merci de prendre les mesures nécessaires rapidement.\n\n"
            f"Cordialement,\nNudge"
        )

    return subject, body


def send(to_email: str, subject: str, body: str, simulate: bool = MAIL_SIMULATE) -> bool:
    """
    Envoie un mail ou l'affiche en simulation.
    Le paramètre `simulate` prend par défaut la valeur de MAIL_SIMULATE dans settings.py.
    Retourne True si l'opération a réussi.
    """
    if not to_email:
        print("[NUDGE] Aucun email destinataire — relance ignorée.")
        return False

    if simulate:
        _print_simulation(to_email, subject, body)
        return True

    return _send_smtp(to_email, subject, body)


# ── Privé ─────────────────────────────────────────────────────────────────────

def _print_simulation(to_email: str, subject: str, body: str) -> None:
    sep = "─" * 52
    print(f"\n[NUDGE SIMULATION] {sep}")
    print(f"  À       : {to_email}")
    print(f"  Sujet   : {subject}")
    print(f"  Message :")
    for line in body.splitlines():
        print(f"    {line}")
    print(f"  {sep}\n")


def _send_smtp(to_email: str, subject: str, body: str) -> bool:
    """Envoi réel via SMTP avec STARTTLS (Gmail port 587)."""
    if not SMTP_USER or not SMTP_PASS:
        print("[NUDGE] SMTP_USER ou SMTP_PASS non configurés — envoi annulé.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = SMTP_USER
        msg["To"]      = to_email
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"[NUDGE] ✅ Mail envoyé à {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[NUDGE] ❌ Authentification SMTP échouée — vérifiez SMTP_USER et SMTP_PASS.")
        return False
    except smtplib.SMTPConnectError:
        print(f"[NUDGE] ❌ Impossible de se connecter à {SMTP_HOST}:{SMTP_PORT}.")
        return False
    except smtplib.SMTPRecipientsRefused:
        print(f"[NUDGE] ❌ Adresse refusée par le serveur : {to_email}")
        return False
    except TimeoutError:
        print(f"[NUDGE] ❌ Timeout — connexion à {SMTP_HOST} trop lente.")
        return False
    except smtplib.SMTPException as e:
        print(f"[NUDGE] ❌ Erreur SMTP : {e}")
        return False
