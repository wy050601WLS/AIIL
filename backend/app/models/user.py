"""用户模型模块"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from app.database import Base


class User(Base):
    """用户表模型

    存储用户账号信息、个人资料和偏好设置。
    密码使用 bcrypt 哈希存储，偏好以 JSON 文本存储在 preferences 字段。
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)       # 用户名，唯一
    password_hash = Column(String(255), nullable=False)               # bcrypt 哈希后的密码
    nickname = Column(String(50), nullable=True)                      # 昵称，默认等于用户名
    avatar = Column(String(255), nullable=True)                       # 头像（emoji 字符）
    preferences = Column(Text, nullable=True)                         # JSON 偏好设置（字体、密度、默认模型等）
    created_at = Column(DateTime, default=datetime.now)               # 注册时间
