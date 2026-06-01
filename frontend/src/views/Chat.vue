<script setup>
import { onMounted } from 'vue'
import { useChatStore } from '../stores/chat'
import Sidebar from '../components/Sidebar.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'

const chatStore = useChatStore()

onMounted(() => {
  chatStore.loadConversations()
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
    <Sidebar />

    <main class="chat-main">
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
</style>
