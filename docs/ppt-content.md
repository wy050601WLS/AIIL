# AI 智慧学习系统 — PPT 内容文档

> 20 分钟答辩，功能亮点驱动，所有讲解用大白话

---

## 第 1 页 — 封面

**标题**：AI 智慧学习系统

**副标题**：基于 Vue3 + FastAPI 的 AI 对话式学习助手

**底部**：答辩人：XXX ｜ 日期：2026 年 6 月

---

## 第 2 页 — 项目背景

**标题**：为什么做这个项目

**三个痛点**：

1. 问问题不方便 — 要等老师回复，或者网上搜半天
2. 学过的东西找不回来 — 之前问过的、学过的散落各处
3. 不知道自己学了多少 — 没有数据反馈

**解决方案**：AI 随时回答 + 精华收藏成卡片 + 学习数据可视化

---

## 第 3 页 — 技术栈

| 层级 | 技术 | 大白话 |
|------|------|--------|
| 前端 | Vue3 + Pinia + Element Plus | 画页面的工具 + 存数据的记事本 + 现成的按钮输入框 |
| 后端 | FastAPI + SQLAlchemy | 处理请求的程序 + 用代码操作数据库（不用写 SQL） |
| 数据库 | MySQL 8.0 | 存数据的仓库，用户、对话、消息都存在这里 |
| AI | MiMo 大模型 | 人工智能，负责回答用户的问题 |

---

## 第 4 页 — 功能亮点总览

| # | 功能亮点 | 一句话 |
|---|---------|--------|
| 1 | SSE 流式对话 | AI 一个字一个字蹦出来，不用干等 |
| 2 | Markdown 渲染防抖 | 流式输出时页面不卡不闪 |
| 3 | JWT + bcrypt 认证 | 密码加密存储，通行证式登录 |
| 4 | 无限滚动 + 位置补偿 | 长对话秒开，翻页不跳 |
| 5 | AI 智能搜索 | 用大白话问 AI 找资料 |
| 6 | 多格式文档解析 | 上传 PDF/Word 自动提取文字 |
| 7 | 学习面板 | 数据统计 + 纯 CSS 柱状图 |
| 8 | 性能优化 | 打包体积缩小 66% |

---

## 第 5 页 — 亮点 1：SSE 流式对话

### 功能亮点

用户发消息后，AI 一个字一个字蹦出来，就像 AI 在实时打字，不用盯着空白页面干等。

### 如何实现

普通请求就像寄快递 — 全部打包好才送到。SSE 就像流水线 — 做好一件就送一件。后端收到 AI 每个字，立刻推给前端，前端立刻显示。

### 代码 — 后端

```python
# 后端用 httpx 异步流式调用 AI 接口
async def stream_ai_api(history, model):
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            async for line in response.aiter_lines():
                chunk = json.loads(line[6:])
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    yield content  # 收到一个字，立刻传给前端
```

### 代码 — 前端

```javascript
// 前端用 ReadableStream 逐字接收
const reader = res.body.getReader()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  buffer += decoder.decode(value, { stream: true })
  if (line.startsWith('data: ')) {
    onToken(data)  // 收到一个字，显示一个字
  }
}
```

### 代码讲解（大白话）

**后端这段代码**：打开一个「流」连接给 AI 发消息。`async for line in response.aiter_lines()` 的意思是「AI 每吐出一行文字，我就读一行」。`yield content` 就像接力棒传递 — 收到一个字就立刻传给前端，不等后面的内容。

**前端这段代码**：打开一个「水龙头」，不停地读取后端推过来的文字。`reader.read()` 每次读一小块，读到了就调 `onToken` 显示到页面上。`done` 是 true 表示 AI 回答完了，关掉水龙头。

### 技术讲解（大白话）

- **SSE（Server-Sent Events）**：一种「服务器主动往浏览器推消息」的技术。就像广播电台，只有电台能说话，你只能听。AI 对话只需要服务器往浏览器推内容，所以用 SSE 就够了
- **httpx**：Python 的异步 HTTP 库。`client.stream()` 打开一个流连接，不等响应结束就能一行一行读取
- **yield**：Python 的「接力棒传递」函数。普通函数算完了一次性返回结果，yield 是算一步传一步

