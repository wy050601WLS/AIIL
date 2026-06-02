# 第五轮功能优化清单（H-1 ~ H-12）

## 优化项目

| 编号 | 文件 | 问题 | 类型 | 状态 |
|------|------|------|------|------|
| H-1 | Settings.vue:58 | 修改密码 `validate()` 校验失败未拦截，进入 catch 显示误导性错误 | Bug | 已修复 |
| H-2 | Sidebar.vue:469 | 移动端操作按钮不可用（hover 在触摸屏无效） | Bug | 已修复 |
| H-3 | Sidebar.vue:57 | `goSettings()` 用 `window.location.href` 导致整页刷新 | UX | 已修复 |
| H-4 | chat.js:87 | `sendMessage` 流式失败时空 assistant 消息残留，无错误提示 | Bug | 已修复 |
| H-5 | Sidebar.vue:25 | 搜索过滤逻辑与归档模式不同步 | Bug | 已修复 |
| H-6 | api/index.js:20 | 401 响应用 `window.location.href` 跳登录页 | UX | 跳过（401 需完整重置状态） |
| H-7 | ChatMessage.vue:5+42 | `marked.setOptions` 重复调用 | 冗余 | 已修复 |
| H-8 | Sidebar.vue:131 | 归档区入口无已归档数量提示 | UX | 已修复 |
| H-9 | ChatInput.vue:50 | 发送按钮可重复发送 | Bug | 跳过（已正确检查 loading） |
| H-10 | chat.js:86 | SSE 多行 data 事件解析 | Bug | 跳过（API 单行 data，buffer 逻辑正确） |
| H-11 | ChatMessage.vue:75 | 复制 AI 消息复制原始 Markdown 而非渲染文本 | UX | 已修复 |
| H-12 | Settings.vue:84 | `savePreferences` 可能覆盖后端其他偏好字段 | Bug | 跳过（当前偏好字段全在表单中） |

## 修复详情

### H-1：Settings.vue 校验拦截
`handleSubmit` 中 `await formRef.value.validate()` 加 try-catch，校验失败直接 return，不再进入 API 调用。

### H-2：移动端操作按钮
添加 `expandedId` 状态和 `toggleExpand()` 方法。移动端显示 `⋯` 展开按钮，点击后展开操作栏（重命名/置顶/提示词/归档/删除）。桌面端仍使用 hover 展示。

### H-3：Vue Router 导航
`goSettings()` 改用 `router.push('/settings')`，保持 SPA 状态不丢失。

### H-4：sendMessage 错误处理
`streamChat` 失败时：
- 移除残留的空 assistant 消息
- `ElMessage.error` 提示用户
- AI 未返回内容时也移除空消息并提示

### H-5：归档搜索
搜索逻辑改为从 `chatStore.conversations` 出发，按当前归档模式过滤后再搜索关键词，确保归档模式下可搜索归档会话。

### H-7：marked 重复配置
删除 `<script setup>` 中的 `marked.setOptions` 调用，仅保留模块级 `<script>` 块中的单次配置。

### H-8：归档数量
`archive-toggle` 按钮文本改为"已归档 (N)"，显示当前归档会话数量。

### H-11：复制渲染文本
AI 消息复制时取 `.content` 元素的 `innerText`（渲染后文本），用户消息仍复制原始内容。
