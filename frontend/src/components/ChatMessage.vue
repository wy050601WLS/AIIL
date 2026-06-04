<!--
  ChatMessage 组件 — 消息气泡

  功能：显示用户/AI 消息，支持 Markdown 渲染、代码高亮、图片预览、操作按钮
  Props: role, content, images, isLast, loading, createdAt, fontSize, density
  Events: regenerate — 重新生成, edit — 编辑消息, delete — 删除消息, saveCard — 提取卡片
-->
<script>
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml'
import java from 'highlight.js/lib/languages/java'
import cpp from 'highlight.js/lib/languages/cpp'
import csharp from 'highlight.js/lib/languages/csharp'
import sql from 'highlight.js/lib/languages/sql'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import markdown from 'highlight.js/lib/languages/markdown'
import go from 'highlight.js/lib/languages/go'
import rust from 'highlight.js/lib/languages/rust'
import yaml from 'highlight.js/lib/languages/yaml'
import DOMPurify from 'dompurify'

// 注册常用语言（仅打包需要的语言，约 150KB 替代全量 1MB+）
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('java', java)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('c', cpp)
hljs.registerLanguage('csharp', csharp)
hljs.registerLanguage('cs', csharp)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('shell', bash)
hljs.registerLanguage('json', json)
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('md', markdown)
hljs.registerLanguage('go', go)
hljs.registerLanguage('rust', rust)
hljs.registerLanguage('rs', rust)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('yml', yaml)

// 配置 Markdown 渲染器：使用 marked-highlight 扩展启用代码高亮
marked.use(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value
      }
      // 未知语言不使用 highlightAuto（避免遍历所有语言）
      return code
    },
  }),
)

// 启用换行转 <br> 和 GFM 语法
marked.use({ breaks: true, gfm: true })
</script>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const props = defineProps({
  role: { type: String, required: true },         // 消息角色：'user' 或 'assistant'
  content: { type: String, default: '' },          // 消息文本内容
  images: { type: Array, default: () => [] },      // 图片列表（base64 dataUrl）
  isLast: { type: Boolean, default: false },       // 是否为最后一条消息（显示重新生成按钮）
  loading: { type: Boolean, default: false },      // AI 是否正在生成
  createdAt: { type: String, default: '' },        // 消息创建时间
  fontSize: { type: Number, default: 15 },         // 字体大小（来自用户偏好）
  density: { type: String, default: 'normal' },    // 消息密度：compact/normal/relaxed
})

const previewImage = ref(null)  // 全屏预览的图片 URL

// 根据密度设置消息行间距
const densityMap = { compact: 4, normal: 8, relaxed: 14 }
const rowStyle = computed(() => {
  const v = densityMap[props.density] ?? 8
  return { '--row-gap': v + 'px' }
})

const emit = defineEmits(['regenerate', 'edit', 'delete', 'saveCard'])
const bubbleRef = ref(null)

// 流式输出时 Markdown 渲染防抖：每 150ms 最多重新解析一次，避免每个 token 都触发全量 parse
const renderedContent = ref('')
let renderTimer = null

watch(() => props.content, (val) => {
  if (props.role === 'user') return
  if (renderTimer) clearTimeout(renderTimer)
  // 如果内容为空或加载结束，立即渲染
  if (!val || !props.loading) {
    renderedContent.value = DOMPurify.sanitize(marked.parse(val || ''))
    return
  }
  renderTimer = setTimeout(() => {
    renderedContent.value = DOMPurify.sanitize(marked.parse(val))
  }, 150)
}, { immediate: true })

const rendered = computed(() => {
  if (props.role === 'user') return null
  return renderedContent.value
})

/** 头像显示：用户显示 emoji 头像或「你」，AI 显示「AI」 */
const avatarDisplay = computed(() => {
  if (props.role === 'user') return userStore.avatar || '你'
  return 'AI'
})

/** 格式化消息时间为 HH:MM */
const timeDisplay = computed(() => {
  if (!props.createdAt) return ''
  const d = new Date(props.createdAt)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
})

/** 气泡字体大小样式（跟随用户偏好） */
const bubbleStyle = computed(() => ({
  fontSize: props.fontSize + 'px',
}))

/** 给代码块注入复制按钮 */
function injectCopyButtons() {
  if (!bubbleRef.value) return
  const pres = bubbleRef.value.querySelectorAll('pre')
  pres.forEach(pre => {
    if (pre.querySelector('.code-copy-btn')) return
    pre.style.position = 'relative'
    const btn = document.createElement('button')
    btn.className = 'code-copy-btn'
    btn.textContent = '复制'
    btn.addEventListener('click', () => {
      const code = pre.querySelector('code')?.textContent || pre.textContent
      navigator.clipboard.writeText(code).then(() => {
        btn.textContent = '已复制'
        setTimeout(() => { btn.textContent = '复制' }, 1500)
      })
    })
    pre.appendChild(btn)
  })
}

// AI 消息内容变化时重新注入复制按钮（防抖，避免流式输出时频繁 DOM 操作）
let copyBtnTimer = null
watch(() => props.content, () => {
  if (props.role !== 'assistant') return
  if (copyBtnTimer) clearTimeout(copyBtnTimer)
  copyBtnTimer = setTimeout(() => {
    nextTick(injectCopyButtons)
  }, 300)
})

