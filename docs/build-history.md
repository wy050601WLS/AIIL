# AI 智慧学习系统 — 全周期构建历程

## 项目信息

| 项目 | 说明 |
|------|------|
| 项目名称 | AIIL（AI 智慧学习系统） |
| 技术栈 | 前端 Vue3 + Vite + Pinia + Element Plus，后端 Python FastAPI，AI 小米 MiMo |
| 数据库 | MySQL，数据库名 `ai`，账号 `root` |

---

## A-1：克隆仓库并创建 .gitignore

| 维度 | 内容 |
|------|------|
| 执行工作 | 克隆远程仓库，创建 .gitignore 文件 |
| 实现手段 | git clone + 手写忽略规则 |
| 新增功能 | 项目初始化，排除 `__pycache__`、`node_modules`、`.env`、IDE 配置等不需版本控制的文件 |
| 移除功能 | 无 |
| 调整功能 | 无 |

## A-2：创建后端目录结构与依赖配置

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/` 目录及子目录，创建 `requirements.txt` |
| 实现手段 | mkdir + 手写 requirements.txt |
| 新增功能 | 后端项目骨架，依赖：fastapi, uvicorn, sqlalchemy, pymysql, python-jose, bcrypt, python-dotenv, httpx |
| 移除功能 | 无 |
| 调整功能 | 原 passlib[bcrypt] 替换为 bcrypt>=4.0.0（兼容性问题） |

## A-3：创建前端项目

| 维度 | 内容 |
|------|------|
| 执行工作 | 使用 Vite 创建 Vue3 项目到 `frontend/` 目录 |
| 实现手段 | npm create vue@latest |
| 新增功能 | 前端项目脚手架，含 Vite 开发服务器 |
| 移除功能 | 无 |
| 调整功能 | 无 |

## B-1：创建数据库表结构

| 维度 | 内容 |
|------|------|
| 执行工作 | 编写 ORM 模型定义 users、conversations、messages 三张表 |
| 实现手段 | SQLAlchemy declarative_base，含主键、外键、索引 |
| 新增功能 | users（用户表）、conversations（会话表）、messages（消息表） |
| 移除功能 | 移除旧表 topic, knowledge_card, chat_session, topic_relation（旧方案遗留） |
| 调整功能 | 技术栈从 React+Node.js 变更为 FastAPI+Vue3，数据模型重新设计 |

## C-1：配置模块 config.py + 数据库模块 database.py

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/config.py` 和 `backend/app/database.py` |
| 实现手段 | 自定义 Settings 类读取 .env，SQLAlchemy create_engine + sessionmaker |
| 新增功能 | 统一配置管理（数据库、JWT、AI 模型、服务器），数据库连接与 get_db 依赖注入 |
| 移除功能 | 无 |
| 调整功能 | 未使用 pydantic-settings，改用自定义类 + os.getenv（简化依赖） |

## C-2：ORM 模型 user.py + conversation.py

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/models/user.py` 和 `backend/app/models/conversation.py` |
| 实现手段 | SQLAlchemy Column 定义，relationship 关联 |
| 新增功能 | User、Conversation、Message 三个 ORM 模型，含级联删除 |
| 移除功能 | 无 |
| 调整功能 | 无 |

## C-3：Pydantic Schema user.py + conversation.py

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/schemas/user.py` 和 `backend/app/schemas/conversation.py` |
| 实现手段 | Pydantic BaseModel 定义请求/响应模型 |
| 新增功能 | UserCreate, UserLogin, UserResponse, Token, ConversationCreate, ConversationResponse, MessageResponse, ChatRequest |
| 移除功能 | 无 |
| 调整功能 | 无 |

## C-4：安全工具 security.py

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/utils/security.py` |
| 实现手段 | bcrypt 密码哈希，python-jose JWT 编解码，HTTPBearer 认证 |
| 新增功能 | hash_password, verify_password, create_access_token, decode_access_token, get_current_user |
| 移除功能 | 无 |
| 调整功能 | 原 passlib 替换为 bcrypt 直接调用 |

## C-5：认证路由 auth.py + 认证服务 auth_service.py

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/routers/auth.py` 和 `backend/app/services/auth_service.py` |
| 实现手段 | FastAPI APIRouter，POST /register 和 POST /login 端点，service 层封装业务逻辑 |
| 新增功能 | 用户注册（返回用户信息）、用户登录（返回 JWT token） |
| 移除功能 | 无 |
| 调整功能 | 无 |

