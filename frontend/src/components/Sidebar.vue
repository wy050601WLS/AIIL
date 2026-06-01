<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'

const chatStore = useChatStore()
const userStore = useUserStore()
const themeStore = useThemeStore()

const editingId = ref(null)
const editTitle = ref('')

async function handleNew() {
  await chatStore.newConversation()
}

async function handleSelect(id) {
  if (editingId.value === id) return
  await chatStore.selectConversation(id)
}

function handleLogout() {
  userStore.logout()
}

function goSettings() {
  window.location.href = '/settings'
}

function startRename(conv) {
  editingId.value = conv.id
  editTitle.value = conv.title
}

async function confirmRename(conv) {
  const title = editTitle.value.trim()
  if (!title) {
    editingId.value = null
    return
  }
  if (title !== conv.title) {
    await chatStore.rename(conv.id, title)
  }
  editingId.value = null
}

async function handleDelete(conv) {
  try {
    await ElMessageBox.confirm(`确定删除会话「${conv.title}」？`, '删除会话', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await chatStore.remove(conv.id)
    ElMessage.success('会话已删除')
  } catch {
    // cancelled
  }
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
        <template v-if="editingId === conv.id">
          <input
            v-model="editTitle"
            class="edit-input"
            @blur="confirmRename(conv)"
            @keyup.enter="confirmRename(conv)"
            @keyup.escape="editingId = null"
            autofocus
          />
        </template>
        <template v-else>
          <span class="conv-title">{{ conv.title }}</span>
          <div class="conv-actions">
            <el-button text size="small" class="action-btn" @click.stop="startRename(conv)">重命名</el-button>
            <el-button text size="small" class="action-btn delete-btn" @click.stop="handleDelete(conv)">删除</el-button>
          </div>
        </template>
      </div>
      <div v-if="chatStore.conversations.length === 0" class="empty-hint">
        暂无会话，点击上方开始
      </div>
    </div>

    <div class="sidebar-footer">
      <span class="username">{{ userStore.username }}</span>
      <div class="footer-actions">
        <el-button text size="small" @click="themeStore.toggle">
          {{ themeStore.theme === 'dark' ? '浅色' : '深色' }}
        </el-button>
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
  position: relative;
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

.conv-actions {
  display: none;
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  gap: 2px;
}

.conv-item:hover .conv-actions {
  display: flex;
}

.conv-item:hover .conv-title {
  padding-right: 100px;
}

.action-btn {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 4px;
  height: auto;
}

.action-btn:hover {
  color: var(--text-primary);
}

.delete-btn:hover {
  color: var(--danger);
}

.edit-input {
  width: 100%;
  background: var(--bg-tertiary);
  border: 1px solid var(--accent);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 14px;
  padding: 2px 6px;
  outline: none;
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
