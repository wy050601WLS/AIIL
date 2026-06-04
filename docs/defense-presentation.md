# AI 智慧学习系统 — 答辩文档

> 总时长：20 分钟
> 重点：技术亮点

---

## 一、项目概述（2 分钟）

### 为什么做这个项目

学生学习有三个问题：
1. **问问题不方便** — 要等老师回复，或者网上搜半天
2. **学过的东西找不回来** — 之前问过的、学过的散落各处
3. **不知道自己学了多少** — 没有数据反馈

**AI 智慧学习**就是解决这三个问题：AI 随时回答问题，精华内容可以收藏成卡片，学习数据有面板可以看。

### 技术栈

```
前端：Vue3 + Pinia + Element Plus
后端：Python FastAPI + SQLAlchemy
数据库：MySQL
AI：MiMo 大模型
```

---

## 二、功能演示（4 分钟）

> 这部分快速过一遍功能，实现细节放到技术亮点里讲。

### 2.1 注册登录

**演示**：注册 → 登录 → 改头像昵称

密码加密存储，登录后发 JWT 通行证，前端每次请求带上验证身份。

### 2.2 AI 对话（核心功能）

**演示**：发问题 → AI 一个字一个字蹦出来 → 代码有高亮 → 可以停止/重新生成

用 SSE 流式传输，AI 边回答边显示，不用等全部答完。

### 2.3 会话管理

**演示**：新建、重命名、置顶、归档、搜索、导出

### 2.4 知识卡片

**演示**：从 AI 回复提取卡片 → 标签筛选 → 编辑

### 2.5 学习资料和知识库

**演示**：添加资料 → AI 搜索推荐 → 上传 PDF 文档

### 2.6 学习面板

**演示**：统计数据、趋势图、热门标签

### 2.7 对话模板

**演示**：选模板 → 自动填充输入框

---

## 三、技术亮点（10 分钟）— 重点

### 3.1 流式对话 — SSE 实时推送

**问题**：AI 回复可能要等好几秒才全部生成完，用户盯着空白页面干等。

**方案**：用 SSE（Server-Sent Events）实现「边回答边显示」。

```
用户发消息 → 后端问 AI → AI 一个字一个字回答
                         → 后端收到一个字就推给前端
                         → 前端立刻显示
```

**后端**用 httpx 异步流式调用 AI 接口：
```python
async def stream_ai_api(history, model):
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", ai_url, json=payload) as response:
            async for line in response.aiter_lines():
                content = parse_sse_line(line)
                if content:
                    yield content  # 收到一个字，立刻返回
```

**前端**用 ReadableStream 逐字接收：
```javascript
const reader = response.body.getReader()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  onToken(parsedText)  // 收到一个字，显示一个字
}
```

**效果**：用户立刻看到 AI 在「打字」，体验好很多。

---

### 3.2 Markdown 渲染优化 — 150ms 防抖

**问题**：AI 每秒可能输出几十个字，如果每个字都重新渲染 Markdown（转 HTML + 代码高亮 + 安全过滤），页面会卡。

**方案**：加 150ms 防抖 —— 每 150 毫秒最多渲染一次，AI 停止回答后立刻渲染最终版本。

```javascript
watch(() => props.content, (val) => {
  if (renderTimer) clearTimeout(renderTimer)
  if (!val || !props.loading) {
    renderedContent.value = DOMPurify.sanitize(marked.parse(val || ''))
    return  // 流式结束，立刻渲染
  }
  renderTimer = setTimeout(() => {
    renderedContent.value = DOMPurify.sanitize(marked.parse(val))
  }, 150)  // 流式中，150ms 渲染一次
})
```

渲染管线：**marked**（Markdown → HTML）→ **highlight.js**（代码高亮）→ **DOMPurify**（防 XSS 注入）

**效果**：CPU 占用降低 90%，页面不卡不闪。

---

### 3.3 前端性能 — 打包体积优化 66%

**问题**：初始打包 2MB，加载慢。

**三个优化**：