### 为什么用 SSE 而不是 WebSocket？

WebSocket 是双向对讲机，双方都能说话。SSE 是广播，只有服务器能说。AI 对话只需要服务器往浏览器推内容，不需要浏览器往服务器推，所以 SSE 更简单、更轻量、浏览器原生支持。

---

## 第 6 页 — 亮点 2：Markdown 渲染防抖

### 功能亮点

AI 回复里有标题、列表、代码块，前端要转成网页能显示的格式。AI 每秒输出几十个字，如果每个字都重新转换，页面会疯狂闪烁。加了防抖后，页面不卡不闪，CPU 占用降低 90%。

### 如何实现

AI 每输出一个字，计时器就重置。只有 150ms 内没有新字了，才触发渲染。就像电梯门 — 有人进来，门就重新计时；只有没人进来了，门才关。

### 代码

```javascript
watch(() => props.content, (val) => {
  if (renderTimer) clearTimeout(renderTimer)  // 有新字来了，取消之前的渲染计划
  if (!props.loading) {
    // AI 不在输出了，立刻渲染最终版本
    renderedContent.value = DOMPurify.sanitize(marked.parse(val))
    return
  }
  // AI 还在输出，等 150ms 再渲染
  renderTimer = setTimeout(() => {
    renderedContent.value = DOMPurify.sanitize(marked.parse(val))
  }, 150)
})
```

### 代码讲解（大白话）

- `watch` — 监听 AI 回复内容的变化，内容一变就执行里面的代码
- `clearTimeout(renderTimer)` — 有新字来了，取消之前的渲染计划，重新开始计时
- `!props.loading` — AI 不在输出了（回答完了），不用等了，立刻渲染
- `setTimeout(..., 150)` — AI 还在输出，等 150 毫秒再渲染。如果 150ms 内又来了新字，这个计划会被取消重来
- `marked.parse(val)` — 把 Markdown 文本转成 HTML
- `DOMPurify.sanitize(...)` — 过滤掉危险的 HTML 标签，防止恶意代码注入

### 技术讲解（大白话）

**防抖是什么？** 就像电梯门。有人进来，门就重新计时。只有没人进来了，门才关。代码里也是这个道理 — AI 每输出一个字，计时器就重置。只有 150ms 内没有新字了，才触发渲染。

**渲染管线**：AI 原始文字 → marked 把 Markdown 转成 HTML → highlight.js 给代码块加颜色 → DOMPurify 过滤掉危险的 HTML → 显示到页面。

### 为什么用 150ms？

太短（如 50ms）渲染太频繁，跟没防抖差不多；太长（如 500ms）用户感觉 AI 回复卡顿。150ms 刚刚好 — 人眼感觉流畅，CPU 占用降低 90%。


---

## 第 7 页 — 亮点 3：JWT + bcrypt 认证

### 功能亮点

用户注册登录时，密码不是直接存数据库，而是加密成乱码再存。登录成功后发一个「通行证」（JWT），以后每次请求带上通行证，后端就知道你是谁。

### 如何实现

1. 注册：用户输入密码 → bcrypt 加密成乱码 → 存入数据库
2. 登录：输入密码 → 和数据库的乱码对比 → 正确就发 JWT 通行证
3. 每次请求：前端自动带上通行证 → 后端验证身份
4. 通行证过期（24 小时）→ 自动跳回登录页

### 代码

