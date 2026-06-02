<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import SystemPromptDialog from './SystemPromptDialog.vue'

defineProps({
  visible: { type: Boolean, default: true },
})
const emit = defineEmits(['close'])

const chatStore = useChatStore()
const userStore = useUserStore()
const themeStore = useThemeStore()
const router = useRouter()

const editingId = ref(null)
const editTitle = ref('')
const searchQuery = ref('')
const promptDialogVisible = ref(false)
const promptConvId = ref(null)
const promptConvPrompt = ref('')
const expandedId = ref(null)

const searchFiltered = computed(() => {
  if (!searchQuery.value.trim()) return null
  const q = searchQuery.value.toLowerCase()
  let list = chatStore.conversations
  if (!chatStore.showArchived) {
    list = list.filter(c => !c.archived)
  } else {
    list = list.filter(c => c.archived)
  }
  return list.filter(c => c.title.toLowerCase().includes(q))
})

const pinnedList = computed(() => {
  const src = searchFiltered.value ?? chatStore.filteredConversations
  return src.filter(c => c.pinned)
})

const normalList = computed(() => {
  const src = searchFiltered.value ?? chatStore.filteredConversations
  return src.filter(c => !c.pinned)
})

const archivedCount = computed(() => chatStore.conversations.filter(c => c.archived).length)

async function handleNew() {
  await chatStore.newConversation()
  emit('close')
}

