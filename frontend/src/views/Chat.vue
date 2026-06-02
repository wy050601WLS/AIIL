<!--
  Chat 视图 — 主对话页面

  布局：左侧 Sidebar + 右侧消息区 + 底部输入框
  功能：AI 流式对话、消息操作（编辑/删除/重新生成/提取卡片）、键盘快捷键
-->
<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'
import { useCardsStore } from '../stores/cards'
import Sidebar from '../components/Sidebar.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'

const chatStore = useChatStore()
const userStore = useUserStore()
const cardsStore = useCardsStore()
const sidebarVisible = ref(false)      // 侧边栏是否显示（移动端控制）
const messagesAreaRef = ref(null)      // 消息区域 DOM 引用（用于自动滚动）

// 从用户偏好中读取字体大小和消息密度
const fontSize = computed(() => userStore.preferences?.fontSize || 15)
const density = computed(() => userStore.preferences?.messageDensity || 'normal')

/** 滚动到消息列表底部 */
function scrollToBottom() {
  nextTick(() => {
    if (messagesAreaRef.value) {
      messagesAreaRef.value.scrollTop = messagesAreaRef.value.scrollHeight
    }
  })
}

/** 滚动事件处理：滚动到顶部时加载更多历史消息 */
async function handleScroll() {
  const el = messagesAreaRef.value
  if (!el || !chatStore.hasMore || chatStore.loadingMore) return
  // 距顶部 50px 时触发加载
  if (el.scrollTop < 50) {
    const prevHeight = el.scrollHeight
    await chatStore.loadMoreMessages()
    // 保持滚动位置不变（加载旧消息后页面高度增加，需补偿偏移）
    nextTick(() => {
      el.scrollTop = el.scrollHeight - prevHeight
    })
  }
}

// 监听消息数量变化和最后一条消息内容变化，自动滚动到底部
watch(() => chatStore.messages.length, (newLen, oldLen) => {
  // 新消息追加到底部时才自动滚动（加载历史消息时不滚动）
  if (newLen > oldLen && !chatStore.loadingMore) {
    scrollToBottom()
  }
})
watch(() => chatStore.messages[chatStore.messages.length - 1]?.content, scrollToBottom)

onMounted(() => {
  chatStore.loadConversations()
  chatStore.loadModels()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

/** 全局键盘快捷键处理 */
function handleKeydown(e) {
  // Ctrl+N: 新建对话
  if (e.ctrlKey && e.key === 'n') {
    e.preventDefault()
    chatStore.newConversation()
  }
  // Ctrl+K: 聚焦搜索
  if (e.ctrlKey && e.key === 'k') {
    e.preventDefault()
    sidebarVisible.value = true
    setTimeout(() => {
      document.querySelector('.search-input')?.focus()
    }, 100)
  }
  // Ctrl+Shift+E: 导出当前会话
  if (e.ctrlKey && e.shiftKey && e.key === 'E') {
    e.preventDefault()
    chatStore.exportCurrent()
  }
  // Escape: 关闭侧边栏
  if (e.key === 'Escape') {
    sidebarVisible.value = false
  }
}

/** 发送消息（来自 ChatInput 组件的 send 事件） */
async function handleSend({ content, images }) {
  await chatStore.sendMessage(content, images)
}

/** 重新生成最后一条 AI 回复 */
async function handleRegenerate() {
  await chatStore.regenerate()
}

/** 停止 AI 流式生成 */
function handleStop() {
  chatStore.stopStreaming()
}

/** 编辑消息（弹出输入框，保存后同步更新） */
async function handleEdit(msg) {
  try {
    const { value } = await ElMessageBox.prompt('编辑消息内容', '编辑消息', {
      inputValue: msg.content,
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputValidator: (val) => val.trim() ? true : '消息内容不能为空',
    })
    if (value && value !== msg.content) {
      await chatStore.editMessage(msg.id, value)
      ElMessage.success('消息已更新')
    }
  } catch {
    // 用户取消编辑
  }
}

/** 删除消息（带确认弹窗） */
async function handleDelete(msg) {
  try {
    await ElMessageBox.confirm('确定删除这条消息？', '删除消息', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await chatStore.deleteMessage(msg.id)
  } catch {
    // 用户取消删除
  }
}

/** 将 AI 消息保存为知识卡片 */
async function handleSaveCard(msg) {
  if (!msg.content?.trim()) return
  await cardsStore.addCard(msg.content, `对话 #${chatStore.currentId}`)
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

      <div ref="messagesAreaRef" class="messages-area" @scroll="handleScroll">
        <div v-if="chatStore.loadingMore" class="loading-more">加载更多消息...</div>
        <div v-if="chatStore.messages.length === 0" class="welcome">
          <h2>有什么可以帮你的？</h2>
        </div>

        <ChatMessage
          v-for="(msg, i) in chatStore.messages"
          :key="msg.id || i"
          :role="msg.role"
          :content="msg.content"
          :images="msg.images || []"
          :is-last="i === chatStore.messages.length - 1"
          :loading="chatStore.loading"
          :created-at="msg.created_at"
          :font-size="fontSize"
          :density="density"
          @regenerate="handleRegenerate"
          @edit="() => handleEdit(msg)"
          @delete="() => handleDelete(msg)"
          @save-card="() => handleSaveCard(msg)"
        />
      </div>

      <ChatInput :loading="chatStore.loading" @send="handleSend" @stop="handleStop" />
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

.loading-more {
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  padding: 8px 0;
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
