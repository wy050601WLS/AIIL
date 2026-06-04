# AI 智慧学习系统 — 全周期构建历程

## 项目信息

| 项目 | 说明 |
|------|------|
| 项目名称 | AIIL（AI 智慧学习系统） |
| 技术栈 | 前端 Vue3 + Vite + Pinia + Element Plus，后端 Python FastAPI，AI 小米 MiMo |
| 数据库 | MySQL，数据库名 `ai`，账号 `root` |
| 迁移工具 | Alembic |

## 项目结构

```
AIIL/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM 模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── routers/         # API 路由（auth / history / chat / cards）
│   │   ├── services/        # 业务逻辑层
│   │   ├── utils/           # 工具（JWT / 密码哈希）
│   │   ├── config.py        # 统一配置
│   │   ├── database.py      # 数据库连接
│   │   └── main.py          # FastAPI 入口
│   ├── alembic/             # 数据库迁移
│   ├── tests/               # pytest 单元测试
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios 请求封装
│   │   ├── components/      # ChatMessage / ChatInput / Sidebar / SystemPromptDialog
│   │   ├── router/          # Vue Router 路由配置
│   │   ├── stores/          # Pinia 状态管理（user / chat / theme）
│   │   ├── views/           # Login / Register / Chat / Settings / Cards
│   │   ├── style.css        # 全局主题变量
│   │   └── main.js          # 应用入口
│   └── Dockerfile
├── docker-compose.yml
└── docs/
    ├── build-history.md     # 本文档
    └── project-plan.md      # 项目计划
```

## 最终功能清单

| 类别 | 功能 |
|------|------|
| 用户认证 | 注册、登录、JWT 鉴权、修改密码 |
| 用户资料 | 头像选择、昵称编辑、偏好设置（字体大小 / 消息密度 / 默认模型） |
| 对话管理 | 新建、重命名、删除、置顶、归档、搜索、导出 Markdown |
| AI 对话 | SSE 流式输出、Markdown 渲染 + 代码高亮、重新生成、多模型切换、语音输入、图片识别 |
| 消息操作 | 编辑、删除、复制（渲染文本）、时间戳 |
| 系统提示词 | 每个会话可独立设置，内置学习助手默认提示词 |
| UI 体验 | 深色 / 浅色主题、移动端响应式、消息密度调节、自动滚动、输入框自适应 |
| 快捷键 | Ctrl+N 新建、Ctrl+K 搜索、Ctrl+Shift+E 导出、Escape 关闭侧边栏 |
| 工程化 | Docker 部署、Alembic 数据库迁移、GitHub Actions CI、pytest 单元测试 |

---

## 阶段一：项目初始化（A-1 ~ A-3）

从零搭建前后端项目骨架。

### A-1：克隆仓库并创建 .gitignore
- 克隆远程仓库，创建 .gitignore 排除 `__pycache__`、`node_modules`、`.env` 等

### A-2：创建后端目录结构与依赖配置
- 创建 `backend/app/` 目录及子目录，编写 requirements.txt
- 依赖：fastapi, uvicorn, sqlalchemy, pymysql, python-jose, bcrypt, python-dotenv, httpx

### A-3：创建前端项目
- `npm create vue@latest` 创建 Vue3 + Vite 项目到 `frontend/`

---

## 阶段二：数据库与后端核心（B-1 ~ C-8）

设计数据模型，搭建后端服务的完整链路。

### B-1：创建数据库表结构
- ORM 模型定义 users / conversations / messages 三张表
- 移除旧方案遗留表（topic, knowledge_card 等），技术栈从 React+Node.js 变更为 FastAPI+Vue3

### C-1：配置模块 + 数据库模块
- `config.py` 自定义 Settings 类读取 .env，`database.py` SQLAlchemy 连接与 get_db 依赖注入

### C-2：ORM 模型
- User、Conversation、Message 三个 ORM 模型，含级联删除

