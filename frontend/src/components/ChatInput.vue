<script setup>
import { ref, nextTick } from 'vue'

defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['send'])
const input = ref('')
const textareaRef = ref(null)

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 150) + 'px'
}

function handleSend() {
  const text = input.value.trim()
  if (!text) return
  emit('send', text)
  input.value = ''
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
  })
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="input-area">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="input"
        class="input-box"
        placeholder="输入你的问题... (Enter 发送，Shift+Enter 换行)"
        rows="1"
        :disabled="loading"
        @input="autoResize"
        @keydown="handleKeydown"
      ></textarea>
      <button
        class="send-btn"
        :disabled="!input.trim() || loading"
        @click="handleSend"
      >
        <span v-if="loading" class="loading-dot">...</span>
        <span v-else>发送</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.input-area {
  padding: 16px 24px 24px;
  background: var(--bg-primary);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 12px 16px;
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--accent);
}

.input-box {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 15px;
  font-family: var(--font-sans);
  line-height: 1.5;
  resize: none;
  min-height: 24px;
  max-height: 150px;
}

.input-box::placeholder {
  color: var(--text-muted);
}

.send-btn {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-dot {
  animation: blink 1.2s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@media (max-width: 768px) {
  .input-area {
    padding: 12px 16px 16px;
  }

  .input-wrapper {
    padding: 10px 12px;
  }

  .input-box {
    font-size: 16px; /* prevent iOS zoom */
  }
}
</style>
