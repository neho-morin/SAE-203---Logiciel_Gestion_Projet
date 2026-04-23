from datetime import date

_SUBJECTS = {
    "j-2":        "⏰ Rappel : tâche à rendre dans 2 jours",
    "jour-j":     "🔔 Aujourd'hui : échéance de votre tâche",
    "depassement": "🚨 Retard : tâche en dépassement",
    "manuel":     "📧 Relance manuelle",
}


def build_message(task: dict, type_: str) -> tuple[str, str]:
    """Retourne (sujet, corps) selon le type de relance."""
    subject    = _SUBJECTS.get(type_, "Relance Nudge")
    titre      = task["titre"]
    echeance   = task.get("echeance", "—")
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


def send(to_email: str, subject: str, body: str, simulate: bool = True) -> bool:
    """
    Envoie (ou simule) un mail.
    Retourne True si l'envoi a réussi (ou la simulation s'est déroulée correctement).
    """
    if not to_email:
        print("[NUDGE] Aucun email destinataire — relance ignorée.")
        return False

    if simulate:
        sep = "─" * 52
        print(f"\n[NUDGE SIMULATION] {sep}")
        print(f"  À       : {to_email}")
        print(f"  Sujet   : {subject}")
        print(f"  Message :")
        for line in body.splitlines():
            print(f"    {line}")
        print(f"  {sep}\n")
        return True

    # ── Phase 5 : envoi SMTP réel ──────────────────────────────────────────
    # import smtplib
    # from email.mime.text import MIMEText
    # from config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    # msg = MIMEText(body, "plain", "utf-8")
    # msg["Subject"] = subject
    # msg["From"]    = SMTP_USER
    # msg["To"]      = to_email
    # with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
    #     server.login(SMTP_USER, SMTP_PASS)
    #     server.send_message(msg)
    # return True
    return False
