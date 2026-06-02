# AI 智慧学习系统 — 项目全景文档

## 一、项目概览

| 项目 | 说明 |
|------|------|
| 项目名称 | AIIL（AI 智慧学习系统） |
| 定位 | 基于 AI 的个人学习助手，支持对话问答、知识卡片、学习面板 |
| 技术栈 | 前端 Vue3 + Vite + Pinia + Element Plus，后端 Python FastAPI，AI MiMo |
| 数据库 | MySQL 8.0，Alembic 迁移管理 |
| 部署 | Docker Compose（MySQL + 后端 + 前端 Nginx） |
| CI | GitHub Actions（后端 pytest + 前端 vite build） |

---

## 二、功能清单

### 核心功能

| 功能 | 说明 |
|------|------|
| AI 对话 | SSE 流式输出，支持多轮对话、Markdown 渲染、代码高亮 |
| 多模型切换 | 支持配置多个 AI 模型，用户可下拉切换 |
| 图片识别 | 上传/粘贴图片，AI 多模态识别分析 |
| 语音输入 | 浏览器 Web Speech API，中文实时语音转文字 |
| 会话管理 | 新建、重命名、置顶、归档、删除、搜索、导出 Markdown |
| 系统提示词 | 每个对话可自定义 system prompt |
| 知识卡片 | 收藏 AI 回复精华，支持标签分类和筛选 |
| 学习面板 | 统计卡片（对话/消息/卡片/活跃天数）+ 30 天趋势图 + 热门标签 |

### 用户系统

| 功能 | 说明 |
|------|------|
| 注册/登录 | 用户名 + 密码，JWT 认证 |
| 个人设置 | 头像（emoji）、昵称、字体大小、消息密度、默认模型 |
| 密码修改 | 验证旧密码后设置新密码 |
| 深色/浅色主题 | 一键切换，localStorage 持久化 |

---

## 三、技术架构

