from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), default="新对话")
    pinned = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum("user", "assistant", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    conversation = relationship("Conversation", back_populates="messages")
