from datetime import date
from database.db import get_connection


def get_recent(limit: int = 10) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM relances ORDER BY envoyee_le DESC LIMIT ?", (limit,)
    ).fetchall()
    return [
        {
            "email":     row["email"],
            "taskTitle": row["tache_titre"],
            "date":      row["envoyee_le"][:10],
            "mode":      row["mode"],
        }
        for row in rows
    ]


def log(tache_id: int, tache_titre: str, email: str,
        mode: str = "Simulation", type_: str = "manuel") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO relances (tache_id, tache_titre, email, type, mode) VALUES (?, ?, ?, ?, ?)",
        (tache_id, tache_titre, email, type_, mode),
    )
    conn.commit()


def already_sent_today(tache_id: int, type_: str) -> bool:
    today = date.today().isoformat()
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM relances WHERE tache_id = ? AND type = ? AND date(envoyee_le) = ?",
        (tache_id, type_, today),
    ).fetchone()
    return row is not None


def send_manual_reminder(task_id: int) -> tuple[bool, str]:
    """
    Relance manuelle directe sur une tâche.
    Envoie le mail (simulation ou réel selon settings) et enregistre l'historique.
    Aucune déduplication — une relance manuelle est toujours autorisée.
    Retourne (succès, message_utilisateur).
    """
    import services.task_service as task_service
    import services.mail_service as mail_service
    from config.settings import MAIL_SIMULATE

    task = task_service.get_by_id(task_id)
    if not task:
        return False, "Tâche introuvable."

    email = task.get("responsable_email") or ""
    if not email:
        return False, f"Aucun email pour la tâche « {task['titre']} »."

    subject, body = mail_service.build_message(task, "manuel")
    ok = mail_service.send(email, subject, body)

    if ok:
        mode = "Simulation" if MAIL_SIMULATE else "Réel"
        masked = email[:3] + "***" + email[email.find("@"):] if "@" in email else email
        log(task_id, task["titre"], masked, mode=mode, type_="manuel")

    return ok, ("Relance envoyée." if ok else "Échec de l'envoi.")


def get_tasks_needing_reminder() -> list[tuple[dict, str]]:
    """
    Retourne la liste des (tâche, type_relance) à traiter aujourd'hui.

    Règles :
      - diff == 2  → 'j-2'
      - diff == 0  → 'jour-j'
      - diff < 0   → 'depassement'
    Une relance du même type déjà envoyée aujourd'hui est ignorée.
    """
    import services.task_service as task_service  # import local pour éviter la circularité

    tasks = task_service.get_all()
    today = date.today()
    results = []

    for task in tasks:
        if task["statut"] == "Terminée":
            continue
        echeance_str = task.get("echeance", "")
        if not echeance_str:
            continue
        try:
            echeance = date.fromisoformat(echeance_str)
        except ValueError:
            continue

        diff = (echeance - today).days

        if diff == 2:
            type_ = "j-2"
        elif diff == 0:
            type_ = "jour-j"
        elif diff < 0:
            type_ = "depassement"
        else:
            continue

        email = task.get("responsable_email") or ""
        if not email:
            print(f"[NUDGE] Tâche '{task['titre']}' ignorée — aucun email responsable.")
            continue

        if not already_sent_today(task["id"], type_):
            results.append((task, type_))

    return results
