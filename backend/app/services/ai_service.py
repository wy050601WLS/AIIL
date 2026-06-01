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


def create_assistant_message(conversation_id: int, db: Session) -> Message:
    msg = Message(conversation_id=conversation_id, role="assistant", content="")
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def update_assistant_message(msg_id: int, content: str, db: Session) -> None:
    db.query(Message).filter(Message.id == msg_id).update({"content": content})
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


def stream_chat(data: ChatRequest, user: User, db: Session):
    verify_conversation_owner(data.conversation_id, user, db)
    save_user_message(data.conversation_id, data.content, db)

    history = load_history(data.conversation_id, db)

    url = f"{settings.AI_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.AI_MODEL,
        "max_tokens": 4096,
        "stream": True,
        "messages": history,
    }

    assistant_msg = create_assistant_message(data.conversation_id, db)
    full_response = ""

    try:
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
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            full_response += content
                            yield f"data: {content}\n\n"
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    finally:
        if full_response:
            update_assistant_message(assistant_msg.id, full_response, db)
        yield "data: [DONE]\n\n"