### C-3：Pydantic Schema
- UserCreate, UserLogin, UserResponse, Token, ConversationCreate, ChatRequest 等请求/响应模型

### C-4：安全工具
- bcrypt 密码哈希，python-jose JWT 编解码，HTTPBearer 认证

### C-5：认证路由 + 服务
- POST /register、POST /login 端点，service 层封装业务逻辑

### C-6：会话管理路由 + 服务
- POST /conversations、GET /conversations、GET /conversations/{id}/messages

### C-7：AI 对话路由 + 服务
- httpx 流式调用 MiMo API（OpenAI 兼容格式），SSE StreamingResponse，消息持久化

### C-8：应用入口
- FastAPI 实例 + CORSMiddleware + 路由挂载

---

## 阶段三：前端开发（D-1 ~ D-6）

实现完整的前端界面和交互。

### D-1：API 封装 + 路由 + 状态管理
- Axios 请求拦截器（自动带 token、401 跳转），Vue Router 路由守卫，Pinia stores

### D-2：全局样式 + 入口文件
- CSS 变量定义科技深色主题，main.js 注册 Element Plus / Pinia / Router

### D-3：登录页 + 注册页
- Element Plus 表单组件，居中卡片布局，表单验证

### D-4：对话主页 + 侧边栏
- Flex 左右布局，侧边栏会话列表 + 右侧消息区域

### D-5：消息组件 + 输入组件
- 消息气泡（用户右侧 / AI 左侧），textarea 自适应高度，Enter 发送

### D-6：SSE 流式对话集成
- fetch + ReadableStream 读取 SSE，onToken 回调逐 token 更新消息

---

## 阶段四：联调与部署（E-1 ~ E-3, CI-1）

前后端联调、Git 提交、CI 配置。

### E-1：前后端联调测试
- curl 测试所有端点，修复 AI 模型配置（从 Anthropic SDK 改为 httpx + OpenAI 格式）

| 端点 | 结果 |
|------|------|
| GET / | 正常 |
| POST /auth/register | 正常 |
| POST /auth/login | 正常，返回 JWT token |
| POST /conversations | 正常 |
| GET /conversations | 正常 |
| GET /conversations/{id}/messages | 正常 |
| POST /chat | 正常，SSE 流式输出 AI 回复 |

### CI-1：GitHub Actions CI/CD
- push/PR 触发，后端依赖安装 + 导入验证，前端 npm ci + 生产构建

### E-2：Git 提交与推送
- 全部代码提交推送到远程

### E-3：历程文档归档
- 修正不准确记录（A-2 依赖列表、C-7 实现手段），补全所有任务变更

---

## 阶段五：第一轮功能扩展（F-1 ~ F-11）

在 MVP 基础上增加用户管理和交互体验功能。

### F-1：用户设置（修改密码）
- 后端 PUT /auth/password，前端 Settings.vue 页面，修改成功后自动退出登录

### F-2：深色 / 浅色主题切换
- CSS 变量 + `.light` 类覆盖，Pinia theme store + localStorage 持久化

### F-3：Markdown 渲染 + 代码高亮
- marked 解析 Markdown，highlight.js 语法高亮，AI 消息支持标题、列表、表格、代码块

### F-4：会话重命名 / 删除
- 后端 PUT/DELETE /conversations/{id}，hover 显示操作按钮，内联编辑标题

### F-5：消息复制 / 重新生成
- navigator.clipboard 复制，chat store regenerate 方法重新发送最后一条用户消息

### F-6：对话导出 + 多模型切换
- GET /models 和 GET /conversations/{id}/export，前端模型选择器 + Markdown 导出

### F-7：移动端响应式优化
- 侧边栏改为抽屉式，CSS 媒体查询适配 375px+

### F-8：侧边栏会话搜索
- computed 属性实时按标题关键词过滤会话列表

### F-9：Docker 容器化部署
- 多阶段构建 Dockerfile，docker-compose 编排 MySQL + Backend + Frontend

