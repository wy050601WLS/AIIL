"""AI 对话路由模块

核心端点：
- POST /chat：SSE 流式对话（真流式 — 收到 AI chunk 立即转发给前端）
- GET /conversations/{id}/export：导出对话为 Markdown
- GET /models：可用模型列表
- PUT/DELETE /messages/{id}：编辑/删除消息

所有端点均需登录认证。
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, SessionLocal
from app.limiter import limiter
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.conversation import ChatRequest
from app.services.ai_service import verify_conversation_owner, save_user_message, load_history, stream_ai_api
from app.utils.security import get_current_user


class MessageUpdate(BaseModel):
    """编辑消息请求体"""
    content: str = Field(..., min_length=1)

router = APIRouter(tags=["AI 对话"])


@router.post("/chat")
@limiter.limit("20/minute")
async def chat(data: ChatRequest, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """SSE 真流式对话端点

    流程：
    1. 校验会话归属权
    2. 若为重新生成，删除上一条 AI 回复；否则保存用户消息
    3. 加载完整对话历史（含 system prompt）
    4. 以异步生成器调用 AI API，每收到一个 chunk 立即转发给前端（低延迟）
    5. 流结束后将 AI 完整回复存入数据库
    """
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
        save_user_message(data.conversation_id, data.content, db, data.images)

    # 自动更新会话标题：若标题仍为默认值「新对话」，用用户消息前 30 字更新
    conv = db.query(Conversation).filter(Conversation.id == data.conversation_id).first()
    if conv and conv.title == "新对话" and data.content and not data.regenerate:
        conv.title = data.content[:30].replace("\n", " ").strip()
        if not conv.title:
            conv.title = "图片对话"
        db.commit()

    history, conv = load_history(data.conversation_id, db)

    async def generate():
        """真流式 SSE 生成器：收到 AI chunk 立即转发，流结束后存库"""
        full_response = ""
        try:
            async for chunk in stream_ai_api(history, model=data.model):
                full_response += chunk
                yield f"data: {chunk}\n\n"
        except Exception:
            yield "data: [ERROR] AI 服务暂时不可用，请稍后重试\n\n"
        # 流结束后将完整回复存入数据库（使用独立 session 避免依赖注入的 session 已关闭）
        if full_response:
            save_db = SessionLocal()
            try:
                msg = Message(
                    conversation_id=data.conversation_id,
                    role="assistant",
                    content=full_response,
                )
                save_db.add(msg)
                save_db.commit()
            finally:
                save_db.close()
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/conversations/{conversation_id}/export")
def export_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """导出会话为 Markdown 文件

    生成格式：标题 + 用户/AI 消息交替排列，返回 .md 文件下载。
    """
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
    """返回可用的 AI 模型列表和默认模型 ID"""
    return {
        "models": [
            {"id": "mimo-v2.5-pro", "name": "MiMo v2.5 Pro", "vision": False},
            {"id": "gpt-4o", "name": "GPT-4o", "vision": True},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "vision": True},
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "vision": True},
            {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5", "vision": True},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "vision": True},
        ],
        "default": settings.AI_MODEL,
    }


def _verify_message_owner(message_id: int, user: User, db: Session) -> Message:
    """校验消息归属权：先查消息是否存在，再查所属会话是否属于当前用户"""
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
    """编辑消息内容（仅修改文本，不影响图片）"""
    msg = _verify_message_owner(message_id, user, db)
    msg.content = data.content
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "role": msg.role, "content": msg.content, "created_at": str(msg.created_at)}


@router.delete("/messages/{message_id}")
def delete_message(message_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除单条消息"""
    msg = _verify_message_owner(message_id, user, db)
    db.delete(msg)
    db.commit()
    return {"message": "消息已删除"}
