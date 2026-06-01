from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.conversation import ChatRequest
from app.services.ai_service import stream_chat
from app.utils.security import get_current_user

router = APIRouter(tags=["AI 对话"])


@router.post("/chat")
def chat(data: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return StreamingResponse(
        stream_chat(data, user, db),
        media_type="text/event-stream",
    )
