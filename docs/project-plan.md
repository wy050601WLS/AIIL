# AI 智慧学习系统 — 全周期实施计划

## 一、项目概述

| 项目 | 说明 |
|------|------|
| 项目名称 | AIIL（AI 智慧学习系统） |
| 仓库地址 | https://github.com/wy050601WLS/AIIL.git |
| 数据库 | MySQL 本地服务，数据库名 `ai`，账号 `root`，密码 `root` |
| 技术栈 | 前端 Vue3 + Vite + Pinia + Element Plus，后端 Python FastAPI，AI 小米 MiMo |
| 交付物 | 源码 + 项目全周期历程文档（docs/build-history.md） |

## 二、数据库表结构

| 表名 | 用途 | 字段 |
|------|------|------|
| `users` | 用户表 | id, username, password_hash, created_at |
| `conversations` | 对话会话表 | id, user_id, title, created_at |
| `messages` | 消息表 | id, conversation_id, role, content, created_at |

## 三、任务分解（串行执行，逐项核验）

---

### 阶段 A：项目基础设施搭建

#### A-1：克隆仓库并创建 .gitignore
- **执行工作内容**：克隆远程仓库，创建 .gitignore 文件
- **落地实现手段**：git clone + 手写 Python/Vue 项目忽略规则
- **新增功能及开发目的**：项目初始化，排除 node_modules、__pycache__、.env 等不需要版本控制的文件
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：仓库克隆成功，.gitignore 覆盖 Python 和 Node.js 常见忽略项

#### A-2：创建后端目录结构与依赖配置
- **执行工作内容**：创建 backend/ 目录及 app/ 子目录，创建 requirements.txt
- **落地实现手段**：mkdir + 手写 requirements.txt（fastapi, uvicorn, sqlalchemy, pymysql, python-jose, passlib, bcrypt, anthropic, python-dotenv）
- **新增功能及开发目的**：后端项目骨架，明确所有 Python 依赖
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：目录结构完整，requirements.txt 内容正确

#### A-3：创建前端项目
- **执行工作内容**：使用 Vite 创建 Vue3 项目到 frontend/ 目录，安装依赖
- **落地实现手段**：npm create vue@latest + npm install element-plus axios pinia vue-router
- **新增功能及开发目的**：前端项目脚手架，开发热更新
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：frontend/ 目录存在，npm run dev 可启动

---

### 阶段 B：数据库建表

#### B-1：创建 users、conversations、messages 三张表
- **执行工作内容**：编写 SQL 建表脚本并执行
- **落地实现手段**：CREATE TABLE SQL，含主键、外键、索引
- **新增功能及开发目的**：数据库基础结构，支撑用户、会话、消息三大核心实体
- **移除功能及废弃原因**：移除旧表 topic, knowledge_card, chat_session, topic_relation（旧方案遗留，与新设计不兼容）
- **调整功能及修改动因**：技术栈从 React+Node.js 变更为 FastAPI+Vue3，数据模型重新设计
- **验收标准**：三张表存在，外键和索引正确

---

### 阶段 C：后端核心模块

#### C-1：配置模块 config.py + 数据库模块 database.py
- **执行工作内容**：创建 `backend/app/config.py` 和 `backend/app/database.py`
- **落地实现手段**：pydantic-settings 读取 .env，SQLAlchemy create_engine + sessionmaker
- **新增功能及开发目的**：统一配置管理与数据库连接
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：模块可导入，数据库连接成功

#### C-2：ORM 模型 user.py + conversation.py
- **执行工作内容**：创建 `backend/app/models/user.py` 和 `backend/app/models/conversation.py`
- **落地实现手段**：SQLAlchemy declarative_base，定义 User, Conversation, Message 三个模型类
- **新增功能及开发目的**：ORM 映射，Python 对象操作数据库
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：模型类可导入，与数据库表结构一致

#### C-3：Pydantic Schema user.py + conversation.py
- **执行工作内容**：创建 `backend/app/schemas/user.py` 和 `backend/app/schemas/conversation.py`
- **落地实现手段**：定义请求/响应 Pydantic 模型（UserCreate, UserLogin, Token, ChatRequest 等）
- **新增功能及开发目的**：API 数据校验与序列化
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：Schema 类可导入，字段类型正确

#### C-4：安全工具 security.py
- **执行工作内容**：创建 `backend/app/utils/security.py`
- **落地实现手段**：passlib bcrypt 密码哈希，python-jose JWT 编解码
- **新增功能及开发目的**：密码加密与 Token 生成/验证
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：函数可调用，哈希/验证/Token 生成均正常

#### C-5：认证路由 auth.py + 认证服务 auth_service.py
- **执行工作内容**：创建 `backend/app/routers/auth.py` 和 `backend/app/services/auth_service.py`
- **落地实现手段**：FastAPI APIRouter，POST /register 和 POST /login 端点
- **新增功能及开发目的**：用户注册和登录 API
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：注册返回用户信息，登录返回 JWT token

