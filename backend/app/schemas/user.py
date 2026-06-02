"""用户相关 Pydantic 模型

定义认证和用户管理的请求/响应数据结构，用于参数校验和序列化。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """注册请求体"""
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """登录请求体"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应体（不含密码）"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """更新个人资料请求体（所有字段可选）"""
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=255)
    preferences: Optional[str] = None


class Token(BaseModel):
    """登录成功后返回的 JWT Token"""
    access_token: str
    token_type: str = "bearer"


class ChangePassword(BaseModel):
    """修改密码请求体"""
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
