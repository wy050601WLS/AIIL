<script setup>
import { ref, onMounted } from 'vue'
import { useChatStore } from '../stores/chat'
import Sidebar from '../components/Sidebar.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'

const chatStore = useChatStore()
const sidebarVisible = ref(false)

onMounted(() => {
  chatStore.loadConversations()
  chatStore.loadModels()
})

async function handleSend(content) {
  await chatStore.sendMessage(content)
}

async function handleRegenerate() {
  await chatStore.regenerate()
}
</script>

<template>
  <div class="chat-layout">
    <Sidebar :visible="sidebarVisible" @close="sidebarVisible = false" />

    <main class="chat-main">
      <div class="chat-header">
        <div class="header-left">
          <el-button class="menu-btn" text @click="sidebarVisible = true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12h18M3 6h18M3 18h18" />
            </svg>
          </el-button>
          <el-select
            v-if="chatStore.models.length > 0"
            :model-value="chatStore.currentModel"
            size="small"
            class="model-select"
            @update:model-value="chatStore.setModel"
          >
            <el-option
              v-for="m in chatStore.models"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            />
          </el-select>
        </div>
        <div class="header-right">
          <el-button
            v-if="chatStore.currentId"
            text
            size="small"
            @click="chatStore.exportCurrent"
          >导出</el-button>
        </div>
      </div>

      <div class="messages-area">
        <div v-if="chatStore.messages.length === 0" class="welcome">
          <h2>有什么可以帮你的？</h2>
          <p>输入你的问题，AI 将为你解答</p>
        </div>

        <ChatMessage
          v-for="(msg, i) in chatStore.messages"
          :key="i"
          :role="msg.role"
          :content="msg.content"
          :is-last="i === chatStore.messages.length - 1"
          :loading="chatStore.loading"
          @regenerate="handleRegenerate"
        />
      </div>

      <ChatInput :loading="chatStore.loading" @send="handleSend" />
    </main>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-btn {
  display: none;
  color: var(--text-secondary);
  padding: 4px;
}

.model-select {
  width: 180px;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
}

.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.welcome h2 {
  font-size: 24px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.welcome p {
  font-size: 14px;
}

/* 移动端 */
@media (max-width: 768px) {
  .menu-btn {
    display: block;
  }

  .model-select {
    width: 140px;
  }

  .messages-area {
    padding: 16px 0;
  }
}
</style>