async function handleSelect(id) {
  if (editingId.value === id) return
  if (expandedId.value === id) {
    expandedId.value = null
    return
  }
  expandedId.value = null
  await chatStore.selectConversation(id)
  emit('close')
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function handleLogout() {
  userStore.logout()
}

function goSettings() {
  emit('close')
  router.push('/settings')
}

function goCards() {
  emit('close')
  router.push('/cards')
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

async function handlePin(conv) {
  await chatStore.pin(conv.id)
  ElMessage.success(conv.pinned ? '已取消置顶' : '已置顶')
}

async function handleArchive(conv) {
  await chatStore.archive(conv.id)
  ElMessage.success(conv.archived ? '已取消归档' : '已归档')
}

function openPromptDialog(conv) {
  promptConvId.value = conv.id
  promptConvPrompt.value = conv.system_prompt || ''
  promptDialogVisible.value = true
}

async function savePrompt(prompt) {
  await chatStore.updateSystemPrompt(promptConvId.value, prompt)
  ElMessage.success('系统提示词已保存')
}
</script>

<template>
  <div class="sidebar-overlay" :class="{ visible }" @click="emit('close')"></div>
  <aside class="sidebar" :class="{ visible }">
    <div class="sidebar-header">
      <h2 class="logo">AI 智慧学习</h2>
      <el-button type="primary" text class="new-btn" @click="handleNew">
        + 新对话
      </el-button>
    </div>

    <div class="search-box">
      <input
        v-model="searchQuery"
        class="search-input"
        placeholder="搜索会话..."
      />
    </div>

    <div class="archive-toggle">
      <el-button text size="small" @click="chatStore.toggleShowArchived">
        {{ chatStore.showArchived ? '返回会话' : `已归档${archivedCount > 0 ? ` (${archivedCount})` : ''}` }}
      </el-button>
    </div>

    <div class="conversation-list">
      <!-- 置顶会话 -->
      <template v-if="pinnedList.length > 0">
        <div class="group-label">置顶</div>
        <div
          v-for="conv in pinnedList"
          :key="conv.id"
          class="conv-item"
          :class="{ active: conv.id === chatStore.currentId, expanded: expandedId === conv.id }"
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
            <span class="pin-icon">📌</span>
            <span class="conv-title">{{ conv.title }}</span>
            <button class="expand-btn" @click.stop="toggleExpand(conv.id)">⋯</button>
            <div class="conv-actions">
              <el-button text size="small" class="action-btn" @click.stop="startRename(conv)">重命名</el-button>
              <el-button text size="small" class="action-btn" @click.stop="handlePin(conv)">取消置顶</el-button>
              <el-button text size="small" class="action-btn" @click.stop="openPromptDialog(conv)">提示词</el-button>
              <el-button text size="small" class="action-btn" @click.stop="handleArchive(conv)">归档</el-button>
              <el-button text size="small" class="action-btn delete-btn" @click.stop="handleDelete(conv)">删除</el-button>
            </div>
          </template>
        </div>
      </template>

      <!-- 普通会话 -->
      <template v-if="normalList.length > 0">
        <div v-if="pinnedList.length > 0" class="group-label">全部会话</div>
        <div
          v-for="conv in normalList"
          :key="conv.id"
          class="conv-item"
          :class="{ active: conv.id === chatStore.currentId, expanded: expandedId === conv.id }"
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
            <button class="expand-btn" @click.stop="toggleExpand(conv.id)">⋯</button>
            <div class="conv-actions">
              <el-button text size="small" class="action-btn" @click.stop="startRename(conv)">重命名</el-button>
              <el-button text size="small" class="action-btn" @click.stop="handlePin(conv)">置顶</el-button>
              <el-button text size="small" class="action-btn" @click.stop="openPromptDialog(conv)">提示词</el-button>
              <el-button text size="small" class="action-btn" @click.stop="handleArchive(conv)">归档</el-button>
              <el-button text size="small" class="action-btn delete-btn" @click.stop="handleDelete(conv)">删除</el-button>
            </div>
          </template>
        </div>
      </template>

      <div v-if="pinnedList.length === 0 && normalList.length === 0" class="empty-hint">
        {{ chatStore.showArchived ? '没有已归档的会话' : '暂无会话，点击上方开始' }}
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="user-info">
        <span v-if="userStore.avatar" class="user-avatar">{{ userStore.avatar }}</span>
        <span class="username">{{ userStore.displayName }}</span>
      </div>
      <div class="footer-actions">
        <el-button text size="small" @click="goCards">卡片</el-button>
        <el-button text size="small" @click="themeStore.toggle">
          {{ themeStore.theme === 'dark' ? '浅色' : '深色' }}
        </el-button>
        <el-button text size="small" @click="goSettings">设置</el-button>
        <el-button text size="small" @click="handleLogout">退出</el-button>
      </div>
    </div>
  </aside>

  <SystemPromptDialog
    v-model:visible="promptDialogVisible"
    :initial-prompt="promptConvPrompt"
    @save="savePrompt"
  />
</template>

<style scoped>
.sidebar-overlay {
  display: none;
}

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

.search-box {
  padding: 8px 16px 0;
}

.search-input {
  width: 100%;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  padding: 6px 10px;
  outline: none;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-input:focus {
  border-color: var(--accent);
}

.archive-toggle {
  padding: 4px 16px;
  display: flex;
  justify-content: flex-end;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.group-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 12px 4px;
  font-weight: 600;
}

.conv-item {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-bottom: 2px;
  transition: background 0.15s;
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
}

.conv-item:hover {
  background: var(--bg-hover);
}

.conv-item.active {
  background: var(--accent-bg);
  border-left: 3px solid var(--accent);
}

.pin-icon {
  font-size: 12px;
  flex-shrink: 0;
}

.conv-title {
  font-size: 14px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
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
  background: var(--bg-secondary);
  padding: 2px 4px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow);
}

.conv-item:hover .conv-actions {
  display: flex;
}

.action-btn {
  font-size: 11px;
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

.expand-btn {
  display: none;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 16px;
  cursor: pointer;
  padding: 2px 4px;
  flex-shrink: 0;
  line-height: 1;
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
  flex: 1;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  font-size: 20px;
}

.username {
  font-size: 14px;
  color: var(--text-secondary);
}

.footer-actions {
  display: flex;
  gap: 4px;
}

/* 移动端 */
@media (max-width: 768px) {
  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 100;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
  }

  .sidebar-overlay.visible {
    opacity: 1;
    pointer-events: auto;
  }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 101;
    transform: translateX(-100%);
    transition: transform 0.2s;
    width: 280px;
    min-width: 280px;
  }

  .sidebar.visible {
    transform: translateX(0);
  }

  .expand-btn {
    display: block;
  }

  .conv-item:hover .conv-actions {
    display: none;
  }

  .conv-item.expanded .conv-actions {
    display: flex;
    position: static;
    transform: none;
    box-shadow: none;
    background: transparent;
    padding: 4px 0 0;
    flex-wrap: wrap;
    gap: 4px;
  }
}
</style>