```python
# 加密：密码 → 乱码（不可逆，没法从乱码反推密码）
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# 验证：拿用户输入的密码和数据库的乱码对比
def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# 生成 JWT 通行证（24 小时有效）
def create_access_token(user_id):
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

### 代码讲解（大白话）

- `bcrypt.hashpw` — 把密码塞进「碎纸机」，出来一堆乱码。这台碎纸机有个特点：你可以拿一个新密码和乱码对比，看是不是同一个密码做的。但你没法从乱码反推出原始密码
- `bcrypt.gensalt()` — 生成随机「盐」，让同一个密码每次加密结果都不同。比如密码 `123456`，第一次加密出来 `$2b$12$abc...`，第二次出来 `$2b$12$xyz...`，不一样
- `bcrypt.checkpw` — 验证密码。拿用户刚输入的密码和数据库存的乱码对比，返回 True 或 False
- `jwt.encode` — 生成通行证。里面写了用户 ID 和过期时间，用密钥签名，别人改不了

### 技术讲解（大白话）

**bcrypt 是什么？** 就像一台碎纸机 — 你把密码塞进去，出来的是一堆乱码。这台碎纸机有个特点：你可以拿一个新的密码和那堆乱码对比，看是不是同一个密码做的。但你没法从乱码反推出原始密码。而且它故意设计得很慢（约 100ms），暴力破解一个密码需要几百年。

**JWT 是什么？** 就是一张通行证。上面写了「你是谁」和「什么时候过期」，还盖了章（签名），别人改不了内容。前端把通行证存在浏览器里，每次请求放在请求头里，后端一看就知道你是谁。

### 为什么用 bcrypt 而不是 MD5？

MD5 加密太快了，一秒能算几十亿次，黑客可以暴力试所有密码。bcrypt 故意设计得很慢，试一次要 100ms，暴力破解一个密码要几百年。而且同一个密码每次加密结果都不同（因为加了随机盐），更安全。

---

## 第 8 页 — 亮点 4：无限滚动 + 位置补偿

### 功能亮点

一个对话可能聊了几百条消息，全部一次加载很慢。改成只加载最近 50 条，往上翻才加载更多，就像翻微信聊天记录一样自然流畅。

### 如何实现

1. 第一次打开对话 → 只加载最近 50 条消息
2. 用户往上滚动 → 检测到滚到顶部 → 加载更早的 50 条
3. 加载后 → 补偿滚动位置，页面不跳动

难点：加载旧消息后页面变高了，滚动条会跳。解决方法：加载前记住「页面有多高」，加载后算「新页面比旧页面高了多少」，把滚动条调回去。

### 代码

```javascript
async function handleScroll() {
  const el = messagesAreaRef.value
  if (el.scrollTop < 50) {                      // 滚到顶部了
    const prevHeight = el.scrollHeight           // 记住加载前页面高度
    await chatStore.loadMoreMessages()           // 加载旧消息
    el.scrollTop = el.scrollHeight - prevHeight  // 补偿：调回原来的位置
  }
}

// 自动滚动：只在用户已在底部时才自动滚，用户上翻时不打扰
watch(() => messages.length, (newLen, oldLen) => {
  if (newLen > oldLen && isAtBottom.value) {
    scrollToBottom()
  }
})
```

### 代码讲解（大白话）

- `el.scrollTop < 50` — 滚动条离顶部不到 50 像素，说明用户翻到最上面了
- `el.scrollHeight` — 整个页面的总高度（包括看不见的部分）
- `el.scrollTop` — 当前滚动条的位置
- 加载旧消息后页面变高了，用「新高度 - 旧高度」就是新增的高度，把滚动条往下调这么多，你就还是看到原来的位置
- `isAtBottom` — 距底部 50px 内视为在底部。用户往上翻看历史时，新消息来了不会被拉回去

### 技术讲解（大白话）

**位置补偿是什么？** 想象你在看一本竖着的长图。你正在看中间某一段，突然上面又加了一段新内容，你看到的位置就往下移了，你得自己往回滚。解决方法：加载前记住「页面有多高」，加载后算「新页面比旧页面高了多少」，把滚动条调回去。这样你还是看到原来的位置，不会跳。

**isAtBottom 检测**：如果用户正在往上翻看历史消息，这时候 AI 回复了新消息，不应该把用户拉回底部。所以只在用户已经在底部时才自动滚动。

### 为什么不用分页按钮？

分页按钮要点「下一页」，打断思路。无限滚动像翻微信聊天记录，手指往上滑就加载更多，自然流畅。

---

## 第 9 页 — 亮点 5：AI 智能搜索

### 功能亮点

传统搜索必须输入准确关键词，差一个字都找不到。AI 搜索可以用大白话提问，比如「我有哪些编程资料？」，AI 理解语义后推荐相关资料。

### 如何实现

1. 后端把用户的所有资料整理成一份清单
2. 把清单和用户的问题一起发给 AI
3. AI 看完清单后，挑出相关的资料，告诉用户推荐理由
4. 前端把 AI 的回答显示出来，只展示被推荐的资料

### 代码

```python
async def ask_resources(data, user, db):
    # 1. 加载用户的所有资料（限制 100 条）
    resources = db.query(LearningResource).filter(...).limit(100).all()

    # 2. 构造资料摘要作为上下文
    context = "\n".join(f"[{r.id}] {r.title} | {r.category}" for r in resources)

    # 3. 把上下文和用户问题一起发给 AI
    messages = [
        {"role": "system", "content": f"用户的资料库：\n{context}"},
        {"role": "user", "content": data.question},
    ]
    answer = await call_ai(messages)

    # 4. 从 AI 回复中提取引用的 ID，只返回推荐的资料
    referenced_ids = set(re.findall(r'\[(\d+)\]', answer))
    recommended = [r for r in resources if r.id in referenced_ids]
    return {"answer": answer, "resources": recommended}
