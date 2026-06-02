"""AI 对话服务模块

核心职责：
1. save_user_message — 保存用户消息到数据库
2. load_history — 加载完整对话历史，转换为 OpenAI 兼容格式（含多模态）
3. verify_conversation_owner — 校验会话归属权
4. stream_ai_api — 真流式调用 AI API，以异步生成器逐 chunk 转发

注意：采用「真流式 SSE」模式——后端收到 AI 每个 chunk 后立即转发给前端，
     实现低延迟的逐 token 显示效果。
"""

import json
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.conversation import ChatRequest


def save_user_message(conversation_id: int, content: str, db: Session, images: list[str] | None = None) -> None:
    """保存用户消息到数据库

    Args:
        conversation_id: 所属会话 ID
        content: 消息文本内容
        db: 数据库会话
        images: 可选的 base64 图片列表，序列化为 JSON 存储
    """
    import json
    msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=content,
        images=json.dumps(images) if images else None,
    )
    db.add(msg)
    db.commit()


def load_history(conversation_id: int, db: Session) -> tuple[list[dict], Conversation]:
    """加载会话的完整对话历史

    返回 OpenAI 兼容的消息列表格式：
    - 首条为 system prompt（统一使用配置中的默认提示词）
    - 纯文本消息直接返回 {"role": ..., "content": ...}
    - 含图片的消息转为多模态格式：content 为数组，包含 text 和 image_url 类型

    Returns:
        (messages_history, conversation_object) 元组
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    history = []
    history.append({"role": "system", "content": settings.DEFAULT_SYSTEM_PROMPT})
    for m in messages:
        if not m.content:
            continue
        if m.images:
            # 多模态消息：将图片转为 OpenAI vision 格式
            img_list = json.loads(m.images)
            parts = [{"type": "text", "text": m.content}]
            for img_url in img_list:
                parts.append({"type": "image_url", "image_url": {"url": img_url}})
            history.append({"role": m.role, "content": parts})
        else:
            history.append({"role": m.role, "content": m.content})
    return history, conv


def verify_conversation_owner(conversation_id: int, user: User, db: Session) -> Conversation:
    """校验会话是否属于当前用户，返回会话对象；不存在则抛出 404"""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conv:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return conv


async def stream_ai_api(history: list[dict], model: str | None = None):
    """真流式调用 AI API — 以异步生成器逐 chunk 转发

    使用 httpx.AsyncClient 读取 SSE 流，每收到一个 content chunk 立即 yield，
    实现低延迟的逐 token 转发。调用方可在迭代过程中将 chunk 实时推送给前端。

    Args:
        history: OpenAI 格式的消息列表（含 system prompt）
        model: 指定模型 ID，为空则使用默认模型

    Yields:
        str — 每次产出一个 content chunk 文本
    """
    url = f"{settings.AI_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or settings.AI_MODEL,
        "max_tokens": 4096,
        "stream": True,
        "messages": history,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue
