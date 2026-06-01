from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token


def register_user(data: UserCreate, db: Session) -> UserResponse:
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def login_user(data: UserLogin, db: Session) -> Token:
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = create_access_token(user.id)
    return Token(access_token=token)


def change_password(user: User, old_password: str, new_password: str, db: Session) -> None:
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
    user.password_hash = hash_password(new_password)
    db.commit()


def update_profile(user: User, nickname: str | None, avatar: str | None, preferences: str | None, db: Session) -> UserResponse:
    if nickname is not None:
        user.nickname = nickname
    if avatar is not None:
        user.avatar = avatar
    if preferences is not None:
        user.preferences = preferences
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)
