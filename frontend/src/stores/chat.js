import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createConversation, getConversations, getMessages, streamChat,
  renameConversation, deleteConversation, getModels, exportConversation,
  editMessage as editMessageApi, deleteMessage as deleteMessageApi,
  pinConversation as pinConversationApi, archiveConversation as archiveConversationApi,
  updateSystemPrompt as updateSystemPromptApi,
} from '../api/chat'
import { useUserStore } from './user'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentId = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const models = ref([])
  const currentModel = ref(localStorage.getItem('model') || '')
  const showArchived = ref(false)
  let abortController = null

  const filteredConversations = computed(() => {
    let list = conversations.value
    if (!showArchived.value) {
      list = list.filter(c => !c.archived)
    } else {
      list = list.filter(c => c.archived)
    }
    return list
  })

  const pinnedConversations = computed(() => filteredConversations.value.filter(c => c.pinned))
  const normalConversations = computed(() => filteredConversations.value.filter(c => !c.pinned))

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
      // ignore
    }
  }

  function setModel(modelId) {
    currentModel.value = modelId
    localStorage.setItem('model', modelId)
  }

  async function loadConversations() {
    const { data } = await getConversations()
    conversations.value = data
  }

  async function newConversation(title = '新对话') {
    const { data } = await createConversation(title)
    conversations.value.unshift(data)
    currentId.value = data.id
    messages.value = []
    return data
  }

  async function selectConversation(id) {
    currentId.value = id
    const { data } = await getMessages(id)
    messages.value = data
  }

  async function sendMessage(content, images) {
    if (!currentId.value) {
      await newConversation((content || '').slice(0, 20) || '图片对话')
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

  async function regenerate() {
    if (!currentId.value || loading.value) return
    const lastUserIdx = [...messages.value].reverse().findIndex(m => m.role === 'user')
    if (lastUserIdx === -1) return
    const lastUserContent = messages.value[messages.value.length - 1 - lastUserIdx].content
    if (messages.value[messages.value.length - 1].role === 'assistant') {
      messages.value.pop()
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
    } catch {
      loading.value = false
    } finally {
      abortController = null
    }
  }

  function stopStreaming() {
    if (abortController) {
      abortController.abort()
      abortController = null
      loading.value = false
    }
  }

  async function rename(id, title) {
    const { data } = await renameConversation(id, title)
    const conv = conversations.value.find(c => c.id === id)
    if (conv) conv.title = data.title
  }

  async function remove(id) {
    await deleteConversation(id)
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (currentId.value === id) {
      currentId.value = null
      messages.value = []
    }
  }

  async function exportCurrent() {
    if (!currentId.value) return
    await exportConversation(currentId.value)
  }

  async function editMessage(messageId, content) {
    await editMessageApi(messageId, content)
    const msg = messages.value.find(m => m.id === messageId)
    if (msg) msg.content = content
  }

  async function deleteMessage(messageId) {
    await deleteMessageApi(messageId)
    messages.value = messages.value.filter(m => m.id !== messageId)
  }

  async function pin(id) {
    const { data } = await pinConversationApi(id)
    const conv = conversations.value.find(c => c.id === id)
    if (conv) conv.pinned = data.pinned
  }

  async function archive(id) {
    const { data } = await archiveConversationApi(id)
    const conv = conversations.value.find(c => c.id === id)
    if (conv) conv.archived = data.archived
  }

  function toggleShowArchived() {
    showArchived.value = !showArchived.value
  }

  async function updateSystemPrompt(conversationId, systemPrompt) {
    await updateSystemPromptApi(conversationId, systemPrompt)
    const conv = conversations.value.find(c => c.id === conversationId)
    if (conv) conv.system_prompt = systemPrompt
  }

  return {
    conversations, currentId, messages, loading, models, currentModel,
    showArchived, filteredConversations, pinnedConversations, normalConversations,
    loadConversations, newConversation, selectConversation, sendMessage,
    rename, remove, regenerate, stopStreaming, loadModels, setModel, exportCurrent,
    editMessage, deleteMessage, pin, archive, toggleShowArchived,
    updateSystemPrompt,
  }
})
