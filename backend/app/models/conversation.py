"""会话、消息和知识卡片模型模块

定义核心业务模型：Conversation（会话）、Message（消息）、KnowledgeCard（知识卡片）。
三者关系：User 1→N Conversation 1→N Message，User 1→N KnowledgeCard。
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    """会话表模型

    每个会话属于一个用户，包含标题、置顶/归档状态。
    与 Message 为一对多关系，级联删除。
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), default="新对话")                       # 会话标题，可重命名
    pinned = Column(Boolean, default=False)                              # 是否置顶
    archived = Column(Boolean, default=False)                            # 是否归档
    system_prompt = Column(Text, nullable=True)                          # 已废弃，保留列兼容旧数据
    created_at = Column(DateTime, default=datetime.now)

    # 级联删除：会话删除时自动删除所有关联消息
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """消息表模型

    存储对话中的每条消息，支持 user 和 assistant 两种角色。
    images 字段存储 JSON 格式的 base64 图片列表（多模态消息）。
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum("user", "assistant", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)                               # 消息文本内容
    images = Column(Text, nullable=True)                                 # JSON 数组：base64 data URL 列表
    created_at = Column(DateTime, default=datetime.now)

    conversation = relationship("Conversation", back_populates="messages")


class KnowledgeCard(Base):
    """知识卡片表模型

    从 AI 回复中提取的精华内容，支持标签分类和来源追溯。
    """

    __tablename__ = "knowledge_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)                               # 卡片内容
    source = Column(String(200), nullable=True)                          # 来源标记（如对话 ID）
    tags = Column(String(500), nullable=True)                            # 标签，逗号分隔
    created_at = Column(DateTime, default=datetime.now)
