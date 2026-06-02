# AI 智慧学习系统 — 项目全景文档

## 零、项目背景

### 为什么做这个项目

传统学习方式存在几个痛点：

- **答疑效率低** — 遇到问题需要等老师/同学回复，或在海量搜索结果中筛选
- **知识碎片化** — 学习过程中的问答散落在各处，难以回顾和整理
- **缺乏数据反馈** — 不清楚自己的学习频率、知识覆盖范围、薄弱环节

AI 对话式学习可以即时解答问题，但通用聊天工具（如 ChatGPT）缺乏学习场景的专属功能：知识沉淀、学习数据追踪、个性化偏好等。

### 项目定位

**AI 智慧学习（AIIL）** 是一个面向学生的 AI 对话式学习助手，目标是：

1. **即时答疑** — 通过 AI 多轮对话，快速解答学习问题
2. **知识沉淀** — 将 AI 回复中的精华内容提取为知识卡片，便于回顾
3. **学习可视化** — 通过数据面板追踪学习频率和知识覆盖
4. **多模态交互** — 支持图片识别（拍题/看图）和语音输入，降低使用门槛

### 技术选型理由

| 选型 | 理由 |
|------|------|
| Vue3 + Vite | 轻量、快速、生态成熟，适合中小型项目 |
| FastAPI | 异步高性能，原生支持 SSE 流式响应，自动 API 文档 |
| MySQL | 成熟可靠，适合结构化数据存储 |
| MiMo AI | 国内可用，兼容 OpenAI 接口格式，成本可控 |
| Alembic | 数据库版本管理，支持升级/回滚 |
| Docker Compose | 一键部署，环境一致性 |

### 项目仓库

GitHub：https://github.com/wy050601WLS/AIIL.git

---

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

### AI 对话

| 功能 | 说明 |
|------|------|
| 流式对话 | SSE 实时输出，逐字显示 AI 回复 |
| 多轮对话 | 自动加载历史消息作为上下文 |
| Markdown 渲染 | 标题、列表、加粗、引用、表格等富文本展示 |
| 代码高亮 | highlight.js 语法高亮，支持多语言 |
| 停止生成 | 对话过程中可随时中断 AI 输出 |
| 重新生成 | 对最后一条 AI 回复重新生成 |
| 多模型切换 | 下拉选择不同 AI 模型，偏好持久化到 localStorage |
| 自定义系统提示词 | 统一使用配置的默认学习助手提示词 |

### 消息操作

| 功能 | 说明 |
|------|------|
| 复制消息 | 一键复制消息文本（AI 消息复制渲染后的纯文本） |
| 编辑消息 | 用户消息支持修改内容 |
| 删除消息 | 删除单条消息，带确认弹窗 |
| 提取卡片 | AI 回复一键保存为知识卡片 |
| 图片消息 | 消息中展示图片缩略图，点击全屏预览 |

### 图片识别

| 功能 | 说明 |
|------|------|
| 图片上传 | 点击按钮选择图片文件 |
| 粘贴图片 | Ctrl+V 直接粘贴剪贴板中的图片 |
| 多图支持 | 最多 5 张图片，带缩略图预览和移除 |
| AI 多模态 | 图片以 base64 发送，转为 OpenAI 多模态格式识别 |

### 语音输入

| 功能 | 说明 |
|------|------|
| 语音转文字 | 浏览器 Web Speech API，中文实时识别 |
| 连续录音 | continuous 模式，持续识别不停顿 |
| 实时反馈 | 录音中显示脉冲红点动画 |
| 浏览器兼容 | 不支持的浏览器自动隐藏按钮 |

### 会话管理

| 功能 | 说明 |
|------|------|
| 新建会话 | 一键创建新对话 |
| 重命名 | 会话标题行内编辑 |
| 置顶/取消置顶 | 重要会话置顶显示 |
| 归档/取消归档 | 归档会话单独查看 |
| 删除 | 带确认弹窗，级联删除关联消息 |
| 搜索 | 按标题关键词实时过滤 |
| 导出 Markdown | 下载完整对话记录为 .md 文件 |
| 下拉菜单 | 会话 hover 显示 ⋯ 按钮，点击弹出操作菜单 |

