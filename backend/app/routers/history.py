"""会话管理路由模块

提供会话的 CRUD 操作：创建、列表、消息查询、重命名、删除、置顶切换、归档切换。
前缀：/conversations，所有端点需登录。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse, MessageResponse
from app.services.chat_service import (
    create_conversation, list_conversations, get_messages,
    rename_conversation, delete_conversation,
    toggle_pin, toggle_archive,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/conversations", tags=["会话管理"])


@router.post("", response_model=ConversationResponse)
def create(data: ConversationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """创建新会话"""
    return create_conversation(data, user, db)


@router.get("", response_model=list[ConversationResponse])
def list_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的会话列表（置顶优先，其次按创建时间倒序）"""
    return list_conversations(user, db)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def messages(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取指定会话的消息列表（按时间正序）"""
    return get_messages(conversation_id, user, db)


@router.put("/{conversation_id}", response_model=ConversationResponse)
def rename(conversation_id: int, data: ConversationUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """重命名会话标题"""
    return rename_conversation(conversation_id, data.title, user, db)


@router.delete("/{conversation_id}")
def delete(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除会话及其所有关联消息"""
    delete_conversation(conversation_id, user, db)
    return {"message": "会话已删除"}


@router.put("/{conversation_id}/pin", response_model=ConversationResponse)
def pin(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """切换会话的置顶状态"""
    return toggle_pin(conversation_id, user, db)


@router.put("/{conversation_id}/archive", response_model=ConversationResponse)
def archive(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """切换会话的归档状态"""
    return toggle_archive(conversation_id, user, db)