### F-10：后端单元测试
- pytest + FastAPI TestClient + SQLite 内存数据库，8 个测试用例

### F-11：CI/CD 工作流更新
- CI 流程添加后端单元测试步骤

---

## 阶段六：第二轮功能扩展（F-12 ~ F-20）

增强用户个性化和对话管理能力。

### F-12：用户头像 + 昵称
- User 模型新增 nickname / avatar / preferences 字段，PUT /auth/profile 端点，16 个预设 emoji 头像

### F-13：用户偏好设置
- JSON 字符串存储偏好，前端字体大小滑块、消息密度选择、默认模型选择

### F-14：消息时间戳
- ChatMessage 组件显示 HH:MM 格式时间

### F-15：消息编辑 / 删除
- 后端 PUT/DELETE /messages/{id}，前端 hover 操作栏

### F-16：会话置顶 + 归档
- Conversation 模型新增 pinned / archived 字段，toggle 端点，侧边栏分组显示

### F-17：系统提示词
- Conversation 模型新增 system_prompt 字段，SystemPromptDialog 弹窗编辑

### F-18：键盘快捷键
- Ctrl+N 新建、Ctrl+K 搜索、Ctrl+Shift+E 导出、Escape 关闭侧边栏

### F-19：默认学习助手系统提示词
- config.py 新增 DEFAULT_SYSTEM_PROMPT，会话无自定义提示词时自动使用

### F-20：数据库字段迁移
- ALTER TABLE 添加第二轮扩展所需的新字段

---

## 阶段七：第三轮优化（G-1 ~ G-6）

修复功能缺陷，改进交互体验。

### G-1：修复事件处理器写法错误
- `@edit="handleEdit(msg)"` → `@edit="() => handleEdit(msg)"`，避免渲染时立即执行

### G-2：消息区域自动滚动
- watch 监听 messages 长度和最后一条消息内容，nextTick + scrollTop 滚动到底部

### G-3：编辑消息弹窗替换原生 prompt
- 原生 prompt() 替换为 ElMessageBox.prompt，textarea 输入 + 内容校验

### G-4：输入框自动调整高度
- @input 事件触发 autoResize，scrollHeight 动态设置高度，最大 150px

### G-5：修复重新生成消息重复 bug
- ChatRequest 新增 regenerate 标志，后端区分重新生成模式，跳过重复保存用户消息

### G-6：marked.setOptions 优化
- 从组件内调用改为普通 `<script>` 块模块级单次调用

---

## 阶段八：第四轮优化（G-7 ~ G-10）

修复表单校验和偏好加载问题。

### G-7：修复登录 / 注册表单校验错误提示
- validate() 失败后直接 return，不进入 API catch 分支

### G-8：设置页偏好数据加载时序修复
- onMounted 中 await loadProfile() 后再赋值表单，避免空值覆盖

### G-9：默认模型偏好生效
- loadModels 优先级：localStorage > 偏好 defaultModel > 服务端默认值

### G-10：消息密度设置应用到消息组件
- ChatMessage 新增 density prop，CSS 变量 --row-gap 控制行间距

---

## 阶段九：第五轮优化（H-1 ~ H-12）

全面排查并修复 Bug 和体验问题。

### H-1：修复设置页修改密码校验拦截
- validate() 加 try-catch，校验失败不再显示"旧密码错误"

### H-2：移动端侧边栏操作按钮修复
- 添加 ⋯ 展开按钮 + expandedId 状态，移动端点击展开操作菜单

### H-3：设置页导航改用 Vue Router
- `window.location.href` 替换为 `router.push`，避免整页刷新丢失状态

### H-4：消息发送错误处理
- 流式失败时移除空 assistant 消息，ElMessage 错误提示

### H-5：归档会话搜索修复
- 搜索逻辑从 conversations 全量出发，按归档模式过滤后再搜索

### H-7：marked 配置去重
- 移除 script setup 中重复的 marked.setOptions 调用

### H-8：归档会话数量提示
- 归档按钮显示"已归档 (N)"