| 优化项 | 怎么做 | 效果 |
|--------|--------|------|
| Element Plus | 按需导入，用 `unplugin-vue-components` 自动注册 | 只打包用到的组件 |
| highlight.js | 从 190+ 语言裁到 15 个常用语言 | 体积大幅缩小 |
| 代码分包 | vendor-vue / vendor-markdown / vendor-hljs 分开 | 可并行加载 |

最终打包 **666KB**，缩小了 66%。

---

### 3.4 无限滚动 — 长对话不卡顿

**问题**：一个对话可能有几百条消息，一次全部加载很慢。

**方案**：第一次只加载最近 50 条，用户往上滚动时再加载更多。

难点是加载旧消息后页面高度变了，滚动条会跳。解决方法：加载前记住页面高度，加载后补偿滚动位置。

```javascript
if (滚动到顶部了) {
  const 旧高度 = 页面.scrollHeight
  await 加载更多消息()
  页面.scrollTop = 页面.scrollHeight - 旧高度  // 补偿
}
```

同时限制 AI 上下文窗口最多 50 条消息，避免 token 超限。最近 10 条保留图片数据，更早的只保留文字。

---

### 3.5 安全防护

| 风险 | 防护措施 |
|------|----------|
| 密码泄露 | bcrypt 加密存储，数据库里看不到明文 |
| 接口被刷 | 限流中间件，60 次/分钟 |
| AI 回复注入恶意代码 | DOMPurify 过滤 HTML |
| 越权操作 | 每个接口校验资源是否属于当前用户 |
| SQL 注入 | SQLAlchemy ORM 参数化查询 |

关键代码 — 密码加密：
```python
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)
```

---

### 3.6 后端异步 + 数据库优化

**异步改造**：AI 搜索接口原来是同步的，调 AI 时会阻塞整个服务器。改成 `async def` + `httpx.AsyncClient`，不卡其他请求。

**数据库索引**：给高频查询加了 4 个复合索引：
- 会话：`(user_id, pinned, created_at)`
- 模板：`(is_builtin, user_id)`
- 资料/文档：`(visibility, user_id)`

**列表限制**：所有列表接口加 `.limit(200)`，防止一次返回太多数据。

---

### 3.7 工程化实践

- **数据库迁移**：Alembic 管理表结构版本，改了可以升级/回滚
- **容器化**：Docker Compose 一键部署（数据库 + 后端 + 前端）
- **CI 自动化**：GitHub Actions 每次提交自动跑测试和构建
- **单元测试**：23 个测试用例覆盖核心功能

---

## 四、技术架构（2 分钟）

### 整体结构

```
前端（Vue3 + Pinia）→ 后端（FastAPI）→ 数据库（MySQL）
                                    → AI（MiMo API）
```

### 后端分层

```
Router（接收请求）→ Service（业务逻辑）→ Model（操作数据库）
```

7 张表：用户、对话、消息、知识卡片、学习资料、知识库文档、对话模板。删除用户时级联删除所有关联数据。

### 前端结构

8 个 Pinia store 管理状态，每个功能模块独立。API 层统一封装 Axios 请求。

---

## 五、总结（2 分钟）

### 项目成果

- **50+ 功能**：AI 对话、知识卡片、学习资料、知识库、学习面板、对话模板
- **33 次迭代**：从基础版到功能完整的系统
- **23 个测试**：核心功能自动化测试
- **体积优化 66%**：2MB → 666KB

### 不足之处

- 只支持一个 AI 服务商，不能自由切换
- 知识库只能提取文字，不能识别图片里的内容
- 没有协作功能，不能和同学共享资料

### 未来方向

| 方向 | 说明 |
|------|------|
| RAG 智能检索 | 问问题时自动从知识库里找相关内容 |
| 对话分支 | 一个问题可以分多个方向探索 |
| 学习计划 | 设定目标，追踪进度，提醒复习 |
| 协作空间 | 和同学共享资料和笔记 |

---

## 附：答辩前准备清单

- [ ] 后端启动：`cd backend && python -m uvicorn app.main:app --reload`
- [ ] 前端启动：`cd frontend && npm run dev`
- [ ] 数据库有数据，能正常登录
- [ ] AI 能正常回复
- [ ] 准备一个 PDF 文档演示知识库上传
