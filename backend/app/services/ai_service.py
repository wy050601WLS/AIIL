import json
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.conversation import ChatRequest


def save_user_message(conversation_id: int, content: str, db: Session) -> None:
    msg = Message(conversation_id=conversation_id, role="user", content=content)
    db.add(msg)
    db.commit()


def load_history(conversation_id: int, db: Session) -> list[dict]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in messages if m.content]


def verify_conversation_owner(conversation_id: int, user: User, db: Session) -> Conversation:
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return conv


def call_ai_api(history: list[dict], model: str | None = None) -> tuple[list[str], str]:
    url = f"{settings.AI_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or settings.AI_MODEL,
        "max_tokens": 4096,
        "stream": True,
        "messages": history,
    }

    chunks = []
    full = ""
    with httpx.Client(timeout=120.0) as client:
        with client.stream("POST", url, headers=headers, json=payload) as response:
            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        full += content
                        chunks.append(content)
                except json.JSONDecodeError:
                    continue
    return chunks, full
