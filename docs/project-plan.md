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

| 编号 | 任务 | 实现手段 | 目的 | 验收标准 |
|------|------|---------|------|---------|
| A-1 | 克隆仓库并创建 .gitignore | git clone + 手写 Python/Vue 忽略规则 | 排除 node_modules、__pycache__、.env 等 | .gitignore 覆盖常见忽略项 |
| A-2 | 创建后端目录与依赖配置 | mkdir + 手写 requirements.txt | 后端项目骨架，明确 Python 依赖 | 目录结构完整，requirements.txt 正确 |
| A-3 | 创建前端项目 | npm create vue@latest + npm install | 前端脚手架，开发热更新 | npm run dev 可启动 |

---

### 阶段 B：数据库建表

| 编号 | 任务 | 实现手段 | 目的 | 验收标准 |
|------|------|---------|------|---------|
| B-1 | 创建 users / conversations / messages 表 | CREATE TABLE SQL，含主键、外键、索引 | 支撑用户、会话、消息三大核心实体 | 三张表存在，外键和索引正确 |

> **备注：** 移除旧表 topic, knowledge_card, chat_session, topic_relation（旧方案遗留）。技术栈从 React+Node.js 变更为 FastAPI+Vue3，数据模型重新设计。

---

### 阶段 C：后端核心模块

| 编号 | 任务 | 实现手段 | 目的 | 验收标准 |
|------|------|---------|------|---------|
| C-1 | 配置模块 config.py + 数据库模块 database.py | pydantic-settings 读 .env，SQLAlchemy create_engine | 统一配置管理与数据库连接 | 模块可导入，连接成功 |
| C-2 | ORM 模型 user.py + conversation.py | SQLAlchemy declarative_base，定义 User/Conversation/Message | ORM 映射，Python 对象操作数据库 | 模型可导入，与表结构一致 |
| C-3 | Pydantic Schema user.py + conversation.py | 定义请求/响应 Pydantic 模型 | API 数据校验与序列化 | Schema 可导入，字段正确 |
| C-4 | 安全工具 security.py | passlib bcrypt 哈希，python-jose JWT 编解码 | 密码加密与 Token 生成/验证 | 函数可调用，流程正常 |
| C-5 | 认证路由 auth.py + 服务 auth_service.py | FastAPI APIRouter，POST /register 和 /login | 用户注册和登录 API | 注册返回用户信息，登录返回 JWT |
| C-6 | 会话管理路由 history.py + 服务 chat_service.py | GET/POST /conversations，GET .../messages | 会话创建、列表、消息查询 | 三个接口可正常调用 |
| C-7 | AI 对话路由 chat.py + 服务 ai_service.py | POST /chat，SSE StreamingResponse，httpx 调用 MiMo | AI 流式对话核心功能 | 发送消息后收到 SSE 流式响应 |
| C-8 | 应用入口 main.py + 环境变量 .env | FastAPI 实例 + CORS + 路由挂载 | 后端服务入口，所有模块集成 | uvicorn 启动无报错 |

---

### 阶段 D：前端核心模块

| 编号 | 任务 | 实现手段 | 目的 | 验收标准 |
|------|------|---------|------|---------|
| D-1 | API 封装 + 路由 + 状态管理 | Axios 拦截器，Vue Router，Pinia store | API 调用、页面路由、全局状态 | 模块可导入，路由可切换 |
| D-2 | 全局样式 + 入口文件 | CSS 变量深色主题，main.js 注册插件 | 科技深色 UI，应用入口配置 | 主题生效，应用可启动 |
| D-3 | 登录页 + 注册页 | Element Plus 表单，居中卡片布局 | 用户登录注册界面 | 注册/登录流程可走通 |
| D-4 | 对话主页 Chat.vue + 侧边栏 Sidebar.vue | 左侧会话列表 + 右侧对话区域 | 对话主界面框架 | 布局正确，会话列表可展示 |
| D-5 | 消息组件 + 输入组件 | 消息气泡渲染，输入框 + 发送按钮 | 对话交互核心组件 | 气泡正确显示，输入发送正常 |
| D-6 | SSE 流式对话集成 | fetch + ReadableStream 读取 SSE | AI 回复实时流式输出 | AI 回复逐字显示，流畅 |

---

### 阶段 E：联调与交付

| 编号 | 任务 | 实现手段 | 目的 | 验收标准 |
|------|------|---------|------|---------|
| E-1 | 前后端联调测试 | 手动测试 + 浏览器验证 | 确保系统整体可用 | 所有页面功能正常，无报错 |
| E-2 | Git 提交与推送 | git add + commit + push | 代码版本管理 | 代码推送到远程仓库 |
| E-3 | 历程文档归档 | 更新 docs/build-history.md | 项目交付物完整性 | 文档完整覆盖所有变更 |

---

## 四、执行规则

1. **串行执行**：每次仅执行一项细分任务
2. **完成即停**：任务完成后暂停，等待核验
3. **核验通过**：确认无问题后方可进入下一任务
4. **实时记录**：每项任务完成后同步更新 docs/build-history.md
