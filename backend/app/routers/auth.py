"""认证路由模块

提供用户注册、登录、获取/更新个人资料、修改密码等端点。
前缀：/auth
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.limiter import limiter
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, ChangePassword, UserUpdate
from app.services.auth_service import register_user, login_user, change_password, update_profile
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """用户注册，返回用户信息（不含密码）"""
    return register_user(data, db)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """用户登录，返回 JWT 访问令牌"""
    return login_user(data, db)


@router.put("/password")
def update_password(data: ChangePassword, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """修改密码（需验证旧密码）"""
    change_password(user, data.old_password, data.new_password, db)
    return {"message": "密码修改成功"}


@router.get("/profile", response_model=UserResponse)
def get_profile(user: User = Depends(get_current_user)):
    """获取当前登录用户的个人信息"""
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
def edit_profile(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新个人资料（昵称、头像、偏好设置），仅更新非空字段"""
    return update_profile(user, data.nickname, data.avatar, data.preferences, db)