// AI 加载结束时立即渲染最终内容并注入复制按钮
watch(() => props.loading, (val) => {
  if (val || props.role !== 'assistant') return
  if (renderTimer) clearTimeout(renderTimer)
  renderedContent.value = DOMPurify.sanitize(marked.parse(props.content || ''))
  nextTick(injectCopyButtons)
})

/** 复制消息内容（AI 消息复制渲染后的纯文本） */
function copyContent() {
  let text = props.content
  if (props.role === 'assistant' && bubbleRef.value) {
    text = bubbleRef.value.querySelector('.content')?.innerText || props.content
  }
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制')
  })
}
</script>

<template>
  <div class="message-row" :class="role" :style="rowStyle">
    <div class="avatar" :class="role">
      {{ avatarDisplay }}
    </div>
    <div ref="bubbleRef" class="bubble" :style="bubbleStyle">
      <div v-if="images && images.length > 0" class="msg-images">
        <img
          v-for="(img, i) in images"
          :key="i"
          :src="img"
          class="msg-img"
          @click="previewImage = img"
        />
      </div>
      <div v-if="role === 'user'" class="content" v-text="content"></div>
      <div v-else class="content markdown-body" v-html="rendered"></div>
      <div v-if="loading && !content && role === 'assistant'" class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
      <div v-if="!loading && content" class="msg-actions">
        <el-button text size="small" class="msg-action-btn" @click="copyContent">复制</el-button>
        <el-button v-if="role === 'user'" text size="small" class="msg-action-btn" @click="emit('edit')">编辑</el-button>
        <el-button text size="small" class="msg-action-btn delete-msg-btn" @click="emit('delete')">删除</el-button>
        <el-button v-if="role === 'assistant'" text size="small" class="msg-action-btn" @click="emit('saveCard')">提取卡片</el-button>
        <el-button v-if="role === 'assistant' && isLast" text size="small" class="msg-action-btn" @click="emit('regenerate')">重新生成</el-button>
      </div>
      <div v-if="timeDisplay" class="time-stamp">{{ timeDisplay }}</div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="previewImage" class="img-preview-overlay" @click="previewImage = null">
      <img :src="previewImage" class="img-preview-full" />
    </div>
  </Teleport>
</template>

<style scoped>
.message-row {
  display: flex;
  gap: 12px;
  padding: var(--row-gap, 8px) 24px;
  max-width: 800px;
  margin: 0 auto;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.avatar.user {
  background: var(--user-bubble);
  color: #fff;
  font-size: 18px;
}

.avatar.assistant {
  background: var(--bg-tertiary);
  color: var(--accent);
  border: 1px solid var(--border);
}

.bubble {
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  max-width: 70%;
  line-height: 1.6;
  word-break: break-word;
  position: relative;
}

.user .bubble {
  background: var(--user-bubble);
  color: #fff;
  border-bottom-right-radius: var(--radius-sm);
  white-space: pre-wrap;
}

.assistant .bubble {
  background: var(--assistant-bubble);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-bottom-left-radius: var(--radius-sm);
}

.msg-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.15s;
}

.bubble:hover .msg-actions {
  opacity: 1;
}

.msg-action-btn {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 6px;
  height: auto;
}

.msg-action-btn:hover {
  color: var(--accent);
}

.delete-msg-btn:hover {
  color: var(--danger);
}

.time-stamp {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
  opacity: 0.7;
}

.msg-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.msg-img {
  max-width: 200px;
  max-height: 200px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  object-fit: cover;
  border: 1px solid var(--border);
}

.img-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.img-preview-full {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: var(--radius-sm);
}

/* Markdown 样式 */
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 16px 0 8px;
  font-weight: 600;
}
.markdown-body :deep(h1) { font-size: 1.4em; }
.markdown-body :deep(h2) { font-size: 1.2em; }
.markdown-body :deep(h3) { font-size: 1.1em; }

.markdown-body :deep(p) {
  margin: 8px 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(code) {
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.9em;
}

.markdown-body :deep(pre) {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  overflow-x: auto;
  margin: 12px 0;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 0.85em;
  line-height: 1.5;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid var(--accent);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text-secondary);
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 12px 0;
  width: 100%;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid var(--border);
  padding: 6px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: var(--bg-tertiary);
  font-weight: 600;
}

.markdown-body :deep(a) {
  color: var(--accent);
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 16px 0;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0.32s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* 代码块复制按钮 */
.markdown-body :deep(pre) {
  position: relative;
}

.markdown-body :deep(.code-copy-btn) {
  position: absolute;
  top: 6px;
  right: 6px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-muted);
  font-size: 11px;
  padding: 2px 8px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
  font-family: inherit;
}

.markdown-body :deep(pre:hover .code-copy-btn) {
  opacity: 1;
}

.markdown-body :deep(.code-copy-btn:hover) {
  color: var(--accent);
  border-color: var(--accent);
}

@media (max-width: 768px) {
  .message-row {
    padding: var(--row-gap, 8px) 16px;
    gap: 8px;
  }

  .avatar {
    width: 30px;
    height: 30px;
    min-width: 30px;
    font-size: 11px;
  }

  .avatar.user {
    font-size: 16px;
  }

  .bubble {
    max-width: 85%;
  }
}
</style>
