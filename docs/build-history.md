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
│   │   ├── routers/         # API 路由（auth / history / chat）
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
│   │   ├── views/           # Login / Register / Chat / Settings
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