### H-11：AI 消息复制渲染文本
- AI 消息复制 innerText 而非原始 Markdown

---

## 阶段十：工程化改进（I-1）

### I-1：Alembic 数据库迁移
- 集成 Alembic，env.py 读取应用 DATABASE_URL 并导入所有 ORM 模型
- 生成初始迁移脚本，数据库 stamp 到当前版本
- 移除 main.py 中的 `Base.metadata.create_all()`，表结构改由 alembic 管理
- 以后修改 ORM 模型后：`alembic revision --autogenerate -m "描述"` → `alembic upgrade head`

---

## 阶段十一：安全加固与质量改进

后端安全加固、前端 UX 改进、测试扩展、文档补充。

### J-1：后端安全加固
- HTTPException/status 导入统一移至文件顶部
- edit_message 改用 Pydantic MessageUpdate 校验请求体
- 提取 `_verify_message_owner` 消除重复鉴权代码
- CORS 从 `allow_origins=["*"]` 改为配置化（CORS_ORIGINS 环境变量）
- 添加 slowapi 全局限流（60 次/分钟）

### J-2：流式输出停止按钮
- ChatInput 新增红色"停止"按钮（loading 时显示）
- streamChat 支持 AbortSignal，chat store 新增 stopStreaming 方法

### J-3：消息删除确认
- 删除消息前弹出 ElMessageBox.confirm 确认对话框

### J-4：测试扩展至 21 个用例
- 新增 test_messages.py：消息编辑/删除/越权/空内容校验（5 个）
- 新增 test_features.py：置顶/归档/系统提示词/偏好/改密/模型列表（9 个）
- 测试环境禁用限流

### J-5：README.md
- 项目入口文档：技术栈、快速开始、环境变量、测试命令、文档链接

---

## 阶段十二：语音输入 + 图片识别

新增语音输入和图片识别功能。

### K-1：语音输入
- ChatInput 新增麦克风按钮，使用 Web Speech API（SpeechRecognition）
- 支持中文实时语音转文字，录音中显示脉冲红点动画
- 不支持的浏览器自动隐藏按钮

### K-2：图片上传与预览
- ChatInput 新增图片按钮（支持点击选择 + 粘贴图片）
- 最多 5 张图片，选中后显示缩略图预览（可移除）
- 图片转为 base64 data URL 随消息发送

### K-3：后端多模态支持
- Message 模型新增 `images` 字段（Text, JSON 数组）
- ChatRequest 新增 `images: list[str] | None` 字段
- save_user_message 存储图片数据
- load_history 自动将含图片的消息转为 OpenAI 多模态 content 格式
- Alembic 迁移添加 images 列

### K-4：消息图片显示
- ChatMessage 组件消息气泡中显示图片缩略图
- 点击图片可全屏预览

---

## 阶段十三：知识卡片

新增知识卡片功能，收藏 AI 回复中的精华内容。

### L-1：后端知识卡片 CRUD
- KnowledgeCard 模型：id, user_id, content, source, tags, created_at
- KnowledgeCardCreate / KnowledgeCardResponse Pydantic schemas
- cards 路由：POST /cards, GET /cards, DELETE /cards/{card_id}
- 所有接口需登录，删除操作校验归属权
- Alembic 迁移创建 knowledge_cards 表

### L-2：前端知识卡片页面
- api/cards.js：createCard, getCards, deleteCard
- stores/cards.js：Pinia store，loadCards / addCard / removeCard
- views/Cards.vue：卡片列表页，支持标签筛选、删除
- 路由 /cards，需登录

### L-3：对话中提取卡片
- ChatMessage 气泡操作栏新增「提取卡片」按钮（仅 assistant 消息）
- 点击后将消息内容保存为知识卡片，来源标记为对话 ID
- Sidebar 底栏新增「卡片」入口

---

## 阶段十四：学习进度面板

新增学习数据可视化面板，展示用户学习轨迹。

