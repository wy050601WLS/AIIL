"""会话、消息、知识卡片、对话模板和学习资料模型模块

定义核心业务模型：Conversation、Message、KnowledgeCard、PromptTemplate、LearningResource。
关系：User 1→N Conversation 1→N Message，User 1→N KnowledgeCard/PromptTemplate/LearningResource。
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


class PromptTemplate(Base):
    """对话模板表模型

    预设的 prompt 模板，用于快速发起常用对话。
    user_id 为 NULL 时表示系统内置模板（所有用户可见），非 NULL 时表示用户自建模板。
    """

    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(100), nullable=False)                          # 模板标题
    content = Column(Text, nullable=False)                               # 模板 prompt 内容
    category = Column(String(50), nullable=True)                         # 分类标签（翻译/解释/练习等）
    is_builtin = Column(Boolean, default=False)                          # 是否为系统内置模板
    created_at = Column(DateTime, default=datetime.now)


class LearningResource(Base):
    """学习资料表模型

    用户收集的学习资料（链接、笔记、文章等），支持分类和标签管理。
    AI 辅助搜索功能基于此表中的资料进行分析和推荐。
    """

    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)                          # 资料标题
    url = Column(String(500), nullable=True)                             # 可选的链接地址
    description = Column(Text, nullable=True)                            # 资料描述/笔记
    category = Column(String(50), nullable=True)                         # 分类（编程/数学/英语等）
    resource_type = Column(String(20), nullable=True)                    # 类型（article/video/course/tool/book/other）
    tags = Column(String(500), nullable=True)                            # 标签，逗号分隔
    visibility = Column(String(10), default="public")                    # 可见性：public/private/draft
    created_at = Column(DateTime, default=datetime.now)


class KnowledgeDocument(Base):
    """知识库文档表模型

    用户上传的学习文档（PDF/DOCX/TXT/MD），系统自动解析文件内容并存储。
    支持全文搜索和标签管理。
    """

    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)                          # 文档标题（默认取文件名）
    file_type = Column(String(10), nullable=False)                       # 文件类型：pdf/docx/txt/md
    file_path = Column(String(500), nullable=False)                      # 磁盘存储路径
    file_size = Column(Integer, nullable=True)                           # 文件大小（字节）
    content_text = Column(Text, nullable=True)                           # 解析后的纯文本内容
    tags = Column(String(500), nullable=True)                            # 标签，逗号分隔
    visibility = Column(String(10), default="public")                    # 可见性：public/private/draft
    created_at = Column(DateTime, default=datetime.now)
