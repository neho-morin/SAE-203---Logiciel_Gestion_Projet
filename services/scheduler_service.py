from apscheduler.schedulers.background import BackgroundScheduler
import services.relance_service as relance_service
import services.mail_service as mail_service

_scheduler: BackgroundScheduler | None = None


def run_check() -> None:
    """
    Point d'entrée du scheduler.
    Détecte les tâches à relancer, simule l'envoi et logue en DB.
    """
    print("[NUDGE] Vérification des relances…")
    tasks_to_remind = relance_service.get_tasks_needing_reminder()

    if not tasks_to_remind:
        print("[NUDGE] Aucune relance à envoyer.")
        return

    for task, type_ in tasks_to_remind:
        email = task.get("responsable_email") or ""
        subject, body = mail_service.build_message(task, type_)
        success = mail_service.send(email, subject, body, simulate=True)

        if success:
            relance_service.log(
                tache_id=task["id"],
                tache_titre=task["titre"],
                email=email or "—",
                mode="Simulation",
                type_=type_,
            )
            print(f"[NUDGE] Relance '{type_}' loguée pour : {task['titre']}")


def start(run_immediately: bool = False) -> None:
    """
    Démarre le scheduler APScheduler en arrière-plan.
    La vérification est lancée chaque jour à 8h00.
    """
    global _scheduler

    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(run_check, "cron", hour=8, minute=0, id="daily_check")
    _scheduler.start()
    print("[NUDGE] Scheduler démarré — vérification quotidienne à 08h00.")

    if run_immediately:
        run_check()


def stop() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        print("[NUDGE] Scheduler arrêté.")
