"""安全工具模块

提供密码哈希、JWT 令牌编解码、当前用户依赖注入等认证相关功能。
"""

from datetime import datetime, timedelta

from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

# FastAPI HTTP Bearer 认证方案，自动从 Authorization 头提取 Bearer Token
security_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """将明文密码用 bcrypt 哈希，返回哈希字符串"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否匹配 bcrypt 哈希值"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    """为指定用户创建 JWT 访问令牌

    Token 载荷包含 sub（用户 ID）和 exp（过期时间）。
    """
    expire = datetime.now() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """解码 JWT Token，返回用户 ID；无效则返回 None"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI 依赖注入：从请求中解析当前登录用户

    流程：提取 Bearer Token → 解码获取 user_id → 查询数据库 → 返回 User 对象。
    认证失败时抛出 401 异常。
    """
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user
