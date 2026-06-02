from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import KnowledgeCard
from app.models.user import User
from app.schemas.conversation import KnowledgeCardCreate, KnowledgeCardResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/cards", tags=["知识卡片"])


@router.post("", response_model=KnowledgeCardResponse)
def create_card(data: KnowledgeCardCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
    return (
        db.query(KnowledgeCard)
        .filter(KnowledgeCard.user_id == user.id)
        .order_by(KnowledgeCard.created_at.desc())
        .all()
    )


@router.delete("/{card_id}")
def delete_card(card_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card = db.query(KnowledgeCard).filter(
        KnowledgeCard.id == card_id,
        KnowledgeCard.user_id == user.id,
    ).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")
    db.delete(card)
    db.commit()
    return {"message": "卡片已删除"}