### M-1：后端统计 API
- GET /dashboard/stats：返回对话数、消息数、卡片数、活跃天数
- 最近 30 天每日消息数（GROUP BY DATE）
- 知识卡片热门标签 Top 10
- DashboardStats / DailyMessage / TagCount Pydantic schemas

### M-2：前端学习面板页面
- api/dashboard.js + stores/dashboard.js
- views/Dashboard.vue：统计卡片（4 宫格）、30 天柱状图（纯 CSS）、热门标签
- 路由 /dashboard，Sidebar 底栏新增「面板」入口

---

## 阶段十五：UI 优化

全面优化界面交互和视觉体验。

### N-1：侧边栏底栏图标化
- 底栏按钮从文字改为 SVG 图标（面板、卡片、主题切换、设置、退出）
- 深色/浅色主题切换按钮显示太阳/月亮图标
- 新对话按钮改为实心 primary 样式

### N-2：会话操作下拉菜单
- 会话项 hover 显示 ⋯ 按钮
- 点击弹出 el-dropdown 菜单：重命名、置顶、归档、删除
- 替代原来的一排内联操作按钮，解决布局拥挤问题

### N-3：清理重复内容
- 移除 Chat.vue 中重复的欢迎副标题
- 移除侧边栏多余的文字标签

---

## 阶段十六：移除系统提示词功能

彻底移除每个会话自定义系统提示词的功能，统一使用配置文件中的默认提示词。

### O-1：后端清理
- 移除 `conversations.system_prompt` 相关逻辑（保留数据库列，不破坏现有数据）
- 移除 `update_system_prompt` 服务函数
- 移除 `PUT /conversations/{id}/prompt` 路由端点
- 移除 `SystemPromptUpdate` schema
- ai_service 统一使用 `settings.DEFAULT_SYSTEM_PROMPT`
- 移除 `test_system_prompt` 测试用例

### O-2：前端清理
- 删除 `SystemPromptDialog.vue` 组件
- Sidebar 移除提示词对话框相关逻辑和导入
- chat store 移除 `updateSystemPrompt` 函数
- chat API 移除 `updateSystemPrompt` 请求函数

---

## 阶段十七：项目全景文档

创建 `docs/project-overview.md` 作为项目全景参考文档，供其他 AI 全面了解项目。

### P-1：文档结构
- 项目背景与定位（痛点分析、技术选型理由）
- 功能清单（50+ 功能项，涵盖所有已实现特性）
- 技术架构图（前端/后端/数据库/AI）
- 数据库设计（ER 关系、4 张表结构）
- API 接口一览（5 组路由、20+ 端点）
- 前端路由与文件清单

### P-2：深度分析
- 核心实现模式（SSE 流式对话、认证流程、图片管线、状态管理、测试模式）
- 技术债务（10 项已知问题）
- 扩展方向（高/中/低价值分类）
- 改进建议（P0/P1/P2 优先级）
- 开发约定（后端分层、前端模式、Git 规范）

---

## 阶段十八：全项目注释补充

为后端和前端所有源文件补充中文注释和 docstring，代码注释率从 ~3% 提升至全覆盖。

### Q-1：后端注释（15 个文件）
- 核心文件：main.py / config.py / database.py — 模块文件头、实例说明
- 模型层：models/user.py / conversation.py — 模型类 docstring、字段注释
- Schema 层：schemas/user.py / conversation.py — 14 个 schema 类 docstring
- 工具层：utils/security.py — 5 个函数 docstring（哈希/JWT/依赖注入）
- 服务层：services/ — 15 个函数 docstring（重点：ai_service 的 SSE 回放和多模态转换）
- 路由层：routers/ — 22 个端点 docstring

### Q-2：前端注释（19 个文件）
- API 层：api/ — 5 个文件、22 个函数 JSDoc（重点：streamChat 的 SSE 解析流程）
- Store 层：stores/ — 5 个文件、32 个函数注释（重点：chat store 的流式对话逻辑）
- 组件层：components/ — 3 个 Vue 组件头注释（Props/Events 说明）、31 个函数注释
- 视图层：views/ — 6 个页面组件头注释、22 个函数注释
- 其他：router/index.js 路由表注释、main.js 入口注释

