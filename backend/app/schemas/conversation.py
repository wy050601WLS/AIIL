"""会话、消息、卡片、模板、学习资料和面板相关 Pydantic 模型

定义对话系统所有请求/响应的数据结构。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ===== 会话相关 =====

class ConversationCreate(BaseModel):
    """创建会话请求体"""
    title: str = Field(default="新对话", max_length=100)


class ConversationUpdate(BaseModel):
    """更新会话标题请求体"""
    title: str = Field(..., min_length=1, max_length=100)


class ConversationResponse(BaseModel):
    """会话信息响应体"""
    id: int
    title: str
    pinned: bool = False
    archived: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# ===== 消息相关 =====

class MessageResponse(BaseModel):
    """消息信息响应体（含可选图片）"""
    id: int
    role: str
    content: str
    images: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    """AI 对话请求体

    通过 SSE 流式返回 AI 回复。regenerate=True 时重新生成最后一条回复。
    """
    conversation_id: int
    content: str = ""
    model: str | None = None          # 指定 AI 模型，为空则用默认模型
    regenerate: bool = False          # 是否为重新生成
    images: list[str] | None = None   # base64 图片列表（多模态输入）


# ===== 知识卡片相关 =====

class KnowledgeCardCreate(BaseModel):
    """创建知识卡片请求体"""
    content: str = Field(..., min_length=1)
    source: str | None = None         # 来源标记
    tags: str | None = None           # 逗号分隔的标签


class KnowledgeCardUpdate(BaseModel):
    """更新知识卡片请求体（所有字段可选）"""
    content: str | None = Field(None, min_length=1)
    tags: str | None = None


class KnowledgeCardResponse(BaseModel):
    """知识卡片响应体"""
    id: int
    content: str
    source: str | None = None
    tags: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ===== 对话模板相关 =====

class TemplateCreate(BaseModel):
    """创建对话模板请求体"""
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    category: str | None = Field(None, max_length=50)


class TemplateUpdate(BaseModel):
    """更新对话模板请求体（所有字段可选）"""
    title: str | None = Field(None, min_length=1, max_length=100)
    content: str | None = Field(None, min_length=1)
    category: str | None = None


class TemplateResponse(BaseModel):
    """对话模板响应体"""
    id: int
    title: str
    content: str
    category: str | None = None
    is_builtin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# ===== 学习资料相关 =====

class ResourceCreate(BaseModel):
    """创建学习资料请求体"""
    title: str = Field(..., min_length=1, max_length=200)
    url: str | None = Field(None, max_length=500)
    description: str | None = None
    category: str | None = Field(None, max_length=50)
    resource_type: str | None = Field(None, max_length=20)
    tags: str | None = None


class ResourceUpdate(BaseModel):
    """更新学习资料请求体（所有字段可选）"""
    title: str | None = Field(None, min_length=1, max_length=200)
    url: str | None = None
    description: str | None = None
    category: str | None = None
    resource_type: str | None = None
    tags: str | None = None


class ResourceResponse(BaseModel):
    """学习资料响应体"""
    id: int
    title: str
    url: str | None = None
    description: str | None = None
    category: str | None = None
    resource_type: str | None = None
    tags: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResourceAskRequest(BaseModel):
    """AI 辅助搜索请求体"""
    question: str = Field(..., min_length=1)


# ===== 学习面板相关 =====

class DailyMessage(BaseModel):
    """每日消息统计"""
    date: str
    count: int


class TagCount(BaseModel):
    """标签出现次数统计"""
    tag: str
    count: int


class DashboardStats(BaseModel):
    """学习面板统计数据响应体"""
    conversation_count: int           # 对话总数
    message_count: int                # 消息总数
    card_count: int                   # 知识卡片数
    active_days: int                  # 最近 30 天活跃天数
    daily_messages: list[DailyMessage]  # 最近 30 天每日消息数
    top_tags: list[TagCount]          # 热门标签 Top 10
