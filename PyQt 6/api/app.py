from datetime import date
from fastapi import FastAPI, Depends, HTTPException, Query

from api.auth import verify_token
from api.schemas import (
    ManualReminderRequest, MailPreviewRequest, MailPreviewResponse,
    AssistantChatRequest, AssistantChatResponse,
)
import services.project_service as project_service
import services.task_service as task_service
import services.relance_service as relance_service
import services.mail_service as mail_service
import services.openclaw_service as openclaw_service
from services.context_service import build_nudge_context
from database.db import init_db

init_db()

app = FastAPI(
    title="Nudge API",
    version="1.0.0",
    description="API locale Nudge — accès réservé à OpenClaw via token Bearer",
)


def _is_late(task: dict) -> bool:
    if task["statut"] == "Terminée":
        return False
    try:
        return (date.fromisoformat(task["echeance"]) - date.today()).days < 0
    except (ValueError, TypeError):
        return False



@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "nudge-api"}


@app.get("/projects", tags=["Projets"], dependencies=[Depends(verify_token)])
async def get_projects():
    return project_service.get_all()


@app.get("/tasks", tags=["Tâches"], dependencies=[Depends(verify_token)])
async def get_tasks():
    return task_service.get_all()


@app.get("/tasks/late", tags=["Tâches"], dependencies=[Depends(verify_token)])
async def get_late_tasks():
    return [t for t in task_service.get_all() if _is_late(t)]


@app.get("/reminders", tags=["Relances"], dependencies=[Depends(verify_token)])
async def get_reminders(limit: int = Query(default=20, ge=1, le=200)):
    return relance_service.get_recent(limit)


@app.post("/reminders/manual", tags=["Relances"], dependencies=[Depends(verify_token)])
async def post_manual_reminder(body: ManualReminderRequest):
    ok, message = relance_service.send_manual_reminder(body.task_id)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message}


@app.post("/ai/mail-preview", tags=["AI"], dependencies=[Depends(verify_token)], response_model=MailPreviewResponse)
async def post_mail_preview(body: MailPreviewRequest):
    """
    Retourne un aperçu du mail de relance pour une tâche.
    Si custom_body est fourni (reformulation OpenClaw), il remplace le corps généré.
    """
    task = task_service.get_by_id(body.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")

    subject, built_body = mail_service.build_message(task, body.type_)
    final_body = body.custom_body if body.custom_body else built_body

    return MailPreviewResponse(subject=subject, body=final_body)


@app.post("/assistant/chat", tags=["Assistant"], dependencies=[Depends(verify_token)], response_model=AssistantChatResponse)
async def assistant_chat(body: AssistantChatRequest):
    """
    Récupère le contexte Nudge (tâches, projets, retards, priorités) depuis la base,
    puis appelle OpenClaw avec ce contexte + le message utilisateur.
    Le token OpenClaw reste côté serveur — le frontend ne le voit jamais.
    """
    nudge_context = build_nudge_context()
    try:
        reply = await openclaw_service.ask(body.message, nudge_context)
        return AssistantChatResponse(reply=reply)
    except openclaw_service.OpenClawError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
