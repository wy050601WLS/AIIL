# AI 智慧学习系统 — 答辩文档

> 总时长：20 分钟

---

## 一、项目概述（2 分钟）

### 1.1 项目背景与定位

传统学习三个痛点：答疑效率低、知识碎片化、缺乏数据反馈。

**AI 智慧学习（AIIL）** = AI 对话 + 知识沉淀 + 学习可视化 + 多模态交互

### 1.2 技术栈

```
前端：Vue3 + Vite + Pinia + Element Plus
后端：Python FastAPI + SQLAlchemy ORM
数据库：MySQL 8.0 + Alembic 迁移
AI：MiMo（OpenAI 兼容接口）
部署：Docker Compose + GitHub Actions CI
```

FastAPI 原生支持异步和 SSE 流式响应，Vue3 组合式 API 开发效率高。

### 1.3 整体架构

```
┌─────────────────────────────────────┐
│          前端 (Vue3 + Vite)         │
│  Views → Components → Stores        │
│  API Layer (Axios + fetch SSE)      │
└──────────────┬──────────────────────┘
               │ HTTP + SSE
┌──────────────▼──────────────────────┐
│         后端 (FastAPI)              │
│  Routers → Services → Models        │
│  Pydantic Schemas + JWT Auth        │
└──────────┬───────────┬──────────────┘
           │           │
     ┌─────▼─────┐ ┌───▼──────────┐
     │ MySQL 8.0 │ │ MiMo AI API  │
     │ (Alembic) │ │ (OpenAI 兼容)│
     └───────────┘ └──────────────┘
```

后端分层：Router（路由）→ Service（业务逻辑）→ Model（ORM）→ Schema（数据校验）

---

## 二、功能演示与实现（10 分钟）

### 2.1 用户认证系统（1 分钟）

**演示**：注册 → 登录 → 个人资料 → 偏好设置 → 主题切换

**实现原理**：

```
前端                          后端
Login.vue ──POST /auth/login──→ auth.py
  │                               │
  │ ←── { access_token } ────────│  bcrypt 校验密码
  │                               │  python-jose 生成 JWT
  │ localStorage 存储 token       │
  │                               │
  │ ──GET /auth/profile ─────────→│  HTTPBearer 校验 token
  │ ←── { nickname, avatar } ────│  解析 user_id 查询用户
```

**关键代码**：
- `utils/security.py`：`hash_password()`（bcrypt 哈希）、`create_token()`（JWT 编码）、`get_current_user()`（FastAPI 依赖注入，自动从 Header 解析 token）
- `stores/user.js`：token 持久化到 localStorage，Axios 拦截器自动带 token，401 时自动跳转登录页
- 主题切换：CSS 变量 + `.light` 类覆盖，Pinia theme store + localStorage 持久化

---

### 2.2 AI 流式对话（3 分钟）— 核心功能

**演示**：发送问题 → 逐字输出 → Markdown 渲染 → 代码高亮 → 停止/重新生成

**实现原理 — SSE 真流式**：

```
前端 (Chat.vue + chat.js)                后端 (chat.py + ai_service.py)
─────────────────────────                ─────────────────────────────
sendMessage()                            │
  │                                      │
  fetch('/chat', {method:'POST'})  ─────→│ chat 端点接收请求
  │                                      │
  │                                      │ save_user_message() 存库
  │                                      │
  │                                      │ load_history() 加载上下文
  │                                      │   ↓
  │                                      │ stream_ai_api() 异步生成器
  │                                      │   │
  │                                      │   httpx.AsyncClient.stream()
  │                                      │   │
  │  ←── SSE: data: {"token":"你"} ──────│   │ yield content chunk
  │  onToken → msg.content += token      │   │
  │  ←── SSE: data: {"token":"好"} ──────│   │ yield content chunk
  │  onToken → msg.content += token      │   │
  │  ←── SSE: data: [DONE] ─────────────│   │ 流结束
  │                                      │   │
  │                                      │ 将完整回复存入数据库
```

