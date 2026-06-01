# AI 智慧学习 - 对话式学习助手设计文档

## 1. 项目概述

**项目名称**：AI 智慧学习（AIIL - AI Intelligent Learning）

**产品定位**：面向学生的 AI 对话式学习助手，通过自然语言问答帮助学生理解知识点、获取学习辅导。

**技术栈**：
- 后端：Python FastAPI
- 前端：Vue3 + Vite + Pinia + Vue Router + Element Plus
- 数据库：MySQL（数据库名：AI）
- AI 模型：小米 MiMo（Anthropic 兼容接口）
- 认证：JWT（JSON Web Token）

**Git 仓库**：https://github.com/wy050601WLS/AIIL.git

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────┐
│                   Vue3 前端                       │
│  (Vite + Pinia + Vue Router + Element Plus)      │
│  科技深色主题                                      │
└──────────────────────┬──────────────────────────┘
                       │ REST API + SSE
┌──────────────────────▼──────────────────────────┐
│                  FastAPI 后端                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ 用户模块  │ │ 对话模块  │ │  AI 服务模块     │ │
│  │ 注册/登录 │ │ 会话管理  │ │ MiMo API 调用    │ │
│  │ JWT 鉴权  │ │ 消息存储  │ │ SSE 流式输出     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────┬──────────────────────────┘
                       │
              ┌────────▼────────┐
              │     MySQL       │
              │   数据库: AI     │
              └─────────────────┘
```

### 2.2 架构方案

采用**前后端分离 + SSE 流式响应**方案：
- 前端独立部署（Vite dev server / Nginx 静态托管）
- 后端 FastAPI 提供 REST API + SSE 流式接口
- AI 回复采用 Server-Sent Events 逐 token 输出，体验接近 ChatGPT
- 前后端通过 CORS 处理跨域

## 3. 目录结构

### 3.1 后端结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口，CORS 配置
│   ├── config.py            # 环境变量配置（数据库、JWT、API Key）
│   ├── database.py          # SQLAlchemy 数据库连接与会话管理
│   ├── models/              # SQLAlchemy ORM 模型
│   │   ├── user.py          # 用户模型
│   │   └── conversation.py  # 会话与消息模型
│   ├── schemas/             # Pydantic 请求/响应数据模型
│   │   ├── user.py          # 用户相关 schema
│   │   └── conversation.py  # 对话相关 schema
│   ├── routers/             # API 路由层
│   │   ├── auth.py          # 认证相关接口（注册/登录）
│   │   ├── chat.py          # 对话接口（发送消息、SSE 流式响应）
│   │   └── history.py       # 历史记录接口（会话列表、消息查询）
│   ├── services/            # 业务逻辑层
│   │   ├── auth_service.py  # 认证业务（密码哈希、JWT 生成/验证）
│   │   ├── chat_service.py  # 对话业务（会话管理、消息存储）
│   │   └── ai_service.py    # AI 服务（MiMo API 调用、流式处理）
│   └── utils/               # 工具函数
│       └── security.py      # 安全工具（bcrypt、JWT 编解码）
├── requirements.txt         # Python 依赖
└── .env                     # 环境变量（不提交 Git）
```

### 3.2 前端结构

```
frontend/
├── src/
│   ├── api/                 # API 请求封装（Axios 实例 + 请求/响应拦截器）
│   │   ├── auth.js          # 认证相关 API
│   │   └── chat.js          # 对话相关 API + SSE 连接
│   ├── views/               # 页面级组件
│   │   ├── Login.vue        # 登录页
│   │   ├── Register.vue     # 注册页
│   │   └── Chat.vue         # 对话主页面
│   ├── components/          # 可复用组件
│   │   ├── ChatMessage.vue  # 单条消息气泡组件
│   │   ├── ChatInput.vue    # 消息输入框组件
│   │   └── Sidebar.vue      # 侧边栏（会话列表）
│   ├── stores/              # Pinia 状态管理
│   │   ├── user.js          # 用户状态（token、用户信息）
│   │   └── chat.js          # 对话状态（当前会话、消息列表）
│   ├── router/              # Vue Router 路由配置
│   │   └── index.js
│   ├── App.vue              # 根组件
│   ├── main.js              # 应用入口
│   └── style.css            # 全局样式（科技深色主题）
├── index.html               # HTML 入口
├── vite.config.js           # Vite 配置（代理、别名）
├── package.json
└── .env                     # 前端环境变量
```

## 4. 数据库设计

### 4.1 用户表 (users)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希（bcrypt） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 注册时间 |

### 4.2 对话会话表 (conversations)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 会话ID |
| user_id | INT | FK → users.id, NOT NULL | 所属用户 |
| title | VARCHAR(100) | DEFAULT '新对话' | 会话标题（首条消息摘要） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 4.3 消息表 (messages)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 消息ID |
| conversation_id | INT | FK → conversations.id, NOT NULL | 所属会话 |
| role | ENUM('user', 'assistant') | NOT NULL | 消息角色 |
| content | TEXT | NOT NULL | 消息内容 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 发送时间 |

### 4.4 索引设计

