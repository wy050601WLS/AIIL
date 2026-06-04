"""
FastAPI 应用入口模块

负责初始化应用实例、注册中间件（CORS、限流）和挂载所有路由。
uvicorn 启动命令：python -m uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, SessionLocal  # noqa: F401 — 确保 SQLAlchemy 模型被注册到 Base.metadata
from app.limiter import limiter
from app.routers import auth, history, chat, cards, dashboard, templates, resources, knowledge

app = FastAPI(title="AI 智慧学习系统")


@app.on_event("startup")
def init_builtin_templates():
    """启动时初始化内置模板，避免每次请求都检查"""
    from app.routers.templates import ensure_builtin_templates
    db = SessionLocal()
    try:
        ensure_builtin_templates(db)
    finally:
        db.close()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 中间件：允许前端跨域访问后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各业务路由模块
app.include_router(auth.router)       # 认证：注册/登录/资料/密码
app.include_router(history.router)    # 会话管理：CRUD/置顶/归档/导出
app.include_router(chat.router)       # AI 对话：SSE 流式/消息编辑/模型列表
app.include_router(cards.router)      # 知识卡片：增删查
app.include_router(dashboard.router)  # 学习面板：统计数据
app.include_router(templates.router)  # 对话模板：增删查改
app.include_router(resources.router)  # 学习资料：增删查改 + AI 搜索
app.include_router(knowledge.router)  # 知识库：文档上传/解析/搜索


@app.get("/")
def root():
    """健康检查端点，返回系统名称"""
    return {"message": "AI 智慧学习系统 API"}