**前端流式读取代码**（`api/chat.js` `streamChat`）：
```javascript
const reader = response.body.getReader()
const decoder = new TextDecoder()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  buffer += decoder.decode(value, { stream: true })
  // 解析 SSE 行: data: {"token": "..."}
  // 调用 onToken 回调逐 token 更新 UI
}
```

**后端流式生成代码**（`services/ai_service.py`）：
```python
async def stream_ai_api(history, model):
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, ...) as response:
            async for line in response.aiter_lines():
                chunk = json.loads(line[6:])  # 解析 SSE
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    yield content  # 立即转发，非回放式
```

**Markdown 渲染优化**（`ChatMessage.vue`）：
- 使用 `marked` 解析 + `highlight.js` 代码高亮 + `DOMPurify` 防 XSS
- **防抖**：流式输出时每 150ms 最多重新解析一次（避免每个 token 触发全量 parse）
- 加载结束时立即渲染最终内容

---

### 2.3 图片识别与语音输入（1 分钟）

**演示**：上传图片 → AI 分析图片 → 语音输入转文字

**图片识别实现**：

```
前端 ChatInput.vue                    后端 ai_service.py
──────────────────                    ──────────────────
选择/粘贴图片                         │
  │                                   │
FileReader.readAsDataURL()            │
  → base64 dataUrl                    │
  │                                   │
sendMessage(content, [dataUrl]) ─────→│ save_user_message(images=...)
  │                                   │   images 存入 DB（JSON 数组）
  │                                   │
  │                                   │ load_history() 检测含图片的消息
  │                                   │   ↓ 转为 OpenAI 多模态格式
  │                                   │   {
  │                                   │     "role": "user",
  │                                   │     "content": [
  │                                   │       {"type":"text","text":"..."},
  │                                   │       {"type":"image_url","image_url":{"url":"data:..."}}
  │                                   │     ]
  │                                   │   }
  │                                   │
  │                                   │ 发送给 AI API（支持视觉的模型）
```

**语音输入**：浏览器 Web Speech API（`SpeechRecognition`），`lang: 'zh-CN'`，`interimResults: true` 实时显示，`continuous: true` 连续录音。

---

### 2.4 会话管理（1 分钟）

**演示**：新建 → 重命名 → 置顶 → 归档 → 搜索 → 导出 → 无限滚动

**实现原理**：

| 功能 | 前端 | 后端 |
|------|------|------|
| 列表 | Sidebar.vue：computed 分组（置顶/普通） | `GET /conversations` 按 pinned DESC, created_at DESC |
| 搜索 | computed 实时按标题过滤 | 纯前端过滤 |
| 置顶/归档 | store 调用 toggle API | `PUT /conversations/{id}/pin` 更新 boolean 字段 |
| 导出 | `GET /conversations/{id}/export` | 后端拼接 Markdown 文本返回 |
| 无限滚动 | `@scroll` 检测距顶 < 50px → `loadMoreMessages()` | `GET /messages?skip=N&limit=50` 分页查询 |
| 标题自动更新 | 发送消息后同步本地标题 | 后端：标题仍为「新对话」时，取用户消息前 30 字更新 |

**无限滚动关键代码**：
```javascript
// Chat.vue handleScroll
if (el.scrollTop < 50) {
  const prevHeight = el.scrollHeight
  await chatStore.loadMoreMessages()  // prepend 旧消息
  nextTick(() => {
    el.scrollTop = el.scrollHeight - prevHeight  // 补偿滚动位置
  })
}
```

---

### 2.5 知识卡片（0.5 分钟）

**演示**：提取卡片 → 标签筛选 → 编辑 → 删除

**实现**：
- 前端：`ChatMessage.vue` 的「提取卡片」按钮 → `cardsStore.addCard(msg.content, source)`
- 后端：`POST /cards` 创建 KnowledgeCard（content + source + tags）
- 列表页 `Cards.vue`：computed 按标签过滤 + 排序
- 编辑：`PUT /cards/{id}` 部分更新（仅传入的字段被修改）

---

### 2.6 学习资料与 AI 搜索（1.5 分钟）

**演示**：添加资料 → 筛选排序 → AI 搜索推荐 → 上传文档 → 知识库管理

