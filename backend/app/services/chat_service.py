"""会话管理服务模块

处理会话的 CRUD 操作，包括创建、列表查询、重命名、删除、置顶和归档。
所有操作均校验用户归属权。
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationResponse, MessageResponse


def create_conversation(data: ConversationCreate, user: User, db: Session) -> ConversationResponse:
    """创建新会话，默认标题为「新对话」"""
    conv = Conversation(user_id=user.id, title=data.title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationResponse.model_validate(conv)


def list_conversations(user: User, db: Session, limit: int = 500) -> list[ConversationResponse]:
    """获取用户的会话列表，置顶优先，其次按创建时间倒序（默认上限 500）"""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.pinned.desc(), Conversation.created_at.desc())
        .limit(limit)
        .all()
    )
    return [ConversationResponse.model_validate(c) for c in convs]


def get_messages(conversation_id: int, user: User, db: Session, skip: int = 0, limit: int = 0) -> dict:
    """获取指定会话的消息列表（按时间正序）

    先校验会话归属权，再返回该会话的消息。
    支持分页：skip 跳过前 N 条，limit 限制返回数量（0 表示返回全部）。

    Returns:
        {"total": 总数, "messages": 消息列表}
    """
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 查询总数
    total = db.query(Message).filter(Message.conversation_id == conversation_id).count()

    query = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    if skip > 0:
        query = query.offset(skip)
    if limit > 0:
        query = query.limit(limit)

    messages = query.all()
    return {"total": total, "messages": [MessageResponse.model_validate(m) for m in messages]}


def rename_conversation(conversation_id: int, title: str, user: User, db: Session) -> ConversationResponse:
    """重命名会话标题"""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    conv.title = title
    db.commit()
    db.refresh(conv)
    return ConversationResponse.model_validate(conv)


def delete_conversation(conversation_id: int, user: User, db: Session) -> None:
    """删除会话及其所有关联消息（级联删除）"""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    db.delete(conv)
    db.commit()


def toggle_pin(conversation_id: int, user: User, db: Session) -> ConversationResponse:
    """切换会话的置顶状态"""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    conv.pinned = not conv.pinned
    db.commit()
    db.refresh(conv)
    return ConversationResponse.model_validate(conv)


def toggle_archive(conversation_id: int, user: User, db: Session) -> ConversationResponse:
    """切换会话的归档状态"""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    conv.archived = not conv.archived
    db.commit()
    db.refresh(conv)
    return ConversationResponse.model_validate(conv)