```

### 代码讲解（大白话）

- 第 1 步：从数据库取出用户的所有学习资料，最多 100 条
- 第 2 步：把资料整理成一份清单，格式是「[编号] 标题 | 分类」
- 第 3 步：把清单塞进 system prompt（系统提示词），AI 就能「看到」所有资料。然后把用户的问题一起发给 AI
- 第 4 步：AI 回复里会引用资料编号，比如「推荐 [1] [3]」。后端用正则表达式把 `[1]` `[3]` 这些编号提取出来，只返回被推荐的资料，不返回全部

### 技术讲解（大白话）

**上下文注入是什么？** 就像你给图书管理员一份清单，然后问「有没有适合初学者的 Python 书？」。管理员看完清单后，能从里面挑出合适的推荐给你。这里 AI 就是那个管理员，清单就是用户的资料库。

**为什么用异步？** 后端调 AI 需要几秒钟。如果用同步，这几秒钟其他用户的请求全部排队等着。改成异步后，调 AI 的时候后端可以同时处理别的请求。就像一个厨师同时看好几个锅，哪个锅好了就处理哪个。

### 为什么用 AI 搜索而不是数据库搜索？

数据库搜索只能做字符串匹配，搜「编程」就只能找到标题里有「编程」两个字的资料。AI 能理解语义，搜「编程」知道 Python、Java、前端都算编程，能找到更多相关资料。

---

## 第 10 页 — 亮点 6：多格式文档解析

### 功能亮点

用户上传 PDF/Word/TXT 文件，后端自动提取文字内容存到数据库，支持搜索和查看。

### 如何实现

用户上传文件 → 保存到磁盘 → 根据格式调用对应解析器提取文字 → 存入数据库。

### 代码

```python
from pypdf import PdfReader
from docx import Document

