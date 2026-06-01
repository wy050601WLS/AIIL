from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)
    preferences = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