#### C-6：会话管理路由 history.py + 对话服务 chat_service.py
- **执行工作内容**：创建 `backend/app/routers/history.py` 和 `backend/app/services/chat_service.py`
- **落地实现手段**：GET /conversations, POST /conversations, GET /conversations/{id}/messages
- **新增功能及开发目的**：会话的创建、列表查询、消息查询
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：三个接口可正常调用

#### C-7：AI 对话路由 chat.py + AI 服务 ai_service.py
- **执行工作内容**：创建 `backend/app/routers/chat.py` 和 `backend/app/services/ai_service.py`
- **落地实现手段**：POST /chat 端点，SSE StreamingResponse，Anthropic SDK 调用 MiMo API
- **新增功能及开发目的**：AI 流式对话核心功能
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：发送消息后收到 SSE 流式响应

#### C-8：应用入口 main.py + 环境变量 .env
- **执行工作内容**：创建 `backend/app/main.py` 和 `backend/.env`
- **落地实现手段**：FastAPI 实例，CORS 中间件，路由挂载，.env 配置数据库和 API Key
- **新增功能及开发目的**：后端服务入口，所有模块集成
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：uvicorn 启动无报错，所有 API 端点可访问

---

### 阶段 D：前端核心模块

#### D-1：API 请求封装 + 路由配置 + 状态管理
- **执行工作内容**：创建 `frontend/src/api/auth.js`、`frontend/src/api/chat.js`、`frontend/src/router/index.js`、`frontend/src/stores/user.js`、`frontend/src/stores/chat.js`
- **落地实现手段**：Axios 实例 + 拦截器，Vue Router 路由定义，Pinia store
- **新增功能及开发目的**：前端基础设施，API 调用、页面路由、全局状态管理
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：模块可导入，路由可切换

#### D-2：全局样式 + 入口文件
- **执行工作内容**：创建 `frontend/src/style.css`（科技深色主题），修改 `frontend/src/main.js` 和 `frontend/src/App.vue`
- **落地实现手段**：CSS 变量定义深色主题色板，main.js 注册 Element Plus/Pinia/Router
- **新增功能及开发目的**：科技深色 UI 基础，应用入口配置
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：深色主题生效，应用可启动

#### D-3：登录页 Login.vue + 注册页 Register.vue
- **执行工作内容**：创建 `frontend/src/views/Login.vue` 和 `frontend/src/views/Register.vue`
- **落地实现手段**：Element Plus 表单组件，居中卡片布局，表单验证
- **新增功能及开发目的**：用户登录注册界面
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：页面可访问，注册/登录流程可走通

#### D-4：对话主页 Chat.vue + 侧边栏 Sidebar.vue
- **执行工作内容**：创建 `frontend/src/views/Chat.vue` 和 `frontend/src/components/Sidebar.vue`
- **落地实现手段**：左侧会话列表侧边栏 + 右侧对话区域布局
- **新增功能及开发目的**：对话主界面框架
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：页面布局正确，会话列表可展示

#### D-5：消息组件 ChatMessage.vue + 输入组件 ChatInput.vue
- **执行工作内容**：创建 `frontend/src/components/ChatMessage.vue` 和 `frontend/src/components/ChatInput.vue`
- **落地实现手段**：消息气泡渲染，输入框 + 发送按钮，Markdown 支持
- **新增功能及开发目的**：对话交互核心组件
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：消息气泡正确显示，输入发送功能正常

#### D-6：SSE 流式对话集成
- **执行工作内容**：在 Chat.vue 和 api/chat.js 中实现 SSE 流式接收与渲染
- **落地实现手段**：fetch + ReadableStream 读取 SSE 数据，逐 token 更新消息内容
- **新增功能及开发目的**：AI 回复实时流式输出
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：AI 回复逐字显示，打字效果流畅

---

### 阶段 E：联调与交付

#### E-1：前后端联调测试
- **执行工作内容**：启动前后端，测试所有 API 接口和页面功能
- **落地实现手段**：手动测试 + 浏览器验证
- **新增功能及开发目的**：确保系统整体可用
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：所有页面功能正常，无报错

#### E-2：Git 提交与推送
- **执行工作内容**：将所有代码提交到 Git 仓库
- **落地实现手段**：git add + git commit + git push
- **新增功能及开发目的**：代码版本管理
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：代码推送到远程仓库

#### E-3：历程文档归档
- **执行工作内容**：更新 docs/build-history.md，记录所有迭代变更
- **落地实现手段**：按标准化模板补全所有任务的变更记录
- **新增功能及开发目的**：项目交付物完整性
- **移除功能及废弃原因**：无
- **调整功能及修改动因**：无
- **验收标准**：文档完整覆盖所有变更

---

## 四、执行规则

1. **串行执行**：每次仅执行一项细分任务
2. **完成即停**：任务完成后暂停，等待核验
3. **核验通过**：确认无问题后方可进入下一任务
4. **实时记录**：每项任务完成后同步更新 docs/build-history.md