**学习资料 CRUD**：
- 前端 `Resources.vue`：el-dialog 表单 + el-select 筛选 + computed 排序
- 后端 `resources.py`：标准 CRUD，`WHERE visibility='public' OR user_id=:me`

**AI 辅助搜索实现**：
```
用户输入问题 → POST /resources/ask
                │
                ├─ 加载最近 100 条资料
                ├─ 构造资料摘要上下文
                ├─ 拼接 system prompt（角色 + 规则 + 输出格式 + 资料库）
                │
                ├─ httpx.AsyncClient 调用 AI（非流式）
                │
                └─ 返回 { answer, resources: [...] }
                   │
                   ├─ 前端 marked.parse 渲染 Markdown 回答
                   └─ 显示「相关资料」列表
```

**知识库文档**：
- 上传：`POST /knowledge/upload`（multipart/form-data）
- 解析：`document_parser.py` — PDF 用 pypdf，DOCX 用 python-docx，TXT/MD 直接读取
- 列表接口用 `DocumentListResponse`（不含 content_text），详情接口用 `DocumentResponse`（含全文）

---

### 2.7 学习面板（0.5 分钟）

**演示**：统计卡片 → 30 天趋势图 → 热门标签

**实现**：
- 后端 `dashboard.py`：5 个 SQL 查询（COUNT + GROUP BY DATE + 标签统计）
- 前端 `Dashboard.vue`：统计卡片（4 宫格）+ 纯 CSS 柱状图 + 标签列表
- 柱状图：每个 `<div>` 高度 = `(count / maxCount) * 100%`

---

### 2.8 对话模板（0.5 分钟）

**演示**：打开模板面板 → 选择模板填充 → 保存自定义模板

**实现**：
- 后端：`prompt_templates` 表，`is_builtin=True` 为系统内置（23 个），`user_id` 为用户自建
- 启动时 `ensure_builtin_templates()` 检查并补全缺失模板
- 前端 `ChatInput.vue`：el-popover 模板面板，按分类分组，点击填充输入框

---

## 三、关键技术实现（3 分钟）

### 3.1 后端分层架构

```
app/
├── main.py              # FastAPI 实例 + 中间件 + 路由注册
├── config.py            # Settings 类，读 .env 环境变量
├── database.py          # SQLAlchemy 连接 + get_db 依赖注入
├── limiter.py           # slowapi 共享限流器
├── models/              # ORM 模型（7 张表）
│   ├── user.py          #   User
│   └── conversation.py  #   Conversation / Message / KnowledgeCard /
│                        #   PromptTemplate / LearningResource / KnowledgeDocument
├── schemas/             # Pydantic 请求/响应模型（20+）
│   └── conversation.py
├── routers/             # API 路由（8 个模块）
│   ├── auth.py          #   注册/登录/资料/改密
│   ├── chat.py          #   SSE 流式/消息编辑/模型列表
│   ├── history.py       #   会话 CRUD/置顶/归档/导出
│   ├── cards.py         #   知识卡片 CRUD
│   ├── dashboard.py     #   学习面板统计
│   ├── templates.py     #   对话模板 CRUD
│   ├── resources.py     #   学习资料 CRUD + AI 搜索
│   └── knowledge.py     #   知识库文档上传/解析/搜索
├── services/            # 业务逻辑层
│   ├── ai_service.py    #   流式 AI 调用 + 历史加载 + 上下文窗口
│   ├── auth_service.py  #   注册/登录/改密
│   ├── chat_service.py  #   会话管理
│   └── document_parser.py  # PDF/DOCX/TXT/MD 解析
└── utils/
    └── security.py      # JWT 编解码 + bcrypt 哈希 + get_current_user
```

### 3.2 数据库 ER 图

