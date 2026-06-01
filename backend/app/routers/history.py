from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationResponse, MessageResponse
from app.services.chat_service import create_conversation, list_conversations, get_messages
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