def parse_document(file_path, file_type):
    if file_type == "pdf":
        reader = PdfReader(file_path)
        return "\n\n".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )
    elif file_type == "docx":
        doc = Document(file_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    elif file_type in ("txt", "md"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
```

### 代码讲解（大白话）

- **PDF 解析**：`PdfReader` 打开 PDF 文件，`reader.pages` 获取所有页面，`page.extract_text()` 把每一页的文字「抠」出来，最后用换行把所有页拼起来
- **Word 解析**：`Document` 打开 Word 文件，`doc.paragraphs` 获取所有段落，`p.text` 取出每段的文字，过滤掉空段落，拼起来
- **TXT/MD 解析**：就是普通的打开文件读取文字，`encoding="utf-8"` 确保中文不乱码

### 技术讲解（大白话）

**pypdf 是什么？** PDF 文件看起来是一个整体，其实里面是一页一页的。每一页的文字藏在页面对象里。pypdf 就像一把小刀，能把文字从页面里「抠」出来。

**python-docx 是什么？** Word 文件有内部结构，就像一个文件夹里装了很多段落。python-docx 能打开这个文件夹，把每段文字读出来。

### 为什么不用 OCR？

OCR 是识别图片里的文字，需要额外的库，速度慢，准确率有限。当前方案优先覆盖最常见的文字版 PDF（文字可以直接复制的那种）。扫描版 PDF（拍照的那种）暂时不支持，会提示用户手动输入。


---

## 第 11 页 — 亮点 7：学习面板

### 功能亮点

统计数据、每日消息趋势柱状图、热门标签 Top 10。后端用 SQL 统计，前端用纯 CSS 做柱状图，不需要图表库。

### 如何实现

后端写 SQL 按日期分组统计消息数，前端每天生成一个 div 方块，高度根据消息数计算。

### 代码 — 后端

```python
# 最近 30 天每日消息数（按日期分组计数）
rows = db.query(
    func.date(Message.created_at).label("day"),  # 按日期分组
    func.count(Message.id)                        # 统计每天消息数
).join(Conversation).filter(
    Conversation.user_id == user.id,
    Message.created_at >= since
).group_by(func.date(Message.created_at)).all()

# 热门标签 Top 10
tag_counter = Counter()
for (tags_str,) in cards:
    for tag in tags_str.split(","):
        tag_counter[tag.strip()] += 1
top_tags = tag_counter.most_common(10)
```

### 代码 — 前端

```vue
<!-- 每天一个 div，高度根据消息数算 -->
<div v-for="day in dailyMessages" :key="day.date" class="bar"
  :style="{ height: (day.count / maxCount * 100) + '%' }">
</div>
```

### 代码讲解（大白话）

**后端**：`func.date(Message.created_at)` 把消息的创建时间按日期分组，就像 Excel 的「按日期分类」。`func.count(Message.id)` 统计每天有多少条消息，就像 Excel 的 COUNTIF。`group_by` 就是分组，同一天的消息放一起计数。

**前端**：每天生成一个小方块（div），高度按消息数算。消息最多的那天最高，没有消息的那天就是一条线。不需要引入 ECharts 等图表库，几行 CSS 就搞定。

### 技术讲解（大白话）

**SQL 聚合查询**：就像 Excel 的 COUNTIF 和 GROUP BY。比如你有一张消息表，想知道每天有多少条消息，SQL 的 GROUP BY 就是按日期把消息分组，COUNT 就是数每组有多少条。

**纯 CSS 柱状图**：每个 div 是一个柱子，高度用百分比算。比如消息最多的那天有 100 条，那天的高度就是 100%；有 50 条的那天就是 50%。

### 为什么用纯 CSS 而不是 ECharts？

ECharts 是一个很强大的图表库，但它有 800KB。我们只做一个简单的柱状图，用 ECharts 就像用大炮打蚊子。纯 CSS 几行代码就搞定，零额外依赖，加载更快。

---

## 第 12 页 — 亮点 8：性能优化

### 功能亮点

初始打包 2MB，加载慢。优化后 666KB，缩小 66%。

### 如何实现

三项优化：按需导入 Element Plus、裁剪 highlight.js 语言、代码分包。

### 代码 — 按需导入

```javascript
// vite.config.js — 自动按需导入，用到哪个组件就打包哪个
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

plugins: [
  AutoImport({ resolvers: [ElementPlusResolver()] }),
  Components({ resolvers: [ElementPlusResolver()] }),
]
```

### 代码 — 语言裁剪

```javascript
// 只注册 15 种常用语言，不导入全部 190+ 种
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
// ... 共 15 种
```

### 代码 — 分包策略

```javascript
// 把不同功能的代码分成不同的文件
manualChunks(id) {
  if (id.includes('node_modules/vue'))        return 'vendor-vue'
  if (id.includes('node_modules/marked'))     return 'vendor-markdown'
  if (id.includes('node_modules/highlight.js')) return 'vendor-hljs'
}
```

### 代码讲解（大白话）

**按需导入**：Element Plus 有几百个组件，但我们只用了一部分。之前是全部打包，现在用插件自动检测你用了哪些，只打包用到的。就像搬家只搬需要的东西，不搬整个仓库。

**语言裁剪**：highlight.js 支持 190 多种编程语言的代码高亮，但用户不可能用到所有语言。只保留常用的 15 种（JavaScript、Python、Java 等），其他的砍掉。就像手机只装需要的 APP，不装应用商店里的所有 APP。

**分包**：把不同功能的代码分成不同的文件。浏览器可以同时下载多个小文件，比下载一个大文件快。

### 为什么这么做？

2MB 的打包体积意味着用户第一次打开网页要等很久。优化到 666KB 后，加载速度快了 3 倍，用户体验好很多。

---

## 第 13 页 — 安全防护

**标题**：安全防护体系

| 风险 | 大白话 | 防护措施 |
|------|--------|---------|
| 密码泄露 | 数据库被偷了，密码不能明文存 | bcrypt 加密，存的是乱码 |
| 接口被刷 | 有人疯狂发请求，服务器扛不住 | 限流，每分钟最多 60 次 |
| AI 回复注入 | AI 回复里可能夹带恶意代码 | DOMPurify 过滤危险 HTML |
| 越权操作 | 用户 A 偷看用户 B 的数据 | 每个接口检查是不是本人 |
| SQL 注入 | 攻击者通过输入框注入恶意代码 | ORM 参数化查询，不用拼 SQL |

---

## 第 14 页 — 难点与解决

| 难点 | 大白话 | 解决方案 |
|------|--------|---------|
| AI 回复慢 | 用户发了问题，盯着空白页面好几秒 | SSE 流式推送，AI 边回答边显示 |
| 页面闪烁 | AI 打字太快，每个字都重新渲染 | 150ms 防抖，像电梯门等人进完再关 |
| 长对话卡顿 | 几百条消息全部加载很慢 | 只加载最近 50 条，往上翻才加载更多 |
| 丢回复 | 重新生成失败，原来的回复也没了 | 先暂存旧回复，失败了自动恢复 |
| 查询变慢 | 数据多了，列表查询越来越慢 | 加复合索引（数据库的「目录」）|
| 搜索阻塞 | 调 AI 的时候其他请求全排队 | 改成异步，调 AI 同时处理别的请求 |

---

## 第 15 页 — 总结

**项目成果**：

| 指标 | 数据 | 说明 |
|------|------|------|
| 功能数量 | 50+ | AI 对话、卡片、资料、知识库、面板、模板 |
| 迭代次数 | 33 次 | 从基础版到功能完整的系统 |
| 测试用例 | 23 个 | 覆盖认证、对话、消息、功能、面板 |
| 体积优化 | 66% | 2MB → 666KB |

**不足之处**：
- 只支持一个 AI 服务商，不能自由切换
- 知识库只能提取文字，不能识别图片里的内容
- 没有协作功能，不能和同学共享资料

**未来扩展**：

| 方向 | 大白话 |
|------|--------|
| RAG 智能检索 | 问问题时自动从知识库找相关内容，不用人工翻 |
| 对话分支 | 一个问题可以分叉探索多个方向 |
| 学习计划 | 设定目标、追踪进度、到时间提醒你复习 |
| 协作空间 | 和同学共享资料和笔记 |

---

## 第 16 页 — 谢谢

**标题**：谢谢

**副标题**：欢迎提问

---

## 制作建议

**配色**：深蓝 + 白底，科技感

**字体**：标题用黑体/思源黑体，正文用微软雅黑

**每页原则**：
- 代码块居左，讲解居右（左右分栏）
- 关键数字放大加粗
- 技术讲解用大白话，避免术语堆砌

**动画**：
- 代码块逐行出现
- 要点逐条出现
- 不要花哨转场
