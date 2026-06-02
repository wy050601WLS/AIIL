from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base  # noqa: F401 — 确保模型被注册
from app.routers import auth, history, chat, cards, dashboard

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(title="AI 智慧学习系统")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(history.router)
app.include_router(chat.router)
app.include_router(cards.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "AI 智慧学习系统 API"}