## C-6：会话管理路由 history.py + 对话服务 chat_service.py

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/routers/history.py` 和 `backend/app/services/chat_service.py` |
| 实现手段 | FastAPI APIRouter，service 层封装业务逻辑，get_current_user 依赖注入鉴权 |
| 新增功能 | POST /conversations（创建会话）、GET /conversations（会话列表）、GET /conversations/{id}/messages（消息列表） |
| 移除功能 | 无 |
| 调整功能 | 无 |

## C-7：AI 对话路由 chat.py + AI 服务 ai_service.py

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/routers/chat.py` 和 `backend/app/services/ai_service.py` |
| 实现手段 | httpx 流式调用 MiMo API（OpenAI 兼容格式），SSE StreamingResponse，用户消息和助手回复持久化到数据库 |
| 新增功能 | POST /chat 端点，流式 AI 对话，自动保存对话历史，会话所有权校验 |
| 移除功能 | 无 |
| 调整功能 | 无 |

## C-8：应用入口 main.py + 环境变量 .env

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `backend/app/main.py`，确认 `.env` 配置完整 |
| 实现手段 | FastAPI 实例 + CORSMiddleware + 路由挂载，启动时自动建表 |
| 新增功能 | 后端服务入口，CORS 跨域支持，自动注册 auth/history/chat 三组路由 |
| 移除功能 | 无 |
| 调整功能 | 无 |

## D-1：API 请求封装 + 路由配置 + 状态管理

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `api/index.js`、`api/auth.js`、`api/chat.js`、`router/index.js`、`stores/user.js`、`stores/chat.js` |
| 实现手段 | Axios 实例 + 请求/响应拦截器，Vue Router 路由守卫，Pinia 组合式 store |
| 新增功能 | API 统一请求封装（自动带 token、401 跳转），路由配置（登录/注册/对话页），用户状态管理（登录/注册/登出），对话状态管理（会话列表/消息/SSE 流式） |
| 移除功能 | 无 |
| 调整功能 | 无 |

## D-2：全局样式 + 入口文件

| 维度 | 内容 |
|------|------|
| 执行工作 | 重写 `style.css`、`main.js`、`App.vue` |
| 实现手段 | CSS 变量定义科技深色主题色板，main.js 注册 Element Plus（含深色模式）/Pinia/Router，App.vue 使用 router-view |
| 新增功能 | 科技深色 UI 主题（深蓝紫色调），Element Plus 深色样式覆盖，全局滚动条美化 |
| 移除功能 | 移除 Vite 默认模板样式（HelloWorld 组件引用） |
| 调整功能 | style.css 从 Vite 默认样式完全重写为项目深色主题 |

## D-3：登录页 Login.vue + 注册页 Register.vue

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `views/Login.vue` 和 `views/Register.vue` |
| 实现手段 | Element Plus 表单组件，居中卡片布局，表单验证（用户名/密码长度、确认密码一致性） |
| 新增功能 | 登录页面（用户名+密码，回车提交）、注册页面（含确认密码校验），登录/注册页互跳链接 |
| 移除功能 | 无 |
| 调整功能 | 无 |

## D-4：对话主页 Chat.vue + 侧边栏 Sidebar.vue

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `views/Chat.vue` 和 `components/Sidebar.vue` |
| 实现手段 | Flex 左右布局，侧边栏会话列表 + 右侧消息区域，onMounted 加载会话列表 |
| 新增功能 | 对话主页面框架，侧边栏（会话列表、新建对话、当前用户、退出登录），消息区域（欢迎页+消息列表） |
| 移除功能 | 无 |
| 调整功能 | 无 |

## D-5：消息组件 ChatMessage.vue + 输入组件 ChatInput.vue

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `components/ChatMessage.vue` 和 `components/ChatInput.vue` |
| 实现手段 | 消息气泡（用户右侧蓝色/AI 左侧深色），textarea 自适应高度，Enter 发送 + Shift+Enter 换行 |
| 新增功能 | 消息气泡组件（头像+气泡，用户/AI 双方样式），输入组件（多行输入、发送按钮、加载状态） |
| 移除功能 | 无 |
| 调整功能 | 无 |

## D-6：SSE 流式对话集成

| 维度 | 内容 |
|------|------|
| 执行工作 | 确认 SSE 流式链路完整性，无需额外代码 |
| 实现手段 | fetch + ReadableStream 读取 SSE 数据流，onToken 回调逐 token 更新消息，Vue 响应式自动重渲染 |
| 新增功能 | AI 回复逐字显示（打字效果），完整链路：Chat.vue → chatStore.sendMessage → streamChat → onToken → ChatMessage.vue |
| 移除功能 | 无 |
| 调整功能 | D-1 的 api/chat.js 和 stores/chat.js 已包含完整 SSE 实现，本任务为验证确认 |

## E-1：前后端联调测试

