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


class KnowledgeCardCreate(BaseModel):
    content: str = Field(..., min_length=1)
    source: str | None = None
    tags: str | None = None


class KnowledgeCardResponse(BaseModel):
    id: int
    content: str
    source: str | None = None
    tags: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyMessage(BaseModel):
    date: str
    count: int


class TagCount(BaseModel):
    tag: str
    count: int


class DashboardStats(BaseModel):
    conversation_count: int
    message_count: int
    card_count: int
    active_days: int
    daily_messages: list[DailyMessage]
    top_tags: list[TagCount]