---

## 阶段十九：P0 技术债务修复 + 对话标题自动更新

清理已知技术债务，提升项目健壮性。

### R-1：修复 init_db.sql
- 同步完整表结构：users 表补全 nickname/avatar/preferences 列
- conversations 表补全 pinned/archived/system_prompt 列
- messages 表补全 images 列
- 新增 knowledge_cards 表定义

### R-2：清理残留文件
- 删除 HelloWorld.vue（Vite 脚手架残留组件）

### R-3：统一 AI 模型默认值
- config.py 的 AI_MODEL 默认值从 claude-sonnet-4-20250514 改为 mimo-v2.5-pro
- 与 .env.example 保持一致

### R-4：对话标题自动更新
- 后端：chat 端点中，若会话标题仍为「新对话」，用用户消息前 30 字自动更新
- 前端：chat store sendMessage 中同步更新本地会话标题
- 支持多行文本（换行替换为空格）和纯图片对话（回退为「图片对话」）

---

## 阶段二十：知识卡片编辑功能

支持对已保存的知识卡片进行内容和标签的编辑。

### S-1：后端 PUT /cards/{id}
- 新增 KnowledgeCardUpdate schema（content/tags 均可选）
- cards 路由新增 update_card 端点，部分更新（仅传入的字段被修改）

### S-2：前端卡片编辑 UI
- Cards.vue 新增编辑模式：textarea 编辑内容、input 编辑标签
- cards store 新增 editCard action
- cards API 新增 updateCard 请求函数

---

## 阶段二十一：消息分页与无限滚动

支持长对话的消息分页加载，首屏仅加载最新 50 条，向上滚动自动加载更早的消息。

### T-1：后端分页支持
- chat_service.get_messages 新增 skip/limit 参数，返回 {total, messages} 结构
- history 路由 messages 端点透传 skip/limit 查询参数

### T-2：前端无限滚动
- chat store 新增 hasMore/loadingMore 状态
- selectConversation 首次加载 50 条，loadMoreMessages 追加加载
- Chat.vue 新增 handleScroll：距顶部 50px 时触发加载，加载后补偿滚动位置保持视觉不变

---

## 阶段二十二：真流式 SSE 改造

将 SSE 对话从「回放式」（先收集完整响应再逐 chunk 回放）改为「真流式」（收到 AI chunk 立即转发），显著降低首 token 延迟。

### U-1：后端异步流式
- ai_service.call_ai_api 改为 async 生成器 stream_ai_api，使用 httpx.AsyncClient
- 每收到一个 content chunk 立即 yield，而非先收集到列表
- chat 端点改为 async def，内部异步生成器边转发边收集完整回复
- 流结束后将完整回复存入数据库（保证数据持久化）

---

## 阶段二十三：对话模板功能

新增对话模板系统，支持预设 prompt 模板和用户自定义模板，快速发起常用对话。

### V-1：后端模板 CRUD
- 新增 PromptTemplate 模型（prompt_templates 表），user_id 为 NULL 表示系统内置模板
- 新增 TemplateCreate / TemplateUpdate / TemplateResponse schema
- 新增 /templates 路由：GET（列表）、POST（创建）、PUT（更新）、DELETE（删除）
- 内置 5 个学习场景模板：翻译为中文、概念解释、练习题、代码审查、总结要点
- 首次访问时自动种子内置模板

### V-2：前端模板集成
- 新增 api/templates.js 和 stores/templates.js
- ChatInput.vue 新增模板选择面板（el-popover），按分类分组展示，点击即填充输入框
- 支持「保存为模板」：将当前输入框内容保存为自定义模板
- Settings.vue 新增模板管理区域：查看/编辑/删除自定义模板

---

