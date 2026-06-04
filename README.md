# AI 智慧学习系统

基于 AI 的智能学习助手，支持流式对话、知识卡片、学习资料库、知识库文档管理、学习面板等功能。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + Pinia + Element Plus |
| 后端 | Python FastAPI + SQLAlchemy |
| AI | 小米 MiMo（OpenAI 兼容格式） |
| 数据库 | MySQL 8 |
| 迁移 | Alembic |
| 部署 | Docker Compose |

## 功能特性

| 类别 | 功能 |
|------|------|
| 用户认证 | 注册、登录、JWT 鉴权、修改密码 |
| 用户资料 | 头像选择、昵称编辑、偏好设置（字体大小 / 消息密度 / 默认模型） |
| 对话管理 | 新建、重命名、删除、置顶、归档、搜索、导出 Markdown |
| AI 对话 | SSE 真流式输出、Markdown 渲染 + 代码高亮、重新生成、多模型切换、语音输入、图片识别 |
| 消息操作 | 编辑、删除、复制（渲染文本）、时间戳 |
| 知识卡片 | 收藏 AI 回复精华、编辑、标签筛选 |
| 对话模板 | 内置学习场景模板、自定义模板、快速填充 |
| 学习资料库 | 收集链接资料、分类/类型筛选、AI 辅助搜索推荐 |
| 知识库文档 | 上传 PDF/DOCX/TXT/MD、自动解析内容、全文搜索 |
| 可见性控制 | 公共/私人/草稿三种可见性，控制资料访问权限 |
| 学习面板 | 对话数/消息数/卡片数统计、30 天活跃趋势、热门标签 |
| UI 体验 | 深色 / 浅色主题、移动端响应式、消息密度调节 |
| 工程化 | Docker 部署、Alembic 数据库迁移、GitHub Actions CI、pytest 单元测试 |

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

在 `backend/.env` 中配置（参考 `.env.example`）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DB_HOST | MySQL 地址 | localhost |
| DB_PORT | MySQL 端口 | 3306 |
| DB_USER | MySQL 用户名 | root |
| DB_PASSWORD | MySQL 密码 | root |
| DB_NAME | 数据库名 | ai |
| JWT_SECRET_KEY | JWT 密钥（生产环境务必更换） | - |
| AI_API_KEY | AI API 密钥 | - |
| AI_BASE_URL | AI API 地址 | - |
| AI_MODEL | AI 模型 ID | mimo-v2.5-pro |
| CORS_ORIGINS | 允许的跨域来源（逗号分隔） | http://localhost:5173 |
| UPLOAD_DIR | 文件上传目录 | ./uploads |
| MAX_FILE_SIZE | 最大文件大小（字节） | 20971520 (20MB) |

## 测试

```bash
cd backend
python -m pytest tests/ -v
```

## 项目文档

- [构建历程](docs/build-history.md)
- [项目全景](docs/project-overview.md)
- API 文档：启动后端后访问 http://localhost:8000/docs
