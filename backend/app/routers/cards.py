"""知识卡片路由模块

提供知识卡片的创建、列表查询和删除功能。
前缀：/cards，所有端点需登录。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import KnowledgeCard
from app.models.user import User
from app.schemas.conversation import KnowledgeCardCreate, KnowledgeCardUpdate, KnowledgeCardResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/cards", tags=["知识卡片"])


@router.post("", response_model=KnowledgeCardResponse)
def create_card(data: KnowledgeCardCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """创建知识卡片，从 AI 回复中提取精华内容保存"""
    card = KnowledgeCard(
        user_id=user.id,
        content=data.content,
        source=data.source,
        tags=data.tags,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.get("", response_model=list[KnowledgeCardResponse])
def list_cards(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的知识卡片列表（按创建时间倒序）"""
    return (
        db.query(KnowledgeCard)
        .filter(KnowledgeCard.user_id == user.id)
        .order_by(KnowledgeCard.created_at.desc())
        .all()
    )


@router.put("/{card_id}", response_model=KnowledgeCardResponse)
def update_card(card_id: int, data: KnowledgeCardUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新知识卡片内容和标签（仅更新非空字段）"""
    card = db.query(KnowledgeCard).filter(
        KnowledgeCard.id == card_id,
        KnowledgeCard.user_id == user.id,
    ).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")
    if data.content is not None:
        card.content = data.content
    if data.tags is not None:
        card.tags = data.tags
    db.commit()
    db.refresh(card)
    return card


@router.delete("/{card_id}")
def delete_card(card_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除知识卡片（校验归属权）"""
    card = db.query(KnowledgeCard).filter(
        KnowledgeCard.id == card_id,
        KnowledgeCard.user_id == user.id,
    ).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")
    db.delete(card)
    db.commit()
    return {"message": "卡片已删除"}