| 维度 | 内容 |
|------|------|
| 执行工作 | 启动后端服务，测试所有 API 端点，修复 AI 模型配置 |
| 实现手段 | curl 逐一测试各端点，排查 MiMo API 模型名称和请求格式 |
| 新增功能 | 无 |
| 移除功能 | 移除 Anthropic SDK 依赖（ai_service.py 改用 httpx 直接调用 OpenAI 兼容格式） |
| 调整功能 | ① AI 模型从 `claude-sonnet-4-20250514` 改为 `mimo-v2.5-pro`（MiMo 平台实际可用模型）；② AI_BASE_URL 从 `/anthropic` 改为根路径（OpenAI 兼容端点）；③ ai_service.py 从 Anthropic SDK 改为 httpx + OpenAI SSE 格式 |

## CI-1：GitHub Actions CI/CD 工作流

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 `.github/workflows/ci.yml` |
| 实现手段 | GitHub Actions，push/PR 触发，并行执行 backend 和 frontend 两个 job |
| 新增功能 | 后端检查（Python 依赖安装 + 模块导入验证），前端检查（npm ci + 生产构建） |
| 移除功能 | 无 |
| 调整功能 | 无 |

## E-2：Git 提交与推送

| 维度 | 内容 |
|------|------|
| 执行工作 | 将所有代码提交到 Git 仓库并推送到远程 |
| 实现手段 | git add + git commit + git push |
| 新增功能 | 代码版本管理，2 个 commit（主功能 + CI 调整） |
| 移除功能 | CI 工作流文件因 GitHub token 缺少 workflow 权限暂时从 Git 移除（文件保留在本地） |
| 调整功能 | 无 |

## E-3：历程文档归档

| 维度 | 内容 |
|------|------|
| 执行工作 | 完善 docs/build-history.md，修正不准确记录，补全所有任务变更 |
| 实现手段 | 逐项核对实际实现与文档记录的一致性 |
| 新增功能 | 无 |
| 移除功能 | 无 |
| 调整功能 | 修正 A-2 依赖列表（anthropic→httpx），修正 C-7 实现手段（Anthropic SDK→httpx），补全 E-2/E-3 记录 |

---

### E-1 测试结果

| 端点 | 结果 |
|------|------|
| GET / | 正常 |
| POST /auth/register | 正常 |
| POST /auth/login | 正常，返回 JWT token |
| POST /conversations | 正常 |
| GET /conversations | 正常 |
| GET /conversations/{id}/messages | 正常 |
| POST /chat | 正常，SSE 流式输出 AI 回复 |

---

## 项目完成

所有任务（A-1 ~ E-3 + CI-1）已完成。系统包含：

- **后端**：FastAPI + MySQL + JWT 认证 + MiMo AI 流式对话
- **前端**：Vue3 + Element Plus 科技深色主题 + SSE 流式渲染
- **CI/CD**：GitHub Actions 工作流（待推送）
- **文档**：项目计划 + 全周期构建历程

---

## 功能扩展阶段

### F-1：用户设置（修改密码）

| 维度 | 内容 |
|------|------|
| 执行工作 | 后端添加 PUT /auth/password 端点，前端新增 Settings.vue 页面 |
| 实现手段 | FastAPI 端点 + auth_service.change_password，Vue3 表单 + Element Plus 验证 |
| 新增功能 | 修改密码页面，旧密码验证 + 新密码设置，修改成功后自动退出登录 |

### F-2：深色/浅色主题切换

| 维度 | 内容 |
|------|------|
| 执行工作 | 添加 .light CSS 类覆盖主题变量，创建 theme store |
| 实现手段 | CSS 变量 + Pinia store + localStorage 持久化 |
| 新增功能 | 浅色主题配色，侧边栏主题切换按钮，刷新后保持选择 |

### F-3：Markdown 渲染 + 代码高亮

| 维度 | 内容 |
|------|------|
| 执行工作 | 安装 marked + highlight.js，重写 ChatMessage 组件 |
| 实现手段 | marked 解析 Markdown，highlight.js 语法高亮，v-html 渲染 |
| 新增功能 | AI 消息支持标题、列表、表格、引用、代码块等 Markdown 格式 |

### F-4：会话重命名/删除

| 维度 | 内容 |
|------|------|
| 执行工作 | 后端添加 PUT/DELETE /conversations/{id}，前端侧边栏添加操作按钮 |
| 实现手段 | FastAPI 端点 + chat_service，hover 显示操作按钮，内联编辑标题 |
| 新增功能 | 会话重命名（内联编辑），会话删除（确认对话框） |

### F-5：消息复制/重新生成

| 维度 | 内容 |
|------|------|
| 执行工作 | ChatMessage 组件添加操作按钮，chat store 添加 regenerate 方法 |
| 实现手段 | navigator.clipboard API 复制，重新发送最后一条用户消息 |
| 新增功能 | 消息复制到剪贴板，最后一条 AI 消息支持重新生成 |

### F-6：对话导出 + 多模型切换

