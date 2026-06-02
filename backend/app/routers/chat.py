from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.conversation import ChatRequest
from app.services.ai_service import verify_conversation_owner, save_user_message, load_history, call_ai_api
from app.utils.security import get_current_user


class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1)

router = APIRouter(tags=["AI 对话"])


@router.post("/chat")
def chat(data: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    verify_conversation_owner(data.conversation_id, user, db)

    if data.regenerate:
        last_assistant = (
            db.query(Message)
            .filter(Message.conversation_id == data.conversation_id, Message.role == "assistant")
            .order_by(Message.created_at.desc())
            .first()
        )
        if last_assistant:
            db.delete(last_assistant)
            db.commit()
    else:
        save_user_message(data.conversation_id, data.content, db)

    history, conv = load_history(data.conversation_id, db)
    chunks, full_response = call_ai_api(history, model=data.model)

    if full_response:
        msg = Message(
            conversation_id=data.conversation_id,
            role="assistant",
            content=full_response,
        )
        db.add(msg)
        db.commit()

    def generate():
        for chunk in chunks:
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/conversations/{conversation_id}/export")
def export_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = verify_conversation_owner(conversation_id, user, db)
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    lines = [f"# {conv.title}\n"]
    for m in messages:
        label = "用户" if m.role == "user" else "AI"
        lines.append(f"**{label}**: {m.content}\n")

    content = "\n".join(lines)
    return PlainTextResponse(
        content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="conversation-{conversation_id}.md"'},
    )


@router.get("/models")
def list_models():
    return {
        "models": [
            {"id": "mimo-v2.5-pro", "name": "MiMo v2.5 Pro"},
        ],
        "default": "mimo-v2.5-pro",
    }


def _verify_message_owner(message_id: int, user: User, db: Session) -> Message:
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    conv = db.query(Conversation).filter(
        Conversation.id == msg.conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作")
    return msg


@router.put("/messages/{message_id}")
def edit_message(message_id: int, data: MessageUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = _verify_message_owner(message_id, user, db)
    msg.content = data.content
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "role": msg.role, "content": msg.content, "created_at": str(msg.created_at)}


@router.delete("/messages/{message_id}")
def delete_message(message_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = _verify_message_owner(message_id, user, db)
    db.delete(msg)
    db.commit()
    return {"message": "消息已删除"}
