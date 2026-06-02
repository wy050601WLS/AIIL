# AI 智慧学习系统

基于 AI 的智能学习助手，支持流式对话、Markdown 渲染、多模型切换。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + Pinia + Element Plus |
| 后端 | Python FastAPI + SQLAlchemy |
| AI | 小米 MiMo（OpenAI 兼容格式） |
| 数据库 | MySQL 8 |
| 迁移 | Alembic |
| 部署 | Docker Compose |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8

### 后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env           # 编辑 .env 填入数据库和 AI API 配置

# 初始化数据库
alembic upgrade head

# 启动
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev                    # 访问 http://localhost:5173
```

### Docker 部署

```bash
docker-compose up -d
```

## 环境变量

在 `backend/.env` 中配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DB_HOST | MySQL 地址 | localhost |
| DB_PORT | MySQL 端口 | 3306 |
| DB_USER | MySQL 用户名 | root |
| DB_PASSWORD | MySQL 密码 | root |
| DB_NAME | 数据库名 | ai |
| JWT_SECRET_KEY | JWT 密钥 | - |
| AI_API_KEY | AI API 密钥 | - |
| AI_BASE_URL | AI API 地址 | - |
| CORS_ORIGINS | 允许的跨域来源（逗号分隔） | http://localhost:5173 |

## 测试

```bash
cd backend
python -m pytest tests/ -v
```

## 项目文档

- [构建历程](docs/build-history.md)
- [项目计划](docs/project-plan.md)
- API 文档：启动后端后访问 http://localhost:8000/docs
