from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=255)
    preferences: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
