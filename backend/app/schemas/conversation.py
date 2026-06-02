from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str = Field(default="新对话", max_length=100)


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)


class ConversationResponse(BaseModel):
    id: int
    title: str
    pinned: bool = False
    archived: bool = False
    system_prompt: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    images: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    conversation_id: int
    content: str = ""
    model: str | None = None
    regenerate: bool = False
    images: list[str] | None = None


class SystemPromptUpdate(BaseModel):
    system_prompt: Optional[str] = None
