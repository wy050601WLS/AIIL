<script setup>
defineProps({
  role: { type: String, required: true },
  content: { type: String, default: '' },
})
</script>

<template>
  <div class="message-row" :class="role">
    <div class="avatar">
      {{ role === 'user' ? '你' : 'AI' }}
    </div>
    <div class="bubble">
      <div class="content" v-text="content"></div>
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
  white-space: pre-wrap;
}

.user .bubble {
  background: var(--user-bubble);
  color: #fff;
  border-bottom-right-radius: var(--radius-sm);
}

.assistant .bubble {
  background: var(--assistant-bubble);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-bottom-left-radius: var(--radius-sm);
}
</style>