### 知识卡片

| 功能 | 说明 |
|------|------|
| 提取卡片 | 从 AI 回复中一键保存精华内容 |
| 卡片列表 | 按创建时间倒序展示 |
| 标签筛选 | 支持按标签过滤卡片 |
| 删除卡片 | 带确认弹窗 |
| 来源标记 | 记录卡片来源（对话 ID） |

### 学习面板

| 功能 | 说明 |
|------|------|
| 统计卡片 | 对话总数、消息总数、知识卡片数、活跃天数 |
| 趋势图 | 最近 30 天消息量柱状图（纯 CSS 实现） |
| 热门标签 | 知识卡片标签 Top 10，带数量角标 |

### 用户系统

| 功能 | 说明 |
|------|------|
| 注册 | 用户名 + 密码，密码强度验证 |
| 登录 | JWT 认证，Token 24 小时有效 |
| 个人资料 | emoji 头像选择、昵称修改 |
| 偏好设置 | 字体大小（12-20）、消息密度（紧凑/正常/宽松）、默认模型 |
| 密码修改 | 验证旧密码后设置新密码 |
| 深色/浅色主题 | 一键切换，localStorage 持久化 |

### 界面与交互

| 功能 | 说明 |
|------|------|
| 响应式布局 | 移动端适配，侧边栏抽屉式展开 |
| 键盘快捷键 | Ctrl+N 新建、Ctrl+K 搜索、Ctrl+Shift+E 导出、Esc 关闭侧边栏 |
| 自动滚动 | 新消息自动滚动到底部 |
| 输入框自适应 | textarea 高度随内容自动调整（最大 150px） |
| 侧边栏图标导航 | 底栏图标按钮：面板、卡片、主题切换、设置、退出 |

### 安全

| 功能 | 说明 |
|------|------|
| JWT 认证 | 所有 API 需 Bearer Token |
| 密码哈希 | bcrypt 加密存储 |
| 接口限流 | slowapi 全局 60 次/分钟 |
| CORS 配置 | 可配置允许的跨域来源 |
| 归属校验 | 所有操作校验资源归属权 |
| 401 自动跳转 | Token 过期自动跳转登录页 |

### 部署与测试

| 功能 | 说明 |
|------|------|
| Docker Compose | 一键部署 MySQL + 后端 + 前端 Nginx |
| Alembic 迁移 | 数据库版本管理，支持升级/回滚 |
| CI 工作流 | GitHub Actions：后端 pytest + 前端 vite build |
| 单元测试 | 24 个 pytest 测试，覆盖认证、对话、消息、功能、面板 |

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
│  │ Cards    │ │          │ │ dashboard    │  │
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
| system_prompt | TEXT | （已废弃，保留列） |
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
│   ├── history.py         # 会话管理路由（CRUD/置顶/归档）
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
├── test_features.py       # 8 个测试：置顶/归档/资料/密码/模型
└── test_dashboard.py      # 3 个测试：空数据/结构验证/未授权
```

共 **24 个测试**，全部通过。

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
│   └── ChatInput.vue      # 输入区（文本/图片上传/语音/发送）
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
| UI 优化 | 侧边栏图标化、下拉菜单重构、主题切换图标化、移除系统提示词 |

---

## 十一、核心实现模式

### SSE 流式对话（最关键的数据流）

```
前端 ChatInput emit('send', {content, images[]})
  → chatStore.sendMessage(content, images)
    → 乐观更新：push 用户消息 + 空的 assistant 占位到 messages[]
    → 创建 AbortController，loading=true
    → api/chat.js: streamChat() 用原生 fetch（非 Axios）读取 SSE
      → POST /api/chat，body: {conversation_id, content, model, regenerate, images}
        → FastAPI: get_current_user 解析 JWT
        → verify_conversation_owner 校验归属
        → save_user_message 存用户消息到 DB
        → load_history 构建完整历史（含 system prompt + 多模态格式）
        → call_ai_api: httpx 流式调用 AI，收集所有 chunk
        → 存 assistant 回复到 DB
        → StreamingResponse 逐 chunk 回放给前端
      → 前端 onToken: messages[idx].content += token（逐字追加）
      → onDone: loading=false
    → 中断：AbortController.abort() 触发 fetch signal
