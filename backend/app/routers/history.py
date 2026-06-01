from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse, MessageResponse
from app.services.chat_service import (
    create_conversation, list_conversations, get_messages,
    rename_conversation, delete_conversation,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/conversations", tags=["会话管理"])


@router.post("", response_model=ConversationResponse)
def create(data: ConversationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_conversation(data, user, db)


@router.get("", response_model=list[ConversationResponse])
def list_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_conversations(user, db)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def messages(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_messages(conversation_id, user, db)


@router.put("/{conversation_id}", response_model=ConversationResponse)
def rename(conversation_id: int, data: ConversationUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return rename_conversation(conversation_id, data.title, user, db)


@router.delete("/{conversation_id}")
def delete(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_conversation(conversation_id, user, db)
    return {"message": "会话已删除"}
