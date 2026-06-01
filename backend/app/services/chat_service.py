from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationResponse, MessageResponse


def create_conversation(data: ConversationCreate, user: User, db: Session) -> ConversationResponse:
    conv = Conversation(user_id=user.id, title=data.title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationResponse.model_validate(conv)


def list_conversations(user: User, db: Session) -> list[ConversationResponse]:
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return [ConversationResponse.model_validate(c) for c in convs]


def get_messages(conversation_id: int, user: User, db: Session) -> list[MessageResponse]:
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [MessageResponse.model_validate(m) for m in messages]