```

**关键细节：** 后端是"回放式 SSE"——先完整接收 AI 响应并存库，再逐 chunk 回放给前端。保证数据完整性，前端看到的是逐字效果。

### 认证流程

```
登录 → POST /auth/login → 返回 {access_token: "jwt..."}
  → 前端存 localStorage.setItem('token', token)
  → Axios 拦截器自动附加 Authorization: Bearer {token}
  → 后端 get_current_user: HTTPBearer → decode_access_token → 查 DB → 返回 User 对象
  → 401 时前端拦截器自动清 token 并跳转 /login
```

### 图片处理管线

```
前端选择/粘贴图片 → FileReader.readAsDataURL → base64 data URL
  → emit('send', {content, images: [base64, ...]})
  → 后端 save_user_message: JSON.stringify(images) 存入 messages.images 列
  → load_history: 含图片的消息转为 OpenAI 多模态格式：
    [{"type":"text","text":"..."}, {"type":"image_url","image_url":{"url":"data:..."}}]
  → 前端显示：ChatMessage 读取 msg.images，展示缩略图，点击 Teleport 全屏预览
```

### 状态管理模式

所有 Store 使用 Pinia Composition API（`defineStore` + `ref` + `computed`）：

| Store | 核心状态 | 关键操作 |
|-------|---------|---------|
| user | token, username, nickname, avatar, preferences | login, logout, loadProfile, saveProfile |
| chat | conversations, currentId, messages, loading, models, currentModel | sendMessage（含 SSE）, regenerate, stopStreaming |
| cards | cards, loading | loadCards, addCard, removeCard |
| dashboard | stats, loading | loadStats |
| theme | theme | toggle（深色/浅色，持久化到 localStorage） |

### 测试模式

- 测试数据库：SQLite 内存（`sqlite:///./test.db`），每个测试自动 create_all/drop_all
- `conftest.py` 提供 `client`（未认证）和 `auth_client`（已登录）fixture
- slowapi 在测试中通过 `enabled=False` 禁用
- 测试中不调用真实 AI API，仅测试 CRUD 和认证

---

## 十二、技术债务与已知问题

| 问题 | 位置 | 说明 |
|------|------|------|
| system_prompt 列残留 | conversations 表 | 已废弃但保留列，未做迁移删除 |
| 回放式 SSE | ai_service.call_ai_api | 后端等 AI 全部返回再回放，非真流式。延迟 = AI 完整响应时间 |
| 图片存 base64 | messages.images | 大图会撑爆数据库，应改为文件存储 + URL 引用 |
| 无分页 | 会话列表、消息列表、卡片列表 | 全量加载，数据量大时性能差 |
| 偏好存 JSON 文本 | users.preferences | 无 schema 验证，前端直接 JSON.parse |
| init_db.sql 未同步 | backend/init_db.sql | 仍用旧表结构，缺少 knowledge_cards 表 |
| HelloWorld.vue 残留 | frontend/src/components/ | Vite 脚手架组件，未删除 |
| 无前端测试 | frontend/tests/ | 只有后端 24 个 pytest，前端无 Vitest |
| AI 模型硬编码默认值 | config.py | AI_MODEL 默认值与 .env.example 不一致 |
| conversations 无标题自动更新 | - | 新建时标题"新对话"，不会根据首条消息自动重命名 |

---

## 十三、扩展方向

### 高价值（核心学习场景）

| 方向 | 说明 | 改动范围 |
|------|------|---------|
| **对话内搜索** | 搜索当前会话的消息内容 | 前端 Chat.vue |
| **知识卡片编辑** | 卡片内容修改 + 标签编辑 | 后端 PUT /cards/{id} + 前端 Cards.vue |
| **卡片复习模式** | 间隔复习（类 Anki），按遗忘曲线推送 | 新表 reviews + 新路由 + 前端复习页 |
| **对话标题自动更新** | 首次 AI 回复后用摘要更新标题 | 后端 chat.py |
| **批量导出** | 导出所有知识卡片为 Markdown/CSV | 后端新端点 + 前端按钮 |

### 中等价值（体验提升）

