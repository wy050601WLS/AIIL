# AI 智慧学习系统 — 答辩文档

> 总时长：20 分钟

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

## 二、功能演示 + 技术亮点（8 分钟）

### 2.1 注册登录

**演示**：注册 → 登录 → 改头像昵称

**技术亮点 — JWT 认证 + bcrypt 加密**：

密码不是直接存数据库，而是用 **bcrypt** 加密后再存。比如密码 `123456`，存到数据库变成一串乱码 `$2b$12$XyZ...`，即使数据库被偷也看不到原始密码。

登录成功后，后端生成一个 **JWT Token**（通行证），前端存起来，以后每次请求都带上，后端看到通行证就知道你是谁。

```python
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())  # 加密

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)           # 验证

def create_token(user_id):
    return jwt.encode({"sub": str(user_id)}, SECRET_KEY)       # 生成通行证
```

---

### 2.2 AI 对话 — 最核心的功能

**演示**：发问题 → AI 一个字一个字蹦出来 → 代码有高亮 → 可以停止/重新生成

**技术亮点 1 — SSE 流式推送**：

普通请求要等 AI 全部回答完才返回，用户盯着空白页面干等。改用 **SSE（Server-Sent Events）**，AI 边回答边显示。

```
用户发消息 → 后端问 AI → AI 一个字一个字回答
                         → 后端收到一个字就推给前端
                         → 前端立刻显示
```

后端用 **httpx** 异步流式调用 AI 接口，前端用 **ReadableStream** 逐字接收：

```python
# 后端
async def stream_ai_api(history, model):
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", ai_url, json=payload) as response:
            async for line in response.aiter_lines():
                content = parse_sse_line(line)
                if content:
                    yield content  # 收到一个字，立刻返回
```

```javascript
// 前端
const reader = response.body.getReader()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  onToken(parsedText)  // 收到一个字，显示一个字
}
```

**技术亮点 2 — Markdown 渲染 150ms 防抖**：

AI 每秒可能输出几十个字，如果每个字都重新渲染 Markdown（转 HTML + 代码高亮 + 安全过滤），页面会卡。加了 **150ms 防抖** —— 每 150 毫秒最多渲染一次，AI 停止回答后立刻渲染最终版本。

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

### 2.3 会话管理

**演示**：新建、重命名、置顶、归档、搜索、导出

**技术亮点 — 无限滚动 + 滚动位置补偿**：

长对话可能有几百条消息，一次全部加载很慢。第一次只加载最近 50 条，用户往上滚动时再加载更多。

难点是加载旧消息后页面高度变了，滚动条会跳。解决方法：加载前记住页面高度，加载后补偿滚动位置。

```javascript
if (滚动到顶部了) {
  const 旧高度 = 页面.scrollHeight
  await 加载更多消息()
  页面.scrollTop = 页面.scrollHeight - 旧高度  // 补偿
}
```

搜索是纯前端过滤，不需要请求后端。导出是后端把消息拼成 Markdown，前端下载 `.md` 文件。

---

### 2.4 知识卡片

**演示**：从 AI 回复提取卡片 → 标签筛选 → 编辑

AI 回复旁边有「提取卡片」按钮，点击保存到数据库。前端用标签筛选和搜索过滤，纯前端操作。

---

### 2.5 学习资料和知识库

**演示**：添加资料 → AI 搜索推荐 → 上传 PDF 文档

**技术亮点 — AI 智能搜索**：

用户输入自然语言问题（比如「我有哪些编程资料？」），后端把用户的资料库信息发给 AI，让 AI 分析哪些资料相关，返回推荐结果和学习建议。

**技术亮点 — 多格式文档解析**：

上传 PDF/Word/TXT 文件，后端自动提取文字内容存到数据库：
- PDF → **pypdf** 提取文字
- Word → **python-docx** 提取文字
- TXT/MD → 直接读取

---

### 2.6 学习面板

**演示**：统计数据、趋势图、热门标签

**技术亮点 — SQL 聚合查询 + 纯 CSS 图表**：

后端写 SQL 统计对话数、消息数、每天消息趋势、热门标签。前端柱状图用纯 CSS 做 —— 每天一个 `<div>`，高度根据消息数计算，不需要图表库。

---

### 2.7 对话模板

**演示**：选模板 → 自动填充输入框

数据库存了 23 个内置模板，用户也可以创建自己的。启动时后端自动检查内置模板是否完整，缺失的自动补全。

---

## 三、技术亮点详解（4 分钟）

### 3.1 打包体积优化 66%

**问题**：初始打包 2MB，加载慢。

