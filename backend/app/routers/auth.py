from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, ChangePassword, UserUpdate
from app.services.auth_service import register_user, login_user, change_password, update_profile
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    return register_user(data, db)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    return login_user(data, db)


@router.put("/password")
def update_password(data: ChangePassword, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    change_password(user, data.old_password, data.new_password, db)
    return {"message": "密码修改成功"}


@router.get("/profile", response_model=UserResponse)
def get_profile(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
def edit_profile(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_profile(user, data.nickname, data.avatar, data.preferences, db)
