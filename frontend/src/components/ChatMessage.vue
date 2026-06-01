<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { ElMessage } from 'element-plus'

const props = defineProps({
  role: { type: String, required: true },
  content: { type: String, default: '' },
  isLast: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['regenerate'])

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

const rendered = computed(() => {
  if (props.role === 'user') return null
  return marked.parse(props.content || '')
})

function copyContent() {
  navigator.clipboard.writeText(props.content).then(() => {
    ElMessage.success('已复制')
  })
}
</script>

<template>
  <div class="message-row" :class="role">
    <div class="avatar">
      {{ role === 'user' ? '你' : 'AI' }}
    </div>
    <div class="bubble">
      <div v-if="role === 'user'" class="content" v-text="content"></div>
      <div v-else class="content markdown-body" v-html="rendered"></div>
      <div v-if="!loading && content" class="msg-actions">
        <el-button text size="small" class="msg-action-btn" @click="copyContent">复制</el-button>
        <el-button v-if="role === 'assistant' && isLast" text size="small" class="msg-action-btn" @click="emit('regenerate')">重新生成</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-row {
  display: flex;
  gap: 12px;
  padding: 8px 24px;
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

.user .avatar {
  background: var(--user-bubble);
  color: #fff;
}

.assistant .avatar {
  background: var(--bg-tertiary);
  color: var(--accent);
  border: 1px solid var(--border);
}

.bubble {
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  max-width: 70%;
  line-height: 1.6;
  font-size: 15px;
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
</style>