```
┌─────────────────────────────────────────────┐
│                   前端 (Vue3)                │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │
│  │  Views   │ │Components│ │   Stores     │  │
│  │ Chat     │ │Sidebar   │ │ user (Pinia) │  │
│  │ Login    │ │ChatMsg   │ │ chat         │  │
│  │ Settings │ │ChatInput │ │ cards        │  │
│  │ Cards    │ │SysPrompt │ │ dashboard    │  │
│  │Dashboard │ │          │ │ theme        │  │
│  └─────────┘ └──────────┘ └──────────────┘  │
│           │         API Layer (Axios)        │
│           │    auth / chat / cards / dash    │
└───────────┼─────────────────────────────────┘
            │ HTTP + SSE
┌───────────┼─────────────────────────────────┐
│           ▼       后端 (FastAPI)             │
│  ┌──────────────────────────────────────┐   │
│  │            Routers                   │   │
│  │  auth / history / chat / cards / dash│   │
│  └──────────┬───────────────────────────┘   │
│  ┌──────────▼───────────────────────────┐   │
│  │           Services                   │   │
│  │  auth_service / chat_service / ai    │   │
│  └──────────┬───────────────────────────┘   │
│  ┌──────────▼───────────────────────────┐   │
│  │  Models (SQLAlchemy) + Schemas (Pyd) │   │
│  │  User / Conversation / Message / Card│   │
│  └──────────┬───────────────────────────┘   │
│             │                               │
│  ┌──────────▼───┐  ┌──────────────────┐    │
│  │   MySQL 8.0  │  │  MiMo AI API     │    │
│  │   (alembic)  │  │  (OpenAI compat) │    │
│  └──────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## 四、数据库设计

### ER 关系

```
users 1──n conversations 1──n messages
users 1──n knowledge_cards
```

### 表结构

#### users
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| username | VARCHAR(50) UNIQUE | 用户名 |
| password_hash | VARCHAR(255) | bcrypt 哈希密码 |
| nickname | VARCHAR(50) | 昵称 |
| avatar | VARCHAR(255) | 头像（emoji） |
| preferences | TEXT | JSON 偏好设置 |
| created_at | DATETIME | 注册时间 |

#### conversations
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| user_id | INT FK→users | 所属用户，CASCADE 删除 |
| title | VARCHAR(100) | 会话标题，默认"新对话" |
| pinned | BOOLEAN | 是否置顶 |
| archived | BOOLEAN | 是否归档 |
| system_prompt | TEXT | 自定义系统提示词 |
| created_at | DATETIME | 创建时间 |

#### messages
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| conversation_id | INT FK→conversations | 所属会话，CASCADE 删除 |
| role | ENUM('user','assistant') | 消息角色 |
| content | TEXT | 消息内容 |
| images | TEXT | JSON 数组（base64 图片列表） |
| created_at | DATETIME | 发送时间 |

#### knowledge_cards
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增主键 |
| user_id | INT FK→users | 所属用户，CASCADE 删除 |
| content | TEXT | 卡片内容 |
| source | VARCHAR(200) | 来源（如对话 ID） |
| tags | VARCHAR(500) | 标签（逗号分隔） |
| created_at | DATETIME | 创建时间 |

---

## 五、API 接口一览

### 认证 `/auth`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /auth/register | 注册 | × |
| POST | /auth/login | 登录，返回 JWT | × |
| GET | /auth/profile | 获取个人信息 | ✓ |
| PUT | /auth/profile | 更新昵称/头像/偏好 | ✓ |
| PUT | /auth/password | 修改密码 | ✓ |

### 会话 `/conversations`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /conversations | 新建会话 | ✓ |
| GET | /conversations | 会话列表（置顶优先） | ✓ |
| GET | /conversations/{id}/messages | 获取消息列表 | ✓ |
| PUT | /conversations/{id} | 重命名 | ✓ |
| DELETE | /conversations/{id} | 删除会话 | ✓ |
| PUT | /conversations/{id}/pin | 切换置顶 | ✓ |
| PUT | /conversations/{id}/archive | 切换归档 | ✓ |
| PUT | /conversations/{id}/system-prompt | 设置提示词 | ✓ |
| GET | /conversations/{id}/export | 导出 Markdown | ✓ |

### AI 对话

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /chat | 发送消息（SSE 流式） | ✓ |
| GET | /models | 可用模型列表 | ✓ |
| PUT | /messages/{id} | 编辑消息 | ✓ |
| DELETE | /messages/{id} | 删除消息 | ✓ |

### 知识卡片 `/cards`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /cards | 创建卡片 | ✓ |
| GET | /cards | 卡片列表（最新优先） | ✓ |
| DELETE | /cards/{id} | 删除卡片 | ✓ |

### 学习面板 `/dashboard`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /dashboard/stats | 统计数据 | ✓ |

返回结构：
```json
{
  "conversation_count": 42,
  "message_count": 356,
  "card_count": 18,
  "active_days": 12,
  "daily_messages": [{"date": "2026-06-01", "count": 15}, ...],
  "top_tags": [{"tag": "Python", "count": 5}, ...]
}
```

---

## 六、前端路由

| 路径 | 页面 | 认证 | 说明 |
|------|------|------|------|
| /login | Login | × | 登录页 |
| /register | Register | × | 注册页 |
| / | Chat | ✓ | 主对话页（默认） |
| /settings | Settings | ✓ | 个人设置 |
| /cards | Cards | ✓ | 知识卡片 |
| /dashboard | Dashboard | ✓ | 学习面板 |

---

## 七、环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DB_HOST | localhost | MySQL 主机 |
| DB_PORT | 3306 | MySQL 端口 |
| DB_USER | root | MySQL 用户 |
| DB_PASSWORD | root | MySQL 密码 |
| DB_NAME | ai | 数据库名 |
| JWT_SECRET_KEY | aiil-secret-key | JWT 签名密钥 |
| JWT_ALGORITHM | HS256 | JWT 算法 |
| JWT_EXPIRE_hours | 24 | Token 有效期（小时） |
| AI_API_KEY | - | MiMo API 密钥 |
| AI_BASE_URL | https://token-plan-cn.xiaomimimo.com | AI 接口地址 |
| AI_MODEL | mimo-v2.5-pro | 默认 AI 模型 |
| CORS_ORIGINS | http://localhost:5173 | 允许的跨域来源 |
| HOST | 0.0.0.0 | 服务监听地址 |
| PORT | 8000 | 服务监听端口 |

---

## 八、文件清单

### 后端 `backend/app/`

```
app/
├── __init__.py
├── config.py              # 环境变量配置（Settings 类）
├── database.py            # SQLAlchemy 引擎、Session、Base、get_db
├── main.py                # FastAPI 入口，挂载中间件和路由
├── models/
│   ├── user.py            # User 模型
│   └── conversation.py    # Conversation / Message / KnowledgeCard 模型
├── schemas/
│   ├── user.py            # 用户相关 Pydantic 模型
│   └── conversation.py    # 对话/消息/卡片/面板 Pydantic 模型
├── routers/
│   ├── auth.py            # 认证路由（注册/登录/资料/密码）
│   ├── history.py         # 会话管理路由（CRUD/置顶/归档/提示词）
│   ├── chat.py            # AI 对话路由（SSE/导出/模型/消息编辑）
│   ├── cards.py           # 知识卡片路由（增删查）
│   └── dashboard.py       # 学习面板路由（统计）
├── services/
│   ├── ai_service.py      # AI 调用、消息存储、历史加载（多模态）
│   ├── auth_service.py    # 注册/登录/改密/更新资料
│   └── chat_service.py    # 会话 CRUD 业务逻辑
└── utils/
    └── security.py        # bcrypt 哈希、JWT 编解码、get_current_user
