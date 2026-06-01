<script setup>
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'

const chatStore = useChatStore()
const userStore = useUserStore()

async function handleNew() {
  await chatStore.newConversation()
}

async function handleSelect(id) {
  await chatStore.selectConversation(id)
}

function handleLogout() {
  userStore.logout()
}

function goSettings() {
  window.location.href = '/settings'
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2 class="logo">AI 智慧学习</h2>
      <el-button type="primary" text class="new-btn" @click="handleNew">
        + 新对话
      </el-button>
    </div>

    <div class="conversation-list">
      <div
        v-for="conv in chatStore.conversations"
        :key="conv.id"
        class="conv-item"
        :class="{ active: conv.id === chatStore.currentId }"
        @click="handleSelect(conv.id)"
      >
        <span class="conv-title">{{ conv.title }}</span>
      </div>
      <div v-if="chatStore.conversations.length === 0" class="empty-hint">
        暂无会话，点击上方开始
      </div>
    </div>

    <div class="sidebar-footer">
      <span class="username">{{ userStore.username }}</span>
      <div class="footer-actions">
        <el-button text size="small" @click="goSettings">设置</el-button>
        <el-button text size="small" @click="handleLogout">退出</el-button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  min-width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar-header {
  padding: 20px 16px 12px;
  border-bottom: 1px solid var(--border);
}

.logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.new-btn {
  width: 100%;
  justify-content: center;
  height: 36px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
}

.new-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conv-item {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-bottom: 2px;
  transition: background 0.15s;
}

.conv-item:hover {
  background: var(--bg-hover);
}

.conv-item.active {
  background: var(--accent-bg);
  border-left: 3px solid var(--accent);
}

.conv-title {
  font-size: 14px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.conv-item.active .conv-title {
  color: var(--text-primary);
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  padding: 40px 16px;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.username {
  font-size: 14px;
  color: var(--text-secondary);
}

.footer-actions {
  display: flex;
  gap: 4px;
}
</style>