```
users
  PK id
  ├── username, password_hash, nickname, avatar, preferences(JSON)
  │
  ├─1→N─ conversations
  │        PK id, FK user_id
  │        ├── title, pinned, archived, created_at
  │        │
  │        └─1→N─ messages
  │                 PK id, FK conversation_id
  │                 ├── role(user/assistant), content(Text), images(JSON)
  │                 └── created_at
  │                 INDEX(conversation_id, created_at)
  │
  ├─1→N─ knowledge_cards
  │        PK id, FK user_id
  │        ├── content(Text), source, tags, created_at
  │
  ├─1→N─ learning_resources
  │        PK id, FK user_id
  │        ├── title, url, description, category, resource_type
  │        ├── tags, visibility, created_at
  │        INDEX(visibility, user_id)
  │
  ├─1→N─ knowledge_documents
  │        PK id, FK user_id
  │        ├── title, file_type, file_path, file_size
  │        ├── content_text(Text), tags, visibility, created_at
  │        INDEX(visibility, user_id)
  │
  └─1→N─ prompt_templates
           PK id, FK user_id(NULL=内置)
           ├── title, content(Text), category, is_builtin, created_at
           INDEX(is_builtin, user_id)
```

### 3.3 前端状态管理

```
stores/
├── user.js       # token / username / nickname / avatar / preferences
│                 # login() / register() / logout() / loadProfile() / saveProfile()
├── chat.js       # conversations / messages / models / currentModel / loading
│                 # sendMessage() / streamChat / loadMoreMessages / regenerate
├── cards.js      # cards[] — loadCards / addCard / editCard / removeCard
├── dashboard.js  # stats — loadStats()
├── resources.js  # resources[] / aiAnswer / aiResults — loadResources / ask
├── knowledge.js  # documents[] / currentDoc — loadDocuments / addDocument / editDocument
├── templates.js  # templates[] / groupedTemplates — loadTemplates（带缓存）
└── theme.js      # isDark — toggle()
```

### 3.4 API 接口一览（8 组路由、25+ 端点）

| 路由模块 | 方法 | 端点 | 功能 |
|---------|------|------|------|
| auth | POST | /auth/register | 注册 |
| auth | POST | /auth/login | 登录 |
| auth | GET | /auth/profile | 获取资料 |
| auth | PUT | /auth/profile | 更新资料 |
| auth | PUT | /auth/password | 修改密码 |
| chat | POST | /chat | AI 流式对话 |
| chat | GET | /models | 模型列表 |
| history | POST | /conversations | 新建会话 |
| history | GET | /conversations | 会话列表 |
| history | GET | /conversations/{id}/messages | 消息列表（分页） |
| history | PUT | /conversations/{id} | 重命名 |
| history | DELETE | /conversations/{id} | 删除会话 |
| history | PUT | /conversations/{id}/pin | 置顶切换 |
| history | PUT | /conversations/{id}/archive | 归档切换 |
| history | GET | /conversations/{id}/export | 导出 Markdown |
| chat | PUT | /messages/{id} | 编辑消息 |
| chat | DELETE | /messages/{id} | 删除消息 |
| cards | POST | /cards | 创建卡片 |
| cards | GET | /cards | 卡片列表 |
| cards | PUT | /cards/{id} | 编辑卡片 |
| cards | DELETE | /cards/{id} | 删除卡片 |
| dashboard | GET | /dashboard/stats | 学习统计 |
| templates | GET | /templates | 模板列表 |
| templates | POST | /templates | 创建模板 |
| resources | POST | /resources | 创建资料 |
| resources | GET | /resources | 资料列表 |
| resources | POST | /resources/ask | AI 搜索 |
| knowledge | POST | /knowledge/upload | 上传文档 |
| knowledge | GET | /knowledge | 文档列表 |
| knowledge | GET | /knowledge/{id} | 文档详情 |

---

## 四、技术亮点与难点（3 分钟）

### 4.1 性能优化

| 优化项 | 措施 | 效果 |
|--------|------|------|
| 前端体积 | Element Plus 按需导入（unplugin） + highlight.js 精简 15 种语言 | 1942KB → 666KB（-66%） |
| 流式渲染 | Markdown 解析 150ms 防抖，代码块注入 300ms 防抖 | CPU 占用降 ~90% |
| 后端异步 | resources/ask 从 sync httpx 改为 async httpx.AsyncClient | 不阻塞事件循环 |
| 查询优化 | 4 个复合索引 + 列表上限 200-500 + AI 上下文窗口 50 条 | 防止数据量增长后卡顿 |
| 懒加载 | 模板缓存、Tab 按需加载、profile 去重 | 减少冗余 API 调用 |
| chunk 拆分 | Vite manualChunks 分离 vendor-vue/hljs/markdown | 更好的缓存和并行加载 |

