"""
数据库连接模块

配置 SQLAlchemy 引擎、会话工厂和 ORM 基类。
提供 get_db 依赖注入函数，供路由层获取数据库会话。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# 创建数据库引擎，pool_pre_ping 检测连接是否存活
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# 会话工厂：autocommit=False 需手动 commit，autoflush=False 需手动 flush
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型基类，所有模型继承此类
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：获取数据库会话，请求结束后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
