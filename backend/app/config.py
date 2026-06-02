"""
应用配置模块

从环境变量读取所有配置项，提供全局 settings 单例。
环境变量通过 .env 文件加载（python-dotenv）。
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置类，所有配置项从环境变量读取并提供默认值"""

    # ===== 数据库配置 =====
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_NAME: str = os.getenv("DB_NAME", "ai")

    @property
    def DATABASE_URL(self) -> str:
        """构建 MySQL 连接字符串（pymysql 驱动，utf8mb4 编码）"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # ===== JWT 认证配置 =====
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "aiil-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    # ===== AI 模型配置 =====
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/anthropic")
    AI_MODEL: str = os.getenv("AI_MODEL", "claude-sonnet-4-20250514")

    # ===== 默认系统提示词 =====
    # 所有会话统一使用此提示词，不再支持每个会话单独设置
    DEFAULT_SYSTEM_PROMPT: str = os.getenv(
        "DEFAULT_SYSTEM_PROMPT",
        "你是「AI 智慧学习」系统的学习助手。你的职责是帮助用户学习知识、解答学习中遇到的问题。"
        "请围绕学习场景提供准确、有条理的回答，适当使用举例、类比和分步骤讲解来帮助理解。"
        "如果用户提出与学习无关的问题，请礼貌地引导回学习话题。"
        "回答请使用中文，除非用户明确要求使用其他语言。",
    )

    # ===== 服务器配置 =====
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # ===== 跨域配置 =====
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")


# 全局配置单例，所有模块通过 settings 引用
settings = Settings()
