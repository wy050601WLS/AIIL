<script>
import { marked } from 'marked'
import hljs from 'highlight.js'

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})
</script>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const props = defineProps({
  role: { type: String, required: true },
  content: { type: String, default: '' },
  isLast: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  createdAt: { type: String, default: '' },
  fontSize: { type: Number, default: 15 },
  density: { type: String, default: 'normal' },
})

const densityMap = { compact: 4, normal: 8, relaxed: 14 }
const rowStyle = computed(() => {
  const v = densityMap[props.density] ?? 8
  return { '--row-gap': v + 'px' }
})

const emit = defineEmits(['regenerate', 'edit', 'delete'])
const bubbleRef = ref(null)

const rendered = computed(() => {
  if (props.role === 'user') return null
  return marked.parse(props.content || '')
})

const avatarDisplay = computed(() => {
  if (props.role === 'user') return userStore.avatar || '你'
  return 'AI'
})

const timeDisplay = computed(() => {
  if (!props.createdAt) return ''
  const d = new Date(props.createdAt)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
})

const bubbleStyle = computed(() => ({
  fontSize: props.fontSize + 'px',
}))

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
      <div v-if="role === 'user'" class="content" v-text="content"></div>
      <div v-else class="content markdown-body" v-html="rendered"></div>
      <div v-if="!loading && content" class="msg-actions">
        <el-button text size="small" class="msg-action-btn" @click="copyContent">复制</el-button>
        <el-button v-if="role === 'user'" text size="small" class="msg-action-btn" @click="emit('edit')">编辑</el-button>
        <el-button text size="small" class="msg-action-btn delete-msg-btn" @click="emit('delete')">删除</el-button>
        <el-button v-if="role === 'assistant' && isLast" text size="small" class="msg-action-btn" @click="emit('regenerate')">重新生成</el-button>
      </div>
      <div v-if="timeDisplay" class="time-stamp">{{ timeDisplay }}</div>
    </div>
  </div>
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