| 维度 | 内容 |
|------|------|
| 执行工作 | 后端添加 GET /models 和 GET /conversations/{id}/export，前端添加模型选择器和导出按钮 |
| 实现手段 | FastAPI PlainTextResponse 导出 Markdown，前端 Blob 下载 |
| 新增功能 | 模型选择器（支持动态模型列表），导出对话为 Markdown 文件 |

### F-7：移动端响应式优化

| 维度 | 内容 |
|------|------|
| 执行工作 | 侧边栏改为抽屉式，聊天区域和输入组件适配小屏 |
| 实现手段 | CSS 媒体查询 + 汉堡菜单按钮 + overlay 遮罩 |
| 新增功能 | 移动端侧边栏抽屉，响应式布局适配 375px+ |

### F-8：侧边栏会话搜索

| 维度 | 内容 |
|------|------|
| 执行工作 | 侧边栏添加搜索输入框 |
| 实现手段 | computed 属性实时过滤会话列表 |
| 新增功能 | 按标题关键词搜索会话 |

### F-9：Docker 容器化部署

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 backend/Dockerfile、frontend/Dockerfile、docker-compose.yml |
| 实现手段 | 多阶段构建（Node 构建 + Nginx 服务），docker-compose 编排三个服务 |
| 新增功能 | 一键 docker-compose up 启动完整系统（MySQL + Backend + Frontend） |

### F-10：后端单元测试

| 维度 | 内容 |
|------|------|
| 执行工作 | 创建 backend/tests/ 目录，编写认证和会话 API 测试 |
| 实现手段 | pytest + FastAPI TestClient + SQLite 内存数据库 |
| 新增功能 | 8 个测试用例覆盖用户注册/登录/会话 CRUD |

### F-11：CI/CD 工作流更新

| 维度 | 内容 |
|------|------|
| 执行工作 | 更新 ci.yml 添加测试步骤 |
| 实现手段 | GitHub Actions，push/PR 触发后端测试 |
| 新增功能 | CI 流程包含后端单元测试 |

---

## 第二轮功能扩展（用户功能 + 对话体验）

### F-12：用户头像 + 昵称

| 维度 | 内容 |
|------|------|
| 执行工作 | User 模型新增 nickname/avatar/preferences 字段，后端 PUT /auth/profile 端点，前端设置页头像选择器+昵称输入 |
| 实现手段 | SQLAlchemy 新增字段，auth_service.update_profile，16 个预设 emoji 头像 |
| 新增功能 | 用户可选择预设头像和编辑昵称，侧边栏底部和消息气泡显示用户头像 |

### F-13：用户偏好设置

| 维度 | 内容 |
|------|------|
| 执行工作 | User 模型 preferences 字段（JSON 字符串），前端设置页偏好配置区 |
| 实现手段 | JSON 序列化存储，Pinia store 管理偏好状态 |
| 新增功能 | 字体大小滑块（12-20px）、消息密度选择（舒适/紧凑），全局应用偏好 |

### F-14：消息时间戳

| 维度 | 内容 |
|------|------|
| 执行工作 | ChatMessage 组件添加时间显示 |
| 实现手段 | 格式化 created_at 字段为 HH:MM |
| 新增功能 | 每条消息下方显示发送时间 |

### F-15：消息编辑/删除

| 维度 | 内容 |
|------|------|
| 执行工作 | 后端 PUT/DELETE /messages/{id} 端点，前端消息 hover 操作栏 |
| 实现手段 | FastAPI 端点 + 会话所有权校验，ChatMessage 组件操作按钮 |
| 新增功能 | 用户消息可编辑，所有消息可删除 |

### F-16：会话置顶 + 归档

| 维度 | 内容 |
|------|------|
| 执行工作 | Conversation 模型新增 pinned/archived 字段，后端 pin/archive 端点，侧边栏分组显示 |
| 实现手段 | Boolean 字段 + toggle 端点，computed 属性分组排序 |
| 新增功能 | 会话置顶（置顶区在前）、会话归档（独立归档视图），置顶图标标识 |

### F-17：系统提示词

| 维度 | 内容 |
|------|------|
| 执行工作 | Conversation 模型新增 system_prompt 字段，后端端点 + SystemPromptDialog 组件 |
| 实现手段 | Text 字段存储，load_history 注入首条 system message |
| 新增功能 | 每个会话可设置独立系统提示词，影响 AI 回答风格和行为 |

### F-18：键盘快捷键

| 维度 | 内容 |
|------|------|
| 执行工作 | Chat.vue 添加全局 keydown 监听 |
| 实现手段 | onMounted/onUnmounted 生命周期管理事件监听 |
| 新增功能 | Ctrl+N 新建对话、Ctrl+K 聚焦搜索、Ctrl+Shift+E 导出对话、Escape 关闭侧边栏 |