### 4.2 安全防护

| 层面 | 措施 | 实现位置 |
|------|------|----------|
| 认证 | JWT + bcrypt | `utils/security.py` |
| 限流 | slowapi 全局 60/min，AI 20/min，登录 10/min | `limiter.py` + 路由装饰器 |
| XSS | DOMPurify 清理 marked 输出 | `ChatMessage.vue` rendered 计算属性 |
| 归属校验 | 每个操作验证 user_id 匹配 | 各 router 端点 |
| SQL 注入 | SQLAlchemy ORM 参数化查询 | 全部 Model 查询 |

### 4.3 工程化实践

- **Alembic 迁移**：`alembic revision --autogenerate` → `alembic upgrade head`
- **Docker Compose**：MySQL + Backend + Frontend Nginx 一键部署
- **GitHub Actions CI**：push 触发，后端 pytest + 前端 vite build
- **23 个测试用例**：覆盖认证、对话、消息、功能、面板

### 4.4 遇到的难点与解决

| 难点 | 原因 | 解决方案 |
|------|------|----------|
| SSE 首 token 延迟 2-3 秒 | 回放式：先收集完整响应再逐 chunk 回放 | 改为真流式：httpx.AsyncClient 边收边转发 |
| 流式时 Markdown 闪烁 | 每个 token 触发全量 marked.parse + DOMPurify | 150ms 防抖，loading 结束立即渲染 |
| 长对话卡顿 | 加载全部消息到内存构建 AI 上下文 | 上下文窗口 50 条 + 消息分页加载（每页 50 条） |
| 重新生成丢失回复 | 删除旧 AI 消息后流式失败 | 暂存旧消息副本，失败时自动恢复 |
| 无限滚动位置跳动 | prepend 旧消息后 scrollTop 归零 | 加载前记录 scrollHeight，加载后补偿差值 |

---

## 五、总结与展望（2 分钟）

### 5.1 项目成果

| 维度 | 数据 |
|------|------|
| 功能 | 50+ 功能项，涵盖对话、卡片、资料、知识库、面板、模板 |
| 迭代 | 33 个阶段，从 MVP 到完整系统 |
| 测试 | 23 个 pytest 用例 |
| 性能 | 前端体积 -66%，流式 CPU -90% |
| 代码 | 全量中文注释，模块级 docstring |
| 部署 | Docker 一键部署，CI 自动化 |

### 5.2 已知不足

- AI 模型单一服务商，未实现多供应商自动切换
- 知识库仅支持纯文本解析，不支持图片/表格提取
- 缺少协作功能（共享资料、团队学习）
- 无限滚动未实现虚拟列表（超长对话仍有性能瓶颈）

### 5.3 未来方向

| 优先级 | 方向 | 价值 |
|--------|------|------|
| 高 | RAG 检索增强：基于知识库文档的精准问答 | 知识库从「存储」升级为「智能检索」 |
| 高 | 对话分支：同一话题多角度探索 | 支持发散性学习 |
| 中 | 学习计划：设定目标、追踪进度、提醒复习 | 从被动问答到主动规划 |
| 中 | 多语言支持：界面国际化 | 扩大适用范围 |
| 低 | 协作空间：共享资料和学习笔记 | 支持团队学习 |

---

## 附：答辩前检查清单

- [ ] 后端运行中：`cd backend && python -m uvicorn app.main:app --reload`
- [ ] 前端运行中：`cd frontend && npm run dev`
- [ ] 数据库已初始化，种子数据已加载
- [ ] 测试账号可登录
- [ ] AI API Key 有效，对话功能正常
- [ ] 至少 2-3 个历史会话（含长对话）用于演示
- [ ] 准备一张图片用于演示图片识别
- [ ] 准备一个 PDF 文档用于演示知识库上传