| 优化项 | 怎么做 | 效果 |
|--------|--------|------|
| Element Plus | 按需导入，`unplugin-vue-components` 自动注册 | 只打包用到的组件 |
| highlight.js | 从 190+ 语言裁到 15 个常用语言 | 体积大幅缩小 |
| 代码分包 | vendor-vue / vendor-markdown / vendor-hljs 分开 | 可并行加载 |

最终打包 **666KB**，缩小了 66%。

### 3.2 安全防护

| 风险 | 防护措施 |
|------|----------|
| 密码泄露 | bcrypt 加密存储，数据库里看不到明文 |
| 接口被刷 | 限流中间件，60 次/分钟 |
| AI 回复注入恶意代码 | DOMPurify 过滤 HTML |
| 越权操作 | 每个接口校验资源是否属于当前用户 |
| SQL 注入 | SQLAlchemy ORM 参数化查询 |

### 3.3 后端异步 + 数据库索引

**异步改造**：AI 搜索接口原来是同步的，调 AI 时阻塞整个服务器。改成 `async def` + `httpx.AsyncClient`，不卡其他请求。

**数据库索引**：给高频查询加了 4 个复合索引：
- 会话：`(user_id, pinned, created_at)`
- 模板：`(is_builtin, user_id)`
- 资料/文档：`(visibility, user_id)`

**列表限制**：所有列表接口加 `.limit(200)`，防止一次返回太多数据。

---

## 四、项目难点与解决（4 分钟）

### 4.1 AI 回复慢，用户干等

**问题**：AI 生成回复可能需要好几秒，用户盯着空白页面，以为系统卡了。

**解决**：SSE 流式推送，AI 边回答边显示。后端用 httpx 异步流式调用，前端用 ReadableStream 逐字接收。用户立刻看到 AI 在「打字」，体验好很多。

### 4.2 流式输出时页面闪烁

**问题**：AI 每秒输出几十个字，每个字都重新渲染 Markdown，页面疯狂闪烁，CPU 飙高。

**解决**：150ms 防抖。流式输出中每 150ms 渲染一次，AI 停止回答后立刻渲染最终版本。再加 DOMPurify 过滤 HTML 防止 XSS 注入。CPU 占用降低 90%。

### 4.3 长对话几百条消息卡顿

**问题**：一个对话几百条消息，全部加载很慢，滚动也卡。

**解决**：
- 只加载最近 50 条消息，滚动到顶部时再加载更多
- 加载旧消息后补偿滚动位置，防止页面跳动
- AI 上下文窗口限制 50 条，避免 token 超限
- 最近 10 条保留图片数据，更早的只保留文字

### 4.4 重新生成失败丢回复

**问题**：用户点「重新生成」，如果 AI 返回失败，原来的回复也没了。

**解决**：重新生成前先暂存旧回复，失败了自动恢复。同时 AI 回复为空时也自动恢复，不会出现空白消息。

```javascript
// 暂存旧回复
let oldMessage = messages.pop()
// 生成新回复
await streamChat(...)
// 失败时恢复
if (!newContent && oldMessage) messages.push(oldMessage)
```

### 4.5 数据库查询变慢

**问题**：数据量增长后，列表查询变慢。

**解决**：分析高频查询路径，加了 4 个复合索引。同时所有列表接口限制最大返回 200 条，避免一次传输太多数据。

---

## 五、总结（2 分钟）

### 项目成果

- **50+ 功能**：AI 对话、知识卡片、学习资料、知识库、学习面板、对话模板
- **33 次迭代**：从最初能聊天的基础版，到现在功能完整的系统
- **23 个测试**：核心功能都有自动化测试
- **性能优化**：打包体积缩小 66%，流式渲染 CPU 占用降 90%

### 不足之处

- 只支持一个 AI 服务商，不能自由切换
- 知识库只能提取文字，不能识别图片里的内容
- 没有协作功能，不能和同学共享资料

### 未来扩展

| 方向 | 说明 |
|------|------|
| RAG 智能检索 | 问问题时自动从知识库里找相关内容，回答更精准 |
| 对话分支 | 一个问题可以分多个方向探索 |
| 学习计划 | 设定学习目标，追踪进度，提醒复习 |
| 协作空间 | 和同学共享资料和笔记 |

---

## 附：答辩前准备清单

- [ ] 后端启动：`cd backend && python -m uvicorn app.main:app --reload`
- [ ] 前端启动：`cd frontend && npm run dev`
- [ ] 数据库有数据，能正常登录
- [ ] AI 能正常回复
- [ ] 准备一个 PDF 文档演示知识库上传