| 方向 | 说明 | 改动范围 |
|------|------|---------|
| **消息分页** | 长会话消息分页加载，避免一次全量 | 后端分页参数 + 前端无限滚动 |
| **图片文件存储** | base64 改为上传到服务器/对象存储 | 后端新上传端点 + 迁移 |
| **对话模板** | 预设 prompt 模板（翻译、解释、练习等） | 新表 + 前端模板选择器 |
| **多语言支持** | i18n，界面和 AI 提示词切换语言 | vue-i18n + 配置化 prompt |
| **消息引用/回复** | 引用某条消息进行追问 | messages 表加 parent_id + 前端引用 UI |

### 低价值（锦上添花）

| 方向 | 说明 |
|------|------|
| WebSocket 替代 SSE | 支持双向通信，但当前场景不需要 |
| 用户头像上传 | 替代 emoji 头像，需要文件存储 |
| 对话分享 | 生成公开链接分享对话记录 |
| 无障碍优化 | ARIA 标签、键盘焦点指示、屏幕阅读器支持 |
| 前端单元测试 | Vitest 测试组件和 store |

---

## 十四、改进建议（按优先级）

### P0 — 应该做

1. **修复 init_db.sql** — 同步 knowledge_cards 表结构，否则 Docker 部署会缺表
2. **删除 HelloWorld.vue** — 清理无用文件
3. **AI 模型默认值统一** — config.py 和 .env.example 的 AI_MODEL 保持一致

### P1 — 建议做

4. **真流式 SSE** — 后端用 `async for` 逐 chunk 转发给前端，而非先收集再回放。降低首 token 延迟
5. **消息分页** — `GET /conversations/{id}/messages?offset=0&limit=50`，前端无限滚动
6. **知识卡片编辑** — `PUT /cards/{id}` 支持修改内容和标签
7. **对话标题自动更新** — 首次 AI 回复后用前 20 字更新标题

### P2 — 可以做

8. **图片存储改为文件** — 上传到 `backend/uploads/`，messages.images 存 URL 列表
9. **卡片复习功能** — 新表 `reviews`（card_id, next_review, interval, ease），间隔重复算法
10. **前端测试** — Vitest 测试 store 和关键组件

---

## 十五、开发约定

### 后端

- **分层：Router → Service → Model**，Router 只做请求解析和响应，Service 做业务逻辑
- **认证：** 所有需登录的端点用 `Depends(get_current_user)`
- **归属校验：** 涉及用户数据的操作必须校验 `resource.user_id == user.id`
- **错误码：** 404 资源不存在，403 无权访问，422 参数验证失败
- **测试：** 新增功能必须有对应 pytest 测试

### 前端

- **状态管理：** 全局状态用 Pinia store，组件内用 ref/computed
- **API 调用：** 非流式用 Axios（自动 token/401），流式用原生 fetch
- **组件通信：** 父子 props/emits，跨组件用 store
- **主题：** 用 CSS 变量（`var(--xxx)`），不要硬编码颜色
- **响应式：** 768px 断点，移动端侧边栏抽屉式

### Git

- 提交信息格式：`type: 中文描述`（feat/fix/refactor/docs）
- 每次功能完成后更新 `docs/build-history.md`
- 单次提交只做一件事

---

## 十六、环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DB_HOST | localhost | MySQL 主机 |
| DB_PORT | 3306 | MySQL 端口 |
| DB_USER | root | MySQL 用户 |
| DB_PASSWORD | root | MySQL 密码 |
| DB_NAME | ai | 数据库名 |
| JWT_SECRET_KEY | aiil-secret-key | JWT 签名密钥 |
| JWT_ALGORITHM | HS256 | JWT 算法 |
| JWT_EXPIRE_HOURS | 24 | Token 有效期（小时） |
| AI_API_KEY | - | MiMo API 密钥 |
| AI_BASE_URL | https://token-plan-cn.xiaomimimo.com | AI 接口地址 |
| AI_MODEL | mimo-v2.5-pro | 默认 AI 模型 |
| CORS_ORIGINS | http://localhost:5173 | 允许的跨域来源 |
| HOST | 0.0.0.0 | 服务监听地址 |
| PORT | 8000 | 服务监听端口 |

---

## 十七、快速启动

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