```

### 后端测试 `backend/tests/`

```
tests/
├── conftest.py            # 测试数据库、client/auth_client fixture
├── test_auth.py           # 4 个测试：注册/重复注册/登录/错误密码
├── test_conversations.py  # 4 个测试：创建/列表/重命名/删除
├── test_messages.py       # 5 个测试：编辑/空内容/删除/不存在/跨用户
├── test_features.py       # 9 个测试：置顶/归档/提示词/资料/密码/模型
└── test_dashboard.py      # 3 个测试：空数据/结构验证/未授权
```

共 **25 个测试**，全部通过。

### 数据库迁移 `backend/alembic/versions/`

| 迁移 | 说明 |
|------|------|
| ab691b1384ad | 初始：规范化索引命名 |
| 17fc4b05d0cc | Message 表新增 images 列 |
| a29b970af45f | 新建 knowledge_cards 表 |

### 前端 `frontend/src/`

```
src/
├── main.js                # 入口：注册 Pinia / Router / Element Plus
├── App.vue                # 根组件：<router-view />
├── style.css              # 全局主题变量（深色/浅色）+ Element Plus 覆盖
├── router/
│   └── index.js           # 6 条路由 + 导航守卫
├── api/
│   ├── index.js           # Axios 实例（拦截器/token/401）
│   ├── auth.js            # 认证 API
│   ├── chat.js            # 对话 API + streamChat SSE
│   ├── cards.js           # 知识卡片 API
│   └── dashboard.js       # 学习面板 API
├── stores/
│   ├── user.js            # 用户状态（token/资料/偏好）
│   ├── chat.js            # 对话状态（会话列表/消息/模型/流式）
│   ├── cards.js           # 知识卡片状态
│   ├── dashboard.js       # 面板统计数据
│   └── theme.js           # 主题切换（深色/浅色）
├── components/
│   ├── Sidebar.vue        # 侧边栏（会话列表/搜索/导航/下拉菜单）
│   ├── ChatMessage.vue    # 消息气泡（Markdown/图片/操作按钮）
│   ├── ChatInput.vue      # 输入区（文本/图片上传/语音/发送）
│   └── SystemPromptDialog.vue  # 系统提示词弹窗
└── views/
    ├── Login.vue          # 登录页
    ├── Register.vue       # 注册页
    ├── Chat.vue           # 主对话页
    ├── Settings.vue       # 设置页（资料/偏好/密码）
    ├── Cards.vue          # 知识卡片页
    └── Dashboard.vue      # 学习面板页
```

### 配置与部署

```
项目根/
├── docker-compose.yml     # 3 服务：db + backend + frontend
├── .env.example           # 环境变量模板
├── .gitignore
├── README.md
├── .github/workflows/ci.yml  # GitHub Actions CI
├── backend/
│   ├── Dockerfile         # Python 3.11 + uvicorn
│   ├── requirements.txt   # 10 个依赖 + pytest
│   ├── alembic.ini        # Alembic 配置
│   └── init_db.sql        # Docker 初始化 SQL
└── frontend/
    ├── Dockerfile         # Node 20 构建 + Nginx 运行
    ├── nginx.conf         # 反向代理 + SSE 配置
    ├── vite.config.js     # 开发代理 + 构建配置
    └── package.json       # Vue3 + Element Plus + marked + highlight.js
```

### 文档 `docs/`

| 文件 | 说明 |
|------|------|
| project-overview.md | 本文档，项目全景 |
| build-history.md | 14 阶段构建历程 |
| project-plan.md | 全周期实施计划 |
| tasks.md | 功能扩展任务清单 |
| optimization-round5.md | 第五轮优化记录 |

---

## 九、快速启动

### 本地开发

```bash
# 后端
cd backend
cp ../.env.example .env    # 填入 AI_API_KEY
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev                # http://localhost:5173
```

### Docker 部署

```bash
cp .env.example .env       # 填入 AI_API_KEY
docker-compose up -d       # 前端 :80, 后端 :8000, MySQL :3306
```

### 运行测试

```bash
cd backend
python -m pytest tests/ -q
```

---

## 十、开发历程

| 阶段 | 内容 |
|------|------|
| 一~三 | 项目初始化、基础架构、核心对话功能 |
| 四~八 | 五轮功能优化（安全/UX/代码质量/测试） |
| 九~十 | Alembic 迁移集成、构建历程文档 |
| 十一 | 全面改进（安全/测试/文档/UX） |
| 十二 | 语音输入 + 图片识别（多模态） |
| 十三 | 知识卡片功能 |
| 十四 | 学习进度面板 |
| UI 优化 | 侧边栏图标化、下拉菜单重构、主题切换图标化 |