- `users.username` — UNIQUE INDEX（登录查询）
- `conversations.user_id` — INDEX（按用户查会话）
- `messages.conversation_id` — INDEX（按会话查消息）

## 5. API 接口设计

### 5.1 认证接口

#### POST /api/auth/register
- 请求体：`{ "username": "string", "password": "string" }`
- 响应：`{ "id": int, "username": "string" }`
- 错误：409 用户名已存在

#### POST /api/auth/login
- 请求体：`{ "username": "string", "password": "string" }`
- 响应：`{ "access_token": "string", "token_type": "bearer" }`
- 错误：401 用户名或密码错误

### 5.2 对话接口

#### GET /api/conversations
- Header：`Authorization: Bearer <token>`
- 响应：`[{ "id": int, "title": "string", "created_at": "datetime" }]`

#### POST /api/conversations
- Header：`Authorization: Bearer <token>`
- 请求体：`{ "title": "string" }`（可选，默认"新对话"）
- 响应：`{ "id": int, "title": "string", "created_at": "datetime" }`

#### GET /api/conversations/{id}/messages
- Header：`Authorization: Bearer <token>`
- 响应：`[{ "id": int, "role": "string", "content": "string", "created_at": "datetime" }]`

#### POST /api/chat
- Header：`Authorization: Bearer <token>`
- 请求体：`{ "conversation_id": int, "content": "string" }`
- 响应：SSE 流式事件流
  - 事件类型：`message`
  - 数据格式：`{ "content": "token片段" }`
  - 结束标记：`{ "done": true }`

## 6. 核心流程

### 6.1 AI 对话流程

```
1. 用户在输入框输入问题，点击发送
2. 前端 POST /api/chat（携带 conversation_id + 用户消息）
3. 后端存储用户消息到 messages 表
4. 后端从 messages 表加载该会话的历史消息（最近 N 条作为上下文）
5. 后端调用 MiMo API（stream=true），传入消息列表
6. MiMo API 返回流式响应
7. 后端通过 SSE 逐 token 转发给前端
8. 前端实时拼接渲染 AI 回复内容
9. 流结束后，后端将完整 AI 回复存入 messages 表
10. 如果是会话首条消息，自动更新会话 title
```

### 6.2 认证流程

```
1. 用户注册：密码经 bcrypt 哈希后存入数据库
2. 用户登录：验证密码哈希，生成 JWT token（有效期 24h）
3. 后续请求：前端在 Authorization header 携带 token
4. 后端中间件验证 token 有效性，提取 user_id
```

## 7. AI 模型配置

- **服务**：小米 MiMo（Anthropic 兼容接口）
- **API Base URL**：`https://token-plan-cn.xiaomimimo.com/anthropic`
- **调用方式**：使用 Anthropic Python SDK，配置自定义 base_url
- **流式输出**：`stream=True`
- **System Prompt**：设定 AI 为学习助手角色，引导式解答而非直接给答案

## 8. 前端 UI 设计

### 8.1 科技深色主题

- **主色调**：深蓝/深灰背景 + 亮色（蓝/青）高亮
- **对话界面**：左侧会话列表侧边栏 + 右侧对话区域
- **消息气泡**：用户消息右对齐（深蓝底），AI 消息左对齐（深灰底）
- **输入区域**：底部固定输入框 + 发送按钮
- **动画**：AI 回复时显示打字光标效果

### 8.2 页面规划

1. **登录页**：居中卡片式表单，科技感渐变背景
2. **注册页**：与登录页风格一致
3. **对话主页**：三栏布局（侧边栏 + 对话区 + 可选详情区）

## 9. 安全设计

- 密码使用 bcrypt 哈希存储，不存明文
- JWT token 设置合理过期时间（24小时）
- API 接口鉴权中间件，未认证返回 401
- 前端 token 存储在 localStorage（V1 简化方案）
- CORS 仅允许前端域名访问
- SQL 注入防护：使用 SQLAlchemy ORM 参数化查询
- .env 文件不提交 Git，敏感配置通过环境变量管理

## 10. V1 MVP 功能清单

| # | 功能 | 说明 |
|---|------|------|
| 1 | 用户注册 | 用户名 + 密码注册，bcrypt 加密存储 |
| 2 | 用户登录 | 用户名 + 密码登录，返回 JWT token |
| 3 | 新建对话 | 创建新的对话会话 |
| 4 | AI 问答对话 | 发送问题，AI 流式回复（SSE） |
| 5 | 对话历史 | 查看历史会话列表和消息记录 |
| 6 | 科技深色 UI | 深色主题，现代化交互设计 |

## 11. 开发计划概览

任务按依赖顺序排列，每次仅执行一个细分任务：

1. 项目初始化（Git、目录结构、依赖配置）
2. 数据库建表（users、conversations、messages）
3. 后端用户注册接口
4. 后端用户登录接口
5. 后端 JWT 鉴权中间件
6. 后端会话管理接口
7. 后端 AI 对话接口（SSE 流式）
8. 后端历史记录接口
9. 前端项目初始化 + 路由配置
10. 前端登录/注册页面
11. 前端对话主页面
12. 前端 SSE 流式对话集成
13. 前端会话历史功能
14. 联调测试与 Bug 修复