## 阶段二十四：学习资料库

新增学习资料收集与 AI 辅助搜索功能，与 AI 对话互补——AI 对话是「问与答」，资料库是「收集与发现」。

### W-1：后端资料 CRUD + AI 搜索
- 新增 LearningResource 模型（learning_resources 表），支持标题/链接/描述/分类/类型/标签
- 新增 /resources 路由：GET（列表，支持分类和类型过滤）、POST（创建）、PUT（更新）、DELETE（删除）
- POST /resources/ask 端点：将用户问题和所有资料上下文发送给 AI，分析相关资料并推荐
- 使用 httpx 非流式调用（stream=False）返回完整 AI 分析结果

### W-2：前端资料库页面
- 新增 api/resources.js 和 stores/resources.js
- 新增 Resources.vue：卡片式资料列表，支持分类/类型筛选和关键词搜索
- AI 搜索区：输入自然语言问题，AI 分析资料库并推荐相关资料
- 新增/编辑对话框：el-form 表单，支持标题/链接/描述/分类/类型/标签
- Sidebar.vue 新增「学习资料」导航入口（书本图标）
- router/index.js 新增 /resources 路由

---

## 阶段二十五：知识库功能

新增个人知识库功能，支持上传学习文档（PDF/DOCX/TXT/MD），系统自动解析文件内容并存储，支持全文搜索和标签管理。

### X-1：后端文档上传与解析
- 新增 KnowledgeDocument 模型（knowledge_documents 表），支持标题/文件类型/文件路径/文件大小/解析内容/标签
- 新增 document_parser.py 解析服务：PDF（pypdf）、DOCX（python-docx）、TXT/MD（直接读取）
- config.py 新增 UPLOAD_DIR 和 MAX_FILE_SIZE 配置
- requirements.txt 新增 pypdf、python-docx 依赖

### X-2：后端知识库路由
- 新增 /knowledge 路由：POST /upload（multipart 文件上传）、GET（列表，支持关键词搜索）、GET /{id}（详情）、PUT /{id}（更新标题/标签）、DELETE /{id}（删除文档+磁盘文件）
- main.py 注册 knowledge 路由
- init_db.sql 新增 knowledge_documents 表 DDL

### X-3：前端知识库页面
- 新增 api/knowledge.js 和 stores/knowledge.js
- 新增 Knowledge.vue：文档列表页，支持上传文件、关键词搜索、删除
- 新增 KnowledgeDetail.vue：文档详情页，展示全文内容，支持编辑标题/标签
- router/index.js 新增 /knowledge 和 /knowledge/:id 路由
- Sidebar.vue 新增「知识库」导航入口（文档图标）

---

## 阶段二十六：合并学习资料与知识库页面

将独立的知识库页面合并到学习资料页面中，使用 Tab 切换展示两个模块。

### Y-1：页面合并
- Resources.vue 增加 Tab 切换（「学习资料」|「知识库文档」）
- Tab 1 展示原有学习资料内容（AI 搜索 + 筛选 + 资料列表）
- Tab 2 展示知识库文档内容（搜索 + 上传 + 文档列表）
- 删除独立的 Knowledge.vue 页面
- 路由移除 /knowledge，保留 /knowledge/:id 详情页
- Sidebar 移除知识库独立导航按钮

---

## 阶段二十七：可见性控制

为学习资料和知识库文档添加可见性选项（公共/私人/草稿），不同可见性影响列表展示和访问权限。

### Z-1：后端可见性支持
- LearningResource 和 KnowledgeDocument 模型新增 `visibility` 列（默认 public）
- ResourceCreate / ResourceUpdate / ResourceResponse / DocumentResponse / DocumentUpdate schema 新增 visibility 字段
- resources.py 和 knowledge.py 列表接口过滤逻辑：`WHERE visibility = 'public' OR user_id = :current_user`
- 详情接口同样过滤，非所有者不可见 private/draft 资料
- init_db.sql 同步 visibility 列

