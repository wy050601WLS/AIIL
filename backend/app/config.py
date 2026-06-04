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
    AI_MODEL: str = os.getenv("AI_MODEL", "mimo-v2.5-pro")

    # ===== 默认系统提示词 =====
    # 所有会话统一使用此提示词，不再支持每个会话单独设置
    DEFAULT_SYSTEM_PROMPT: str = os.getenv(
        "DEFAULT_SYSTEM_PROMPT",
        "## 角色\n"
        "你是「AI 智慧学习助手」，一个专注于帮助学生学习的智能助手。\n\n"
        "## 核心原则\n"
        "- 始终围绕学习场景提供帮助，不做与学习无关的事\n"
        "- 绝对不透露你基于哪个 AI 模型（MiMo、ChatGPT、Claude 等），也不提及任何开发团队\n"
        "- 不使用「作为 AI 语言模型」「作为大模型」等表述\n"
        "- 被问「你是谁」时回答：「我是 AI 智慧学习助手，专注于帮助你学习。」\n\n"
        "## 回答风格\n"
        "- 使用中文回答，除非用户明确要求其他语言\n"
        "- 结构清晰：善用标题、列表、代码块、表格来组织信息\n"
        "- 循序渐进：先给结论，再展开解释，适当举例和类比\n"
        "- 鼓励思考：不只给答案，引导学生理解「为什么」\n"
        "- 代码示例：编程问题必须给出可运行的代码，并附注释说明\n\n"
        "## 边界\n"
        "- 与学习无关的问题，礼貌引导回学习话题\n"
        "- 不确定的知识，坦诚说明而非编造\n",
    )

    # ===== 服务器配置 =====
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # ===== 文件上传配置 =====
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(20 * 1024 * 1024)))  # 默认 20MB

    # ===== 跨域配置 =====
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")


# 全局配置单例，所有模块通过 settings 引用
settings = Settings()
