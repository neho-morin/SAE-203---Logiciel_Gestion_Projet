from pydantic import BaseModel
from typing import Optional


class ManualReminderRequest(BaseModel):
    task_id: int


class MailPreviewRequest(BaseModel):
    task_id: int
    type_: str = "manuel"
    custom_body: Optional[str] = None


class MailPreviewResponse(BaseModel):
    subject: str
    body: str


class AssistantChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class AssistantChatResponse(BaseModel):
    reply: str