### Z-2：前端可见性 UI
- Resources.vue 学习资料表单增加可见性选择器（公共/私人/草稿，含说明文字）
- Resources.vue 知识库上传对话框增加可见性选择器
- 资料卡片和文档卡片显示可见性标签（绿色=公共，橙色=私人，蓝色=草稿）
- KnowledgeDetail.vue 详情页显示可见性标签，编辑模式支持修改可见性
- knowledge.js API 和 store 透传 visibility 参数

### Z-3：种子数据更新
- seed_data.py 资料和文档混合使用不同可见性值，便于测试过滤逻辑

---

## 阶段二十八：质量修复与安全加固

全面审计项目，修复安全、性能和代码质量问题。

### AA-1：安全修复
- 创建 `backend/.env.example` 环境变量模板，新开发者可直接参考
- `.gitignore` 新增 `backend/test.db` 和 `backend/uploads/` 排除规则
- `docker-compose.yml` 移除废弃的 `version: "3.8"` 字段

### AA-2：Bug 修复
- `streamChat` 流结束后处理缓冲区剩余数据，防止最后 chunk 丢失
- `exportConversation` 添加 HTTP 响应状态检查，错误时抛出异常

### AA-3：性能优化
- Dashboard 标签统计限制最近 500 条卡片，避免全量加载到内存

### AA-4：marked 高亮 API 升级
- 安装 `marked-highlight` 扩展，替代已废弃的 `marked.setOptions({ highlight })` 写法
- ChatMessage.vue 改用 `marked.use(markedHighlight({...}))` 新 API

### AA-5：AI 端点独立限流
- 新增 `app/limiter.py` 共享限流器模块
- `/chat` 端点限流 20 次/分钟
- `/resources/ask` 端点限流 10 次/分钟
- `main.py` 改为从 `app.limiter` 导入 limiter 实例

### AA-6：文档更新
- README 更新完整功能清单和环境变量表
- project-overview.md 全面更新：ER 图、API 列表、文件清单、已知问题
- 可见性标签 CSS 提取到全局 style.css，消除组件间重复

---

## 阶段二十九：中等严重性问题修复

修复审计中发现的中等严重性问题，涉及错误处理、安全防护、性能优化和代码健壮性。

### AB-1：前端 Store 错误处理补全
- `cards.js`：loadCards/addCard/editCard/removeCard 全部添加 try-catch + ElMessage.error
- `templates.js`：loadTemplates/addTemplate/editTemplate/removeTemplate 全部添加 try-catch
- `dashboard.js`：loadStats 添加 try-catch + ElMessage.error
- `resources.js`：addResource/editResource/removeResource 添加 try-catch（loadResources/ask 已有）

### AB-2：XSS 防护（DOMPurify）
- 安装 `dompurify` 依赖
- ChatMessage.vue 的 `rendered` computed 属性使用 `DOMPurify.sanitize()` 包裹 `marked.parse()` 输出
- 防止 AI 回复中可能包含的恶意 HTML/JS 注入

### AB-3：数据库查询优化
- Message 模型新增复合索引 `ix_messages_conversation_created(conversation_id, created_at)`
- 覆盖 load_history 和 get_messages 的核心查询路径
- init_db.sql 同步新增索引定义

### AB-4：AI 搜索性能优化
- `/resources/ask` 端点限制加载最近 100 条资料（原为全量加载），避免 prompt 过长导致 token 浪费和超时
- 错误处理细化：区分 TimeoutException（504）和 HTTPStatusError（502），提供更具体的错误信息

### AB-5：重新生成消息容错
- regenerate 函数在删除旧 AI 回复前暂存副本
- 流式失败或无内容时自动恢复旧消息，避免数据丢失
- 恢复时显示提示"重新生成失败，已恢复原回复"

### AB-6：知识库路由参数校验
- KnowledgeDetail.vue onMounted 添加 docId 校验（NaN 检查）
- 无效 ID 时显示错误提示并跳转回资源列表页
