"""学习资料路由模块

提供学习资料的 CRUD 操作和 AI 辅助搜索功能。
前缀：/resources，所有端点需登录。
"""

import json
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.limiter import limiter
from app.models.conversation import LearningResource
from app.models.user import User
from app.schemas.conversation import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceAskRequest
from app.utils.security import get_current_user

router = APIRouter(prefix="/resources", tags=["学习资料"])


@router.post("", response_model=ResourceResponse)
def create_resource(data: ResourceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """创建学习资料"""
    resource = LearningResource(
        user_id=user.id,
        title=data.title,
        url=data.url,
        description=data.description,
        category=data.category,
        resource_type=data.resource_type,
        tags=data.tags,
        visibility=data.visibility,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("", response_model=list[ResourceResponse])
def list_resources(
    category: str | None = None,
    resource_type: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取学习资料列表（公开资料 + 自己的资料），支持按分类和类型过滤"""
    from sqlalchemy import or_
    query = db.query(LearningResource).filter(
        or_(LearningResource.visibility == "public", LearningResource.user_id == user.id)
    )
    if category:
        query = query.filter(LearningResource.category == category)
    if resource_type:
        query = query.filter(LearningResource.resource_type == resource_type)
    return query.order_by(LearningResource.created_at.desc()).all()


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, data: ResourceUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新学习资料（仅更新非空字段）"""
    resource = db.query(LearningResource).filter(
        LearningResource.id == resource_id,
        LearningResource.user_id == user.id,
    ).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资料不存在")
    if data.title is not None:
        resource.title = data.title
    if data.url is not None:
        resource.url = data.url
    if data.description is not None:
        resource.description = data.description
    if data.category is not None:
        resource.category = data.category
    if data.resource_type is not None:
        resource.resource_type = data.resource_type
    if data.tags is not None:
        resource.tags = data.tags
    if data.visibility is not None:
        resource.visibility = data.visibility
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}")
def delete_resource(resource_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除学习资料"""
    resource = db.query(LearningResource).filter(
        LearningResource.id == resource_id,
        LearningResource.user_id == user.id,
    ).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资料不存在")
    db.delete(resource)
    db.commit()
    return {"message": "资料已删除"}


@router.post("/ask")
@limiter.limit("10/minute")
def ask_resources(data: ResourceAskRequest, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """AI 辅助搜索学习资料

    将用户的问题和所有资料的标题/描述发送给 AI，让 AI 分析哪些资料与问题相关并给出建议。
    """
    # 加载公开资料 + 自己的资料
    from sqlalchemy import or_
    resources = (
        db.query(LearningResource)
        .filter(or_(LearningResource.visibility == "public", LearningResource.user_id == user.id))
        .order_by(LearningResource.created_at.desc())
        .all()
    )

    if not resources:
        return {"answer": "你还没有保存任何学习资料。请先添加一些资料，然后再来搜索。", "resources": []}

    # 构造资料摘要作为上下文
    resource_summaries = []
    for r in resources:
        parts = [f"[{r.id}] {r.title}"]
        if r.category:
            parts.append(f"分类：{r.category}")
        if r.resource_type:
            parts.append(f"类型：{r.resource_type}")
        if r.description:
            parts.append(f"描述：{r.description[:200]}")
        if r.tags:
            parts.append(f"标签：{r.tags}")
        resource_summaries.append(" | ".join(parts))

    context = "\n".join(resource_summaries)

    # 构造 AI 请求
    system_prompt = (
        "你是一个学习资料搜索助手。用户有一个学习资料库，你需要根据用户的问题，"
        "从资料库中找出最相关的资料并给出推荐。\n\n"
        "请用中文回答，格式要求：\n"
        "1. 列出最相关的资料（引用资料编号如 [1] [2]）\n"
        "2. 说明为什么推荐这些资料\n"
        "3. 如果资料库中没有相关资料，建议用户搜索什么方向\n\n"
        f"用户的资料库：\n{context}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": data.question},
    ]

    url = f"{settings.AI_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.AI_MODEL,
        "max_tokens": 2048,
        "stream": False,
        "messages": messages,
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 服务暂时不可用，请稍后重试")

    return {"answer": answer, "resources": [ResourceResponse.model_validate(r) for r in resources]}
