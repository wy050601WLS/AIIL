/**
 * 对话状态管理 Store
 *
 * 管理会话列表、当前会话、消息列表、AI 模型、流式对话状态。
 * 核心流程：sendMessage → 乐观更新 → streamChat（SSE） → 逐 token 追加。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createConversation, getConversations, getMessages, streamChat,
  renameConversation, deleteConversation, getModels, exportConversation,
  editMessage as editMessageApi, deleteMessage as deleteMessageApi,
  pinConversation as pinConversationApi, archiveConversation as archiveConversationApi,
} from '../api/chat'
import { useUserStore } from './user'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])        // 会话列表
  const currentId = ref(null)          // 当前选中的会话 ID
  const messages = ref([])             // 当前会话的消息列表
  const loading = ref(false)           // AI 是否正在生成回复
  const models = ref([])               // 可用的 AI 模型列表
  const currentModel = ref(localStorage.getItem('model') || '')  // 当前选中的模型
  const showArchived = ref(false)      // 是否显示已归档会话
  const hasMore = ref(false)           // 是否还有更多历史消息可加载
  const loadingMore = ref(false)       // 是否正在加载更多消息
  let abortController = null           // 用于中断 SSE 流的 AbortController

  /** 根据 showArchived 过滤会话列表 */
  const filteredConversations = computed(() => {
    let list = conversations.value
    if (!showArchived.value) {
      list = list.filter(c => !c.archived)
    } else {
      list = list.filter(c => c.archived)
    }
    return list
  })

  /** 置顶会话列表 */
  const pinnedConversations = computed(() => filteredConversations.value.filter(c => c.pinned))
  /** 普通（非置顶）会话列表 */
  const normalConversations = computed(() => filteredConversations.value.filter(c => !c.pinned))

  /** 加载可用的 AI 模型列表，首次加载时应用用户的默认模型偏好 */
  async function loadModels() {
    try {
      const { data } = await getModels()
      models.value = data.models
      if (!currentModel.value) {
        const userStore = useUserStore()
        const preferred = userStore.preferences?.defaultModel
        if (preferred && data.models.some(m => m.id === preferred)) {
          currentModel.value = preferred
        } else if (data.default) {
          currentModel.value = data.default
        }
      }
    } catch {
      // 加载失败静默处理
    }
  }

  /** 切换当前 AI 模型并持久化到 localStorage */
  function setModel(modelId) {
    currentModel.value = modelId
    localStorage.setItem('model', modelId)
  }

  /** 加载用户的会话列表 */
  async function loadConversations() {
    try {
      const { data } = await getConversations()
      conversations.value = data
    } catch {
      ElMessage.error('加载会话列表失败')
    }
  }

  /** 创建新会话并自动选中 */
  async function newConversation(title = '新对话') {
    try {
      const { data } = await createConversation(title)
      conversations.value.unshift(data)
      currentId.value = data.id
      messages.value = []
      return data
    } catch {
      ElMessage.error('创建会话失败')
      return null
    }
  }

  /** 选中指定会话并加载最新的 50 条消息 */
  async function selectConversation(id) {
    currentId.value = id
    const { data } = await getMessages(id, 0, 50)
    messages.value = data.messages
    hasMore.value = data.total > 50
  }

  /** 加载更多历史消息（向上滚动时触发） */
  async function loadMoreMessages() {
    if (!currentId.value || loadingMore.value || !hasMore.value) return
    loadingMore.value = true
    try {
      const { data } = await getMessages(currentId.value, messages.value.length, 50)
      // 旧消息插入到列表头部
      messages.value = [...data.messages, ...messages.value]
      hasMore.value = messages.value.length < data.total
    } finally {
      loadingMore.value = false
    }
  }

  /**
   * 发送消息并接收 AI 流式回复
   *
   * 流程：
   * 1. 若无当前会话，自动创建（标题取自消息前 20 字）
   * 2. 乐观更新：立即在消息列表中添加用户消息和空的 AI 占位
   * 3. 通过 streamChat 发起 SSE 请求，逐 token 追加到 AI 占位消息
   * 4. 完成后检查 AI 是否有回复，无回复则移除占位并提示错误
   */
  async function sendMessage(content, images) {
    if (!currentId.value) {
      await newConversation((content || '').slice(0, 20) || '图片对话')
    }

    // 自动更新会话标题：若标题仍为「新对话」，用消息前 30 字更新（与后端同步）
    const conv = conversations.value.find(c => c.id === currentId.value)
    if (conv && conv.title === '新对话' && content) {
      conv.title = content.slice(0, 30).replace(/\n/g, ' ').trim() || '图片对话'
    }

    const hasImages = images && images.length > 0
    messages.value.push({
      role: 'user',
      content,
      images: hasImages ? images : undefined,
      created_at: new Date().toISOString(),
    })

    const idx = messages.value.length
    messages.value.push({ role: 'assistant', content: '', created_at: new Date().toISOString() })
    loading.value = true
    abortController = new AbortController()

    try {
      await streamChat(
        currentId.value,
        content,
        (token) => { messages.value[idx].content += token },
        () => { loading.value = false },
        currentModel.value || undefined,
        false,
        abortController.signal,
        hasImages ? images : undefined,
      )
      // AI 未返回任何内容时移除空占位消息
      if (!messages.value[idx].content) {
        messages.value.splice(idx, 1)
        ElMessage.error('AI 未返回回复，请重试')
      }
    } catch {
      if (!abortController.signal.aborted) {
        messages.value.splice(idx, 1)
        ElMessage.error('请求失败，请检查网络后重试')
      }
      loading.value = false
    } finally {
      abortController = null
    }
  }

  /** 重新生成最后一条 AI 回复 */
  async function regenerate() {
    if (!currentId.value || loading.value) return
    const lastUserIdx = [...messages.value].reverse().findIndex(m => m.role === 'user')
    if (lastUserIdx === -1) return
    const lastUserContent = messages.value[messages.value.length - 1 - lastUserIdx].content
    // 暂存旧的 AI 回复，失败时恢复
    let oldMessage = null
    if (messages.value[messages.value.length - 1].role === 'assistant') {
      oldMessage = messages.value.pop()
    }
    const idx = messages.value.length
    messages.value.push({ role: 'assistant', content: '', created_at: new Date().toISOString() })
    loading.value = true
    abortController = new AbortController()
    try {
      await streamChat(
        currentId.value,
        lastUserContent,
        (token) => { messages.value[idx].content += token },
        () => { loading.value = false },
        currentModel.value || undefined,
        true,
        abortController.signal,
      )
      // 流式完成但无内容，恢复旧消息
      if (!messages.value[idx].content && oldMessage) {
        messages.value.splice(idx, 1)
        messages.value.push(oldMessage)
        ElMessage.error('重新生成失败，已恢复原回复')
      }
    } catch {
      // 失败时恢复旧消息
      if (oldMessage) {
        messages.value.splice(idx, 1)
        messages.value.push(oldMessage)
      }
      loading.value = false
    } finally {
      abortController = null
    }
  }

  /** 中断正在进行的 SSE 流式对话 */
  function stopStreaming() {
    if (abortController) {
      abortController.abort()
      abortController = null
      loading.value = false
    }
  }

  /** 重命名会话标题 */
  async function rename(id, title) {
    try {
      const { data } = await renameConversation(id, title)
      const conv = conversations.value.find(c => c.id === id)
      if (conv) conv.title = data.title
    } catch {
      ElMessage.error('重命名失败')
    }
  }

  /** 删除会话（从列表中移除，若是当前会话则清空消息） */
  async function remove(id) {
    try {
      await deleteConversation(id)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (currentId.value === id) {
        currentId.value = null
        messages.value = []
      }
    } catch {
      ElMessage.error('删除会话失败')
    }
  }

  /** 导出当前会话为 Markdown 文件 */
  async function exportCurrent() {
    if (!currentId.value) return
    try {
      await exportConversation(currentId.value)
    } catch (err) {
      ElMessage.error(err.message || '导出失败')
    }
  }

  /** 编辑消息内容并同步更新本地状态 */
  async function editMessage(messageId, content) {
    try {
      await editMessageApi(messageId, content)
      const msg = messages.value.find(m => m.id === messageId)
      if (msg) msg.content = content
    } catch {
      ElMessage.error('编辑消息失败')
    }
  }

  /** 删除消息并从本地列表移除 */
  async function deleteMessage(messageId) {
    try {
      await deleteMessageApi(messageId)
      messages.value = messages.value.filter(m => m.id !== messageId)
    } catch {
      ElMessage.error('删除消息失败')
    }
  }

  /** 切换会话置顶状态 */
  async function pin(id) {
    try {
      const { data } = await pinConversationApi(id)
      const conv = conversations.value.find(c => c.id === id)
      if (conv) conv.pinned = data.pinned
    } catch {
      ElMessage.error('操作失败')
    }
  }

  /** 切换会话归档状态 */
  async function archive(id) {
    try {
      const { data } = await archiveConversationApi(id)
      const conv = conversations.value.find(c => c.id === id)
      if (conv) conv.archived = data.archived
    } catch {
      ElMessage.error('操作失败')
    }
  }

  /** 切换显示/隐藏已归档会话 */
  function toggleShowArchived() {
    showArchived.value = !showArchived.value
  }

  return {
    conversations, currentId, messages, loading, models, currentModel,
    showArchived, filteredConversations, pinnedConversations, normalConversations,
    hasMore, loadingMore,
    loadConversations, newConversation, selectConversation, sendMessage,
    loadMoreMessages,
    rename, remove, regenerate, stopStreaming, loadModels, setModel, exportCurrent,
    editMessage, deleteMessage, pin, archive, toggleShowArchived,
  }
})
